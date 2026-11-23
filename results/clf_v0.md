# v0 Evaluation Report

- Fixed classifier threshold: `0.6422568559646606`
- Threshold selected on `dev_public` only; all other sets use the same threshold.
- Base model: FacebookAI/xlm-roberta-base; English-only training; 2 epochs; seed 42.

## Main metrics

| Model | Evaluation set | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| classifier | dev_public | 0.9390 | 0.0194 | 0.9514 |
| rules | dev_public | 0.0193 | 0.0070 | 0.0374 |
| deberta | dev_public | 0.7459 | 0.1661 | 0.7295 |
| classifier | indirect_eval | 0.6307 | n/a | 0.7735 |
| rules | indirect_eval | 0.0000 | n/a | 0.0000 |
| deberta | indirect_eval | 0.5105 | n/a | 0.6760 |
| classifier | external_eval | 0.5939 | 0.0065 | 0.7405 |
| rules | external_eval | 0.0102 | 0.0000 | 0.0201 |
| deberta | external_eval | 0.6904 | 0.0162 | 0.8047 |
| classifier | overrefusal_eval | n/a | 0.1684 | 0.0000 |
| rules | overrefusal_eval | n/a | 0.0000 | n/a |
| deberta | overrefusal_eval | n/a | 0.0548 | 0.0000 |
| classifier | benign_email_probe | n/a | 1.0000 | 0.0000 |
| rules | benign_email_probe | n/a | 0.0000 | n/a |
| deberta | benign_email_probe | n/a | 0.0000 | n/a |

## Breakdown by source and language

### dev_public

| Model | Group | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| classifier | lang:en | 0.9390 | 0.0194 | 0.9514 |
| classifier | source:aegis2 | n/a | 0.0012 | 0.0000 |
| classifier | source:deepset_pi | 0.3529 | 0.0000 | 0.5217 |
| classifier | source:gandalf | 0.9899 | n/a | 0.9949 |
| classifier | source:hackaprompt | 0.9517 | n/a | 0.9753 |
| classifier | source:jailbreak_llms | 0.5091 | 0.0312 | 0.4786 |
| classifier | source:jb_class | 0.5484 | 0.0094 | 0.6939 |
| classifier | source:llmail | 1.0000 | n/a | 1.0000 |
| classifier | source:spml | 0.9367 | 0.0000 | 0.9673 |
| classifier | source:toxicchat | n/a | 0.0080 | 0.0000 |
| classifier | source:wildguardmix | 0.9600 | n/a | 0.9796 |
| classifier | source:wildjailbreak | 0.9713 | 0.0438 | 0.9598 |
| rules | lang:en | 0.0193 | 0.0070 | 0.0374 |
| rules | source:aegis2 | n/a | 0.0000 | n/a |
| rules | source:deepset_pi | 0.0000 | 0.0000 | 0.0000 |
| rules | source:gandalf | 0.1414 | n/a | 0.2478 |
| rules | source:hackaprompt | 0.0170 | n/a | 0.0335 |
| rules | source:jailbreak_llms | 0.0000 | 0.0257 | 0.0000 |
| rules | source:jb_class | 0.0000 | 0.0000 | 0.0000 |
| rules | source:llmail | 0.0000 | n/a | 0.0000 |
| rules | source:spml | 0.0416 | 0.0000 | 0.0799 |
| rules | source:toxicchat | n/a | 0.0000 | n/a |
| rules | source:wildguardmix | 0.0000 | n/a | 0.0000 |
| rules | source:wildjailbreak | 0.0000 | 0.0000 | 0.0000 |
| deberta | lang:en | 0.7459 | 0.1661 | 0.7295 |
| deberta | source:aegis2 | n/a | 0.0061 | 0.0000 |
| deberta | source:deepset_pi | 0.3529 | 0.0000 | 0.5217 |
| deberta | source:gandalf | 1.0000 | n/a | 1.0000 |
| deberta | source:hackaprompt | 0.9318 | n/a | 0.9647 |
| deberta | source:jailbreak_llms | 0.7818 | 0.0991 | 0.4175 |
| deberta | source:jb_class | 0.5806 | 0.0000 | 0.7347 |
| deberta | source:llmail | 0.5217 | n/a | 0.6857 |
| deberta | source:spml | 0.9928 | 0.1309 | 0.9623 |
| deberta | source:toxicchat | n/a | 0.0240 | 0.0000 |
| deberta | source:wildguardmix | 0.4767 | n/a | 0.6456 |
| deberta | source:wildjailbreak | 0.5943 | 0.6183 | 0.5081 |
### indirect_eval

