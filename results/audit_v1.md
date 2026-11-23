# Public classifier audit v1

The sealed human frozen set and any human dev set were not opened or evaluated.
Scope: public classifier pool before the public 10% dev split.

## Counts by source × label × type × lang

Source | Label | Type | Lang | Rows
---|---|---|---|---:
deepset_pi | attack | injection | en | 203
deepset_pi | benign | none | en | 343
gandalf | attack | extraction | en | 998
hackaprompt | attack | injection | en | 2922
jailbreak_llms | attack | jailbreak | en | 761
jailbreak_llms | benign | none | en | 5572
jailbreak_llms | benign | none | ur | 1
jb_class | attack | jailbreak | en | 509
jb_class | benign | none | en | 1062
llmail | attack | injection | en | 2907
llmail | attack | injection | mixed | 15
spml | attack | injection | en | 2922
spml | benign | none | en | 3372
wildguardmix | attack | jailbreak | en | 2922
wildjailbreak | attack | jailbreak | en | 2921
wildjailbreak | benign | none | en | 5573

## Label review

Deterministic random sample: 420 rows, up to 30 per source and label (seed 42).
The sample IDs are listed below for manual review. Automated cue checks are triage, not label adjudication.

Source | Label | Sample IDs
---|---|---
deepset_pi | attack | deepset_pi-516, deepset_pi-250, deepset_pi-126, deepset_pi-542, deepset_pi-379, deepset_pi-368, deepset_pi-361, deepset_pi-270, deepset_pi-541, deepset_pi-224, deepset_pi-526, deepset_pi-81, deepset_pi-493, deepset_pi-191, deepset_pi-504, deepset_pi-441, deepset_pi-136, deepset_pi-131, deepset_pi-213, deepset_pi-354, deepset_pi-364, deepset_pi-474, deepset_pi-507, deepset_pi-87, deepset_pi-497, deepset_pi-334, deepset_pi-519, deepset_pi-543, deepset_pi-44, deepset_pi-359
deepset_pi | benign | deepset_pi-356, deepset_pi-53, deepset_pi-254, deepset_pi-101, deepset_pi-193, deepset_pi-341, deepset_pi-29, deepset_pi-190, deepset_pi-220, deepset_pi-288, deepset_pi-161, deepset_pi-156, deepset_pi-312, deepset_pi-158, deepset_pi-30, deepset_pi-292, deepset_pi-61, deepset_pi-246, deepset_pi-123, deepset_pi-365, deepset_pi-448, deepset_pi-173, deepset_pi-310, deepset_pi-147, deepset_pi-46, deepset_pi-264, deepset_pi-74, deepset_pi-68, deepset_pi-301, deepset_pi-485
gandalf | attack | gandalf-276, gandalf-749, gandalf-162, gandalf-14, gandalf-709, gandalf-309, gandalf-811, gandalf-366, gandalf-171, gandalf-888, gandalf-313, gandalf-899, gandalf-192, gandalf-45, gandalf-355, gandalf-517, gandalf-685, gandalf-869, gandalf-435, gandalf-249, gandalf-440, gandalf-426, gandalf-292, gandalf-717, gandalf-345, gandalf-746, gandalf-963, gandalf-729, gandalf-697, gandalf-164
hackaprompt | attack | hackaprompt-6487, hackaprompt-7329, hackaprompt-15684, hackaprompt-4182, hackaprompt-18489, hackaprompt-15397, hackaprompt-26790, hackaprompt-23437, hackaprompt-19314, hackaprompt-7546, hackaprompt-9139, hackaprompt-4943, hackaprompt-17614, hackaprompt-9054, hackaprompt-21275, hackaprompt-11806, hackaprompt-17921, hackaprompt-11039, hackaprompt-20811, hackaprompt-24283, hackaprompt-19227, hackaprompt-12116, hackaprompt-17306, hackaprompt-5219, hackaprompt-20771, hackaprompt-17379, hackaprompt-814, hackaprompt-2919, hackaprompt-24023, hackaprompt-7605
jailbreak_llms | attack | jailbreak_llms-690, jailbreak_llms-1161, jailbreak_llms-1292, jailbreak_llms-1155, jailbreak_llms-1273, jailbreak_llms-803, jailbreak_llms-779, jailbreak_llms-1290, jailbreak_llms-830, jailbreak_llms-529, jailbreak_llms-829, jailbreak_llms-284, jailbreak_llms-1397, jailbreak_llms-1244, jailbreak_llms-1154, jailbreak_llms-746, jailbreak_llms-729, jailbreak_llms-1098, jailbreak_llms-1051, jailbreak_llms-1119, jailbreak_llms-1172, jailbreak_llms-877, jailbreak_llms-1179, jailbreak_llms-932, jailbreak_llms-464, jailbreak_llms-844, jailbreak_llms-1069, jailbreak_llms-228, jailbreak_llms-206, jailbreak_llms-701
jailbreak_llms | benign | jailbreak_llms-6516, jailbreak_llms-14881, jailbreak_llms-7170, jailbreak_llms-10257, jailbreak_llms-9999, jailbreak_llms-12333, jailbreak_llms-6714, jailbreak_llms-15095, jailbreak_llms-9087, jailbreak_llms-2964, jailbreak_llms-12269, jailbreak_llms-2040, jailbreak_llms-4611, jailbreak_llms-13250, jailbreak_llms-4941, jailbreak_llms-10080, jailbreak_llms-15046, jailbreak_llms-5823, jailbreak_llms-13634, jailbreak_llms-6002, jailbreak_llms-12146, jailbreak_llms-8715, jailbreak_llms-2147, jailbreak_llms-9024, jailbreak_llms-8366, jailbreak_llms-14017, jailbreak_llms-13136, jailbreak_llms-3576, jailbreak_llms-13328, jailbreak_llms-6786
jb_class | attack | jb_class-907, jb_class-689, jb_class-876, jb_class-367, jb_class-87, jb_class-10, jb_class-448, jb_class-1504, jb_class-298, jb_class-1014, jb_class-1188, jb_class-881, jb_class-1564, jb_class-811, jb_class-981, jb_class-755, jb_class-723, jb_class-1477, jb_class-1355, jb_class-1092, jb_class-1356, jb_class-412, jb_class-902, jb_class-1133, jb_class-1143, jb_class-630, jb_class-293, jb_class-733, jb_class-1119, jb_class-97
jb_class | benign | jb_class-1344, jb_class-1350, jb_class-89, jb_class-1448, jb_class-288, jb_class-737, jb_class-1574, jb_class-1541, jb_class-413, jb_class-663, jb_class-584, jb_class-781, jb_class-997, jb_class-820, jb_class-133, jb_class-248, jb_class-176, jb_class-1164, jb_class-487, jb_class-106, jb_class-193, jb_class-161, jb_class-1020, jb_class-1185, jb_class-1152, jb_class-190, jb_class-1178, jb_class-1081, jb_class-469, jb_class-988
llmail | attack | llmail-11985, llmail-12306, llmail-9686, llmail-7910, llmail-11758, llmail-8453, llmail-11046, llmail-8815, llmail-8889, llmail-7798, llmail-12016, llmail-7802, llmail-7026, llmail-11544, llmail-10764, llmail-10786, llmail-9600, llmail-7455, llmail-581, llmail-7184, llmail-7053, llmail-7738, llmail-10431, llmail-9723, llmail-9565, llmail-9494, llmail-10797, llmail-10481, llmail-6991, llmail-368
spml | attack | spml-12228, spml-15, spml-13883, spml-13870, spml-6494, spml-4714, spml-12872, spml-4129, spml-13674, spml-15571, spml-5017, spml-15032, spml-11456, spml-4558, spml-6762, spml-1195, spml-11014, spml-8819, spml-6577, spml-10323, spml-11830, spml-14779, spml-13322, spml-3824, spml-5421, spml-5345, spml-14326, spml-3711, spml-11139, spml-13287
spml | benign | spml-2354, spml-10038, spml-2521, spml-14726, spml-9292, spml-9301, spml-3574, spml-15081, spml-3022, spml-7819, spml-8427, spml-9283, spml-530, spml-7184, spml-8183, spml-4080, spml-1268, spml-13365, spml-15281, spml-13784, spml-11071, spml-5735, spml-8506, spml-509, spml-11145, spml-8699, spml-15587, spml-11062, spml-10902, spml-5818
wildguardmix | attack | wildguardmix-2953, wildguardmix-3053, wildguardmix-316, wildguardmix-1647, wildguardmix-1233, wildguardmix-3072, wildguardmix-1331, wildguardmix-1761, wildguardmix-1280, wildguardmix-518, wildguardmix-1278, wildguardmix-839, wildguardmix-1967, wildguardmix-2655, wildguardmix-1492, wildguardmix-42, wildguardmix-2009, wildguardmix-456, wildguardmix-516, wildguardmix-1164, wildguardmix-611, wildguardmix-1338, wildguardmix-2719, wildguardmix-766, wildguardmix-474, wildguardmix-403, wildguardmix-3129, wildguardmix-2296, wildguardmix-2072, wildguardmix-1838
wildjailbreak | attack | wildjailbreak-7800, wildjailbreak-4125, wildjailbreak-340, wildjailbreak-3661, wildjailbreak-4976, wildjailbreak-2332, wildjailbreak-7829, wildjailbreak-7510, wildjailbreak-3992, wildjailbreak-5632, wildjailbreak-4149, wildjailbreak-174, wildjailbreak-1078, wildjailbreak-5645, wildjailbreak-7248, wildjailbreak-6694, wildjailbreak-2024, wildjailbreak-1743, wildjailbreak-6435, wildjailbreak-3142, wildjailbreak-6134, wildjailbreak-3660, wildjailbreak-2344, wildjailbreak-4491, wildjailbreak-1701, wildjailbreak-3463, wildjailbreak-4690, wildjailbreak-3841, wildjailbreak-2603, wildjailbreak-5421
wildjailbreak | benign | wildjailbreak-8381, wildjailbreak-13608, wildjailbreak-9188, wildjailbreak-9703, wildjailbreak-8223, wildjailbreak-10089, wildjailbreak-9858, wildjailbreak-8519, wildjailbreak-13570, wildjailbreak-9813, wildjailbreak-11222, wildjailbreak-11582, wildjailbreak-13160, wildjailbreak-11359, wildjailbreak-11265, wildjailbreak-8498, wildjailbreak-11817, wildjailbreak-13257, wildjailbreak-13364, wildjailbreak-9100, wildjailbreak-12479, wildjailbreak-14046, wildjailbreak-12386, wildjailbreak-9465, wildjailbreak-13155, wildjailbreak-15962, wildjailbreak-15770, wildjailbreak-12994, wildjailbreak-10582, wildjailbreak-11082

Potential label issues requiring human review:

- `jailbreak_llms-4611`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-4941`: Benign row contains an explicit jailbreak cue; review source label.

## SPML

6294 selected rows use `text` = User Prompt as classifier input; `system_prompt` stores the paired System Prompt. `orig_label` 1 maps to attack and 0 to benign.
The source label is context dependent, so prompt-only training can introduce label noise.

## Leakage

Shared split groups across public train/dev: 0. Normalized exact text overlaps: 0.
Embedding cosine results are recorded separately when multilingual-e5-small is available.

After benign source-cap regeneration: public pool 33,003 rows; train 29,705; dev_public 3,298; normalized exact-overlap leakage: 0. The benign cap is enforced at 35% per source. Available benign data yields 15,923 rows (target 25,620), so the ratio target cannot be met without violating the cap; shortfall: 9,697 rows.
The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.
