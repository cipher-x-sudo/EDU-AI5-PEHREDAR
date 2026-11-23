# Public classifier audit v1

The sealed human frozen set and any human dev set were not opened or evaluated.
Scope: public classifier pool before the public 10% dev split.

## Counts by source × label × type × lang

Source | Label | Type | Lang | Rows
---|---|---|---|---:
deepset_pi | attack | injection | en | 183
deepset_pi | benign | none | en | 37
gandalf | attack | extraction | en | 898
jailbreak_llms | attack | jailbreak | en | 685
jailbreak_llms | benign | none | en | 3380
jb_class | attack | jailbreak | en | 458
jb_class | benign | none | en | 129
llmail | attack | injection | en | 1109
llmail | attack | injection | mixed | 2
spml | attack | injection | en | 1111
spml | benign | none | en | 3123

## Label review

Deterministic random sample: 300 rows, up to 30 per source and label (seed 42).
The sample IDs are listed below for manual review. Automated cue checks are triage, not label adjudication.

Source | Label | Sample IDs
---|---|---
deepset_pi | attack | deepset_pi-87, deepset_pi-267, deepset_pi-138, deepset_pi-399, deepset_pi-387, deepset_pi-378, deepset_pi-311, deepset_pi-259, deepset_pi-494, deepset_pi-518, deepset_pi-224, deepset_pi-534, deepset_pi-474, deepset_pi-145, deepset_pi-139, deepset_pi-237, deepset_pi-375, deepset_pi-383, deepset_pi-507, deepset_pi-539, deepset_pi-71, deepset_pi-523, deepset_pi-368, deepset_pi-506, deepset_pi-472, deepset_pi-376, deepset_pi-490, deepset_pi-533, deepset_pi-400, deepset_pi-11
deepset_pi | benign | deepset_pi-22, deepset_pi-431, deepset_pi-337, deepset_pi-285, deepset_pi-217, deepset_pi-24, deepset_pi-74, deepset_pi-355, deepset_pi-53, deepset_pi-148, deepset_pi-141, deepset_pi-234, deepset_pi-52, deepset_pi-220, deepset_pi-347, deepset_pi-312, deepset_pi-205, deepset_pi-132, deepset_pi-253, deepset_pi-18, deepset_pi-458, deepset_pi-384, deepset_pi-288, deepset_pi-336, deepset_pi-162, deepset_pi-435, deepset_pi-9, deepset_pi-178, deepset_pi-272, deepset_pi-291
gandalf | attack | gandalf-153, gandalf-852, gandalf-354, gandalf-984, gandalf-421, gandalf-193, gandalf-746, gandalf-36, gandalf-900, gandalf-213, gandalf-53, gandalf-409, gandalf-614, gandalf-824, gandalf-561, gandalf-510, gandalf-284, gandalf-519, gandalf-5, gandalf-335, gandalf-860, gandalf-399, gandalf-896, gandalf-873, gandalf-837, gandalf-183, gandalf-792, gandalf-294, gandalf-708, gandalf-932
jailbreak_llms | attack | jailbreak_llms-1334, jailbreak_llms-1226, jailbreak_llms-806, jailbreak_llms-698, jailbreak_llms-1367, jailbreak_llms-679, jailbreak_llms-932, jailbreak_llms-1305, jailbreak_llms-284, jailbreak_llms-1071, jailbreak_llms-1317, jailbreak_llms-1040, jailbreak_llms-229, jailbreak_llms-725, jailbreak_llms-1364, jailbreak_llms-1082, jailbreak_llms-1292, jailbreak_llms-943, jailbreak_llms-228, jailbreak_llms-1294, jailbreak_llms-858, jailbreak_llms-863, jailbreak_llms-719, jailbreak_llms-700, jailbreak_llms-801, jailbreak_llms-1196, jailbreak_llms-1361, jailbreak_llms-1188, jailbreak_llms-1336, jailbreak_llms-937
jailbreak_llms | benign | jailbreak_llms-5533, jailbreak_llms-14608, jailbreak_llms-11050, jailbreak_llms-6392, jailbreak_llms-3805, jailbreak_llms-6371, jailbreak_llms-3333, jailbreak_llms-2752, jailbreak_llms-14021, jailbreak_llms-12618, jailbreak_llms-5069, jailbreak_llms-4757, jailbreak_llms-11752, jailbreak_llms-12773, jailbreak_llms-10911, jailbreak_llms-12104, jailbreak_llms-12864, jailbreak_llms-7539, jailbreak_llms-12976, jailbreak_llms-3847, jailbreak_llms-8664, jailbreak_llms-3719, jailbreak_llms-6793, jailbreak_llms-11196, jailbreak_llms-3097, jailbreak_llms-3053, jailbreak_llms-6786, jailbreak_llms-4388, jailbreak_llms-5413, jailbreak_llms-14438
jb_class | attack | jb_class-58, jb_class-525, jb_class-1004, jb_class-761, jb_class-825, jb_class-1211, jb_class-765, jb_class-87, jb_class-552, jb_class-885, jb_class-1506, jb_class-904, jb_class-703, jb_class-194, jb_class-1210, jb_class-1568, jb_class-369, jb_class-1294, jb_class-408, jb_class-100, jb_class-735, jb_class-824, jb_class-1502, jb_class-48, jb_class-901, jb_class-1325, jb_class-497, jb_class-120, jb_class-656, jb_class-683
jb_class | benign | jb_class-499, jb_class-190, jb_class-1251, jb_class-174, jb_class-722, jb_class-1263, jb_class-403, jb_class-730, jb_class-1070, jb_class-388, jb_class-1031, jb_class-1018, jb_class-953, jb_class-1507, jb_class-322, jb_class-1032, jb_class-1216, jb_class-17, jb_class-806, jb_class-789, jb_class-1474, jb_class-139, jb_class-1098, jb_class-856, jb_class-440, jb_class-118, jb_class-90, jb_class-694, jb_class-988, jb_class-1139
llmail | attack | llmail-8505, llmail-11666, llmail-11691, llmail-9874, llmail-12163, llmail-6984, llmail-7773, llmail-9255, llmail-329, llmail-95, llmail-21, llmail-7741, llmail-9034, llmail-8559, llmail-9453, llmail-226, llmail-9619, llmail-11615, llmail-6810, llmail-51, llmail-10887, llmail-8068, llmail-10250, llmail-61, llmail-449, llmail-10081, llmail-10946, llmail-10827, llmail-6, llmail-10922
spml | attack | spml-10914, spml-5446, spml-12081, spml-2305, spml-2578, spml-3879, spml-9922, spml-1866, spml-9367, spml-13600, spml-9611, spml-2655, spml-7907, spml-15496, spml-12557, spml-12612, spml-8481, spml-6253, spml-8278, spml-8034, spml-9374, spml-11421, spml-127, spml-11657, spml-778, spml-5810, spml-12984, spml-2868, spml-1555, spml-8097
spml | benign | spml-5161, spml-12900, spml-4554, spml-13810, spml-15959, spml-5436, spml-15343, spml-11636, spml-5046, spml-7267, spml-12053, spml-11133, spml-9271, spml-702, spml-10312, spml-11969, spml-8117, spml-15072, spml-13511, spml-4188, spml-5917, spml-5826, spml-14573, spml-4063, spml-11319, spml-13494, spml-3620, spml-10045, spml-3838, spml-15611

Potential label issues requiring human review:

- `jailbreak_llms-3805`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-2752`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-12618`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-12976`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-3847`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-4388`: Benign row contains an explicit jailbreak cue; review source label.

## SPML

4234 selected rows use `text` = User Prompt as classifier input; `system_prompt` stores the paired System Prompt. `orig_label` 1 maps to attack and 0 to benign.
The source label is context dependent, so prompt-only training can introduce label noise.

## Leakage

Shared split groups across public train/dev: 0. Normalized exact text overlaps: 0.
Embedding cosine results are recorded separately when multilingual-e5-small is available.
The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.
