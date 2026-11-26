# Language-ID router v1

Char n-gram (char_wb 1–5, 200k features) TF-IDF + LogisticRegression, trained on 28662 train-split texts (15,000 English originals + Gemini roman_ur/ur/mixed translations). `langid_v1_routed` applies the gateway rule: probability < 0.6 → mixed (v3 path). `old_8_word` is the previous rule detector (other → en). Gemini's `mixed` and `roman_ur` overlap heavily (short code-mixed lines are often labelled mixed); both route to the same model, so en-vs-non-en accuracy is the routing-relevant number.

## dev (n=8776)

| Detector | Macro-F1 | F1 en | F1 roman_ur | F1 ur | F1 mixed | en vs non-en acc. | Confusion (rows true en/roman_ur/ur/mixed) |
|---|---:|---:|---:|---:|---:|---:|---|
| langid_v1 | 0.945 | 0.9981 | 0.8876 | 1.0 | 0.8944 | 0.9983 | [[3975, 1, 0, 0], [5, 1366, 0, 206], [0, 0, 1602, 0], [9, 134, 0, 1478]] |
| langid_v1_routed | 0.9397 | 0.9979 | 0.8727 | 0.9988 | 0.8895 | 0.9981 | [[3963, 0, 0, 13], [1, 1265, 0, 311], [0, 0, 1598, 4], [3, 57, 0, 1561]] |
| old_8_word | 0.4304 | 0.7242 | 0.1053 | 0.8921 | 0.0 | 0.655 | [[3976, 0, 0, 0], [1485, 92, 0, 0], [0, 0, 1290, 312], [1543, 78, 0, 0]] |

## test (n=1636)

| Detector | Macro-F1 | F1 en | F1 roman_ur | F1 ur | F1 mixed | en vs non-en acc. | Confusion (rows true en/roman_ur/ur/mixed) |
|---|---:|---:|---:|---:|---:|---:|---|
| langid_v1 | 0.9434 | 0.9844 | 0.897 | 1.0 | 0.8921 | 0.9902 | [[506, 0, 0, 0], [5, 331, 0, 45], [0, 0, 373, 0], [11, 26, 0, 339]] |
| langid_v1_routed | 0.9425 | 0.9901 | 0.887 | 0.9973 | 0.8957 | 0.9939 | [[502, 0, 0, 4], [3, 310, 0, 68], [0, 0, 371, 2], [3, 8, 0, 365]] |
| old_8_word | 0.3432 | 0.5734 | 0.0104 | 0.789 | 0.0 | 0.5397 | [[506, 0, 0, 0], [379, 2, 0, 0], [0, 0, 243, 130], [374, 2, 0, 0]] |

## overrefusal (n=6146)

| Detector | Macro-F1 | F1 en | F1 roman_ur | F1 ur | F1 mixed | en vs non-en acc. | Confusion (rows true en/roman_ur/ur/mixed) |
|---|---:|---:|---:|---:|---:|---:|---|
| langid_v1 | 0.9484 | 0.9997 | 0.8922 | 1.0 | 0.9018 | 0.9998 | [[1568, 0, 0, 0], [0, 1291, 0, 192], [0, 0, 1537, 0], [1, 120, 0, 1437]] |
| langid_v1_routed | 0.9436 | 1.0 | 0.8761 | 1.0 | 0.8981 | 1.0 | [[1568, 0, 0, 0], [0, 1202, 0, 281], [0, 0, 1537, 0], [0, 59, 0, 1499]] |
| old_8_word | 0.3936 | 0.5158 | 0.0608 | 0.998 | 0.0 | 0.521 | [[1568, 0, 0, 0], [1435, 48, 0, 0], [0, 0, 1531, 6], [1509, 49, 0, 0]] |

