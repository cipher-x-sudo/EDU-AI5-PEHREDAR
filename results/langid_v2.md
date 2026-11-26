# Language-ID router v2

Char n-gram TF-IDF + LogisticRegression trained on 32251 rows (15,000 English, Gemini train translations, 3589 synthetic code-mixed rows built by clause and word splicing of English train rows with their Gemini roman_ur translation). Roman-Urdu override: ≥ 2 of 105 function-word markers, or any Urdu-script letter, never routes to en. `+override` rows are what the gateway uses (`detect_lang`).

## en vs non-en accuracy (routing-relevant)

| Set | Variant | en-vs-non-en acc. | non-en sent to en | en sent to non-en | Macro-F1 |
|---|---|---:|---:|---:|---:|
| dev (n=8776) | v1 | 0.9981 | 4 | 13 | 0.9397 |
| dev (n=8776) | v1+override | 0.9984 | 0 | 14 | 0.9401 |
| dev (n=8776) | v2 | 0.9932 | 0 | 60 | 0.9345 |
| dev (n=8776) | v2+override (detect_lang) | 0.993 | 0 | 61 | 0.9344 |
| test (n=1636) | v1 | 0.9939 | 6 | 4 | 0.9425 |
| test (n=1636) | v1+override | 0.9945 | 5 | 4 | 0.9425 |
| test (n=1636) | v2 | 0.9914 | 3 | 11 | 0.9408 |
| test (n=1636) | v2+override (detect_lang) | 0.9914 | 3 | 11 | 0.9408 |
| overrefusal (n=6146) | v1 | 1.0 | 0 | 0 | 0.9436 |
| overrefusal (n=6146) | v1+override | 1.0 | 0 | 0 | 0.9436 |
| overrefusal (n=6146) | v2 | 0.9976 | 0 | 15 | 0.9387 |
| overrefusal (n=6146) | v2+override (detect_lang) | 0.9976 | 0 | 15 | 0.9387 |

## English rows sent to the non-English (v3) path

| English set | Variant | Sent to non-en | n | Rate |
|---|---|---:|---:|---:|
| external_eval (en) | v1 | 4 | 506 | 0.79% |
| external_eval (en) | v1+override | 4 | 506 | 0.79% |
| external_eval (en) | v2 | 11 | 506 | 2.17% |
| external_eval (en) | v2+override (detect_lang) | 11 | 506 | 2.17% |
| overrefusal xstest+or_bench (en) | v1 | 0 | 1568 | 0.00% |
| overrefusal xstest+or_bench (en) | v1+override | 0 | 1568 | 0.00% |
| overrefusal xstest+or_bench (en) | v2 | 15 | 1568 | 0.96% |
| overrefusal xstest+or_bench (en) | v2+override (detect_lang) | 15 | 1568 | 0.96% |
| benign_email_probe | v1 | 0 | 100 | 0.00% |
| benign_email_probe | v1+override | 0 | 100 | 0.00% |
| benign_email_probe | v2 | 0 | 100 | 0.00% |
| benign_email_probe | v2+override (detect_lang) | 0 | 100 | 0.00% |
| bipia | v1 | 0 | 125 | 0.00% |
| bipia | v1+override | 0 | 125 | 0.00% |
| bipia | v2 | 1 | 125 | 0.80% |
| bipia | v2+override (detect_lang) | 1 | 125 | 0.80% |
| injecagent | v1 | 0 | 1054 | 0.00% |
| injecagent | v1+override | 0 | 1054 | 0.00% |
| injecagent | v2 | 0 | 1054 | 0.00% |
| injecagent | v2+override (detect_lang) | 0 | 1054 | 0.00% |
