# Classifier v2 (XLM-R base) evaluation

## Limitations (read first)

- **All non-English eval sets are machine-translated** (qwen3:8b, filtered), not the human test set.
- Estimated translation quality after all filters (human review of the v3 sample, `results/labse_filter_v3.md`): roman_ur 24/29 = 82.8% (**optimistic**: the roman_ur LaBSE threshold was fitted on the same review rows), mixed 25/32 = 78.1%, ur 19/31 = 61.3% (ur reviewed 55.9% good before the script check; excluded from training and from the main results).
- `dev_translated_v2` is part of the threshold set, so v2 numbers on it are in-sample for the threshold.
- Translated attack counts per language are small; see the CIs.
- No model was promoted to the gateway.

## Candidates (Phase C)

| Candidate | Epochs | Threshold (2% dev FPR) | F1 threshold | Train rows | Training time | Peak VRAM | Dev FPR en / roman_ur / mixed | Unseen recall | or_bench FPR |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| v2_e1 | 1 | 0.8972 | 0.7775 | 45791 | 617 s | 5.26 GB | 0.014 (35/2525) [0.010–0.019] / 0.035 (23/647) [0.024–0.053] / 0.028 (23/834) [0.018–0.041] | 0.236 (278/1179) [0.212–0.261] | 0.138 (182/1319) [0.120–0.158] |
| v2_e2 | 2 | 0.7383 | 0.6219 | 45791 | 1221 s | 5.26 GB | 0.019 (49/2525) [0.015–0.026] / 0.020 (13/647) [0.012–0.034] / 0.023 (19/834) [0.015–0.035] | 0.421 (496/1179) [0.393–0.449] | 0.203 (268/1319) [0.182–0.226] |

Chosen: **v2_e2** — v2_e2: or_bench FPR 0.2032 vs v2_e1 0.138; unseen recall 0.4207 [0.3928, 0.4491] vs v2_e1 0.2358 [0.2124, 0.2609] (equal or better: CIs overlap or higher)

Models: `deberta` deberta  threshold 0.5000; `v1b` classifier models/clf_v1b threshold 0.4375; `v2` classifier models/clf_v2_e2 threshold 0.7383; `ensemble_routed` ensemble models/clf_v2_e2 threshold 1.0000; `ensemble_max` ensemble_max models/clf_v2_e2 threshold 1.0000. `ensemble_routed`: en → DeBERTa, roman_ur/mixed/ur → v2; `ensemble_max`: attack if either is over its own threshold (risk = score / threshold, so ensemble threshold 1.0).

## Main results

### English sets and translated sets (roman_ur + mixed combined)

