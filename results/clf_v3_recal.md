# v3 recalibration: non-English thresholds, router v2

All numbers come from `results/clf_v3_recal.json` (`python -m scripts.run_v3_evaluation --recal`). Thresholds for the non-English path are chosen on dev rows with lang in roman_ur / ur / mixed only; the English route (DeBERTa 0.5) is unchanged. Router: langid_v2 + Roman-Urdu override (pehredar.langid.detect_lang). Non-English sets are Gemini machine translations, not the human test set.

## Non-English dev thresholds

| Model | Dev non-en FPR target | Threshold | Dev non-en recall | Dev non-en FPR | Dev FPR roman_ur / ur / mixed |
|---|---|---:|---:|---:|---|
| v2 | 2% | 0.8771 | 0.7699 | 0.0197 | 0.0139 / 0.0276 / 0.0176 |
| v2 | 3% | 0.7756 | 0.8244 | 0.0299 | 0.0171 / 0.0498 / 0.0227 |
| v2 | 5% | 0.6038 | 0.8697 | 0.0499 | 0.0299 / 0.0870 / 0.0331 |
| v3 | 2% | 0.9818 | 0.8283 | 0.0197 | 0.0203 / 0.0212 / 0.0176 |
| v3 | 3% | 0.9613 | 0.8671 | 0.0299 | 0.0310 / 0.0371 / 0.0217 |
| v3 | 5% | 0.8879 | 0.9054 | 0.0499 | 0.0470 / 0.0700 / 0.0331 |

Secondary: per-language thresholds (2% FPR per language on dev): v2 roman_ur 0.7065 (dev recall 0.7879), ur 0.9035 (dev recall 0.7515), mixed 0.8483 (dev recall 0.8436); v3 roman_ur 0.9847 (dev recall 0.7879), ur 0.9874 (dev recall 0.7906), mixed 0.9665 (dev recall 0.8880)

**Operating point (dev-only rule: highest dev non-English recall with dev non-English FPR <= 3% over v2/v3 x 2%, 3%, 5%):** v3 at 3% → threshold 0.9613, dev non-en recall 0.8671, dev non-en FPR 0.0299. Test numbers below are reported, not used for the choice. routed_v2 uses v2's threshold at the same level (0.7756); routed_v3_perlang is the secondary per-language variant.

## Test (external_eval + external_translated_gemini), all rows

| Lang | System | Recall [95% CI] | FPR [95% CI] |
|---|---|---|---|
| en | deberta | 0.690 (136/197) [0.623–0.751] | 0.016 (5/309) [0.007–0.037] |
| en | routed_v2 | 0.685 (135/197) [0.617–0.746] | 0.016 (5/309) [0.007–0.037] |
| en | routed_v3 | 0.680 (134/197) [0.612–0.741] | 0.016 (5/309) [0.007–0.037] |
| en | routed_v3_perlang | 0.680 (134/197) [0.612–0.741] | 0.016 (5/309) [0.007–0.037] |
| roman_ur | deberta | 0.605 (72/119) [0.515–0.688] | 0.080 (21/262) [0.053–0.119] |
| roman_ur | routed_v2 | 0.613 (73/119) [0.524–0.696] | 0.046 (12/262) [0.026–0.078] |
| roman_ur | routed_v3 | 0.613 (73/119) [0.524–0.696] | 0.023 (6/262) [0.011–0.049] |
| roman_ur | routed_v3_perlang | 0.504 (60/119) [0.416–0.593] | 0.015 (4/262) [0.006–0.039] |
| ur | deberta | 0.893 (109/122) [0.826–0.937] | 0.777 (195/251) [0.721–0.824] |
| ur | routed_v2 | 0.705 (86/122) [0.619–0.779] | 0.088 (22/251) [0.059–0.129] |
| ur | routed_v3 | 0.590 (72/122) [0.501–0.673] | 0.056 (14/251) [0.034–0.091] |
| ur | routed_v3_perlang | 0.426 (52/122) [0.342–0.515] | 0.028 (7/251) [0.014–0.056] |
| mixed | deberta | 0.592 (71/120) [0.502–0.675] | 0.070 (18/256) [0.045–0.108] |
| mixed | routed_v2 | 0.675 (81/120) [0.587–0.752] | 0.059 (15/256) [0.036–0.094] |
| mixed | routed_v3 | 0.667 (80/120) [0.578–0.745] | 0.023 (6/256) [0.011–0.050] |
| mixed | routed_v3_perlang | 0.633 (76/120) [0.544–0.714] | 0.023 (6/256) [0.011–0.050] |

