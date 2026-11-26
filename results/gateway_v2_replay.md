# Gateway v2_replay: end-to-end evaluation

Every row was sent to `POST /v1/check/input` (L0 normalizer → L1 rules + memory → L2 routed ensemble → session escalation → L3 Qwen3Guard judge when judge_low ≤ risk < block), in-process with the real models (`scripts/eval_gateway.py`). **Full gateway** counts action `block` (HTTP 413 refusals counted as block). **L2 only** counts the routed L2 model over its threshold on the same request. `warn` is not counted as a block. Language for routing comes from the shared detector (`pehredar/langid.py`), not from the dataset label. Translated sets are Gemini machine translations (not the human test set).

- Config: {"PEHREDAR_GUARD_MODEL": "hf.co/QuantFactory/Qwen3Guard-Gen-0.6B-GGUF:Q4_K_M", "PEHREDAR_L2_XLMR_DIR": "/app/models/clf_v3_e3", "PEHREDAR_LANGID_MODEL": "/app/models/langid_v2.joblib"}; policy = {"l2": {"mode": "routed", "xlmr_threshold": 0.9613}, "judge": {"xlmr_floor": 0.0, "block_categories": null}}
- L2: {"loaded": ["deberta", "xlmr"], "errors": {}, "load_seconds": {"deberta": 4.17, "xlmr": 9.3}, "device": "cuda", "vram_allocated_gb": 1.72, "thresholds": {"deberta": 0.5, "xlmr": 0.9629704356193542}}
- GPU memory: {"after_run_all_models_loaded": {"used_mib": 5424, "total_mib": 10240}, "l2_torch_allocated_gb": 1.72}
- Requests: 9061; L3 judge calls: 905 (10.0%)

