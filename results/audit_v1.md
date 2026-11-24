# Public classifier audit v1

The sealed human frozen set and any human dev set were not opened or evaluated.
Scope: public classifier pool before the public 10% dev split.

## Counts by source × label × type × lang

Source | Label | Type | Lang | Rows
---|---|---|---|---:
aegis2 | benign | none | en | 8562
deepset_pi | attack | injection | en | 203
deepset_pi | benign | none | en | 343
gandalf | attack | extraction | en | 998
hackaprompt | attack | injection | en | 5000
jailbreak_llms | attack | jailbreak | en | 761
jailbreak_llms | benign | none | en | 12835
jailbreak_llms | benign | none | ur | 2
jb_class | attack | jailbreak | en | 509
jb_class | benign | none | en | 1062
llmail | attack | injection | en | 4977
llmail | attack | injection | mixed | 23
spml | attack | injection | en | 6635
spml | benign | none | en | 3372
toxicchat | benign | none | en | 8934
wildguardmix | attack | jailbreak | en | 3000
wildjailbreak | attack | jailbreak | en | 6634
wildjailbreak | benign | none | en | 8000

## Label review

Deterministic random sample: 480 rows, up to 30 per source and label (seed 42).
The sample IDs are listed below for manual review. Automated cue checks are triage, not label adjudication.

