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
harm | benign | none | en | aegis2 | 8570
harm | benign | none | en | beavertails | 1455
harm | benign | none | en | toxicchat | 8942
harm | benign | none | other | aegis2 | 19
harm | benign | none | other | toxicchat | 5
indirect_eval | attack | injection | en | bipia | 125
indirect_eval | attack | injection | en | injecagent | 1054
indirect_eval | attack | injection | en | llmail | 1997
indirect_eval | attack | injection | mixed | llmail | 3
injection_train | attack | extraction | en | gandalf | 998
injection_train | attack | injection | en | deepset_pi | 203
injection_train | attack | injection | en | llmail | 1233
injection_train | attack | injection | en | spml | 1234
injection_train | attack | injection | mixed | llmail | 2
injection_train | attack | jailbreak | en | jailbreak_llms | 761
injection_train | attack | jailbreak | en | jb_class | 509
injection_train | benign | none | en | deepset_pi | 41
injection_train | benign | none | en | jailbreak_llms | 3756
injection_train | benign | none | en | jb_class | 143
injection_train | benign | none | en | spml | 3470
multiturn | attack | jailbreak | en | safemtdata | 2274
multiturn | attack | jailbreak | en | tom_gibbs_multiturn | 4439
multiturn | benign | none | en | tom_gibbs_multiturn | 2400
overrefusal_eval | benign | none | en | or_bench | 1319
overrefusal_eval | benign | none | en | xstest | 249
pii_eval | attack | pii | en | ai4privacy | 4953
pii_eval | attack | pii | en | synthetic | 3
pii_eval | attack | pii | other | ai4privacy | 46
pii_eval | attack | pii | roman_ur | ai4privacy | 1
translation_pairs | benign | none | roman_ur | erupd | 58065
urdu_benign | benign | none | mixed | smat26 | 7
urdu_benign | benign | none | other | smat26 | 32
urdu_benign | benign | none | roman_ur | smat26 | 19427

## Filtering by source

Source | Scanned | Kept before balancing | Final classifier | Duplicate | Near duplicate | PII dropped | PII redacted | PII exempt in synthetic eval | Length | Other language | Unclear | Goal cap
---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:
aegis2 | 28216 | 20575 | 0 | 7536 | 0 | 79 | 0 | 0 | 26 | 0 | 0 | 0
ai4privacy | 5017 | 5000 | 0 | 14 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0
beavertails | 10000 | 3379 | 0 | 6605 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0
bipia | 125 | 125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
deepset_pi | 662 | 662 | 244 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
erupd | 65132 | 58065 | 0 | 7066 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0
gandalf | 1000 | 998 | 998 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0
harmbench | 320 | 317 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
injecagent | 1054 | 1054 | 0 | 0 | 0 | 0 | 0 | 703 | 0 | 0 | 0 | 0
jailbreak_llms | 15140 | 13608 | 4517 | 1197 | 0 | 99 | 0 | 0 | 189 | 47 | 0 | 0
jb_class | 1998 | 1961 | 652 | 27 | 0 | 6 | 0 | 0 | 3 | 1 | 0 | 0
llmail | 16470 | 7000 | 1235 | 9458 | 0 | 0 | 13848 | 0 | 12 | 0 | 0 | 0
or_bench | 1319 | 1319 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
safemtdata | 2280 | 2274 | 0 | 0 | 0 | 4 | 0 | 0 | 2 | 0 | 0 | 0
smat26 | 20228 | 19466 | 0 | 560 | 0 | 11 | 0 | 0 | 191 | 0 | 0 | 0
spml | 16012 | 16012 | 4704 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
synthetic | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0
tom_gibbs_multiturn | 6840 | 6839 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 78 | 0
toxicchat | 10165 | 9635 | 0 | 514 | 0 | 16 | 0 | 0 | 0 | 0 | 0 | 0
uci_roman_urdu | 20229 | 0 | 0 | 20026 | 0 | 11 | 0 | 0 | 192 | 0 | 0 | 0
xstest | 250 | 249 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0

Classifier training pool: 4940 attack, 7410 benign (1:1.5).
Every attack source is capped at 25% of final attacks; benign hard negatives are selected first.
PII exemption applies only to synthetic indirect-evaluation sources: injecagent, bipia, agentdojo.
Raw directory size: 0.572 GiB.
