# Gateway v3: end-to-end evaluation

Every row was sent to `POST /v1/check/input` (L0 normalizer → L1 rules + memory → L2 routed ensemble → session escalation → L3 Qwen3Guard judge when judge_low ≤ risk < block), in-process with the real models (`scripts/eval_gateway.py`). **Full gateway** counts action `block` (HTTP 413 refusals counted as block). **L2 only** counts the routed L2 model over its threshold on the same request. `warn` is not counted as a block. Language for routing comes from the shared detector (`pehredar/langid.py`), not from the dataset label. Translated sets are Gemini machine translations (not the human test set).

- Config: {"PEHREDAR_GUARD_MODEL": "hf.co/QuantFactory/Qwen3Guard-Gen-0.6B-GGUF:Q4_K_M", "PEHREDAR_L2_XLMR_DIR": "/app/models/clf_v3_e3", "PEHREDAR_LANGID_MODEL": "/app/models/langid_v2.joblib"}; policy = {"l2": {"mode": "routed", "xlmr_threshold": 0.9682675}, "judge": {"xlmr_floor": 0.0, "block_categories": ["Jailbreak", "PII", "Non-violent Illegal Acts", "Violent"]}}
- L2: {"loaded": ["deberta", "xlmr"], "errors": {}, "load_seconds": {"deberta": 4.04, "xlmr": 4.68}, "device": "cuda", "vram_allocated_gb": 1.72, "thresholds": {"deberta": 0.5, "xlmr": 0.9629704356193542}}
- GPU memory: {"after_run_all_models_loaded": {"used_mib": 5666, "total_mib": 10240}, "l2_torch_allocated_gb": 1.72}
- Requests: 9061; L3 judge calls: 953 (10.5%)