| Eval row | Model | Recall (tp/attacks) [95% CI] | FPR (fp/benign) [95% CI] |
|---|---|---|---|
| external_eval | deberta | 0.690 (136/197) [0.623–0.751] | 0.016 (5/309) [0.007–0.037] |
| external_eval | v1b | 0.660 (130/197) [0.591–0.722] | 0.023 (7/309) [0.011–0.046] |
| external_eval | v2 | 0.812 (160/197) [0.752–0.861] | 0.045 (14/309) [0.027–0.075] |
| external_eval | ensemble_routed | 0.690 (136/197) [0.623–0.751] | 0.016 (5/309) [0.007–0.037] |
| external_eval | ensemble_max | 0.858 (169/197) [0.802–0.900] | 0.058 (18/309) [0.037–0.090] |
| bipia (unseen) | deberta | 0.104 (13/125) [0.062–0.170] | n/a |
| bipia (unseen) | v1b | 0.120 (15/125) [0.074–0.189] | n/a |
| bipia (unseen) | v2 | 0.072 (9/125) [0.038–0.131] | n/a |
| bipia (unseen) | ensemble_routed | 0.104 (13/125) [0.062–0.170] | n/a |
| bipia (unseen) | ensemble_max | 0.168 (21/125) [0.113–0.243] | n/a |
| injecagent (unseen) | deberta | 0.657 (693/1054) [0.628–0.685] | n/a |
| injecagent (unseen) | v1b | 0.083 (87/1054) [0.067–0.101] | n/a |
| injecagent (unseen) | v2 | 0.462 (487/1054) [0.432–0.492] | n/a |
| injecagent (unseen) | ensemble_routed | 0.657 (693/1054) [0.628–0.685] | n/a |
| injecagent (unseen) | ensemble_max | 0.784 (826/1054) [0.758–0.807] | n/a |
| llmail (seen) | deberta | 0.420 (841/2000) [0.399–0.442] | n/a |
| llmail (seen) | v1b | 0.846 (1691/2000) [0.829–0.861] | n/a |
| llmail (seen) | v2 | 0.879 (1759/2000) [0.865–0.893] | n/a |
| llmail (seen) | ensemble_routed | 0.423 (847/2000) [0.402–0.445] | n/a |
| llmail (seen) | ensemble_max | 0.885 (1771/2000) [0.871–0.899] | n/a |
| xstest FPR | deberta | n/a | 0.000 (0/249) [0.000–0.015] |
| xstest FPR | v1b | n/a | 0.000 (0/249) [0.000–0.015] |
| xstest FPR | v2 | n/a | 0.000 (0/249) [0.000–0.015] |
| xstest FPR | ensemble_routed | n/a | 0.000 (0/249) [0.000–0.015] |
| xstest FPR | ensemble_max | n/a | 0.000 (0/249) [0.000–0.015] |
| or_bench FPR | deberta | n/a | 0.065 (86/1319) [0.053–0.080] |
| or_bench FPR | v1b | n/a | 0.375 (495/1319) [0.350–0.402] |
| or_bench FPR | v2 | n/a | 0.203 (268/1319) [0.182–0.226] |
| or_bench FPR | ensemble_routed | n/a | 0.065 (86/1319) [0.053–0.080] |
| or_bench FPR | ensemble_max | n/a | 0.227 (300/1319) [0.206–0.251] |
| benign_email_probe FPR | deberta | n/a | 0.000 (0/100) [0.000–0.037] |
| benign_email_probe FPR | v1b | n/a | 0.250 (25/100) [0.175–0.343] |
| benign_email_probe FPR | v2 | n/a | 0.750 (75/100) [0.657–0.825] |
| benign_email_probe FPR | ensemble_routed | n/a | 0.000 (0/100) [0.000–0.037] |
| benign_email_probe FPR | ensemble_max | n/a | 0.750 (75/100) [0.657–0.825] |
| external_translated (roman_ur+mixed) | deberta | 0.534 (47/88) [0.431–0.635] | 0.070 (19/270) [0.045–0.107] |
| external_translated (roman_ur+mixed) | v1b | 0.409 (36/88) [0.312–0.513] | 0.030 (8/270) [0.015–0.057] |
| external_translated (roman_ur+mixed) | v2 | 0.625 (55/88) [0.521–0.719] | 0.041 (11/270) [0.023–0.071] |
| external_translated (roman_ur+mixed) | ensemble_routed | 0.625 (55/88) [0.521–0.719] | 0.041 (11/270) [0.023–0.071] |
| external_translated (roman_ur+mixed) | ensemble_max | 0.739 (65/88) [0.638–0.819] | 0.096 (26/270) [0.067–0.137] |
| overrefusal_translated FPR (roman_ur+mixed) | deberta | n/a | 0.374 (965/2581) [0.355–0.393] |
| overrefusal_translated FPR (roman_ur+mixed) | v1b | n/a | 0.203 (523/2581) [0.188–0.219] |
| overrefusal_translated FPR (roman_ur+mixed) | v2 | n/a | 0.182 (470/2581) [0.168–0.198] |
| overrefusal_translated FPR (roman_ur+mixed) | ensemble_routed | n/a | 0.182 (470/2581) [0.168–0.198] |
| overrefusal_translated FPR (roman_ur+mixed) | ensemble_max | n/a | 0.452 (1167/2581) [0.433–0.471] |
| dev_translated_v2 (threshold set) (roman_ur+mixed) | deberta | 0.831 (564/679) [0.801–0.857] | 0.256 (379/1481) [0.234–0.279] |
| dev_translated_v2 (threshold set) (roman_ur+mixed) | v1b | 0.879 (597/679) [0.853–0.902] | 0.042 (62/1481) [0.033–0.053] |
| dev_translated_v2 (threshold set) (roman_ur+mixed) | v2 | 0.884 (600/679) [0.857–0.906] | 0.022 (32/1481) [0.015–0.030] |
| dev_translated_v2 (threshold set) (roman_ur+mixed) | ensemble_routed | 0.884 (600/679) [0.857–0.906] | 0.022 (32/1481) [0.015–0.030] |
| dev_translated_v2 (threshold set) (roman_ur+mixed) | ensemble_max | 0.949 (644/679) [0.929–0.963] | 0.266 (394/1481) [0.244–0.289] |

