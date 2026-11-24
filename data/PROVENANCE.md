# Public dataset provenance

Generated 2026-11-24. Revisions are immutable Hub or GitHub commit hashes unless noted.
Rows downloaded counts source rows scanned by the unifier; rows kept are before the final classifier balancing step.
Raw and processed files remain outside Git.

Name | Source URL | Revision | Download date | License | Rows downloaded | Rows kept | Usage | Redistributable | Notes
---|---|---|---|---|---:|---:|---|---|---
aegis2 | https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-2.0 | `d86bb8bedff51d25ac834ab7838f1cc61acb7a2c` | 2026-11-22 | cc-by-4.0 | 28216 | 20537 | eval_only, train | true | —
agentdojo | https://github.com/ethz-spylab/agentdojo | `089ed468cf3ed0322acc66b0211f26d9d90dbf60` | 2026-11-22 | mit | 0 | 0 | skipped | true | Task GOAL definitions are not injected payloads; no eval rows extracted. Synthetic indirect-eval PII exemption applies if payloads become available.
ai4privacy | https://huggingface.co/datasets/ai4privacy/open-pii-masking-500k-ai4privacy | `506996d625ed970a0063432daf6007cf4a3a48e3` | 2026-11-22 | CC-BY-4.0 + Llama Community License | 5017 | 5000 | eval_only | false | CC BY 4.0 plus Llama Community License terms; marked nonredistributable conservatively.
beavertails | https://huggingface.co/datasets/PKU-Alignment/BeaverTails | `8401fe609d288129cc684a9b3be6a93e41cfe678` | 2026-11-22 | cc-by-nc-4.0 | 10000 | 3379 | train | false | 30k train first 10,000 rows only. Noncommercial and nonredistributable.
bipia | https://github.com/microsoft/BIPIA | `a004b69ec0dd446e0afd461d98cb5e96e120a5d0` | 2026-11-22 | mit; source task restrictions | 125 | 125 | eval_only | false | Only text/code attack lists, no licensed WebQA/Summarization contexts. Synthetic indirect-eval PII exemption.
deepset_pi | https://huggingface.co/datasets/deepset/prompt-injections | `4f61ecb038e9c3fb77e21034b22511b523772cdd` | 2026-11-22 | apache-2.0 | 662 | 662 | secondary_eval, train | true | —
dolly | https://huggingface.co/datasets/databricks/databricks-dolly-15k | `bdd27f4d94b9c1f951818a7da7fd7aeea5dbff1a` | 2026-11-24 | cc-by-sa-3.0 | 5061 | 5000 | train | true | CC BY-SA 3.0; first instruction field used as English benign hard negatives.
enron | https://huggingface.co/datasets/LLM-PBE/enron-email | `a4761f17a981d79bd286bfff7dd0d53645aa5027` | 2026-11-24 | apache-2.0 | 2000 | 2000 | train | true | Apache-2.0 card on the pinned mirror; formatted as Subject/Body, truncated and PII-redacted.
erupd | https://github.com/bose9999/ERUPD-dataset | `843d2071885b2db2715bc3146396964d576f4047` | 2026-11-22 | cc-by-4.0 | 65132 | 58065 | eval_only | true | English/Roman Urdu translation pairs, not attacks.
gandalf | https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions | `04737b65e90a6794ec227012e4a255a7def6344b` | 2026-11-22 | mit | 1000 | 998 | train | true | —
hackaprompt | https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset | `25b87fbedfb86840abaf8cd09af7a029208a971a` | 2026-11-23 | mit | 28070 | 5000 | train | true | MIT card; access granted. Maximum 5,000 training rows and 20% per goal after near-deduplication.
harmbench | https://github.com/centerforaisafety/HarmBench | `8e1604d1171fe8a48d8febecd22f600e462bdcdd` | 2026-11-22 | mit | 320 | 317 | eval_only | true | —
injecagent | https://github.com/uiuc-kang-lab/InjecAgent | `f19c9f2c79a41046eb13c03c51a24c567a8ffa07` | 2026-11-22 | mit | 1054 | 1054 | eval_only | true | Synthetic indirect-eval PII exemption; matched rows retained and counted in STATS.md.
injectionshield | https://github.com/mshahzaib7/injectionshield | `f1b8bdcb5bdc0e0d059ebdef8413332956a049b8` | 2026-11-22 | mixed upstream | 0 | 0 | skipped | false | Only 3 display examples and summary metrics in repository; benchmark folders are placeholders. No usable full benchmark rows. Never train.
jailbreak_llms | https://github.com/verazuo/jailbreak_llms | `4f4031bf8be187f4478c7f94f42b08714722c12e` | 2026-11-22 | mit | 15140 | 13608 | train | true | —
jb_class | https://huggingface.co/datasets/jackhhao/jailbreak-classification | `2f2ceeb39658696fd3f462403562b6eea5306287` | 2026-11-22 | apache-2.0 | 1998 | 1961 | secondary_eval, train | true | —
llmail | https://huggingface.co/datasets/microsoft/llmail-inject-challenge | `1063bdf01ec8762b812d5e06ee768a06faa5a6f7` | 2026-11-22 | mit | 11225 | 4000 | eval_only, train | true | MIT card; Phase2 only. Subject and body joined; PII redacted before deduplication; first 2,000 accepted for training, next 2,000 for indirect evaluation.
mhj | https://huggingface.co/datasets/ScaleAI/mhj | `ad6e928f5c2823f53fbb828f6d60dd4137fd43e7` | 2026-11-22 | cc-by-nc-4.0 | 0 | 0 | skipped | false | Gated; repository has no accessible data file until approval. Nonredistributable.
necent_merged | https://huggingface.co/datasets/Necent/llm-jailbreak-prompt-injection-dataset | `4edfb5aeaafe58c9bf489a478a42188f239d7c1e` | 2026-11-22 | mixed upstream | 0 | 0 | skipped | false | Gated; access denied. Mixed upstream licenses require per-source review.
oasst1 | https://huggingface.co/datasets/OpenAssistant/oasst1 | `fdf72ae0827c1cda404aff25b6603abec9e3399b` | 2026-11-24 | apache-2.0 | 5071 | 5000 | train | true | Apache-2.0; English prompter/user messages used as benign hard negatives.
or_bench | https://huggingface.co/datasets/bench-llm/or-bench | `e36d8b80e81837c8a8f264bbb2a49f1b32c7e272` | 2026-11-22 | cc-by-4.0 | 1319 | 1319 | eval_only | true | —
red_queen | https://huggingface.co/datasets/YifanJ/Red_Queen | `8505fdb5270585a820ba49f086ec67e1ad310c9d` | 2026-11-22 | unspecified | 0 | 0 | skipped | false | Official GitHub/HF source; no explicit dataset license; skipped.
safeguard_pi | https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection | `a3a877d608f37b7d20d9945671902df895ecdb46` | 2026-11-22 | unspecified | 0 | 0 | skipped | false | Card does not state a license; skipped pending rights confirmation.
safemtdata | https://huggingface.co/datasets/SafeMTData/SafeMTData | `04af7bd0b6b6044e797e936d79674e348316b9b8` | 2026-11-22 | mit | 2280 | 2274 | train | true | —
smat26 | https://github.com/Smat26/Roman-Urdu-Dataset | `762ba24484024855798ef15d248e45f12a410de3` | 2026-11-22 | gpl-3.0 | 20228 | 19464 | train | true | —
spml | https://huggingface.co/datasets/reshabhs/SPML_Chatbot_Prompt_Injection | `02ce8084e979bc7d4c24ee35d22ecb7f2db96ff5` | 2026-11-22 | mit | 16012 | 15913 | train | true | MIT card; label depends on paired system prompt. Both system and user text retained together.
tensor_trust | https://huggingface.co/datasets/qxcv/tensor-trust | `4de2b2fe01ba0cb6fbf7cbb9f1a3fabaf8157372` | 2026-11-22 | unspecified | 0 | 0 | skipped | false | Card does not state a license; skipped pending rights confirmation.
tom_gibbs_multiturn | https://huggingface.co/datasets/tom-gibbs/multi-turn_jailbreak_attack_datasets | `e3b30257c4d6be5438ea19f0989ac82c24234fe4` | 2026-11-22 | mit | 6840 | 6839 | train | true | —
toxicchat | https://huggingface.co/datasets/lmsys/toxic-chat | `29df8e4dba60e1f4af4b4075c0705c5b313548a8` | 2026-11-22 | cc-by-nc-4.0 | 10165 | 9612 | eval_only, train | false | Latest 0124 config. Noncommercial and nonredistributable.
uci_roman_urdu | https://archive.ics.uci.edu/dataset/458/roman+urdu+data+set | `sha256:78e7cd1d7b0dc8e960a52c9151fc3114c70a3809111d3421581bbad931a6f5a8` | 2026-11-22 | cc-by-4.0 | 20229 | 0 | skipped | true | UCI dataset 458; overlaps Smat26 and is deduplicated.
wildguardmix | https://huggingface.co/datasets/allenai/wildguardmix | `d29c47f41c8b51348b5c8e8c81c039b3132b66d1` | 2026-11-23 | odc-by | 3202 | 3000 | train | false | ODC-By card; access granted. Adversarial harmful train rows capped at 3,000 before global balancing.
wildjailbreak | https://huggingface.co/datasets/allenai/wildjailbreak | `5ddc12a7894f842b0619b8e1c7ee496b198af009` | 2026-11-23 | odc-by | 16026 | 16000 | train | false | ODC-By card; access granted. Adversarial harmful and benign rows capped at 8,000 each before global balancing.
xstest | https://github.com/paul-rottger/exaggerated-safety | `d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d` | 2026-11-22 | cc-by-4.0 | 250 | 249 | eval_only | true | —
ruwv_nsr | https://data.mendeley.com/datasets/v5jfhsvtmd/5 | unavailable | not downloaded | unverified | 0 | 0 | skipped | false | Manual Mendeley download and license review required.