| Eval set | Full gateway recall [95% CI] | Full gateway FPR [95% CI] | L2-only recall [95% CI] | L2-only FPR [95% CI] | warn | L3 calls | L3 outcome | blocks by layer | detected language |
|---|---|---|---|---|---:|---:|---|---|---|
| external_eval | 0.685 (135/197) [0.617–0.746] | 0.016 (5/309) [0.007–0.037] | 0.680 (134/197) [0.612–0.741] | 0.016 (5/309) [0.007–0.037] | 1 | 3 | {"judge_category:Unethical Acts": 1, "judge_controversial": 1, "judge_category:Jailbreak": 1, "judge_unsafe": 1} | {"L2": 137, "L1 rules": 2, "L3 judge": 1} | {"en": 495, "mixed": 11} |
| injecagent (unseen) | 0.666 (702/1054) [0.637–0.694] | n/a | 0.657 (693/1054) [0.628–0.685] | n/a | 19 | 40 | {"judge_category:PII": 25, "judge_unsafe": 9, "judge_controversial": 16} | {"L2": 693, "L3 judge": 9} | {"en": 1054} |
| bipia (unseen) | 0.104 (13/125) [0.062–0.170] | n/a | 0.104 (13/125) [0.062–0.170] | n/a | 1 | 1 | {} | {"L2": 13} | {"en": 124, "mixed": 1} |
| xstest FPR | n/a | 0.000 (0/249) [0.000–0.015] | n/a | 0.000 (0/249) [0.000–0.015] | 0 | 0 | {} | {} | {"en": 249} |
| or_bench FPR | n/a | 0.070 (92/1319) [0.057–0.085] | n/a | 0.068 (89/1319) [0.055–0.082] | 2 | 6 | {"judge_category:Non-violent Illegal Acts": 3, "judge_unsafe": 3, "judge_category:Unethical Acts": 1, "judge_controversial": 1} | {"L2": 89, "L3 judge": 3} | {"en": 1304, "mixed": 15} |
| benign_email_probe FPR | n/a | 0.000 (0/100) [0.000–0.037] | n/a | 0.000 (0/100) [0.000–0.037] | 0 | 0 | {} | {} | {"en": 100} |
| external_translated roman_ur | 0.647 (77/119) [0.558–0.727] | 0.030 (8/262) [0.016–0.059] | 0.613 (73/119) [0.524–0.696] | 0.023 (6/262) [0.011–0.049] | 44 | 60 | {"judge_category:Unethical Acts": 3, "judge_unsafe": 6, "judge_category:Politically Sensitive Topics": 2, "judge_controversial": 15, "judge_category:Sexual Content or Sexual Acts": 9, "judge_category:Jailbreak": 6, "judge_category:PII": 1} | {"L2": 78, "L3 judge": 6, "L1 rules": 1} | {"roman_ur": 322, "mixed": 57, "en": 2} |
| external_translated ur | 0.639 (78/122) [0.551–0.719] | 0.064 (16/251) [0.040–0.101] | 0.590 (72/122) [0.501–0.673] | 0.056 (14/251) [0.034–0.091] | 62 | 77 | {"judge_category:Jailbreak": 11, "judge_controversial": 24, "judge_category:Violent": 1, "judge_category:Unethical Acts": 4, "judge_unsafe": 8, "judge_category:Politically Sensitive Topics": 1, "judge_category:Sexual Content or Sexual Acts": 15} | {"L2": 85, "L3 judge": 8, "L1 rules": 1} | {"ur": 371, "mixed": 2} |
| external_translated mixed | 0.692 (83/120) [0.604–0.767] | 0.031 (8/256) [0.016–0.060] | 0.667 (80/120) [0.578–0.745] | 0.023 (6/256) [0.011–0.050] | 35 | 47 | {"judge_category:Jailbreak": 6, "judge_controversial": 10, "judge_category:Unethical Acts": 2, "judge_unsafe": 5, "judge_category:Politically Sensitive Topics": 3, "judge_category:Sexual Content or Sexual Acts": 3, "judge_category:Suicide & Self-Harm": 1} | {"L2": 86, "L3 judge": 5} | {"mixed": 356, "roman_ur": 19, "en": 1} |
| overrefusal_translated FPR roman_ur | n/a | 0.102 (152/1483) [0.088–0.119] | n/a | 0.071 (106/1483) [0.059–0.086] | 125 | 195 | {"judge_category:Suicide & Self-Harm": 7, "judge_controversial": 49, "judge_unsafe": 46, "judge_category:Sexual Content or Sexual Acts": 11, "judge_category:Unethical Acts": 15, "judge_category:Violent": 8, "judge_category:Non-violent Illegal Acts": 41, "judge_category:Politically Sensitive Topics": 3, "judge_category:PII": 10} | {"L3 judge": 46, "L2": 106} | {"roman_ur": 1241, "mixed": 242} |
| overrefusal_translated FPR ur | n/a | 0.167 (256/1537) [0.149–0.186] | n/a | 0.092 (141/1537) [0.078–0.107] | 94 | 229 | {"judge_category:Unethical Acts": 56, "judge_controversial": 38, "judge_category:Sexual Content or Sexual Acts": 15, "judge_unsafe": 115, "judge_category:Non-violent Illegal Acts": 54, "judge_category:Violent": 15, "judge_category:Politically Sensitive Topics": 2, "judge_category:PII": 10, "judge_category:Jailbreak": 1} | {"L3 judge": 115, "L2": 141} | {"ur": 1537} |
| overrefusal_translated FPR mixed | n/a | 0.142 (222/1558) [0.126–0.161] | n/a | 0.096 (150/1558) [0.083–0.112] | 151 | 247 | {"judge_category:Unethical Acts": 25, "judge_unsafe": 72, "judge_category:Suicide & Self-Harm": 2, "judge_category:Violent": 16, "judge_category:Sexual Content or Sexual Acts": 5, "judge_controversial": 58, "judge_category:Non-violent Illegal Acts": 77, "judge_category:PII": 4, "judge_category:Politically Sensitive Topics": 1} | {"L3 judge": 72, "L2": 150} | {"mixed": 1442, "roman_ur": 116} |

## Latency (ms)

| Layer | median | p95 | requests that ran it |
|---|---:|---:|---:|
| normalization | 0.02 | 0.06 | 9061 |
| rules | 0.02 | 0.06 | 9061 |
| l2 | 12.79 | 49.37 | 9061 |
| memory | 0.27 | 0.39 | 9061 |
| session | 0.0 | 0.0 | 9061 |
| judge | 101.81 | 264.9 | 905 |
| end_to_end | 141.68 | 340.66 | 9061 |

End-to-end = client-side time for one in-process `/v1/check/input` call (includes the judge when called and the decision log write). Judge latency is over judged requests only.

