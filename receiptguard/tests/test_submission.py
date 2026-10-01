"""Corruption and alignment regression checks for the offline submission verifier."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from verify_submission import ROOT, FINAL, check_alignment, check_reference_policy, check_submission, compare


class SubmissionVerificationTests(unittest.TestCase):
    def test_archived_submission_passes(self):
        result = check_submission()
        self.assertEqual(result['correct_automated'], {'regex': 38, 'ai': 45})

    def test_duplicate_ids_are_rejected(self):
        records = [{'case_id': 'a'}, {'case_id': 'a'}]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            check_alignment(records, records, records, 2)

    def test_reordered_labels_are_rejected(self):
        records = [{'case_id': 'a'}, {'case_id': 'b'}]
        with self.assertRaisesRegex(ValueError, 'order mismatch'):
            check_alignment(records, list(reversed(records)), records, 2)

    def test_missing_prediction_is_rejected(self):
        records = [{'case_id': 'a'}, {'case_id': 'b'}]
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            check_alignment(records, records, records[:1], 2)

    def test_wrong_reference_status_is_rejected(self):
        item = {'case_id': 'example', 'claim_metadata': {'claim_category': 'meal', 'submission_date': '2026-09-24'}}
        label = {'ground_truth_fields': {'receipt_date': '2026-09-24', 'currency': 'SGD', 'total': '51.00'},
                 'expected_status': 'PASS', 'expected_checks': {'meal_limit': False, 'submission_window': True}}
        with self.assertRaisesRegex(ValueError, 'Reference status mismatch'):
            check_reference_policy([item], [label])

    def test_numeric_boolean_confusion_is_rejected(self):
        with self.assertRaises(ValueError):
            compare({'complete': True}, {'complete': 1})

    def test_tampered_summary_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'receiptguard'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__'))
            path = copy / FINAL / 'summary.json'
            summary = json.loads(path.read_text())
            summary['headline_metrics']['ai']['correct_automated_count'] = 50
            path.write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, 'correct_automated_count'):
                check_submission(copy)

    def test_missing_snapshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'receiptguard'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__'))
            (copy / 'data/frozen_v1/code_snapshot/receiptguard.py').unlink()
            with self.assertRaisesRegex(ValueError, 'snapshot files'):
                check_submission(copy)

    def test_frozen_input_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'receiptguard'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__'))
            path = copy / 'data/frozen_v1/inputs.json'
            path.write_text(path.read_text() + '\n')
            with self.assertRaisesRegex(ValueError, 'Frozen file changed'):
                check_submission(copy)


if __name__ == '__main__':
    unittest.main()