## Per-language results (translated sets)

### roman_ur

| Eval row | Model | Recall (tp/attacks) [95% CI] | FPR (fp/benign) [95% CI] |
|---|---|---|---|
| external_translated | deberta | 0.500 (20/40) [0.352–0.648] | 0.070 (8/115) [0.036–0.131] |
| external_translated | v1b | 0.400 (16/40) [0.264–0.554] | 0.026 (3/115) [0.009–0.074] |
| external_translated | v2 | 0.550 (22/40) [0.398–0.693] | 0.035 (4/115) [0.014–0.086] |
| external_translated | ensemble_routed | 0.550 (22/40) [0.398–0.693] | 0.035 (4/115) [0.014–0.086] |
| external_translated | ensemble_max | 0.675 (27/40) [0.520–0.799] | 0.104 (12/115) [0.061–0.174] |
| overrefusal_translated FPR | deberta | n/a | 0.409 (469/1147) [0.381–0.438] |
| overrefusal_translated FPR | v1b | n/a | 0.211 (242/1147) [0.188–0.235] |
| overrefusal_translated FPR | v2 | n/a | 0.172 (197/1147) [0.151–0.195] |
| overrefusal_translated FPR | ensemble_routed | n/a | 0.172 (197/1147) [0.151–0.195] |
| overrefusal_translated FPR | ensemble_max | n/a | 0.476 (546/1147) [0.447–0.505] |
| dev_translated_v2 (threshold set) | deberta | 0.830 (249/300) [0.783–0.868] | 0.243 (157/647) [0.211–0.277] |
| dev_translated_v2 (threshold set) | v1b | 0.867 (260/300) [0.824–0.900] | 0.043 (28/647) [0.030–0.062] |
| dev_translated_v2 (threshold set) | v2 | 0.873 (262/300) [0.831–0.906] | 0.020 (13/647) [0.012–0.034] |
| dev_translated_v2 (threshold set) | ensemble_routed | 0.873 (262/300) [0.831–0.906] | 0.020 (13/647) [0.012–0.034] |
| dev_translated_v2 (threshold set) | ensemble_max | 0.947 (284/300) [0.915–0.967] | 0.252 (163/647) [0.220–0.287] |

### mixed

| Eval row | Model | Recall (tp/attacks) [95% CI] | FPR (fp/benign) [95% CI] |
|---|---|---|---|
| external_translated | deberta | 0.562 (27/48) [0.423–0.693] | 0.071 (11/155) [0.040–0.123] |
| external_translated | v1b | 0.417 (20/48) [0.288–0.557] | 0.032 (5/155) [0.014–0.073] |
| external_translated | v2 | 0.688 (33/48) [0.547–0.800] | 0.045 (7/155) [0.022–0.090] |
| external_translated | ensemble_routed | 0.688 (33/48) [0.547–0.800] | 0.045 (7/155) [0.022–0.090] |
| external_translated | ensemble_max | 0.792 (38/48) [0.657–0.883] | 0.090 (14/155) [0.055–0.146] |
| overrefusal_translated FPR | deberta | n/a | 0.346 (496/1434) [0.322–0.371] |
| overrefusal_translated FPR | v1b | n/a | 0.196 (281/1434) [0.176–0.217] |
| overrefusal_translated FPR | v2 | n/a | 0.190 (273/1434) [0.171–0.211] |
| overrefusal_translated FPR | ensemble_routed | n/a | 0.190 (273/1434) [0.171–0.211] |
| overrefusal_translated FPR | ensemble_max | n/a | 0.433 (621/1434) [0.408–0.459] |
| dev_translated_v2 (threshold set) | deberta | 0.831 (315/379) [0.790–0.866] | 0.266 (222/834) [0.237–0.297] |
| dev_translated_v2 (threshold set) | v1b | 0.889 (337/379) [0.854–0.917] | 0.041 (34/834) [0.029–0.056] |
| dev_translated_v2 (threshold set) | v2 | 0.892 (338/379) [0.857–0.919] | 0.023 (19/834) [0.015–0.035] |
| dev_translated_v2 (threshold set) | ensemble_routed | 0.892 (338/379) [0.857–0.919] | 0.023 (19/834) [0.015–0.035] |
| dev_translated_v2 (threshold set) | ensemble_max | 0.950 (360/379) [0.923–0.968] | 0.277 (231/834) [0.248–0.308] |

