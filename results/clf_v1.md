# v1 Evaluation (v0, v1a, v1b, and baselines)

Thresholds are selected on `dev_public_v1b` for v1b; v0 retains its original threshold. The rows below separate seen and unseen indirect sources.

| Model | Eval row | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| v0 | dev_public_v1b | 0.7605 | 0.0186 | 0.8488 |
| v0 | external_eval | 0.0152 | 0.0000 | 0.0300 |
| v0 | bipia (unseen) | 0.0000 | n/a | 0.0000 |
| v0 | injecagent (unseen) | 0.0000 | n/a | 0.0000 |
| v0 | llmail (seen) | 0.9040 | n/a | 0.9496 |
| v0 | xstest FPR | n/a | 0.0000 | n/a |
| v0 | or_bench FPR | n/a | 0.0296 | 0.0000 |
| v0 | benign_email_probe | n/a | 1.0000 | 0.0000 |
| v1a_e1 | dev_public_v1b | 0.1324 | 0.0189 | 0.2274 |
| v1a_e1 | external_eval | 0.0000 | 0.0000 | 0.0000 |
| v1a_e1 | bipia (unseen) | 0.0000 | n/a | 0.0000 |
| v1a_e1 | injecagent (unseen) | 0.0000 | n/a | 0.0000 |
| v1a_e1 | llmail (seen) | 0.9120 | n/a | 0.9540 |
| v1a_e1 | xstest FPR | n/a | 0.0000 | n/a |
| v1a_e1 | or_bench FPR | n/a | 0.0000 | n/a |
| v1a_e1 | benign_email_probe | n/a | 0.9800 | 0.0000 |
| v1a_e2 | dev_public_v1b | 0.3614 | 0.0189 | 0.5188 |
| v1a_e2 | external_eval | 0.0000 | 0.0000 | 0.0000 |
| v1a_e2 | bipia (unseen) | 0.0000 | n/a | 0.0000 |
| v1a_e2 | injecagent (unseen) | 0.0000 | n/a | 0.0000 |
| v1a_e2 | llmail (seen) | 0.8505 | n/a | 0.9192 |
| v1a_e2 | xstest FPR | n/a | 0.0000 | n/a |
| v1a_e2 | or_bench FPR | n/a | 0.0000 | n/a |
| v1a_e2 | benign_email_probe | n/a | 1.0000 | 0.0000 |
| v1b_e1 | dev_public_v1b | 0.8810 | 0.0172 | 0.9225 |
| v1b_e1 | external_eval | 0.4873 | 0.0000 | 0.6553 |
| v1b_e1 | bipia (unseen) | 0.0480 | n/a | 0.0916 |
| v1b_e1 | injecagent (unseen) | 0.0266 | n/a | 0.0518 |
| v1b_e1 | llmail (seen) | 0.6805 | n/a | 0.8099 |
| v1b_e1 | xstest FPR | n/a | 0.0000 | n/a |
| v1b_e1 | or_bench FPR | n/a | 0.2638 | 0.0000 |
| v1b_e1 | benign_email_probe | n/a | 0.0300 | 0.0000 |
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

## Latency and VRAM

- Evaluation latency and cached prediction metadata are stored in `results/v1_evaluation.json`.
- v1b training peak VRAM: 5.24 GB; evaluation peak VRAM was not separately instrumented.

## Numbers-only comparison

- v1b unseen recall vs v0: bipia 0.0480 vs 0.0000; injecagent 0.0266 vs 0.0000.
- v1b unseen recall vs DeBERTa: bipia 0.0480 vs 0.1040; injecagent 0.0266 vs 0.6575.
- v1b OR-Bench FPR vs v0: 0.2638 vs 0.0296; vs DeBERTa: 0.2638 vs 0.0652.
- v1b email-probe FPR vs v0: 0.0300 vs 1.0000; vs DeBERTa: 0.0300 vs 0.0000.

## Limitations

- `llmail` is seen distribution; `bipia` and `injecagent` are unseen.
- `xstest` and `or_bench` are separate FPR rows.
- This is email-fix-only; the repeated synthetic email source is excluded from later training.
- No model was promoted to the gateway.
