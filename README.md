# ReceiptGuard

PE6201 coursework prototype by Mao Siyi. ReceiptGuard compares Regex with GPT-4o-mini extraction and applies shared deterministic reimbursement checks. It processes synthetic receipt **text**, not receipt photographs.

## Documentation map

- [Product documentation](receiptguard/PRODUCT.md): persona, inputs, outputs, architecture, targets and reached metrics.
- [Data explainer](receiptguard/data/README.md): dataset roles, schema, provenance, corrections and freezing.
- [Evaluation explainer](receiptguard/results/README.md): experiment history, scoring definitions, results and offline recomputation.
- [Author review record](receiptguard/data/AUTHOR_REVIEW.md): completed personal label review and its timing.
- [File and module guide](receiptguard/CODE_GUIDE.md): code responsibilities, dependencies and side effects.

The documentation and offline verification tools were updated on 2 October 2026. The frozen implementation, datasets and saved experimental outputs remain those of 24 September 2026; this update performs no new model evaluation.

## Repository layout

The application is in the [`receiptguard/`](receiptguard/) directory. This README is intended for the repository root. This repository contains the code, product documentation, data and evaluation evidence. The written report and recorded video are separate coursework submissions and are not included here.

| Directory | Contents |
|---|---|
| [`receiptguard/`](receiptguard/) | Python extraction, validation and evaluation programs |
| [`data/`](receiptguard/data/) | Development data, generation tools, source records and frozen test data |
| [`prompts/`](receiptguard/prompts/) | Versioned extraction and different-model generation prompts |
| [`results/`](receiptguard/results/) | Recorded development experiments and the final evaluation |
| [`tests/`](receiptguard/tests/) | Offline unit tests, including simulated API responses |
| [`demo/`](receiptguard/demo/) | Offline viewer and its build script |

## Observed frozen-test results

| Metric | Regex + rules | AI + rules |
|---|---:|---:|
| Correct automated handling | 38/50 (76%) | 45/50 (90%) |
| Correct routing including abstention | 43/50 | 50/50 |
| Abstentions | 12/50 | 5/50 |
| Total-field accuracy | 43/50 | 49/50 |
| False releases observed | 0 | 0 |

The final evaluation was run on 24 September 2026 on 50 frozen synthetic cases. Five cases intentionally require abstention. Correct automatic handling includes flagging violations: **90% is not an automatic-approval rate**. The AI pipeline returned 16 PASS, 29 FLAG and 5 ABSTAIN. One item-price/total error remained in an abstained case. These are small-sample synthetic results, not evidence of production safety.

## Start without an API key

Python 3.9+; standard library only. No package installation is required.

1. Download or clone the repository. Open `receiptguard/demo/index.html` in a browser, or on macOS double-click `Open Demo.command`. This shows **saved real API outputs**, not live inference.
2. From a terminal at the repository root, enter the application directory and run:

```sh
cd receiptguard
python3 -m unittest discover -s tests -v
python3 verify_submission.py
python3 compare_development.py
```

The 40 tests run offline; API-related tests use simulated responses. The verifier checks frozen hashes, snapshot copies, case alignment, reference-rule consistency and recomputed saved metrics; success prints `SUBMISSION_CHECK_PASSED`. It does not call a model or prove that every label interpretation is correct. The comparison command reads saved development outputs and writes `results/development_comparison.md`; it makes no model requests. All subsequent commands below assume you are inside `receiptguard/`.

Recorded final metrics are in [summary.json](receiptguard/results/final_20260924T122051343232Z/summary.json), with the 50 per-case outputs in [cases.jsonl](receiptguard/results/final_20260924T122051343232Z/cases.jsonl).

## Live requests (optional for inspecting the submitted evidence)

An OpenRouter account and API key are required. Paid usage may apply. Keys are entered with a hidden terminal prompt and are not saved. Do not put keys in source code, chat or GitHub.

```sh
python3 first_ai_run.py       # one synthetic receipt
python3 run_development.py   # 14 development requests
```

On macOS, the corresponding `.command` launchers can be double-clicked. If downloaded launcher permissions are absent, use the Python commands above.

The submitted final run is retained unchanged. `python3 run_final.py` intentionally refuses to repeat it if any `results/final_*` directory exists. To reproduce a fresh paid 50-case experiment, use a separate copy of the project, move the existing final-results directory OUTSIDE that copy's `results/` directory while preserving the original archive, then run `python3 run_final.py`. The runner verifies hashes first, saves each response, performs no automatic retries and stops on a connection error. Incomplete runs are not headline final scores. Do not tune the code or alter labels after reviewing final predictions and then describe a rerun as an unseen test.

## Architecture and demo policy

Receipt text -> Regex or hosted model -> shared evidence/format validation -> deterministic Python policy checks -> PASS / FLAG / ABSTAIN.

Demo policy: meal category, SGD, positive total at most SGD 50.00, submission 0–30 days after purchase. Missing, unsupported or ambiguous required information leads to ABSTAIN. FLAG and ABSTAIN require review. PASS is not payment authorization. Raw fields and evidence are preserved; evidence occurrence alone does not prove semantic correctness.

Abstention is triggered by missing or ambiguous required information, extraction issues and evidence/format validation. There is no calibrated model-confidence threshold.

