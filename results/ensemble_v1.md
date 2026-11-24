# Ensemble evaluation v1

- `ensemble`: language-routed. `en` -> DeBERTa (threshold 0.5); `ur` / `roman_ur` / `mixed` -> v1b (saved threshold 0.4375).
- `ensemble_max`: attack if either model is over its own threshold.
- Language comes from each row's `lang` label.
- Translated dev rows: none. `translated_v2.jsonl` holds only translations of TRAIN-split rows, so no translated dev rows exist.
- Non-`en` rows per eval set (routed to v1b by `ensemble`): external_eval 0; indirect_eval 20; overrefusal_eval 0; benign_email_probe 0. On `en` rows `ensemble` equals DeBERTa.

| Model | Eval row | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| deberta | external_eval | 0.6904 | 0.0162 | 0.8047 |
| deberta | bipia (unseen) | 0.1040 | n/a | 0.1884 |
| deberta | injecagent (unseen) | 0.6575 | n/a | 0.7934 |
| deberta | llmail (seen) | 0.4205 | n/a | 0.5920 |
| deberta | xstest FPR | n/a | 0.0000 | n/a |
| deberta | or_bench FPR | n/a | 0.0652 | 0.0000 |
| deberta | benign_email_probe | n/a | 0.0000 | n/a |
| v1b_e1 | external_eval | 0.6599 | 0.0227 | 0.7784 |
| v1b_e1 | bipia (unseen) | 0.1200 | n/a | 0.2143 |
| v1b_e1 | injecagent (unseen) | 0.0825 | n/a | 0.1525 |
| v1b_e1 | llmail (seen) | 0.8455 | n/a | 0.9163 |
| v1b_e1 | xstest FPR | n/a | 0.0000 | n/a |
| v1b_e1 | or_bench FPR | n/a | 0.3753 | 0.0000 |
| v1b_e1 | benign_email_probe | n/a | 0.2500 | 0.0000 |
| ensemble | external_eval | 0.6904 | 0.0162 | 0.8047 |
| ensemble | bipia (unseen) | 0.1040 | n/a | 0.1884 |
| ensemble | injecagent (unseen) | 0.6575 | n/a | 0.7934 |
| ensemble | llmail (seen) | 0.4225 | n/a | 0.5940 |
| ensemble | xstest FPR | n/a | 0.0000 | n/a |
| ensemble | or_bench FPR | n/a | 0.0652 | 0.0000 |
| ensemble | benign_email_probe | n/a | 0.0000 | n/a |
| ensemble_max | external_eval | 0.7614 | 0.0356 | 0.8380 |
| ensemble_max | bipia (unseen) | 0.2240 | n/a | 0.3660 |
| ensemble_max | injecagent (unseen) | 0.6727 | n/a | 0.8043 |
| ensemble_max | llmail (seen) | 0.8715 | n/a | 0.9313 |
| ensemble_max | xstest FPR | n/a | 0.0000 | n/a |
| ensemble_max | or_bench FPR | n/a | 0.3942 | 0.0000 |
| ensemble_max | benign_email_probe | n/a | 0.2500 | 0.0000 |

## Numbers-only comparison (generated)

- external_eval recall: 0.6904 (deberta) vs 0.6599 (v1b_e1) vs 0.6904 (ensemble) vs 0.7614 (ensemble_max)
- bipia (unseen) recall: 0.1040 (deberta) vs 0.1200 (v1b_e1) vs 0.1040 (ensemble) vs 0.2240 (ensemble_max)
- injecagent (unseen) recall: 0.6575 (deberta) vs 0.0825 (v1b_e1) vs 0.6575 (ensemble) vs 0.6727 (ensemble_max)
- llmail (seen) recall: 0.4205 (deberta) vs 0.8455 (v1b_e1) vs 0.4225 (ensemble) vs 0.8715 (ensemble_max)
- xstest FPR: 0.0000 (deberta) vs 0.0000 (v1b_e1) vs 0.0000 (ensemble) vs 0.0000 (ensemble_max)
- or_bench FPR: 0.0652 (deberta) vs 0.3753 (v1b_e1) vs 0.0652 (ensemble) vs 0.3942 (ensemble_max)
- benign_email_probe fpr: 0.0000 (deberta) vs 0.2500 (v1b_e1) vs 0.0000 (ensemble) vs 0.2500 (ensemble_max)

## Limitations

- v1b is the interim multilingual classifier; v2 is not trained yet (waits for translation review).
- `llmail` is seen distribution for v1b; `bipia` and `injecagent` are unseen.
- No model was promoted to the gateway.
