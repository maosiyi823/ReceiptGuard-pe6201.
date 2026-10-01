# Evaluation and saved-results explainer

## Three kinds of evidence
1. **Unit tests** in `../tests/` check software behavior offline, including simulated API responses. Passing tests is not a model accuracy score.
2. **Development experiments** reuse 14 cases to inspect errors and revise prompts/validation. They are not held-out final results.
3. **Frozen final evaluation** scores 50 synthetic cases once under the archived implementation and labels. No new inference was performed for this documentation update.

## Saved experiments
All timestamped records below are from 24 September 2026; directory timestamps are UTC.

| Record | Meaning |
|---|---|
| [First API call](first_ai_20260924T115812063749Z.json) | One successful live extraction, not a benchmark |
| [Development run 1](development_20260924T120434935194Z/) | Fourteen original live predictions: Regex 8/14 and AI 9/14 correct automated handling |
| [Development run 2](development_20260924T121101736093Z/) | Fourteen revised-prompt live predictions; AI still 9/14 despite addressing earlier guesses |
| [Offline replay](development_v1_outputs_validation_v02_replay.json) | Earlier saved outputs processed through revised validation; no new model calls |
| [Final run](final_20260924T122051343232Z/) | Authoritative 50-case frozen test: per-case outputs, summary and copied freeze manifest |

`cases.jsonl` has one JSON object per attempted case with its ID, Regex and AI outputs, API usage/log information and timing. Predictions retain fields, evidence, checks, status and review reasons; validation also preserves raw fields for comparison. `summary.json` aggregates outcomes; development and final summaries have different schemas. Final `headline_metrics` is populated only for a complete run. `freeze_manifest.json` identifies the evaluated dataset and implementation. An incomplete run is not a final score.

## Evaluation implementation and definitions
`receiptguard.py:evaluate` computes primary decisions and routing. `fields_match` compares dates/currencies exactly and totals with Decimal numeric equality. `run_development.py:score` adds per-field accuracy and review rate; `run_final.py:metrics` adds raw-field and applicable-rule accuracy. `run_final.py:report` aggregates groups, fixed references, costs and timing. Both extractors receive identical text and feed the same evidence validation and policy checks in these runners.

| Metric | Numerator / denominator |
|---|---|
| Correct automated handling | Non-ABSTAIN predictions with correct status AND all three required fields / all cases |
| Coverage | Non-ABSTAIN predictions / all cases |
| Answered accuracy | Correct automated handling count / non-ABSTAIN count; undefined if none answered |
| Routing accuracy | Correct PASS, FLAG or ABSTAIN status / all cases; ignores field correctness |
| Field accuracy including nulls | Matching value for the named field / all cases; matching null counts as correct |
| Violation recall | Expected FLAG cases predicted FLAG / expected FLAG cases |
| False releases | Count of expected non-PASS cases predicted PASS; not every possible field error |
| Required abstention recall | Expected ABSTAIN cases predicted ABSTAIN / expected ABSTAIN cases |
| Over-abstention | Expected non-ABSTAIN cases predicted ABSTAIN |
| Human review rate | FLAG plus ABSTAIN predictions / all cases |
| Applicable-rule accuracy | Correct check outcome / cases whose expected check is not null |

Raw-field and validated-field scores must not be conflated. Abstention earns no automatic-completion credit, including a correct abstention. FLAG counts as an answered decision but still requires human review.

## Final results and interpretation
| Measure | Regex | AI |
|---|---:|---:|
| Correct automated handling | 38/50 (76%) | 45/50 (90%) |
| Coverage | 38/50 (76%) | 45/50 (90%) |
| Answered accuracy | 38/38 (100%) | 45/45 (100%) |
| Routing | 43/50 (86%) | 50/50 (100%) |
| Date / currency / total accuracy | 48/50; 50/50; 43/50 | 50/50; 50/50; 49/50 |
| Violation recall | 25/29 | 29/29 |
| Mandatory / unnecessary abstentions | 5 / 7 | 5 / 0 |
| False releases observed | 0 | 0 |
| Human review | 37/50 | 34/50 |

Five mandatory abstentions cap valid automatic completion at 45/50. AI still made an item-price-as-total error in an abstained case: 100% routing is not perfect extraction. The improvement over this baseline is seven cases (14 percentage points). On simulated noise it is 7/12 versus 12/12; on different-model cases, 7/10 versus 9/10. Small, constructed subgroups do not establish general superiority or production safety.

Always-ABSTAIN gets 5/50 correct routing but zero automatic completion. Always-PASS, chosen from development data, gets 16/50 routing. FLAG is the largest final-test class (29/50), descriptive context rather than a baseline selected before testing. The simple Regex baseline can be improved; this is not a comparison against all rule-based methods.

Saved API usage totals are 20,445 input and 3,377 output tokens, USD 0.00509295 total and USD 0.000101859 per receipt. Mean AI pipeline latency is about 1.977 seconds, including local processing around the request. Eighty receipts/day would imply USD 0.00814872/day in model usage only. OCR, infrastructure, funding fees and reviewer labor are excluded. Costs are recorded usage, not current price quotations.

## Reproduce offline
Run from `receiptguard/`:
```sh
python3 -m unittest discover -s tests -v
python3 -c "from run_final import verify; print(verify()['status'])"
python3 compare_development.py
```

Expected: all 40 tests pass, verification prints `FROZEN_BEFORE_PREDICTIONS`, and comparison writes `results/development_comparison.md`. That Markdown file is a derived report, not an additional experiment.

To recompute final metrics without an API key or writing results:
```sh
python3 - <<'PYCODE'
import json
from pathlib import Path
from run_final import report, verify
verify()
frozen = Path('data/frozen_v1')
inputs = json.loads((frozen / 'inputs.json').read_text())
labels = json.loads((frozen / 'labels.json').read_text())
rows = [json.loads(line) for line in Path('results/final_20260924T122051343232Z/cases.jsonl').read_text().splitlines()]
assert [x['case_id'] for x in inputs] == [x['case_id'] for x in labels] == [x['case_id'] for x in rows]
cases = [{**x, **y} for x, y in zip(inputs, labels)]
print(json.dumps(report(cases, rows), indent=2))
PYCODE
```

`python3 replay_development.py` replays old outputs without inference but overwrites the working copy's replay JSON; use a separate copy. Optional live development and final requests are documented in the [root README](../../README.md). Final re-runs are deliberately blocked when a final directory exists; do not replace the archived 24 September results or call a tuned re-run an unseen test.

## Single-command submission check
From `receiptguard/`, run `python3 verify_submission.py`. This read-only, offline check rejects missing, duplicate or misaligned cases, changed frozen bytes, inconsistent reference decisions and a saved summary that differs from recomputation. It does not make fresh predictions. The [author review](../data/AUTHOR_REVIEW.md) is a later semantic label review, not a new experiment or independent annotation.
