# ReceiptGuard

See the [product documentation](PRODUCT.md), [data explainer](data/README.md), [evaluation explainer](results/README.md) and [module guide](CODE_GUIDE.md) for the complete submission documentation.

Receipt-text extraction using a Regex baseline or GPT-4o-mini, followed by shared evidence validation and deterministic reimbursement rules.

## Run locally

Python 3.9 or later; standard library only.

Open `demo/index.html` in a browser to explore the saved 50-case evaluation. This is an offline viewer of recorded outputs, not live inference.

From this directory:

```sh
python3 -m unittest discover -s tests -v
python3 verify_submission.py
```

For live extraction, run `python3 first_ai_run.py`. An OpenRouter API key is entered at a hidden prompt and is not saved. Paid usage may apply. `python3 run_development.py` runs 14 development cases.

## Evaluation

The frozen test contains 50 synthetic text receipts, including simulated noise. It contains no real receipt photographs and does not evaluate image OCR. Forty cases were generated locally; ten were generated with Gemini 2.5 Flash-Lite. Labels were reviewed with AI assistance before evaluation; independent human annotation is not claimed. Generation scripts, original candidate records, corrections and frozen hashes are retained under `data/`.

The saved final run is in `results/final_20260924T122051343232Z/`.

| Metric | Regex + rules | AI + rules |
|---|---:|---:|
| Correct automated handling | 38/50 | 45/50 |
| Correct routing including abstention | 43/50 | 50/50 |
| Abstentions | 12/50 | 5/50 |
| Total-field accuracy | 43/50 | 49/50 |

Correct automated handling requires the correct non-abstaining decision and all required fields. Abstention earns no credit in that metric. Five cases require abstention. Correct handling includes flagging violations, so 90% is not an approval rate. An item price was incorrectly extracted as a total in one abstained AI case.

`run_final.py` verifies frozen hashes and refuses to overwrite an existing final run. For a new paid experiment, use a separate project copy and move its existing `results/final_*` folder outside `results/`, preserving the original archive. Then run `python3 run_final.py`. Do not describe a rerun tuned on these test results as an unseen evaluation.

## Policy and scope

Meal claims must be in SGD, have a positive total no greater than SGD 50, and be submitted within 0–30 days of purchase. Missing or ambiguous required information produces ABSTAIN; policy violations produce FLAG. Both require review. PASS is not payment authorization.

The active prompt is `prompts/extract_v2.txt`. Image OCR, arithmetic reconciliation and tax-ID verification are not implemented. Small synthetic-test results do not establish production performance.

## Experiment and review record

Gemini generated ten candidate cases; GPT-4o-mini performed extraction. Mao Siyi ran the API experiments locally and subsequently personally reviewed all 50 frozen receipt texts and reference labels and confirmed that no corrections were needed. Completion was confirmed on 2 October 2026, after the original evaluation; this is author review, not independent third-party annotation. See the [author review record](data/AUTHOR_REVIEW.md).
