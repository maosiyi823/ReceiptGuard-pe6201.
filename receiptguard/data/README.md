# Data explainer

## What was evaluated
All receipt text is synthetic. Merchant names and transactions are fictional. The development suite has 14 cases; the frozen final suite has 50 cases evaluated on 24 September 2026. Simulated OCR-like text noise is not image OCR. These cases are a deliberately challenging suite, not a representative sample of business claims.

## File map and provenance
| Location | Role |
|---|---|
| `dev.json` | Fourteen development cases used for iteration; includes expected fields and statuses |
| `generate_dev.py` | Deterministic, hand-designed development-fixture generator |
| `generate_test_candidate.py` | Seeded local candidate generator (seed 62012026); does not call an extractor |
| `test_candidate_inputs.json`, `test_candidate_labels.json`, `test_candidate_manifest.json` | Original 50 local candidates and provenance; not the final benchmark |
| `independent/20260924T121556999530Z/` | Original Gemini 2.5 Flash-Lite generation record, ten inputs and proposed labels |
| `assemble_reviewed.py` | Combines selected local candidates with ten different-model cases and applies documented corrections |
| `reviewed/` | Assembled inputs, labels, correction log, label audit and manifest preceding freezing |
| `frozen_v1/` | Authoritative final inputs, labels, correction log, label audit, SHA-256 manifest and code snapshot |

The final set contains **40 local cases and 10 Gemini cases**, with 16 clean-varied, 17 distractor, 12 simulated-noise and five insufficient-information cases. Expected statuses are 16 PASS, 29 FLAG and five ABSTAIN. The original candidate distribution differs; do not score the original candidates and call that the saved final experiment.

`independent` denotes a different generation model, not fully independent human authorship. The implementation assistant reviewed proposed labels before scoring. Subsequently, Mao Siyi personally reviewed all 50 frozen cases and confirmed no corrections were needed, with completion confirmed on 2 October 2026. See [AUTHOR_REVIEW.md](AUTHOR_REVIEW.md) for the retrospective author review. Independent third-party verification is not claimed. Two proposed status/reason annotations were corrected, and grouping and interpretation decisions are recorded in [label_corrections.json](frozen_v1/label_corrections.json). Unmodified generator responses remain available for comparison. Another model's answer is not treated as automatically correct.

## Schema and concrete example
Each input has a stable `case_id`, `receipt_text` and `claim_metadata`. This example is the first frozen input:
```json
{
  "case_id": "candidate-001",
  "receipt_text": "Merchant: Practice Kitchen 01\nDate: 2026-09-03\nCurrency: SGD\nTotal: 20.70",
  "claim_metadata": {"claim_category": "meal", "submission_date": "2026-09-24"}
}
```

Expected labels are stored separately in `frozen_v1/labels.json`, aligned by case ID and order. They include `ground_truth_fields`, `expected_status`, `expected_checks`, grouping and provenance. Required fields are date, currency and total; merchant is not part of the primary required-field score. Null means the answer cannot be established under the annotation convention. A null is not zero. Expected checks use null when a rule cannot be evaluated.

Claim metadata is used locally for policy checks. Neither expected answers, expected checks, difficulty groups nor provenance tags are sent to GPT-4o-mini. Inputs alone do not include reference answers. The final runner merges inputs and labels locally for scoring; alignment must be maintained.

## Freeze and reproducibility
The [manifest](frozen_v1/manifest.json) records `FROZEN_BEFORE_PREDICTIONS`, freeze time `2026-09-24T12:20:16.374552+00:00`, 50 cases, zero prediction runs at freeze, model settings, evaluation definitions and hashes. The saved final result directory is `../results/final_20260924T122051343232Z/`.

From the application directory (`receiptguard/`), verify offline:
```sh
python3 -c "from run_final import verify; print(verify()['status'])"
```

Expected output is `FROZEN_BEFORE_PREDICTIONS`. This checks current bytes against the saved manifest; it is an integrity check, not independent proof of the entire experimental history. Preserve the historical manifest, snapshot, inputs and answers unchanged. Generating candidates is different from reproducing hosted model generation: future API responses may differ even at temperature zero. Run generation experiments in a separate copy and retain their new provenance.

`arithmetic_audit.json` audits expected demo-policy labels; it does not mean the application reconciles subtotals, tax and totals. See the [evaluation explainer](../results/README.md) for scoring and the [product document](../PRODUCT.md) for scope and target changes.
