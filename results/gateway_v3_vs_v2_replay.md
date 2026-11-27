# Gateway v3 vs v2_replay

Same eval sets and harness (`scripts/eval_gateway.py`); v2_replay = the gateway_v2 config (xlmr 0.9613, judge on any unsafe) with judge temperature 0; v3 = the config chosen in results/judge_policy_joint.md. Full gateway, action `block` = positive. Wilson 95% CIs.

- v2_replay policy: {"l2": {"mode": "routed", "xlmr_threshold": 0.9613}, "judge": {"xlmr_floor": 0.0, "block_categories": null}}
- v3 policy: {"l2": {"mode": "routed", "xlmr_threshold": 0.9682675}, "judge": {"xlmr_floor": 0.0, "block_categories": ["Jailbreak", "PII", "Non-violent Illegal Acts", "Violent"]}}

| Eval set | v2_replay recall | v3 recall | v2_replay FPR | v3 FPR |
|---|---|---|---|---|
| external_eval | 0.685 (135/197) [0.617–0.746] | 0.685 (135/197) [0.617–0.746] | 0.016 (5/309) [0.007–0.037] | 0.016 (5/309) [0.007–0.037] |
| injecagent (unseen) | 0.666 (702/1054) [0.637–0.694] | 0.666 (702/1054) [0.637–0.694] | n/a | n/a |
| bipia (unseen) | 0.104 (13/125) [0.062–0.170] | 0.104 (13/125) [0.062–0.170] | n/a | n/a |
| xstest FPR | n/a | n/a | 0.000 (0/249) [0.000–0.015] | 0.000 (0/249) [0.000–0.015] |
| or_bench FPR | n/a | n/a | 0.070 (92/1319) [0.057–0.085] | 0.070 (92/1319) [0.057–0.085] |
| benign_email_probe FPR | n/a | n/a | 0.000 (0/100) [0.000–0.037] | 0.000 (0/100) [0.000–0.037] |
| external_translated roman_ur | 0.647 (77/119) [0.558–0.727] | 0.605 (72/119) [0.515–0.688] | 0.030 (8/262) [0.016–0.059] | 0.023 (6/262) [0.011–0.049] |
| external_translated ur | 0.639 (78/122) [0.551–0.719] | 0.598 (73/122) [0.510–0.681] | 0.064 (16/251) [0.040–0.101] | 0.048 (12/251) [0.028–0.082] |
| external_translated mixed | 0.692 (83/120) [0.604–0.767] | 0.633 (76/120) [0.544–0.714] | 0.031 (8/256) [0.016–0.060] | 0.027 (7/256) [0.013–0.055] |
| overrefusal_translated FPR roman_ur | n/a | n/a | 0.102 (152/1483) [0.088–0.119] | 0.088 (130/1483) [0.074–0.103] |
| overrefusal_translated FPR ur | n/a | n/a | 0.167 (256/1537) [0.149–0.186] | 0.130 (200/1537) [0.114–0.148] |
| overrefusal_translated FPR mixed | n/a | n/a | 0.142 (222/1558) [0.126–0.161] | 0.123 (192/1558) [0.108–0.141] |

| | v2_replay | v3 |
|---|---|---|
| L3 judge calls | 905 / 9061 (10.0%) | 953 / 9061 (10.5%) |
| l2 latency p50 / p95 ms | 12.79 / 49.37 | 13.14 / 51.05 |
| judge latency p50 / p95 ms | 101.81 / 264.9 | 106.1 / 275.51 |
| end_to_end latency p50 / p95 ms | 141.68 / 340.66 | 141.71 / 358.47 |

## Judge contribution

Benign rows blocked by the judge vs attacks blocked only by the judge (no L1 rule, memory or L2 hit).

| sets | v2_replay benign blocked | v2_replay judge-only catches | v3 benign blocked | v3 judge-only catches |
|---|---:|---:|---:|---:|
| translated sets | 239 | 13 | 165 | 3 |
| all sets | 242 | 23 | 168 | 13 |
