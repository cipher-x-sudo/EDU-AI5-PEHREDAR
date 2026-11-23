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
harm | benign | none | en | beavertails | 1455
indirect_eval | attack | injection | en | bipia | 125
indirect_eval | attack | injection | en | injecagent | 1054
indirect_eval | attack | injection | en | llmail | 1997
indirect_eval | attack | injection | mixed | llmail | 3
injection_train | attack | extraction | en | gandalf | 998
injection_train | attack | injection | en | deepset_pi | 203
injection_train | attack | injection | en | hackaprompt | 5000
injection_train | attack | injection | en | llmail | 4977
injection_train | attack | injection | en | spml | 6635
injection_train | attack | injection | mixed | llmail | 23
injection_train | attack | jailbreak | en | jailbreak_llms | 761
injection_train | attack | jailbreak | en | jb_class | 509
injection_train | attack | jailbreak | en | wildguardmix | 3000
injection_train | attack | jailbreak | en | wildjailbreak | 6634
injection_train | benign | none | en | aegis2 | 8562
injection_train | benign | none | en | deepset_pi | 343
injection_train | benign | none | en | jailbreak_llms | 12835
injection_train | benign | none | en | jb_class | 1062
injection_train | benign | none | en | spml | 3372
injection_train | benign | none | en | toxicchat | 8934
injection_train | benign | none | en | wildjailbreak | 8000
injection_train | benign | none | ur | jailbreak_llms | 2
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
aegis2 | 28216 | 20555 | 8562 | 7537 | 0 | 79 | 0 | 0 | 26 | 19 | 0 | 0
ai4privacy | 5017 | 5000 | 0 | 14 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0
beavertails | 10000 | 3379 | 0 | 6605 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0
bipia | 125 | 125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
deepset_pi | 662 | 662 | 546 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
erupd | 65132 | 58065 | 0 | 7066 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
gandalf | 1000 | 998 | 998 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0
hackaprompt | 28051 | 5000 | 5000 | 43 | 90092 | 1 | 0 | 0 | 1151 | 941 | 21804 | 482725
harmbench | 320 | 317 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
injecagent | 1054 | 1054 | 0 | 0 | 0 | 0 | 0 | 703 | 0 | 0 | 0 | 0
jailbreak_llms | 15140 | 13608 | 13598 | 1197 | 0 | 99 | 0 | 0 | 189 | 47 | 0 | 0
jb_class | 1998 | 1961 | 1571 | 27 | 0 | 6 | 0 | 0 | 3 | 1 | 0 | 0
llmail | 16470 | 7000 | 5000 | 9458 | 0 | 0 | 13848 | 0 | 12 | 0 | 0 | 0
or_bench | 1319 | 1319 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
safemtdata | 2280 | 2274 | 0 | 0 | 0 | 4 | 0 | 0 | 2 | 0 | 0 | 0
smat26 | 20228 | 19466 | 0 | 560 | 0 | 11 | 0 | 0 | 191 | 0 | 0 | 0
spml | 16012 | 15913 | 10007 | 98 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
synthetic | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
tom_gibbs_multiturn | 6840 | 6839 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 78 | 0
toxicchat | 10165 | 9628 | 8934 | 516 | 0 | 16 | 0 | 0 | 0 | 5 | 0 | 0
uci_roman_urdu | 20229 | 0 | 0 | 20026 | 0 | 11 | 0 | 0 | 192 | 0 | 0 | 0
wildguardmix | 3202 | 3000 | 3000 | 200 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0
wildjailbreak | 16026 | 16000 | 14634 | 2 | 0 | 6 | 0 | 0 | 18 | 0 | 0 | 0
xstest | 250 | 249 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0

## Final classifier source shares

Label | Source | Rows | Share
---|---|---:|---:
attack | deepset_pi | 203 | 0.71%
attack | gandalf | 998 | 3.47%
attack | hackaprompt | 5000 | 17.40%
attack | jailbreak_llms | 761 | 2.65%
attack | jb_class | 509 | 1.77%
attack | llmail | 5000 | 17.40%
attack | spml | 6635 | 23.09%
attack | wildguardmix | 3000 | 10.44%
attack | wildjailbreak | 6634 | 23.08%
benign | aegis2 | 8562 | 19.86%
benign | deepset_pi | 343 | 0.80%
benign | jailbreak_llms | 12837 | 29.78%
benign | jb_class | 1062 | 2.46%
benign | spml | 3372 | 7.82%
benign | toxicchat | 8934 | 20.72%
benign | wildjailbreak | 8000 | 18.56%

Classifier training pool: 28740 attack, 43110 benign.
Actual benign/attack ratio: 1.5000; target: 1.5000.
Every attack source is capped at 25% of final attacks; every benign source is capped at 35% of final benign rows after hard-negative-first selection.
PII exemption applies only to synthetic indirect-evaluation sources: injecagent, bipia, agentdojo.
Raw directory size: 1.257 GiB.