## Manual actions for the team

- WildJailbreak, WildGuardMix, and HackAPrompt access was verified on 2026-11-23; rerun the downloader when refreshing the pinned revisions.
- https://huggingface.co/datasets/Necent/llm-jailbreak-prompt-injection-dataset — click **Accept**, then check every upstream source license before unifying.
- https://huggingface.co/datasets/ScaleAI/mhj — provide requested contact information and click **Accept**; obtain the actual dataset files from the maintainers.
- https://data.mendeley.com/datasets/v5jfhsvtmd/5 — download RUwV-NSR and confirm its dataset license.
- https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection — obtain an explicit dataset license from the maintainer.
- https://huggingface.co/datasets/qxcv/tensor-trust — obtain an explicit dataset license from the maintainer.
- https://huggingface.co/datasets/YifanJ/Red_Queen — obtain an explicit dataset license from the maintainer.
- https://github.com/mshahzaib7/injectionshield — obtain the full benchmark rows from its maintainers for external evaluation; the repository has only 3 display examples.

## Run

Run `docker compose --profile data run --rm data python -m scripts.download_data` and then `docker compose --profile data run --rm data python -m scripts.unify`.
The downloader skips files already present and stops before `data/raw/` exceeds 20 GB.
Unification rebuilds processed files from raw inputs and excludes any exact or normalized frozen-test text from training.
