# Gateway v1: end-to-end evaluation

Every row was sent to `POST /v1/check/input` (L0 normalizer → L1 rules + memory → L2 routed ensemble → session escalation → L3 Qwen3Guard judge when judge_low ≤ risk < block), in-process with the real models (`scripts/eval_gateway.py`). **Full gateway** counts action `block` (HTTP 413 refusals counted as block). **L2 only** counts the routed L2 model over its threshold on the same request. `warn` is not counted as a block. Language for routing comes from the shared detector (`pehredar/langid.py`), not from the dataset label. Translated sets are machine-translated (see `results/clf_v2.md` limitations).

- L2: {"loaded": ["deberta", "v2"], "errors": {}, "load_seconds": {"deberta": 4.25, "v2": 4.86}, "device": "cuda", "vram_allocated_gb": 1.72, "thresholds": {"deberta": 0.5, "v2": 0.738341212272644}}
- GPU memory: {"after_run_all_models_loaded": {"used_mib": 6209, "total_mib": 10240}, "l2_torch_allocated_gb": 1.72}
- Requests: 6292; L3 judge calls: 117 (1.9%)

| Eval set | Full gateway recall [95% CI] | Full gateway FPR [95% CI] | L2-only recall [95% CI] | L2-only FPR [95% CI] | warn | L3 calls | L3 outcome | rule hits | detected language |
|---|---|---|---|---|---:|---:|---|---:|---|
| external_eval | 0.695 (137/197) [0.628–0.755] | 0.016 (5/309) [0.007–0.037] | 0.690 (136/197) [0.623–0.751] | 0.016 (5/309) [0.007–0.037] | 0 | 1 | {"judge_unsafe": 1} | 2 | {"en": 506} |
| injecagent (unseen) | 0.667 (703/1054) [0.638–0.695] | n/a | 0.657 (693/1054) [0.628–0.685] | n/a | 18 | 40 | {"judge_controversial": 16, "judge_unsafe": 10} | 0 | {"en": 1054} |
| bipia (unseen) | 0.104 (13/125) [0.062–0.170] | n/a | 0.104 (13/125) [0.062–0.170] | n/a | 1 | 1 | {} | 0 | {"en": 125} |
| xstest FPR | n/a | 0.000 (0/249) [0.000–0.015] | n/a | 0.000 (0/249) [0.000–0.015] | 0 | 0 | {} | 0 | {"en": 249} |
| or_bench FPR | n/a | 0.065 (86/1319) [0.053–0.080] | n/a | 0.065 (86/1319) [0.053–0.080] | 2 | 2 | {"judge_controversial": 1} | 0 | {"en": 1319} |
| benign_email_probe FPR | n/a | 0.000 (0/100) [0.000–0.037] | n/a | 0.000 (0/100) [0.000–0.037] | 0 | 0 | {} | 0 | {"en": 100} |
| external_translated roman_ur | 0.500 (20/40) [0.352–0.648] | 0.061 (7/115) [0.030–0.120] | 0.500 (20/40) [0.352–0.648] | 0.061 (7/115) [0.030–0.120] | 0 | 1 | {} | 0 | {"en": 150, "roman_ur": 4, "mixed": 1} |
| external_translated mixed | 0.562 (27/48) [0.423–0.693] | 0.071 (11/155) [0.040–0.123] | 0.562 (27/48) [0.423–0.693] | 0.071 (11/155) [0.040–0.123] | 1 | 4 | {"judge_controversial": 1} | 0 | {"roman_ur": 5, "en": 198} |
| overrefusal_translated FPR roman_ur | n/a | 0.410 (470/1147) [0.382–0.439] | n/a | 0.403 (462/1147) [0.375–0.431] | 15 | 31 | {"judge_controversial": 12, "judge_unsafe": 8} | 0 | {"en": 1086, "roman_ur": 61} |
| overrefusal_translated FPR mixed | n/a | 0.343 (492/1434) [0.319–0.368] | n/a | 0.341 (489/1434) [0.317–0.366] | 20 | 37 | {"judge_controversial": 12, "judge_unsafe": 3} | 0 | {"en": 1339, "roman_ur": 95} |

## Latency (ms)

| Layer | median | p95 | requests that ran it |
|---|---:|---:|---:|
| normalization | 0.02 | 0.04 | 6292 |
| rules | 0.02 | 0.05 | 6292 |
| l2 | 21.38 | 46.57 | 6292 |
| memory | 0.35 | 0.46 | 6292 |
| session | 0.0 | 0.0 | 6292 |
| judge | 133.52 | 260.53 | 117 |
| end_to_end | 141.76 | 299.86 | 6292 |

End-to-end = client-side time for one in-process `/v1/check/input` call (includes the judge when called and the decision log write). Judge latency is over judged requests only.