## Generated comparison: roman_ur / mixed vs DeBERTa

Rule: a model beats DeBERTa if its recall is higher with non-overlapping 95% CIs and its FPR on the same set and on overrefusal_translated is at most DeBERTa's + 0.02. Higher recall with overlapping CIs is reported as "higher, not significant". FPR differences are called significant when the 95% CIs do not overlap. ur is in the appendix only.

- roman_ur / external_translated / v2: recall 0.550 (22/40) [0.398–0.693] vs DeBERTa 0.500 (20/40) [0.352–0.648]; FPR same set 0.035 (4/115) [0.014–0.086] vs 0.070 (8/115) [0.036–0.131]; overrefusal_translated FPR 0.172 (197/1147) [0.151–0.195] vs 0.409 (469/1147) [0.381–0.438] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- roman_ur / external_translated / ensemble_routed: recall 0.550 (22/40) [0.398–0.693] vs DeBERTa 0.500 (20/40) [0.352–0.648]; FPR same set 0.035 (4/115) [0.014–0.086] vs 0.070 (8/115) [0.036–0.131]; overrefusal_translated FPR 0.172 (197/1147) [0.151–0.195] vs 0.409 (469/1147) [0.381–0.438] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- roman_ur / external_translated / ensemble_max: recall 0.675 (27/40) [0.520–0.799] vs DeBERTa 0.500 (20/40) [0.352–0.648]; FPR same set 0.104 (12/115) [0.061–0.174] vs 0.070 (8/115) [0.036–0.131]; overrefusal_translated FPR 0.476 (546/1147) [0.447–0.505] vs 0.409 (469/1147) [0.381–0.438] → higher, not significant; FPR not comparable; overrefusal_translated FPR significantly higher than DeBERTa
- roman_ur / dev_translated_v2 (threshold set) / v2: recall 0.873 (262/300) [0.831–0.906] vs DeBERTa 0.830 (249/300) [0.783–0.868]; FPR same set 0.020 (13/647) [0.012–0.034] vs 0.243 (157/647) [0.211–0.277]; overrefusal_translated FPR 0.172 (197/1147) [0.151–0.195] vs 0.409 (469/1147) [0.381–0.438] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- roman_ur / dev_translated_v2 (threshold set) / ensemble_routed: recall 0.873 (262/300) [0.831–0.906] vs DeBERTa 0.830 (249/300) [0.783–0.868]; FPR same set 0.020 (13/647) [0.012–0.034] vs 0.243 (157/647) [0.211–0.277]; overrefusal_translated FPR 0.172 (197/1147) [0.151–0.195] vs 0.409 (469/1147) [0.381–0.438] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- roman_ur / dev_translated_v2 (threshold set) / ensemble_max: recall 0.947 (284/300) [0.915–0.967] vs DeBERTa 0.830 (249/300) [0.783–0.868]; FPR same set 0.252 (163/647) [0.220–0.287] vs 0.243 (157/647) [0.211–0.277]; overrefusal_translated FPR 0.476 (546/1147) [0.447–0.505] vs 0.409 (469/1147) [0.381–0.438] → higher recall, but FPR not comparable; overrefusal_translated FPR significantly higher than DeBERTa
- mixed / external_translated / v2: recall 0.688 (33/48) [0.547–0.800] vs DeBERTa 0.562 (27/48) [0.423–0.693]; FPR same set 0.045 (7/155) [0.022–0.090] vs 0.071 (11/155) [0.040–0.123]; overrefusal_translated FPR 0.190 (273/1434) [0.171–0.211] vs 0.346 (496/1434) [0.322–0.371] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- mixed / external_translated / ensemble_routed: recall 0.688 (33/48) [0.547–0.800] vs DeBERTa 0.562 (27/48) [0.423–0.693]; FPR same set 0.045 (7/155) [0.022–0.090] vs 0.071 (11/155) [0.040–0.123]; overrefusal_translated FPR 0.190 (273/1434) [0.171–0.211] vs 0.346 (496/1434) [0.322–0.371] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- mixed / external_translated / ensemble_max: recall 0.792 (38/48) [0.657–0.883] vs DeBERTa 0.562 (27/48) [0.423–0.693]; FPR same set 0.090 (14/155) [0.055–0.146] vs 0.071 (11/155) [0.040–0.123]; overrefusal_translated FPR 0.433 (621/1434) [0.408–0.459] vs 0.346 (496/1434) [0.322–0.371] → higher, not significant; FPR not comparable; overrefusal_translated FPR significantly higher than DeBERTa
- mixed / dev_translated_v2 (threshold set) / v2: recall 0.892 (338/379) [0.857–0.919] vs DeBERTa 0.831 (315/379) [0.790–0.866]; FPR same set 0.023 (19/834) [0.015–0.035] vs 0.266 (222/834) [0.237–0.297]; overrefusal_translated FPR 0.190 (273/1434) [0.171–0.211] vs 0.346 (496/1434) [0.322–0.371] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- mixed / dev_translated_v2 (threshold set) / ensemble_routed: recall 0.892 (338/379) [0.857–0.919] vs DeBERTa 0.831 (315/379) [0.790–0.866]; FPR same set 0.023 (19/834) [0.015–0.035] vs 0.266 (222/834) [0.237–0.297]; overrefusal_translated FPR 0.190 (273/1434) [0.171–0.211] vs 0.346 (496/1434) [0.322–0.371] → higher, not significant; overrefusal_translated FPR significantly lower than DeBERTa
- mixed / dev_translated_v2 (threshold set) / ensemble_max: recall 0.950 (360/379) [0.923–0.968] vs DeBERTa 0.831 (315/379) [0.790–0.866]; FPR same set 0.277 (231/834) [0.248–0.308] vs 0.266 (222/834) [0.237–0.297]; overrefusal_translated FPR 0.433 (621/1434) [0.408–0.459] vs 0.346 (496/1434) [0.322–0.371] → higher recall, but FPR not comparable; overrefusal_translated FPR significantly higher than DeBERTa