The active extraction prompt is `prompts/extract_v2.txt`. Arithmetic reconciliation, tax-ID verification, image OCR, RAG, agents and LLM-as-judge scoring are not implemented. This is narrower than the initial proposal and is disclosed in the report.

## Data and reproducibility

- `data/dev.json`: 14 synthetic development cases.
- `data/frozen_v1/`: 50 frozen inputs, separate labels, corrections, code snapshot and SHA-256 manifest.
- Final composition: 40 locally generated cases and 10 contributed by Gemini 2.5 Flash-Lite, distinct from the GPT-4o-mini extractor.
- Groups: 16 clean varied, 17 distractor, 12 simulated-noise and 5 insufficient-information cases.
- Labels were checked with AI assistance before scoring. Mao Siyi later personally reviewed all 50 cases and confirmed no corrections were needed; see the [dated author review record](receiptguard/data/AUTHOR_REVIEW.md). Independent third-party annotation is not claimed.
- `data/independent/`: original generation response, prompt and proposed labels, retained for provenance.
- `data/generate_test_candidate.py` and `data/assemble_reviewed.py`: reproducible generation and assembly; generating candidates does not alter the frozen files.

See [label corrections](receiptguard/data/frozen_v1/label_corrections.json) and the [assembly script](receiptguard/data/assemble_reviewed.py) for the review decisions. The different-model generator made errors, including claiming 35 exceeds 50; these were corrected before scoring. This is not a wholly independent benchmark. Synthetic noise cannot establish real-photo/OCR performance.

## Development evidence

Development and final evaluation are separate experiments. The two development runs reuse the same 14 cases for iteration; they are not additional final-test cases.

| Evidence | Purpose |
|---|---|
| [First successful call](receiptguard/results/first_ai_20260924T115812063749Z.json) | One receipt passed through the hosted model and validation |
| [First development run](receiptguard/results/development_20260924T120434935194Z/) | Original 14-case outputs and summary |
| [Second development run](receiptguard/results/development_20260924T121101736093Z/) | Revised-prompt 14-case outputs and summary |
| [Offline replay](receiptguard/results/development_v1_outputs_validation_v02_replay.json) | Original outputs processed through revised validation; no new inference |

In the first development run, AI correctly automated 9/14 cases, versus 8/14 for Regex. Correct AI routing did not imply perfect fields: the model guessed USD from a bare dollar sign and selected a conflicting total in abstained cases. Shared validation and a revised prompt addressed these guesses, but the second live run omitted some otherwise available fields and still correctly automated 9/14 cases. These results are retained rather than selecting only favorable observations.

To reproduce the comparison, run `python3 compare_development.py`. To reproduce the offline replay, run `python3 replay_development.py` in a separate working copy: it overwrites that copy's saved replay JSON. Neither command calls a model. Neither modifies the frozen 50-case test or its final outputs.

## Metrics and interpretation

Correct automated handling requires a non-ABSTAIN prediction with the correct status and all required fields (date, currency and total). Its denominator is all 50 cases; abstention receives no automatic-completion credit. Routing accuracy checks only PASS / FLAG / ABSTAIN. Coverage is the fraction not abstained. FLAG is an answered decision but still requires human review.

The always-ABSTAIN reference achieves zero automated completion and 5/50 correct routing. The development-selected always-PASS reference achieves 16/50 correct routing. The largest final-test class is FLAG, 29/50; this is descriptive context, not a predictor selected before testing.

On the 12 simulated-noise cases, correct automated handling is 7/12 for Regex and 12/12 for AI. On the ten different-model cases, it is 7/10 and 9/10. No false releases were observed in this small set; this is not a guarantee. The AI pipeline still requires review for 34/50 cases (29 FLAG plus 5 ABSTAIN).

## Recorded cost and latency

The final 50 calls used 20,445 input tokens and 3,377 output tokens: averages of 408.90 and 67.54 per receipt. Recorded model usage cost was USD 0.00509295 total, or USD 0.000101859 per receipt. At 80 receipts per day, the illustrative model cost is USD 0.00814872 per day. Mean AI pipeline latency was approximately 1.977 seconds per receipt.

These amounts are computed from saved usage records, not current advertised prices. They exclude OCR, hosting, funding fees and human review. Eighty receipts per day is a scenario assumption. Model availability, pricing and outputs can change; temperature 0 does not guarantee identical future responses.

## Limitations

This is a bounded synthetic-text prototype, not a production reimbursement service. The Regex baseline is simple and can be strengthened. The benchmark was partly designed alongside the implementation and is not wholly independent. A substring evidence check can pass an incorrect interpretation: the final AI error promoted an item price to a total, although missing currency still caused ABSTAIN. Real-receipt validation and operational review would be required before deployment.

The `arithmetic_audit.json` files audit expected demo-policy labels; they do not mean the application implements subtotal-plus-tax reconciliation. The demo is an offline display of saved results, not a live API interface or payment approval screen.

## References

Accessed 24 September 2026:
- [OpenRouter quickstart](https://openrouter.ai/docs/quickstart)
- [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
- [GPT-4o-mini](https://openrouter.ai/openai/gpt-4o-mini)
- [Gemini 2.5 Flash-Lite](https://openrouter.ai/google/gemini-2.5-flash-lite)

Costs in the report come from saved API usage records, not quoted list-price estimates. Reported model costs exclude OCR, hosting, funding fees and human review.
