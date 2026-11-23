# Public data statistics

File | Label | Type | Lang | Source | Rows
---|---|---|---|---|---:
external_eval | attack | injection | en | deepset_pi | 60
external_eval | attack | jailbreak | en | jb_class | 137
external_eval | benign | none | en | deepset_pi | 56
external_eval | benign | none | en | jb_class | 253
harm | attack | harm | en | aegis2 | 11986
harm | attack | harm | en | beavertails | 1924
harm | attack | harm | en | harmbench | 317
harm | attack | harm | en | toxicchat | 688
harm | benign | none | en | aegis2 | 8569
harm | benign | none | en | beavertails | 1455
harm | benign | none | en | toxicchat | 8940
harm | benign | none | other | aegis2 | 19
harm | benign | none | other | toxicchat | 5
indirect_eval | attack | injection | en | bipia | 125
indirect_eval | attack | injection | en | injecagent | 1054
indirect_eval | attack | injection | en | llmail | 1997
indirect_eval | attack | injection | mixed | llmail | 3
injection_train | attack | extraction | en | gandalf | 998
injection_train | attack | injection | en | deepset_pi | 203
injection_train | attack | injection | en | hackaprompt | 2922
injection_train | attack | injection | en | llmail | 2907
injection_train | attack | injection | en | spml | 2922
injection_train | attack | injection | mixed | llmail | 15
injection_train | attack | jailbreak | en | jailbreak_llms | 761
injection_train | attack | jailbreak | en | jb_class | 509
injection_train | attack | jailbreak | en | wildguardmix | 2922
injection_train | attack | jailbreak | en | wildjailbreak | 2921
injection_train | benign | none | en | deepset_pi | 343
injection_train | benign | none | en | jailbreak_llms | 5572
injection_train | benign | none | en | jb_class | 1062
injection_train | benign | none | en | spml | 3372
injection_train | benign | none | en | wildjailbreak | 5573
injection_train | benign | none | ur | jailbreak_llms | 1
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
urdu_benign | benign | none | roman_ur | smat26 | 19433

## Filtering by source

Source | Scanned | Kept before balancing | Final classifier | Duplicate | Near duplicate | PII dropped | PII redacted | PII exempt in synthetic eval | Length | Other language | Unclear | Goal cap
---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:
aegis2 | 28216 | 20574 | 0 | 7537 | 0 | 79 | 0 | 0 | 26 | 0 | 0 | 0
ai4privacy | 5017 | 5000 | 0 | 14 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0
beavertails | 10000 | 3379 | 0 | 6605 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0
bipia | 125 | 125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
deepset_pi | 662 | 662 | 546 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
erupd | 65132 | 58065 | 0 | 7066 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
gandalf | 1000 | 998 | 998 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0
hackaprompt | 28051 | 5000 | 2922 | 43 | 90092 | 1 | 0 | 0 | 1151 | 941 | 21804 | 482725
harmbench | 320 | 317 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
injecagent | 1054 | 1054 | 0 | 0 | 0 | 0 | 0 | 703 | 0 | 0 | 0 | 0
jailbreak_llms | 15140 | 13608 | 6334 | 1197 | 0 | 99 | 0 | 0 | 189 | 47 | 0 | 0
jb_class | 1998 | 1961 | 1571 | 27 | 0 | 6 | 0 | 0 | 3 | 1 | 0 | 0
llmail | 16470 | 7000 | 2922 | 9458 | 0 | 0 | 13848 | 0 | 12 | 0 | 0 | 0
or_bench | 1319 | 1319 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
safemtdata | 2280 | 2274 | 0 | 0 | 0 | 4 | 0 | 0 | 2 | 0 | 0 | 0
smat26 | 20228 | 19466 | 0 | 560 | 0 | 11 | 0 | 0 | 191 | 0 | 0 | 0
spml | 16012 | 15913 | 6294 | 98 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
synthetic | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
tom_gibbs_multiturn | 6840 | 6839 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 78 | 0
toxicchat | 10165 | 9633 | 0 | 516 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0
uci_roman_urdu | 20229 | 0 | 0 | 20026 | 0 | 11 | 0 | 0 | 192 | 0 | 0 | 0
wildguardmix | 3202 | 3000 | 2922 | 200 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0
wildjailbreak | 16026 | 16000 | 8494 | 2 | 0 | 6 | 0 | 0 | 18 | 0 | 0 | 0
xstest | 250 | 249 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0

## Final classifier source shares

Label | Source | Rows | Share
---|---|---:|---:
attack | deepset_pi | 203 | 1.19%
attack | gandalf | 998 | 5.84%
attack | hackaprompt | 2922 | 17.11%
attack | jailbreak_llms | 761 | 4.46%
attack | jb_class | 509 | 2.98%
attack | llmail | 2922 | 17.11%
attack | spml | 2922 | 17.11%
attack | wildguardmix | 2922 | 17.11%
attack | wildjailbreak | 2921 | 17.10%
benign | deepset_pi | 343 | 2.15%
benign | jailbreak_llms | 5573 | 35.00%
benign | jb_class | 1062 | 6.67%
benign | spml | 3372 | 21.18%
benign | wildjailbreak | 5573 | 35.00%

Classifier training pool: 17080 attack, 15923 benign.
Actual benign/attack ratio: 0.9323; target: 1.5000.
Every attack source is capped at 25% of final attacks; every benign source is capped at 35% of final benign rows after hard-negative-first selection.
PII exemption applies only to synthetic indirect-evaluation sources: injecagent, bipia, agentdojo.
Raw directory size: 1.257 GiB.
