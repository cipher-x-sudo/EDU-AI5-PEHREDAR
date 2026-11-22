# RU-Attack human test set

The frozen human test set is not yet collected. Generated examples cannot be presented as human-written or used to claim a human-test baseline.

Copy `data/collection_template.csv` to a private working file. Collect at least 50 Roman Urdu attacks and 50 benign Roman Urdu requests, including benign twins. Each participant must consent to research use. Put `yes` in the `consent` column only after consent is recorded, and put an internal consent record ID in `consent_reference`. Use a pseudonymous `author_code` and a `reviewer` code. Set `attack_family` for attacks; leave it empty for benign requests. Use `source=human` for genuine human-written text. Remove personal data before freezing. Review metadata stays only in the private CSV; the frozen JSONL contains just the model evaluation fields.

Save one JSON object per line in `data/frozen_test/human_v1.jsonl`:

```json
{"id":"ru-0001","text":"<human-written text>","lang":"roman_ur","label":"attack","type":"injection","source":"human","split_group":"family-001"}
```

`lang` is `en`, `ur`, `roman_ur`, or `mixed`. `label` is `attack` or `benign`. Benign records use `type: "none"`. Attack types are `injection`, `jailbreak`, `extraction`, `obfuscation`, or `harm`. Use one `split_group` for paraphrases of the same underlying request.

Seal the reviewed CSV:

```powershell
python -m scripts.freeze_collection data/private_reviewed.csv data/frozen_test/human_v1.jsonl
```

The command requires at least 50 attacks and 50 benign prompts, consent and review metadata, and attack families. It rejects duplicates and common PII patterns and creates a SHA-256 companion file. It refuses to overwrite an existing frozen set. A human reviewer must still check names and contextual personal information the patterns cannot recognize.

Never train on the frozen file or use it to tune thresholds. Keep it private until consent and redistribution checks are complete.

Before training, check the split groups and normalized text against the frozen set:

```powershell
python -m scripts.check_split data/processed/train.jsonl data/frozen_test/human_v1.jsonl
```

Run the rules-only baseline:

```powershell
python -m scripts.evaluate data/frozen_test/human_v1.jsonl --output baseline_rules.json
```

For the temporary English-focused DeBERTa comparison, install the classifier dependencies and run:

```powershell
pip install -e ".[classifier]"
python -m scripts.evaluate data/frozen_test/human_v1.jsonl --detector deberta --output baseline_deberta.json
python -m scripts.evaluate data/frozen_test/human_v1.jsonl --detector combined --classifier-dir models/clf_v1 --output candidate_combined.json
```

The report includes the input SHA-256 hash, predictions, per-language confusion counts, recall, false-positive rate, and latency. Missing language groups receive `null` rates. DeBERTa is only a temporary English prompt-injection baseline; its Roman Urdu result is reported as measured, without presenting it as a multilingual guard.
