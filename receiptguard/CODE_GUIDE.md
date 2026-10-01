# File and module guide

## Reading order and interfaces
Start with [PRODUCT.md](PRODUCT.md) for the input/output contract and architecture, then read `receiptguard.py`, `common_validation.py`, `ai_client.py` and the runners. The [data](data/README.md) and [evaluation](results/README.md) explainers identify the reference files.

Extraction functions return a dictionary containing `fields`, `evidence` and `issues`. Shared validation normalizes/checks the extraction and retains original fields. Policy assessment combines extraction with claim metadata and adds checks, status, review flag and reasons. Evaluation compares these predictions with separate local labels; the hosted model never scores its own answers.

## Core modules (historical frozen bytes retained)
| File | Responsibility and boundary |
|---|---|
| `receiptguard.py` | `extract` uses Regex to parse text; `assess` applies Decimal money and ISO-date rules; `fields_match` and `evaluate` score outputs. The standalone CLI is a development Regex demonstration and does not apply the extra shared validator used by the comparative runners. No network calls. |
| `common_validation.py` | `validate_evidence` checks source evidence, formats and ambiguity for both methods. Preserves raw fields; source occurrence does not prove semantic correctness. No network calls. |
| `ai_client.py` | Constructs the OpenRouter GPT-4o-mini request using the extraction prompt, validates returned structure, records response/usage, and surfaces connection failures. It does not decide reimbursement policy. API credentials are not persisted. |
| `run_development.py` | Loads 14 development fixtures, calls both pipelines, checkpoints JSONL after each case and saves summary metrics. Hidden terminal key prompt; paid API calls; stops on connection failure with no automatic retries. Shared `score` is also used by final evaluation. |
| `run_final.py` | `verify` checks archived hashes; `metrics`/`report` aggregate frozen-case predictions. The main entry point verifies data/code, blocks an existing final run and performs up to 50 paid requests. Partial runs do not receive headline final metrics. |
| `prompts/extract_v2.txt` | Active extraction instructions; part of the freeze. `extract_v1.txt` is retained as an earlier prompt version, not selected automatically by current runners. |

The freeze hashes the five core Python files, active prompt and selected data artifacts. This guide documents their module interfaces without editing those historical files or recomputing their manifest. Any future logic changes require a separately versioned experiment.

## Supporting modules and side effects
| File | Inputs, outputs and side effects |
|---|---|
| `first_ai_run.py` | One synthetic receipt -> a real API response and timestamped record. Paid smoke test, not evaluation evidence by itself. |
| `prepare_independent.py` | Generation prompt -> different-model candidate inputs, proposed labels and generation record. Calls a hosted model; does not freeze or evaluate the cases. |
| `prompts/independent_cases_v1.txt` | Instructions for different-model candidate generation, distinct from the extraction prompt. |
| `data/generate_dev.py` | Writes deterministic development fixtures; run in a separate experimental copy to preserve evidence. |
| `data/generate_test_candidate.py` | Seeded synthetic candidates -> separate input, label and manifest files; no extractor/model call. |
| `data/assemble_reviewed.py` | Local and different-model candidates -> reviewed dataset and correction/audit records. No model calls; output files may be replaced. |
| `compare_development.py` | Reads saved development/replay evidence -> `results/development_comparison.md`; no model calls or frozen-data edits. |
| `replay_development.py` | Applies revised validation to archived extraction outputs -> replaces the working copy's replay JSON. No model calls; run in a separate copy. |
| `demo/build_demo.py` | Saved evaluation records and `template.html` -> `index.html`. Builds an offline display, not a live upload or inference service. |
| `.command` launchers | macOS wrappers for the relevant Python entry points or demo; use the documented Python commands if executable permissions are missing. |

The Python runtime uses the standard library. The HTML demo can be opened locally without an API key. Live calls require network access, an OpenRouter key and usage charges. The credentials prompt requires a terminal; failed or noninteractive key entry must not silently submit requests.

## Test modules
Run `python3 -m unittest discover -s tests -v` from this directory. The 40 tests are offline; mocked responses do not measure hosted-model quality.

| Test file | Review focus |
|---|---|
| `tests/test_core.py` | Extraction, policy decisions and metric behavior |
| `tests/test_guardrails.py` | Evidence, ambiguity and conservative validation behavior |
| `tests/test_ai_client.py` | API response parsing and failure handling using simulated responses |
| `tests/test_development.py` | Development scoring and summary behavior |
| `tests/test_final.py` | Final evaluation completeness, subgroup reporting, fixed references and missing-cost handling |
| `tests/test_submission.py` | Evidence integrity, duplicate/misaligned cases, missing snapshots, inconsistent labels and changed saved scores |

See function and test names for individual checks. No line-by-line commentary is needed to understand the main responsibility of each module. Tests complement, but do not replace, the synthetic evaluation or future real-receipt validation.

## Submission verification added on 2 October 2026
`verify_submission.py` reads frozen data and saved predictions, rejects duplicate/misaligned IDs and incomplete runs, validates reference-rule consistency, compares frozen snapshot copies and recalculates the saved summary. It performs no network calls and writes no files. It supplements the historical runner without changing its evaluated behavior. Errors return a nonzero exit code. `tests/test_submission.py` checks corruption, alignment, and metric mismatch failures in isolated temporary copies.

The verifier's policy-consistency check uses label fields; it cannot independently infer reference fields from arbitrary receipt wording. That semantic review is documented separately in `data/AUTHOR_REVIEW.md`.