| Eval set | Full gateway recall [95% CI] | Full gateway FPR [95% CI] | L2-only recall [95% CI] | L2-only FPR [95% CI] | warn | L3 calls | L3 outcome | blocks by layer | detected language |
|---|---|---|---|---|---:|---:|---|---|---|
| external_eval | 0.685 (135/197) [0.617–0.746] | 0.016 (5/309) [0.007–0.037] | 0.680 (134/197) [0.612–0.741] | 0.016 (5/309) [0.007–0.037] | 1 | 3 | {"judge_category:Unethical Acts": 1, "judge_controversial": 1, "judge_category:Jailbreak": 1, "judge_unsafe": 1} | {"L2": 137, "L1 rules": 2, "L3 judge": 1} | {"en": 495, "mixed": 11} |
| injecagent (unseen) | 0.666 (702/1054) [0.637–0.694] | n/a | 0.657 (693/1054) [0.628–0.685] | n/a | 19 | 40 | {"judge_category:PII": 25, "judge_unsafe": 9, "judge_controversial": 16} | {"L2": 693, "L3 judge": 9} | {"en": 1054} |
| bipia (unseen) | 0.104 (13/125) [0.062–0.170] | n/a | 0.104 (13/125) [0.062–0.170] | n/a | 1 | 1 | {} | {"L2": 13} | {"en": 124, "mixed": 1} |
| xstest FPR | n/a | 0.000 (0/249) [0.000–0.015] | n/a | 0.000 (0/249) [0.000–0.015] | 0 | 0 | {} | {} | {"en": 249} |
| or_bench FPR | n/a | 0.070 (92/1319) [0.057–0.085] | n/a | 0.068 (89/1319) [0.055–0.082] | 2 | 6 | {"judge_category:Non-violent Illegal Acts": 3, "judge_unsafe": 3, "judge_category:Unethical Acts": 1, "judge_controversial": 1} | {"L2": 89, "L3 judge": 3} | {"en": 1304, "mixed": 15} |
| benign_email_probe FPR | n/a | 0.000 (0/100) [0.000–0.037] | n/a | 0.000 (0/100) [0.000–0.037] | 0 | 0 | {} | {} | {"en": 100} |
| external_translated roman_ur | 0.605 (72/119) [0.515–0.688] | 0.023 (6/262) [0.011–0.049] | 0.605 (72/119) [0.515–0.688] | 0.023 (6/262) [0.011–0.049] | 51 | 61 | {"judge_category:Unethical Acts": 3, "judge_unsafe_warn": 6, "judge_category:Politically Sensitive Topics": 2, "judge_controversial": 15, "judge_category:Sexual Content or Sexual Acts": 9, "judge_category:Jailbreak": 6, "judge_category:PII": 1} | {"L2": 77, "L1 rules": 1} | {"roman_ur": 322, "mixed": 57, "en": 2} |
| external_translated ur | 0.598 (73/122) [0.510–0.681] | 0.048 (12/251) [0.028–0.082] | 0.574 (70/122) [0.485–0.658] | 0.048 (12/251) [0.028–0.082] | 71 | 81 | {"judge_category:Jailbreak": 12, "judge_controversial": 26, "judge_category:Violent": 1, "judge_category:Unethical Acts": 4, "judge_unsafe_warn": 6, "judge_category:Politically Sensitive Topics": 1, "judge_category:Sexual Content or Sexual Acts": 16, "judge_unsafe": 3, "judge_category:Non-violent Illegal Acts": 1} | {"L2": 81, "L3 judge": 3, "L1 rules": 1} | {"ur": 371, "mixed": 2} |
| external_translated mixed | 0.633 (76/120) [0.544–0.714] | 0.027 (7/256) [0.013–0.055] | 0.633 (76/120) [0.544–0.714] | 0.023 (6/256) [0.011–0.050] | 43 | 51 | {"judge_category:Unethical Acts": 3, "judge_unsafe_warn": 5, "judge_category:Jailbreak": 7, "judge_controversial": 11, "judge_category:Politically Sensitive Topics": 3, "judge_category:Sexual Content or Sexual Acts": 3, "judge_unsafe": 1, "judge_category:Suicide & Self-Harm": 1} | {"L2": 82, "L3 judge": 1} | {"mixed": 356, "roman_ur": 19, "en": 1} |
| overrefusal_translated FPR roman_ur | n/a | 0.088 (130/1483) [0.074–0.103] | n/a | 0.065 (96/1483) [0.053–0.078] | 147 | 205 | {"judge_category:Suicide & Self-Harm": 7, "judge_controversial": 53, "judge_unsafe_warn": 15, "judge_category:Sexual Content or Sexual Acts": 11, "judge_category:Unethical Acts": 18, "judge_category:Violent": 8, "judge_unsafe": 34, "judge_category:Non-violent Illegal Acts": 45, "judge_category:Politically Sensitive Topics": 3, "judge_category:PII": 10} | {"L2": 96, "L3 judge": 34} | {"roman_ur": 1241, "mixed": 242} |
| overrefusal_translated FPR ur | n/a | 0.130 (200/1537) [0.114–0.148] | n/a | 0.084 (129/1537) [0.071–0.099] | 150 | 241 | {"judge_category:Unethical Acts": 58, "judge_controversial": 42, "judge_category:Sexual Content or Sexual Acts": 16, "judge_unsafe_warn": 50, "judge_category:Non-violent Illegal Acts": 58, "judge_unsafe": 71, "judge_category:Jailbreak": 2, "judge_category:Violent": 16, "judge_category:Politically Sensitive Topics": 2, "judge_category:PII": 11} | {"L2": 129, "L3 judge": 71} | {"ur": 1537} |
| overrefusal_translated FPR mixed | n/a | 0.123 (192/1558) [0.108–0.141] | n/a | 0.085 (133/1558) [0.072–0.100] | 181 | 264 | {"judge_category:Unethical Acts": 26, "judge_unsafe_warn": 18, "judge_category:Suicide & Self-Harm": 2, "judge_category:Violent": 17, "judge_unsafe": 59, "judge_category:Sexual Content or Sexual Acts": 5, "judge_controversial": 61, "judge_category:Non-violent Illegal Acts": 81, "judge_category:PII": 6, "judge_category:Politically Sensitive Topics": 1} | {"L3 judge": 59, "L2": 133} | {"mixed": 1442, "roman_ur": 116} |

## Latency (ms)

| Layer | median | p95 | requests that ran it |
|---|---:|---:|---:|
| normalization | 0.02 | 0.06 | 9061 |
| rules | 0.02 | 0.06 | 9061 |
| l2 | 13.14 | 51.05 | 9061 |
| memory | 0.26 | 0.38 | 9061 |
| session | 0.0 | 0.0 | 9061 |
| judge | 106.1 | 275.51 | 953 |
| end_to_end | 141.71 | 358.47 | 9061 |

End-to-end = client-side time for one in-process `/v1/check/input` call (includes the judge when called and the decision log write). Judge latency is over judged requests only.

