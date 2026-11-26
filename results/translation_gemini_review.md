# Gemini translation review

Source: `data/processed/translation_review_gemini.csv` (100 rows). Reviewer field: {"claude-suggested": 100} — machine-suggested verdicts unless a human edited them.

| Lang/label | Good | n | Good rate |
|---|---:|---:|---:|
| mixed/attack | 16 | 16 | 100.0% |
| mixed/benign | 16 | 16 | 100.0% |
| roman_ur/attack | 17 | 17 | 100.0% |
| roman_ur/benign | 17 | 17 | 100.0% |
| ur/attack | 17 | 17 | 100.0% |
| ur/benign | 17 | 17 | 100.0% |

Overall: {"good": 100}

Rows whose note questions the source label: [{"id": "jailbreak_llms-2497-ur-gemini", "note": "good translation; LABEL_SUSPECT: DAN jailbreak marked benign in source - check label"}]

