# v1 Evaluation (v0, v1a, v1b, and baselines)

Classifier preprocessing: `raw-512-headtail-v1` (raw text, 512 tokens head+tail, shared with `train_v0.py` via `pehredar/clf_text.py`).

v0 and v1a are not scored on `dev_public_v1b` because it may contain their training rows.

## Thresholds

| Model | Threshold | Source |
|---|---:|---|
| v0 | 0.6423 | saved (training report) |
| v1a_e1 | 0.5725 | saved (training report) |
| v1a_e2 | 0.7162 | saved (training report) |
| v1b_e1 | 0.4375 | saved (training report) |
| v1b_e1@dev2% | 0.7098 | 2% benign FPR on dev_public_v1b |
| rules | 0.7500 | fixed |
| deberta | 0.5000 | fixed |

## Sanity check

- v0 external_eval recall: 0.6142 vs reference 0.6142. `results/clf_v0.md` reports 0.5939 because it used the old 256-token eval path; the same model reproduces 0.5939 at 256 tokens and 0.6142 at 512 head+tail.

## Main table

| Model | Eval row | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| v0 | external_eval | 0.6142 | 0.0065 | 0.7562 |
| v0 | bipia (unseen) | 0.0000 | n/a | 0.0000 |
| v0 | injecagent (unseen) | 0.0047 | n/a | 0.0094 |
| v0 | llmail (seen) | 0.9985 | n/a | 0.9992 |
| v0 | xstest FPR | n/a | 0.0000 | n/a |
| v0 | or_bench FPR | n/a | 0.2002 | 0.0000 |
| v0 | benign_email_probe | n/a | 1.0000 | 0.0000 |
| v1a_e1 | external_eval | 0.6751 | 0.0162 | 0.7940 |
| v1a_e1 | bipia (unseen) | 0.0640 | n/a | 0.1203 |
| v1a_e1 | injecagent (unseen) | 0.0569 | n/a | 0.1077 |
| v1a_e1 | llmail (seen) | 1.0000 | n/a | 1.0000 |
| v1a_e1 | xstest FPR | n/a | 0.0000 | n/a |
| v1a_e1 | or_bench FPR | n/a | 0.3609 | 0.0000 |
| v1a_e1 | benign_email_probe | n/a | 1.0000 | 0.0000 |
| v1a_e2 | external_eval | 0.7563 | 0.0162 | 0.8490 |
| v1a_e2 | bipia (unseen) | 0.0880 | n/a | 0.1618 |
| v1a_e2 | injecagent (unseen) | 0.0218 | n/a | 0.0427 |
| v1a_e2 | llmail (seen) | 1.0000 | n/a | 1.0000 |
| v1a_e2 | xstest FPR | n/a | 0.0000 | n/a |
| v1a_e2 | or_bench FPR | n/a | 0.4640 | 0.0000 |
| v1a_e2 | benign_email_probe | n/a | 1.0000 | 0.0000 |
| v1b_e1 | dev_public_v1b | 0.9357 | 0.0341 | 0.9388 |
| v1b_e1 | external_eval | 0.6599 | 0.0227 | 0.7784 |
| v1b_e1 | bipia (unseen) | 0.1200 | n/a | 0.2143 |
| v1b_e1 | injecagent (unseen) | 0.0825 | n/a | 0.1525 |
| v1b_e1 | llmail (seen) | 0.8455 | n/a | 0.9163 |
| v1b_e1 | xstest FPR | n/a | 0.0000 | n/a |
| v1b_e1 | or_bench FPR | n/a | 0.3753 | 0.0000 |
| v1b_e1 | benign_email_probe | n/a | 0.2500 | 0.0000 |
| v1b_e1@dev2% | dev_public_v1b | 0.9024 | 0.0200 | 0.9321 |
| v1b_e1@dev2% | external_eval | 0.5787 | 0.0032 | 0.7308 |
| v1b_e1@dev2% | bipia (unseen) | 0.0640 | n/a | 0.1203 |
| v1b_e1@dev2% | injecagent (unseen) | 0.0389 | n/a | 0.0749 |
| v1b_e1@dev2% | llmail (seen) | 0.7795 | n/a | 0.8761 |
| v1b_e1@dev2% | xstest FPR | n/a | 0.0000 | n/a |
| v1b_e1@dev2% | or_bench FPR | n/a | 0.2835 | 0.0000 |
| v1b_e1@dev2% | benign_email_probe | n/a | 0.2500 | 0.0000 |
| rules | dev_public_v1b | 0.0248 | 0.0124 | 0.0474 |
| rules | external_eval | 0.0102 | 0.0000 | 0.0201 |
| rules | bipia (unseen) | 0.0000 | n/a | 0.0000 |
| rules | injecagent (unseen) | 0.0000 | n/a | 0.0000 |
| rules | llmail (seen) | 0.0010 | n/a | 0.0020 |
| rules | xstest FPR | n/a | 0.0000 | n/a |
| rules | or_bench FPR | n/a | 0.0000 | n/a |
| rules | benign_email_probe | n/a | 0.0000 | n/a |
| deberta | dev_public_v1b | 0.7562 | 0.1715 | 0.7393 |
| deberta | external_eval | 0.6904 | 0.0162 | 0.8047 |
| deberta | bipia (unseen) | 0.1040 | n/a | 0.1884 |
| deberta | injecagent (unseen) | 0.6575 | n/a | 0.7934 |
| deberta | llmail (seen) | 0.4205 | n/a | 0.5920 |
| deberta | xstest FPR | n/a | 0.0000 | n/a |
| deberta | or_bench FPR | n/a | 0.0652 | 0.0000 |
| deberta | benign_email_probe | n/a | 0.0000 | n/a |

## Numbers-only comparison (generated)

- bipia unseen recall: 0.1200 (v1b saved) vs 0.0640 (v1b dev2%) vs 0.0000 (v0) vs 0.1040 (deberta)
- injecagent unseen recall: 0.0825 (v1b saved) vs 0.0389 (v1b dev2%) vs 0.0047 (v0) vs 0.6575 (deberta)
- external_eval recall: 0.6599 (v1b saved) vs 0.5787 (v1b dev2%) vs 0.6142 (v0) vs 0.6904 (deberta)
- OR-Bench FPR: 0.3753 (v1b saved) vs 0.2835 (v1b dev2%) vs 0.2002 (v0) vs 0.0652 (deberta)
- XSTest FPR: 0.0000 (v1b saved) vs 0.0000 (v1b dev2%) vs 0.0000 (v0) vs 0.0000 (deberta)
- email-probe FPR: 0.2500 (v1b saved) vs 0.2500 (v1b dev2%) vs 1.0000 (v0) vs 0.0000 (deberta)

## Latency and VRAM

- Evaluation latency and cached prediction metadata are stored in `results/v1_evaluation.json`.
- v1b training peak VRAM: 5.24 GB (from the training log); evaluation VRAM not instrumented.

## Limitations

- `llmail` is seen distribution; `bipia` and `injecagent` are unseen.
- `xstest` and `or_bench` are separate FPR rows.
- The `v1b_e1@dev2%` threshold is tuned on `dev_public_v1b`, so its dev row is optimistic.
- No model was promoted to the gateway.