Source | Label | Sample IDs
---|---|---
aegis2 | benign | aegis2-1543, aegis2-11252, aegis2-23695, aegis2-22215, aegis2-2103, aegis2-16842, aegis2-15012, aegis2-14287, aegis2-5155, aegis2-11571, aegis2-11472, aegis2-14604, aegis2-20794, aegis2-21545, aegis2-9176, aegis2-11307, aegis2-19814, aegis2-5048, aegis2-20909, aegis2-6455, aegis2-23869, aegis2-10324, aegis2-17931, aegis2-5194, aegis2-26695, aegis2-23843, aegis2-17711, aegis2-20629, aegis2-26554, aegis2-14989
deepset_pi | attack | deepset_pi-213, deepset_pi-420, deepset_pi-219, deepset_pi-407, deepset_pi-403, deepset_pi-507, deepset_pi-375, deepset_pi-144, deepset_pi-539, deepset_pi-459, deepset_pi-491, deepset_pi-259, deepset_pi-417, deepset_pi-179, deepset_pi-495, deepset_pi-386, deepset_pi-513, deepset_pi-511, deepset_pi-410, deepset_pi-500, deepset_pi-333, deepset_pi-533, deepset_pi-169, deepset_pi-70, deepset_pi-522, deepset_pi-363, deepset_pi-385, deepset_pi-542, deepset_pi-364, deepset_pi-223
deepset_pi | benign | deepset_pi-312, deepset_pi-254, deepset_pi-36, deepset_pi-8, deepset_pi-302, deepset_pi-195, deepset_pi-307, deepset_pi-299, deepset_pi-217, deepset_pi-247, deepset_pi-86, deepset_pi-141, deepset_pi-63, deepset_pi-199, deepset_pi-445, deepset_pi-236, deepset_pi-37, deepset_pi-249, deepset_pi-82, deepset_pi-47, deepset_pi-222, deepset_pi-281, deepset_pi-130, deepset_pi-229, deepset_pi-118, deepset_pi-277, deepset_pi-327, deepset_pi-248, deepset_pi-137, deepset_pi-218
gandalf | attack | gandalf-941, gandalf-969, gandalf-621, gandalf-907, gandalf-761, gandalf-39, gandalf-295, gandalf-703, gandalf-56, gandalf-464, gandalf-914, gandalf-942, gandalf-692, gandalf-521, gandalf-230, gandalf-343, gandalf-227, gandalf-326, gandalf-786, gandalf-616, gandalf-596, gandalf-341, gandalf-788, gandalf-638, gandalf-494, gandalf-927, gandalf-637, gandalf-467, gandalf-432, gandalf-300
hackaprompt | attack | hackaprompt-15454, hackaprompt-5930, hackaprompt-5331, hackaprompt-13501, hackaprompt-11765, hackaprompt-14220, hackaprompt-16088, hackaprompt-16472, hackaprompt-27862, hackaprompt-9431, hackaprompt-12372, hackaprompt-26238, hackaprompt-26109, hackaprompt-9393, hackaprompt-4408, hackaprompt-6713, hackaprompt-20206, hackaprompt-7752, hackaprompt-10442, hackaprompt-14406, hackaprompt-6995, hackaprompt-20721, hackaprompt-24056, hackaprompt-14296, hackaprompt-21985, hackaprompt-3108, hackaprompt-16401, hackaprompt-3863, hackaprompt-10156, hackaprompt-20611
jailbreak_llms | attack | jailbreak_llms-736, jailbreak_llms-1199, jailbreak_llms-743, jailbreak_llms-1115, jailbreak_llms-875, jailbreak_llms-1326, jailbreak_llms-889, jailbreak_llms-857, jailbreak_llms-1222, jailbreak_llms-1172, jailbreak_llms-147, jailbreak_llms-1180, jailbreak_llms-780, jailbreak_llms-771, jailbreak_llms-1000, jailbreak_llms-847, jailbreak_llms-1353, jailbreak_llms-723, jailbreak_llms-1019, jailbreak_llms-1121, jailbreak_llms-1398, jailbreak_llms-1336, jailbreak_llms-1266, jailbreak_llms-1063, jailbreak_llms-1267, jailbreak_llms-809, jailbreak_llms-1085, jailbreak_llms-1092, jailbreak_llms-988, jailbreak_llms-719
jailbreak_llms | benign | jailbreak_llms-11228, jailbreak_llms-9583, jailbreak_llms-5480, jailbreak_llms-9683, jailbreak_llms-12230, jailbreak_llms-12274, jailbreak_llms-7766, jailbreak_llms-4479, jailbreak_llms-5772, jailbreak_llms-12917, jailbreak_llms-14587, jailbreak_llms-5395, jailbreak_llms-6793, jailbreak_llms-3598, jailbreak_llms-13720, jailbreak_llms-5592, jailbreak_llms-9491, jailbreak_llms-9033, jailbreak_llms-8321, jailbreak_llms-13535, jailbreak_llms-8731, jailbreak_llms-1691, jailbreak_llms-3188, jailbreak_llms-7984, jailbreak_llms-7589, jailbreak_llms-2754, jailbreak_llms-3850, jailbreak_llms-5207, jailbreak_llms-4077, jailbreak_llms-12140
jb_class | attack | jb_class-1364, jb_class-1339, jb_class-1106, jb_class-152, jb_class-1019, jb_class-437, jb_class-402, jb_class-1341, jb_class-1328, jb_class-1002, jb_class-112, jb_class-606, jb_class-512, jb_class-1093, jb_class-1117, jb_class-85, jb_class-1042, jb_class-793, jb_class-1511, jb_class-340, jb_class-1351, jb_class-1420, jb_class-559, jb_class-293, jb_class-1322, jb_class-38, jb_class-1218, jb_class-621, jb_class-890, jb_class-818
jb_class | benign | jb_class-884, jb_class-234, jb_class-687, jb_class-1509, jb_class-1250, jb_class-1257, jb_class-762, jb_class-521, jb_class-738, jb_class-699, jb_class-867, jb_class-1140, jb_class-1260, jb_class-1156, jb_class-673, jb_class-489, jb_class-1292, jb_class-25, jb_class-1514, jb_class-813, jb_class-1385, jb_class-734, jb_class-149, jb_class-320, jb_class-855, jb_class-252, jb_class-1197, jb_class-798, jb_class-126, jb_class-1131
llmail | attack | llmail-9370, llmail-10126, llmail-10853, llmail-12255, llmail-11566, llmail-7867, llmail-8796, llmail-8738, llmail-12037, llmail-7813, llmail-10531, llmail-11544, llmail-7588, llmail-10017, llmail-7694, llmail-165, llmail-8410, llmail-337, llmail-8038, llmail-9524, llmail-8806, llmail-11441, llmail-11800, llmail-544, llmail-12072, llmail-10530, llmail-9722, llmail-9384, llmail-10554, llmail-6782
spml | attack | spml-1101, spml-10908, spml-5951, spml-4076, spml-450, spml-5013, spml-12852, spml-11002, spml-4587, spml-11383, spml-13304, spml-11183, spml-6147, spml-11177, spml-7570, spml-14219, spml-2702, spml-12196, spml-568, spml-14417, spml-5856, spml-614, spml-10709, spml-66, spml-11424, spml-301, spml-7252, spml-5944, spml-5607, spml-4877
spml | benign | spml-15611, spml-1467, spml-13599, spml-732, spml-8142, spml-15590, spml-14252, spml-14730, spml-2634, spml-1228, spml-7382, spml-6879, spml-15352, spml-3595, spml-8791, spml-11385, spml-10154, spml-3617, spml-6461, spml-5448, spml-11801, spml-11399, spml-5014, spml-13721, spml-4445, spml-14726, spml-12313, spml-1815, spml-11312, spml-14377
toxicchat | benign | toxicchat-7050, toxicchat-5658, toxicchat-3401, toxicchat-8117, toxicchat-9962, toxicchat-5957, toxicchat-9689, toxicchat-10135, toxicchat-5903, toxicchat-2540, toxicchat-3034, toxicchat-5244, toxicchat-2735, toxicchat-2599, toxicchat-3368, toxicchat-5437, toxicchat-5600, toxicchat-4260, toxicchat-664, toxicchat-4140, toxicchat-5232, toxicchat-9243, toxicchat-8927, toxicchat-4959, toxicchat-1708, toxicchat-2358, toxicchat-7886, toxicchat-5510, toxicchat-1605, toxicchat-10060
wildguardmix | attack | wildguardmix-2329, wildguardmix-1521, wildguardmix-619, wildguardmix-2045, wildguardmix-1646, wildguardmix-2762, wildguardmix-3186, wildguardmix-891, wildguardmix-2705, wildguardmix-338, wildguardmix-1037, wildguardmix-1446, wildguardmix-1300, wildguardmix-831, wildguardmix-1596, wildguardmix-3163, wildguardmix-1144, wildguardmix-2473, wildguardmix-417, wildguardmix-319, wildguardmix-1592, wildguardmix-2714, wildguardmix-1508, wildguardmix-1168, wildguardmix-2229, wildguardmix-2454, wildguardmix-1160, wildguardmix-2426, wildguardmix-1838, wildguardmix-795
wildjailbreak | attack | wildjailbreak-3219, wildjailbreak-6925, wildjailbreak-1922, wildjailbreak-4134, wildjailbreak-7932, wildjailbreak-5952, wildjailbreak-460, wildjailbreak-6501, wildjailbreak-7658, wildjailbreak-239, wildjailbreak-3109, wildjailbreak-2461, wildjailbreak-91, wildjailbreak-2587, wildjailbreak-4652, wildjailbreak-1220, wildjailbreak-2606, wildjailbreak-7541, wildjailbreak-3951, wildjailbreak-7956, wildjailbreak-4646, wildjailbreak-93, wildjailbreak-6948, wildjailbreak-7529, wildjailbreak-3208, wildjailbreak-3376, wildjailbreak-2430, wildjailbreak-80, wildjailbreak-7231, wildjailbreak-1970
wildjailbreak | benign | wildjailbreak-13141, wildjailbreak-9141, wildjailbreak-10317, wildjailbreak-9030, wildjailbreak-13864, wildjailbreak-11826, wildjailbreak-11638, wildjailbreak-8685, wildjailbreak-9521, wildjailbreak-13779, wildjailbreak-12872, wildjailbreak-12507, wildjailbreak-8717, wildjailbreak-8511, wildjailbreak-9134, wildjailbreak-11868, wildjailbreak-11830, wildjailbreak-10193, wildjailbreak-15419, wildjailbreak-11586, wildjailbreak-13273, wildjailbreak-12697, wildjailbreak-12288, wildjailbreak-9077, wildjailbreak-10569, wildjailbreak-9920, wildjailbreak-8331, wildjailbreak-12292, wildjailbreak-12884, wildjailbreak-15268

