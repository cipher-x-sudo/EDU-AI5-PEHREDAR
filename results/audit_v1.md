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
jailbreak_llms | benign | none | en | 12842
jailbreak_llms | benign | none | ur | 2
jb_class | attack | jailbreak | en | 509
jb_class | benign | none | en | 1061
llmail | attack | injection | en | 2907
llmail | attack | injection | mixed | 15
spml | attack | injection | en | 2922
spml | benign | none | en | 3372
wildguardmix | attack | harm | en | 2922
wildjailbreak | attack | jailbreak | en | 2921
wildjailbreak | benign | none | en | 8000

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
jailbreak_llms | benign | jailbreak_llms-5413, jailbreak_llms-14375, jailbreak_llms-5828, jailbreak_llms-10208, jailbreak_llms-8133, jailbreak_llms-8858, jailbreak_llms-12024, jailbreak_llms-8165, jailbreak_llms-5545, jailbreak_llms-9409, jailbreak_llms-14611, jailbreak_llms-9727, jailbreak_llms-7428, jailbreak_llms-2186, jailbreak_llms-11974, jailbreak_llms-15018, jailbreak_llms-3788, jailbreak_llms-12795, jailbreak_llms-4108, jailbreak_llms-10057, jailbreak_llms-8881, jailbreak_llms-8840, jailbreak_llms-14559, jailbreak_llms-4909, jailbreak_llms-9602, jailbreak_llms-13151, jailbreak_llms-5028, jailbreak_llms-11884, jailbreak_llms-7144, jailbreak_llms-15094
jb_class | attack | jb_class-761, jb_class-528, jb_class-327, jb_class-461, jb_class-1307, jb_class-1248, jb_class-1571, jb_class-672, jb_class-1258, jb_class-38, jb_class-907, jb_class-689, jb_class-876, jb_class-367, jb_class-87, jb_class-10, jb_class-448, jb_class-1504, jb_class-298, jb_class-1014, jb_class-1188, jb_class-881, jb_class-1564, jb_class-811, jb_class-981, jb_class-755, jb_class-723, jb_class-1477, jb_class-1355, jb_class-1092
jb_class | benign | jb_class-226, jb_class-1206, jb_class-1224, jb_class-924, jb_class-1181, jb_class-1344, jb_class-1350, jb_class-89, jb_class-1448, jb_class-288, jb_class-737, jb_class-1574, jb_class-1541, jb_class-413, jb_class-663, jb_class-584, jb_class-781, jb_class-998, jb_class-820, jb_class-133, jb_class-248, jb_class-176, jb_class-1164, jb_class-487, jb_class-106, jb_class-193, jb_class-161, jb_class-1020, jb_class-1185, jb_class-1152
llmail | attack | llmail-11896, llmail-10544, llmail-10249, llmail-2810, llmail-10568, llmail-8194, llmail-11985, llmail-12306, llmail-9686, llmail-7910, llmail-11758, llmail-8453, llmail-11046, llmail-8815, llmail-8889, llmail-7798, llmail-12016, llmail-7802, llmail-7026, llmail-11544, llmail-10764, llmail-10786, llmail-9600, llmail-7455, llmail-581, llmail-7184, llmail-7053, llmail-7738, llmail-10431, llmail-9723
spml | attack | spml-8855, spml-8605, spml-11974, spml-11175, spml-3740, spml-2374, spml-12228, spml-15, spml-13883, spml-13870, spml-6494, spml-4714, spml-12872, spml-4129, spml-13674, spml-15571, spml-5017, spml-15032, spml-11456, spml-4558, spml-6762, spml-1195, spml-11014, spml-8819, spml-6577, spml-10323, spml-11830, spml-14779, spml-13322, spml-3824
spml | benign | spml-4063, spml-4007, spml-13733, spml-2716, spml-11101, spml-12844, spml-2354, spml-10038, spml-2521, spml-14726, spml-9292, spml-9301, spml-3574, spml-15081, spml-3022, spml-7819, spml-8427, spml-9283, spml-530, spml-7184, spml-8183, spml-4080, spml-1268, spml-13365, spml-15281, spml-13784, spml-11071, spml-5735, spml-8506, spml-509
wildguardmix | attack | wildguardmix-1250, wildguardmix-2286, wildguardmix-1235, wildguardmix-1205, wildguardmix-476, wildguardmix-2953, wildguardmix-3053, wildguardmix-316, wildguardmix-1647, wildguardmix-1233, wildguardmix-3072, wildguardmix-1331, wildguardmix-1761, wildguardmix-1280, wildguardmix-518, wildguardmix-1278, wildguardmix-839, wildguardmix-1967, wildguardmix-2655, wildguardmix-1492, wildguardmix-42, wildguardmix-2009, wildguardmix-456, wildguardmix-516, wildguardmix-1164, wildguardmix-611, wildguardmix-1338, wildguardmix-2719, wildguardmix-766, wildguardmix-474
wildjailbreak | attack | wildjailbreak-6712, wildjailbreak-6295, wildjailbreak-4149, wildjailbreak-3627, wildjailbreak-3043, wildjailbreak-7800, wildjailbreak-4125, wildjailbreak-340, wildjailbreak-3661, wildjailbreak-4976, wildjailbreak-2332, wildjailbreak-7829, wildjailbreak-7510, wildjailbreak-3992, wildjailbreak-5632, wildjailbreak-174, wildjailbreak-1078, wildjailbreak-5645, wildjailbreak-7248, wildjailbreak-6694, wildjailbreak-2024, wildjailbreak-1743, wildjailbreak-6435, wildjailbreak-3142, wildjailbreak-6134, wildjailbreak-3660, wildjailbreak-2344, wildjailbreak-4491, wildjailbreak-1701, wildjailbreak-3463
wildjailbreak | benign | wildjailbreak-13035, wildjailbreak-12341, wildjailbreak-11295, wildjailbreak-13598, wildjailbreak-8827, wildjailbreak-14460, wildjailbreak-15776, wildjailbreak-12485, wildjailbreak-15023, wildjailbreak-8607, wildjailbreak-15370, wildjailbreak-14343, wildjailbreak-10064, wildjailbreak-15484, wildjailbreak-8689, wildjailbreak-14554, wildjailbreak-12459, wildjailbreak-9630, wildjailbreak-15447, wildjailbreak-10849, wildjailbreak-9689, wildjailbreak-9190, wildjailbreak-11103, wildjailbreak-12172, wildjailbreak-10946, wildjailbreak-9285, wildjailbreak-10877, wildjailbreak-8077, wildjailbreak-14543, wildjailbreak-11276

Potential label issues requiring human review:

- `jailbreak_llms-4909`: Benign row contains an explicit jailbreak cue; review source label.

## SPML

6294 selected rows use `text` = User Prompt as classifier input; `system_prompt` stores the paired System Prompt. `orig_label` 1 maps to attack and 0 to benign.
The source label is context dependent, so prompt-only training can introduce label noise.

## Leakage

Shared split groups across public train/dev: 0. Normalized exact text overlaps: 0.
Embedding cosine results are recorded separately when multilingual-e5-small is available.
The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.
