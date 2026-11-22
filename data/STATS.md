# Public data statistics

File | Label | Type | Lang | Source | Rows
---|---|---|---|---|---:
external_eval | attack | injection | en | deepset_pi | 60
external_eval | attack | jailbreak | en | jb_class | 111
external_eval | benign | none | en | deepset_pi | 56
external_eval | benign | none | en | jb_class | 119
harm | attack | harm | en | aegis2 | 11965
harm | attack | harm | en | beavertails | 1924
harm | attack | harm | en | harmbench | 317
harm | attack | harm | en | toxicchat | 688
harm | benign | none | en | aegis2 | 8556
harm | benign | none | en | beavertails | 1455
harm | benign | none | en | toxicchat | 8942
harm | benign | none | other | aegis2 | 18
harm | benign | none | other | toxicchat | 5
indirect_eval | attack | injection | en | bipia | 125
indirect_eval | attack | injection | en | injecagent | 351
injection_train | attack | extraction | en | gandalf | 570
injection_train | attack | injection | en | deepset_pi | 202
injection_train | attack | jailbreak | en | jailbreak_llms | 570
injection_train | attack | jailbreak | en | jb_class | 460
injection_train | benign | none | en | deepset_pi | 41
injection_train | benign | none | en | jailbreak_llms | 1699
injection_train | benign | none | en | jb_class | 62
multiturn | attack | jailbreak | en | safemtdata | 600
multiturn | attack | jailbreak | en | tom_gibbs_multiturn | 4218
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

Source | Downloaded | Kept before balancing | Duplicate | PII | Length | Other language | Unclear
---|---:|---:|---:|---:|---:|---:|---:
aegis2 | 28216 | 20539 | 7328 | 75 | 274 | 0 | 0
ai4privacy | 5017 | 5000 | 14 | 0 | 3 | 0 | 0
beavertails | 10000 | 3379 | 6605 | 16 | 0 | 0 | 0
bipia | 125 | 125 | 0 | 0 | 0 | 0 | 0
deepset_pi | 662 | 661 | 0 | 0 | 1 | 0 | 0
erupd | 65132 | 58065 | 7066 | 0 | 1 | 0 | 0
gandalf | 1000 | 998 | 1 | 0 | 0 | 1 | 0
harmbench | 320 | 317 | 3 | 0 | 0 | 0 | 0
injecagent | 1054 | 351 | 0 | 703 | 0 | 0 | 0
jailbreak_llms | 15140 | 12312 | 1058 | 44 | 1680 | 46 | 0
jb_class | 1306 | 1201 | 18 | 2 | 85 | 0 | 0
or_bench | 1319 | 1319 | 0 | 0 | 0 | 0 | 0
safemtdata | 600 | 600 | 0 | 0 | 0 | 0 | 0
smat26 | 20228 | 19466 | 560 | 11 | 191 | 0 | 0
synthetic | 3 | 3 | 0 | 0 | 0 | 0 | 0
tom_gibbs_multiturn | 6840 | 6618 | 0 | 1 | 221 | 0 | 78
toxicchat | 10165 | 9635 | 514 | 16 | 0 | 0 | 0
uci_roman_urdu | 20229 | 0 | 20026 | 11 | 192 | 0 | 0
xstest | 250 | 249 | 1 | 0 | 0 | 0 | 0

Classifier training pool: 1802 attack, 1802 benign.
Raw directory size: 0.247 GiB.