## Test excluding the 314 near-duplicate rows (e5 > 0.95 to train)

| Lang | System | Recall [95% CI] | FPR [95% CI] |
|---|---|---|---|
| en | deberta | 0.591 (78/132) [0.506–0.671] | 0.016 (5/306) [0.007–0.038] |
| en | routed_v2 | 0.583 (77/132) [0.498–0.664] | 0.016 (5/306) [0.007–0.038] |
| en | routed_v3 | 0.576 (76/132) [0.490–0.657] | 0.016 (5/306) [0.007–0.038] |
| en | routed_v3_perlang | 0.576 (76/132) [0.490–0.657] | 0.016 (5/306) [0.007–0.038] |
| en | (rows removed) | 68 | |
| roman_ur | deberta | 0.571 (60/105) [0.476–0.662] | 0.080 (21/262) [0.053–0.119] |
| roman_ur | routed_v2 | 0.571 (60/105) [0.476–0.662] | 0.046 (12/262) [0.026–0.078] |
| roman_ur | routed_v3 | 0.571 (60/105) [0.476–0.662] | 0.023 (6/262) [0.011–0.049] |
| roman_ur | routed_v3_perlang | 0.457 (48/105) [0.365–0.552] | 0.015 (4/262) [0.006–0.039] |
| roman_ur | (rows removed) | 14 | |
| ur | deberta | 0.897 (96/107) [0.825–0.942] | 0.777 (195/251) [0.721–0.824] |
| ur | routed_v2 | 0.673 (72/107) [0.579–0.754] | 0.088 (22/251) [0.059–0.129] |
| ur | routed_v3 | 0.542 (58/107) [0.448–0.633] | 0.056 (14/251) [0.034–0.091] |
| ur | routed_v3_perlang | 0.374 (40/107) [0.288–0.468] | 0.028 (7/251) [0.014–0.056] |
| ur | (rows removed) | 15 | |
| mixed | deberta | 0.552 (58/105) [0.457–0.644] | 0.070 (18/256) [0.045–0.108] |
| mixed | routed_v2 | 0.638 (67/105) [0.543–0.724] | 0.059 (15/256) [0.036–0.094] |
| mixed | routed_v3 | 0.629 (66/105) [0.533–0.715] | 0.023 (6/256) [0.011–0.050] |
| mixed | routed_v3_perlang | 0.591 (62/105) [0.495–0.680] | 0.023 (6/256) [0.011–0.050] |
| mixed | (rows removed) | 15 | |

## Overrefusal FPR (xstest + or_bench + overrefusal_translated_gemini)

| Lang | deberta | routed_v2 | routed_v3 | routed_v3_perlang |
|---|---|---|---|---|
| en | 0.055 (86/1568) [0.045–0.067] | 0.059 (92/1568) [0.048–0.071] | 0.057 (89/1568) [0.046–0.069] | 0.057 (89/1568) [0.046–0.069] |
| roman_ur | 0.470 (697/1483) [0.445–0.495] | 0.101 (150/1483) [0.087–0.117] | 0.071 (106/1483) [0.059–0.086] | 0.055 (82/1483) [0.045–0.068] |
| ur | 0.971 (1493/1537) [0.962–0.979] | 0.174 (268/1537) [0.156–0.194] | 0.092 (141/1537) [0.078–0.107] | 0.055 (84/1537) [0.044–0.067] |
| mixed | 0.422 (657/1558) [0.397–0.446] | 0.175 (273/1558) [0.157–0.195] | 0.096 (150/1558) [0.083–0.112] | 0.089 (139/1558) [0.076–0.104] |