## Appendix: ur — low translation quality (55.9% good)

### ur (not used for training; machine-translated, low quality)

| Eval row | Model | Recall (tp/attacks) [95% CI] | FPR (fp/benign) [95% CI] |
|---|---|---|---|
| external_translated | deberta | 0.968 (60/62) [0.890–0.991] | 0.855 (141/165) [0.793–0.900] |
| external_translated | v1b | 0.194 (12/62) [0.114–0.308] | 0.024 (4/165) [0.009–0.061] |
| external_translated | v2 | 0.565 (35/62) [0.441–0.681] | 0.079 (13/165) [0.047–0.130] |
| external_translated | ensemble_routed | 0.565 (35/62) [0.441–0.681] | 0.079 (13/165) [0.047–0.130] |
| external_translated | ensemble_max | 1.000 (62/62) [0.942–1.000] | 0.861 (142/165) [0.799–0.905] |
| overrefusal_translated FPR | deberta | n/a | 0.965 (1421/1473) [0.954–0.973] |
| overrefusal_translated FPR | v1b | n/a | 0.121 (179/1473) [0.106–0.139] |
| overrefusal_translated FPR | v2 | n/a | 0.183 (269/1473) [0.164–0.203] |
| overrefusal_translated FPR | ensemble_routed | n/a | 0.183 (269/1473) [0.164–0.203] |
| overrefusal_translated FPR | ensemble_max | n/a | 0.973 (1433/1473) [0.963–0.980] |
| dev_translated_v2 (threshold set) | deberta | 0.942 (370/393) [0.914–0.961] | 0.913 (704/771) [0.891–0.931] |
| dev_translated_v2 (threshold set) | v1b | 0.641 (252/393) [0.593–0.687] | 0.023 (18/771) [0.015–0.037] |
| dev_translated_v2 (threshold set) | v2 | 0.773 (304/393) [0.730–0.812] | 0.040 (31/771) [0.029–0.057] |
| dev_translated_v2 (threshold set) | ensemble_routed | 0.773 (304/393) [0.730–0.812] | 0.040 (31/771) [0.029–0.057] |
| dev_translated_v2 (threshold set) | ensemble_max | 0.982 (386/393) [0.964–0.991] | 0.917 (707/771) [0.895–0.934] |

