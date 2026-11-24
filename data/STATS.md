# Public data statistics

File | Label | Type | Lang | Source | Rows
---|---|---|---|---|---:
external_eval | attack | injection | en | deepset_pi | 60
external_eval | attack | jailbreak | en | jb_class | 137
external_eval | benign | none | en | deepset_pi | 56
external_eval | benign | none | en | jb_class | 253
harm | attack | harm | en | aegis2 | 11984
harm | attack | harm | en | beavertails | 1924
harm | attack | harm | en | harmbench | 317
harm | attack | harm | en | toxicchat | 686
harm | attack | harm | en | wildguardmix | 3000
harm | benign | none | en | beavertails | 1455
indirect_eval | attack | injection | en | bipia | 125
indirect_eval | attack | injection | en | injecagent | 1054
indirect_eval | attack | injection | en | llmail | 1980
indirect_eval | attack | injection | mixed | llmail | 20
injection_train | attack | extraction | en | gandalf | 998
injection_train | attack | injection | en | deepset_pi | 203
injection_train | attack | injection | en | hackaprompt | 4470
injection_train | attack | injection | en | llmail | 1997
injection_train | attack | injection | en | spml | 4470
injection_train | attack | injection | mixed | llmail | 3
injection_train | attack | jailbreak | en | jailbreak_llms | 761
injection_train | attack | jailbreak | en | jb_class | 509
injection_train | attack | jailbreak | en | wildjailbreak | 4469
injection_train | benign | none | en | aegis2 | 748
injection_train | benign | none | en | deepset_pi | 23
injection_train | benign | none | en | dolly | 5000
injection_train | benign | none | en | enron | 257
injection_train | benign | none | en | jailbreak_llms | 3450
injection_train | benign | none | en | jb_class | 102
injection_train | benign | none | en | oasst1 | 5000
injection_train | benign | none | en | spml | 3372
injection_train | benign | none | en | toxicchat | 868
injection_train | benign | none | en | wildjailbreak | 8000
multiturn | attack | jailbreak | en | safemtdata | 2274
multiturn | attack | jailbreak | en | tom_gibbs_multiturn | 4439
multiturn | benign | none | en | tom_gibbs_multiturn | 2400
overrefusal_eval | benign | none | en | or_bench | 1319
overrefusal_eval | benign | none | en | xstest | 249
pii_eval | attack | pii | en | ai4privacy | 4954
pii_eval | attack | pii | en | synthetic | 3
pii_eval | attack | pii | other | ai4privacy | 46
translation_pairs | benign | none | roman_ur | erupd | 58065
urdu_benign | benign | none | mixed | smat26 | 1
urdu_benign | benign | none | other | smat26 | 32
urdu_benign | benign | none | roman_ur | smat26 | 19431

## Filtering by source

Source | Scanned | Kept before balancing | Final classifier | Duplicate | Near duplicate | PII dropped | PII redacted | PII exempt in synthetic eval | Length | Other language | Unclear | Goal cap
---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:
aegis2 | 28216 | 20537 | 748 | 7555 | 0 | 79 | 0 | 0 | 26 | 19 | 0 | 0
ai4privacy | 5017 | 5000 | 0 | 14 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0
beavertails | 10000 | 3379 | 0 | 6605 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0
bipia | 125 | 125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
deepset_pi | 662 | 662 | 226 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
dolly | 5061 | 5000 | 5000 | 60 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0
enron | 2000 | 2000 | 257 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
erupd | 65132 | 58065 | 0 | 7066 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
gandalf | 1000 | 998 | 998 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0
hackaprompt | 28070 | 5000 | 4470 | 65 | 90029 | 1 | 0 | 0 | 1154 | 941 | 21804 | 482763
harmbench | 320 | 317 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
injecagent | 1054 | 1054 | 0 | 0 | 0 | 0 | 0 | 703 | 0 | 0 | 0 | 0
jailbreak_llms | 15140 | 13608 | 4211 | 1197 | 0 | 99 | 0 | 0 | 189 | 47 | 0 | 0
jb_class | 1998 | 1961 | 611 | 27 | 0 | 6 | 0 | 0 | 3 | 1 | 0 | 0
llmail | 11225 | 4000 | 2000 | 7221 | 0 | 0 | 9830 | 0 | 4 | 0 | 0 | 0
oasst1 | 5071 | 5000 | 5000 | 45 | 0 | 3 | 0 | 0 | 20 | 3 | 0 | 0
or_bench | 1319 | 1319 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
safemtdata | 2280 | 2274 | 0 | 0 | 0 | 4 | 0 | 0 | 2 | 0 | 0 | 0
smat26 | 20228 | 19464 | 0 | 562 | 0 | 11 | 0 | 0 | 191 | 0 | 0 | 0
spml | 16012 | 15913 | 7842 | 98 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
synthetic | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
tom_gibbs_multiturn | 6840 | 6839 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 78 | 0
toxicchat | 10165 | 9612 | 868 | 532 | 0 | 16 | 0 | 0 | 0 | 5 | 0 | 0
uci_roman_urdu | 20229 | 0 | 0 | 20026 | 0 | 11 | 0 | 0 | 192 | 0 | 0 | 0
wildguardmix | 3202 | 3000 | 0 | 199 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0
wildjailbreak | 16026 | 16000 | 12469 | 2 | 0 | 6 | 0 | 0 | 18 | 0 | 0 | 0
xstest | 250 | 249 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0

## Final classifier source shares

Label | Source | Rows | Share
---|---|---:|---:
attack | deepset_pi | 203 | 1.14%
attack | gandalf | 998 | 5.58%
attack | hackaprompt | 4470 | 25.00%
attack | jailbreak_llms | 761 | 4.26%
attack | jb_class | 509 | 2.85%
attack | llmail | 2000 | 11.19%
attack | spml | 4470 | 25.00%
attack | wildjailbreak | 4469 | 24.99%
benign | aegis2 | 748 | 2.79%
benign | deepset_pi | 23 | 0.09%
benign | dolly | 5000 | 18.64%
benign | enron | 257 | 0.96%
benign | jailbreak_llms | 3450 | 12.86%
benign | jb_class | 102 | 0.38%
benign | oasst1 | 5000 | 18.64%
benign | spml | 3372 | 12.57%
benign | toxicchat | 868 | 3.24%
benign | wildjailbreak | 8000 | 29.83%

Classifier training pool: 17880 attack, 26820 benign.
Actual benign/attack ratio: 1.5000; target: 1.5000.
Every attack source is capped at 25% of final attacks; every benign source is capped at 35% of final benign rows after hard-negative-first selection.
PII exemption applies only to synthetic indirect-evaluation sources: injecagent, bipia, agentdojo.
Raw directory size: 2.220 GiB.

## v2 split

- Change from v1b: WildGuardMix adversarial-harmful train rows go to `harm` only (see `results/audit_v1.md`).
- `train_public_v2.jsonl`: 40,229 rows; `dev_public_v2.jsonl`: 3,976 rows (group-disjoint split, then 466 dev groups removed by the e5-small embedding audit and 22 by the string near-duplicate repair; `check_split` passes).
- v1b files (`train_public.jsonl`, `dev_public.jsonl`, `dev_public_v1b.jsonl`) are unchanged.