## Significance — recall (McNemar exact on test attack rows)

| Lang | Comparison | routed_v3 right, other wrong | other right, routed_v3 wrong | p | Significant at 0.05 |
|---|---|---:|---:|---:|---|
| en | routed_v3 vs deberta | 0 | 2 | 0.5 | no |
| en | routed_v3 vs routed_v2 | 0 | 1 | 1 | no |
| roman_ur | routed_v3 vs deberta | 21 | 20 | 1 | no |
| roman_ur | routed_v3 vs routed_v2 | 15 | 15 | 1 | no |
| ur | routed_v3 vs deberta | 5 | 42 | <1e-6 | yes |
| ur | routed_v3 vs routed_v2 | 8 | 22 | 0.0161 | yes |
| mixed | routed_v3 vs deberta | 19 | 10 | 0.136 | no |
| mixed | routed_v3 vs routed_v2 | 14 | 15 | 1 | no |

## Significance — FPR (McNemar exact on test benign + overrefusal rows)

| Lang | Comparison | routed_v3 right, other wrong | other right, routed_v3 wrong | p | Significant at 0.05 |
|---|---|---:|---:|---:|---|
| en | routed_v3 vs deberta | 0 | 3 | 0.25 | no |
| en | routed_v3 vs routed_v2 | 4 | 1 | 0.375 | no |
| roman_ur | routed_v3 vs deberta | 647 | 41 | <1e-6 | yes |
| roman_ur | routed_v3 vs routed_v2 | 91 | 41 | 1.6e-05 | yes |
| ur | routed_v3 vs deberta | 1539 | 6 | <1e-6 | yes |
| ur | routed_v3 vs routed_v2 | 168 | 33 | <1e-6 | yes |
| mixed | routed_v3 vs deberta | 577 | 58 | <1e-6 | yes |
| mixed | routed_v3 vs routed_v2 | 172 | 40 | <1e-6 | yes |

## routed_v3 at each dev FPR level (transparency; not used for the choice)

| Level | Lang | Test recall [95% CI] | Test FPR [95% CI] | Overrefusal FPR [95% CI] |
|---|---|---|---|---|
| 2% | roman_ur | 0.546 (65/119) [0.457–0.633] | 0.011 (3/262) [0.004–0.033] | 0.052 (77/1483) [0.042–0.064] |
| 2% | ur | 0.484 (59/122) [0.397–0.571] | 0.040 (10/251) [0.022–0.072] | 0.064 (98/1537) [0.053–0.077] |
| 2% | mixed | 0.575 (69/120) [0.486–0.660] | 0.019 (5/256) [0.008–0.045] | 0.062 (97/1558) [0.051–0.075] |
| 3% | roman_ur | 0.613 (73/119) [0.524–0.696] | 0.023 (6/262) [0.011–0.049] | 0.071 (106/1483) [0.059–0.086] |
| 3% | ur | 0.590 (72/122) [0.501–0.673] | 0.056 (14/251) [0.034–0.091] | 0.092 (141/1537) [0.078–0.107] |
| 3% | mixed | 0.667 (80/120) [0.578–0.745] | 0.023 (6/256) [0.011–0.050] | 0.096 (150/1558) [0.083–0.112] |
| 5% | roman_ur | 0.740 (88/119) [0.654–0.810] | 0.038 (10/262) [0.021–0.069] | 0.109 (161/1483) [0.094–0.125] |
| 5% | ur | 0.721 (88/122) [0.636–0.793] | 0.092 (23/251) [0.062–0.134] | 0.130 (199/1537) [0.114–0.147] |
| 5% | mixed | 0.717 (86/120) [0.630–0.790] | 0.035 (9/256) [0.019–0.066] | 0.143 (223/1558) [0.127–0.161] |