| Model | Group | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| classifier | lang:en | 0.6304 | n/a | 0.7733 |
| classifier | lang:mixed | 1.0000 | n/a | 1.0000 |
| classifier | source:bipia | 0.0000 | n/a | 0.0000 |
| classifier | source:injecagent | 0.0047 | n/a | 0.0094 |
| classifier | source:llmail | 1.0000 | n/a | 1.0000 |
| rules | lang:en | 0.0000 | n/a | 0.0000 |
| rules | lang:mixed | 0.0000 | n/a | 0.0000 |
| rules | source:bipia | 0.0000 | n/a | 0.0000 |
| rules | source:injecagent | 0.0000 | n/a | 0.0000 |
| rules | source:llmail | 0.0000 | n/a | 0.0000 |
| deberta | lang:en | 0.5104 | n/a | 0.6758 |
| deberta | lang:mixed | 0.6667 | n/a | 0.8000 |
| deberta | source:bipia | 0.1040 | n/a | 0.1884 |
| deberta | source:injecagent | 0.6575 | n/a | 0.7934 |
| deberta | source:llmail | 0.4585 | n/a | 0.6287 |
### external_eval

| Model | Group | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| classifier | lang:en | 0.5939 | 0.0065 | 0.7405 |
| classifier | source:deepset_pi | 0.3833 | 0.0000 | 0.5542 |
| classifier | source:jb_class | 0.6861 | 0.0079 | 0.8069 |
| rules | lang:en | 0.0102 | 0.0000 | 0.0201 |
| rules | source:deepset_pi | 0.0000 | 0.0000 | 0.0000 |
| rules | source:jb_class | 0.0146 | 0.0000 | 0.0288 |
| deberta | lang:en | 0.6904 | 0.0162 | 0.8047 |
| deberta | source:deepset_pi | 0.3667 | 0.0000 | 0.5366 |
| deberta | source:jb_class | 0.8321 | 0.0198 | 0.8906 |
### overrefusal_eval

| Model | Group | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| classifier | source:or_bench | n/a | 0.2002 | 0.0000 |
| classifier | source:xstest | n/a | 0.0000 | n/a |
| rules | source:or_bench | n/a | 0.0000 | n/a |
| rules | source:xstest | n/a | 0.0000 | n/a |
| deberta | source:or_bench | n/a | 0.0652 | 0.0000 |
| deberta | source:xstest | n/a | 0.0000 | n/a |
| classifier | or_bench | n/a | 0.2002 | n/a |
| classifier | xstest | n/a | 0.0000 | n/a |
| rules | or_bench | n/a | 0.0000 | n/a |
| rules | xstest | n/a | 0.0000 | n/a |
| deberta | or_bench | n/a | 0.0652 | n/a |
| deberta | xstest | n/a | 0.0000 | n/a |
### benign_email_probe

| Model | Group | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| classifier | lang:en | n/a | 1.0000 | 0.0000 |
| classifier | source:benign_email_probe | n/a | 1.0000 | 0.0000 |
| rules | lang:en | n/a | 0.0000 | n/a |
| rules | source:benign_email_probe | n/a | 0.0000 | n/a |
| deberta | lang:en | n/a | 0.0000 | n/a |
| deberta | source:benign_email_probe | n/a | 0.0000 | n/a |

## Operational measurements

- Training time: **1,718.10 seconds**.
- Peak training VRAM: **5.26 GB**.
- Smoke-test peak VRAM: **5.23 GB**.
- Evaluation latency is reported in `results/v0_evaluation.json`; batched evaluation records per-row median/p95 values.
- Indirect evaluation source scope: LLMail is marked **seen distribution**; BIPIA and InjecAgent are **unseen**.

## Benign email shortcut probe

The 100 synthetic `Subject: ... Body: ...` emails are eval-only and were not used for training. The FPR is the `benign_email_probe` row in the main table.

## Embedding repair explanation

The audit found 935 candidate near-duplicate pairs above cosine 0.95. It moved 1,728 complete `split_group`s from dev to train because split groups must remain intact; one candidate pair can belong to a group containing many related rows, and multiple candidate pairs can reference the same or neighboring groups. The repair removed leakage while preserving group boundaries.

## Limitations

- `dev_public` is in-distribution and is not an independent human test set.
- No Roman Urdu human evaluation has been performed yet.
- ProtectAI DeBERTa is an English-focused baseline and is not a multilingual solution.
- Metrics are descriptive measurements on the listed files; no improvement claim is made.
