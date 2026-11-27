# Final evaluated gateway configuration (v1.0-eval-config)

- Commit: `5120a5b9874211cd4e95acbd5f5cc458b4fa61f4` (final_config: label the joint-sweep threshold and judge report); git tag `v1.0-eval-config`.
- `config/policy.yaml` SHA-256: `a3c17fe3bd11cf66de64e87ba9a54cfd8dd098bd1b1696215744e56e235575d0`.
- Frozen human test set: **not evaluated** (`scripts/eval_frozen.py` is run once by the team after the human test set exists).

## Pipeline

| Layer | Setting |
|---|---|
| L0 | `pehredar/normalizer.py` |
| L1 | rules (`pehredar/rules.py`) + confirmed-attack memory |
| Router | langid_v2 (`/app/models/langid_v2.joblib`): char 1–5 TF-IDF + LR, Roman-Urdu override, low confidence < 0.6 → mixed |
| L2 en | ProtectAI DeBERTa v3 base prompt-injection v2, threshold 0.5 |
| L2 non-en | XLM-R base v3 (`/app/models/clf_v3_e3`, encoder v2 512 head+tail), threshold 0.9682675 (2.75% L2-only dev non-en FPR, chosen jointly with the judge in results/judge_policy_joint.md); the model's own 2% all-dev threshold is 0.9630 |
| L2 mode | routed |
| Gateway thresholds | warn 0.45, judge_low 0.3, block 0.75; L2 scores under their threshold are capped below block |
| L3 judge | `hf.co/QuantFactory/Qwen3Guard-Gen-0.6B-GGUF:Q4_K_M` (temperature 0); XLM-R judge floor 0.0; blocks on unsafe categories ['Jailbreak', 'PII', 'Non-violent Illegal Acts', 'Violent']; controversial / other unsafe → warn (results/judge_policy_joint.md) |
| Output guard | canary + PII redaction + Qwen3Guard on the response |

## Model files (SHA-256)

**xlmr (non-English L2)** — `models/clf_v3_e3`

| file | sha256 |
|---|---|
| config.json | `78ea2ecded05d338715aa452059bd640f3297ada2e20bcd2dced3ded0c759ab2` |
| model.safetensors | `4d059f29658393e3a0187b53ba53709888f828ddec3da25cda228351f4ab046d` |
| model_card.md | `bfe071039936e54b57fd23baf684c06d72f15f9d086a6cef283060119f98eca2` |
| sentencepiece.bpe.model | `cfc8146abe2a0488e9e2a0c56de7952f7c11ab059eca145a0a727afce0db2865` |
| special_tokens_map.json | `06e405a36dfe4b9604f484f6a1e619af1a7f7d09e34a8555eb0b77b66318067f` |
| tokenizer.json | `3a56def25aa40facc030ea8b0b87f3688e4b3c39eb8b45d5702b3a1300fe2a20` |
| tokenizer_config.json | `ccf223ba3d5b3cc7fa6c3bf451f3bb40557a5c92b0aa33f63d17802ff1a96fd9` |
| training_report.json | `1012d321cb4eb6f6b9a85a22dd765520d74145e34a34baa8507aba3aa5f925a4` |

**langid_v2 (router)** — `models/langid_v2.joblib`

| file | sha256 |
|---|---|
| langid_v2.joblib | `e7dab7baf036a22003e43ce9d5c8547427cad26fefc66faa29580f23bc59ccf2` |

**deberta (English L2)** — `models/hf_cache/hub/models--protectai--deberta-v3-base-prompt-injection-v2/snapshots/90c9989b1a342275dd0d1a95aad283c04e075671`

| file | sha256 |
|---|---|
| added_tokens.json | `dc046d04c9b0ada7ae6f1dc89c465801799acdf0c9a6aab8c15a1b2d5ca4e91f` |
| config.json | `05079f4735092040b780d459027afab413faa6eeb66a548571a58832304b60bb` |
| model.safetensors | `6521cb8d0ac08148c81464899c424e6148fcc62befa371089fa4061d8b6e0424` |
| special_tokens_map.json | `9463f61e1b109a8eb4688b829260d7c6b1e6dff04c98ff7269bb89e2b92369b9` |
| spm.model | `c679fbf93643d19aab7ee10c0b99e460bdbc02fedf34b92b05af343b4af586fd` |
| tokenizer.json | `f0a66ad0d735d8dca9ecac4ff50fcdef4bb6adbadd2941a926844844d2c2059b` |
| tokenizer_config.json | `557b3d33d3f41b81ad769244e506549e98a1857d41dd58160aacd4d98d710b5a` |

Ollama IDs: guard 18cf431350f5; protected model (experiments only) 6d7230a92342.

Weights are not in git. XLM-R v3: `scripts/train_classifier.py`, run recorded in `models/clf_v3_e3/model_card.md` (data commit, dataset SHA-256, seed 42) on `data/processed/train_v3.jsonl`; langid_v2: `python -m scripts.train_langid`; DeBERTa from the Hugging Face snapshot above.
