"""Read-only verification of archived ReceiptGuard evidence, without API calls.

Checks artifact integrity and alignment before calling the historical scorer.
Reference-policy consistency is checked separately with Decimal and date arithmetic;
it is not semantic validation of the receipt text or independent human annotation.
"""
import json
import math
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from run_final import report, verify

ROOT = Path(__file__).resolve().parent
FINAL = 'results/final_20260924T122051343232Z'


def read_json(path):
    """Reject non-standard numeric constants rather than accepting NaN/Infinity."""
    def reject(value):
        raise ValueError('Non-finite JSON constant: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=reject)


def case_ids(records, description):
    """Require unique nonempty string IDs; never silently truncate via zip."""
    if not isinstance(records, list) or not records:
        raise ValueError(description + ': expected a nonempty list')
    ids = [row.get('case_id') if isinstance(row, dict) else None for row in records]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError(description + ': missing or invalid case ID')
    if len(set(ids)) != len(ids):
        raise ValueError(description + ': duplicate case ID')
    return ids


def check_alignment(inputs, labels, rows, expected_count):
    """Check exact count, identity and order across all three evidence sources."""
    ids = [case_ids(items, name) for items, name in
           ((inputs, 'inputs'), (labels, 'labels'), (rows, 'predictions'))]
    if any(len(values) != expected_count for values in ids):
        raise ValueError('Incomplete or extra cases; expected ' + str(expected_count))
    if ids[0] != ids[1] or ids[0] != ids[2]:
        raise ValueError('Case identity/order mismatch')


def check_reference_policy(inputs, labels):
    """Recalculate documented reference checks from labels, not model outputs."""
    for item, label in zip(inputs, labels):
        fields = label['ground_truth_fields']
        metadata = item['claim_metadata']
        missing = any(fields.get(key) is None for key in ('receipt_date', 'currency', 'total'))
        unsupported = fields.get('currency') not in (None, 'SGD') or metadata.get('claim_category') != 'meal'
        amount_ok = None
        if fields.get('total') is not None:
            amount = Decimal(fields['total'])
            if not amount.is_finite() or amount <= 0 or amount != amount.quantize(Decimal('.01')):
                raise ValueError('Invalid reference amount: ' + item['case_id'])
            amount_ok = amount <= Decimal('50.00')
        window_ok = None
        if fields.get('receipt_date') is not None:
            age = (date.fromisoformat(metadata['submission_date']) - date.fromisoformat(fields['receipt_date'])).days
            window_ok = 0 <= age <= 30
        checks = {'meal_limit': amount_ok, 'submission_window': window_ok}
        expected = 'ABSTAIN' if missing or unsupported else ('FLAG' if False in checks.values() else 'PASS')
        if label['expected_status'] != expected:
            raise ValueError('Reference status mismatch: ' + item['case_id'])
        for name, value in checks.items():
            if label['expected_checks'].get(name) is not value:
                raise ValueError('Reference rule mismatch: ' + item['case_id'] + '/' + name)


def compare(expected, actual, path='summary'):
    """Compare a recomputed tree, with tight tolerance only for float rounding."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(expected) != set(actual):
            raise ValueError(path + ': different keys')
        for key in expected:
            compare(expected[key], actual[key], path + '/' + key)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            raise ValueError(path + ': different list shape')
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, path + '/' + str(index))
    elif type(expected) is float:
        if type(actual) not in (int, float) or not math.isclose(expected, actual, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(path + ': different numeric value')
    elif type(expected) is not type(actual) or expected != actual:
        raise ValueError(path + ': different value')


def check_submission(root=ROOT):
    """Return a compact report or raise on inconsistent archived evidence."""
    root = Path(root)
    manifest = verify(root)
    if manifest.get('count') != 50 or manifest.get('status') != 'FROZEN_BEFORE_PREDICTIONS':
        raise ValueError('Unexpected frozen evaluation contract')
    frozen = root / 'data/frozen_v1'
    snapshot_root = frozen / 'code_snapshot'
    expected_snapshots = {name for name in manifest['hashes'] if not name.startswith('data/')}
    actual_snapshots = {str(path.relative_to(snapshot_root)) for path in snapshot_root.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    if actual_snapshots != expected_snapshots:
        raise ValueError('Missing or unexpected snapshot files')
    for name in sorted(expected_snapshots):
        if (snapshot_root / name).read_bytes() != (root / name).read_bytes():
            raise ValueError('Snapshot mismatch: ' + name)
    folder = root / FINAL
    compare(manifest, read_json(folder / 'freeze_manifest.json'), 'copied manifest')
    inputs = read_json(frozen / 'inputs.json')
    labels = read_json(frozen / 'labels.json')
    lines = (folder / 'cases.jsonl').read_text(encoding='utf-8').splitlines()
    rows = [json.loads(line) for line in lines]
    check_alignment(inputs, labels, rows, manifest['count'])
    check_reference_policy(inputs, labels)
    for row in rows:
        for method in ('regex', 'ai'):
            if row[method]['status'] not in ('PASS', 'FLAG', 'ABSTAIN'):
                raise ValueError('Unknown prediction status')
            elapsed = row[method + '_seconds']
            if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
                raise ValueError('Invalid latency')
    cases = [{**item, **label} for item, label in zip(inputs, labels)]
    computed = report(cases, rows)
    saved = read_json(folder / 'summary.json')
    if saved.get('dataset_role') != 'FROZEN_SYNTHETIC_TEST_V1' or saved.get('interrupted') is not False:
        raise ValueError('Wrong dataset role or interrupted run')
    if set(saved) != set(computed) | {'dataset_role', 'interrupted'}:
        raise ValueError('Unexpected saved summary keys')
    compare(computed, {key: saved[key] for key in computed})
    if not computed['complete'] or computed['service_failures']:
        raise ValueError('Incomplete evaluation or service failure')
    return {'status': 'SUBMISSION_CHECK_PASSED', 'cases': len(rows),
            'frozen_status': manifest['status'],
            'correct_automated': {method: computed['headline_metrics'][method]['correct_automated_count']
                                  for method in ('regex', 'ai')},
            'scope': 'Archived integrity and scoring; not a fresh model evaluation or semantic label certification.'}


def main():
    try:
        result = check_submission()
    except (OSError, ValueError, TypeError, KeyError, IndexError, InvalidOperation) as exc:
        print('SUBMISSION_CHECK_FAILED: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