Potential label issues requiring human review:

- No automatic cue flags in this sample. Human semantic review remains required.

## SPML

10007 selected rows use `text` = User Prompt as classifier input; `system_prompt` stores the paired System Prompt. `orig_label` 1 maps to attack and 0 to benign.
The source label is context dependent, so prompt-only training can introduce label noise.

## Leakage

Shared split groups across public train/dev: 0. Normalized exact text overlaps: 0.
Embedding model: `intfloat/multilingual-e5-small`; cosine threshold: 0.95. Candidate train/dev near-duplicates: 935; whole split_groups moved: 1728.
The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.


After adding safe ToxicChat and Aegis2 training rows: public pool 71,850 rows; train 64,666; dev_public 7,184; attacks 28,740; benign 43,110; ratio 1:1.5; normalized exact-overlap leakage: 0. Safe ToxicChat/Aegis2 rows were removed from eval-only outputs when duplicated. The frozen human set was not read.
## v1b data regeneration

- Public pool: 62,350 rows; train: 56,115; dev_public: 6,235.
- Exact normalized overlap check: 0; the split is group-disjoint.
- New benign sources: enron (851), dolly (5,000), and oasst1 (5,000).
- BIPIA remains test-only locally; no train split was available.
- The embedding audit was not completed after regeneration because the translation retry occupied the serialized GPU window.
