# Public classifier audit v1

The sealed human frozen set and any human dev set were not opened or evaluated.
Scope: public classifier pool before the public 10% dev split.

## Counts by source × label × type × lang

Source | Label | Type | Lang | Rows
---|---|---|---|---:
deepset_pi | attack | injection | en | 203
deepset_pi | benign | none | en | 41
gandalf | attack | extraction | en | 998
jailbreak_llms | attack | jailbreak | en | 761
jailbreak_llms | benign | none | en | 3756
jb_class | attack | jailbreak | en | 509
jb_class | benign | none | en | 143
llmail | attack | injection | en | 1233
llmail | attack | injection | mixed | 2
spml | attack | injection | en | 1234
spml | benign | none | en | 3470

## Label review

Deterministic random sample: 300 rows, up to 30 per source and label (seed 42).
The sample IDs are listed below for manual review. Automated cue checks are triage, not label adjudication.

Source | Label | Sample IDs
---|---|---
deepset_pi | attack | deepset_pi-516, deepset_pi-250, deepset_pi-126, deepset_pi-542, deepset_pi-379, deepset_pi-368, deepset_pi-361, deepset_pi-270, deepset_pi-541, deepset_pi-224, deepset_pi-526, deepset_pi-81, deepset_pi-493, deepset_pi-191, deepset_pi-504, deepset_pi-441, deepset_pi-136, deepset_pi-131, deepset_pi-213, deepset_pi-354, deepset_pi-364, deepset_pi-474, deepset_pi-507, deepset_pi-87, deepset_pi-497, deepset_pi-334, deepset_pi-519, deepset_pi-543, deepset_pi-44, deepset_pi-359
deepset_pi | benign | deepset_pi-347, deepset_pi-53, deepset_pi-27, deepset_pi-105, deepset_pi-205, deepset_pi-344, deepset_pi-288, deepset_pi-74, deepset_pi-203, deepset_pi-220, deepset_pi-355, deepset_pi-312, deepset_pi-52, deepset_pi-148, deepset_pi-141, deepset_pi-22, deepset_pi-458, deepset_pi-217, deepset_pi-303, deepset_pi-273, deepset_pi-198, deepset_pi-132, deepset_pi-234, deepset_pi-431, deepset_pi-351, deepset_pi-336, deepset_pi-435, deepset_pi-285, deepset_pi-162, deepset_pi-9
gandalf | attack | gandalf-67, gandalf-915, gandalf-894, gandalf-432, gandalf-631, gandalf-276, gandalf-749, gandalf-162, gandalf-14, gandalf-709, gandalf-309, gandalf-811, gandalf-366, gandalf-171, gandalf-888, gandalf-313, gandalf-899, gandalf-192, gandalf-45, gandalf-355, gandalf-517, gandalf-685, gandalf-869, gandalf-435, gandalf-249, gandalf-440, gandalf-426, gandalf-292, gandalf-717, gandalf-345
jailbreak_llms | attack | jailbreak_llms-957, jailbreak_llms-935, jailbreak_llms-898, jailbreak_llms-1077, jailbreak_llms-857, jailbreak_llms-884, jailbreak_llms-1191, jailbreak_llms-774, jailbreak_llms-985, jailbreak_llms-1270, jailbreak_llms-1182, jailbreak_llms-695, jailbreak_llms-192, jailbreak_llms-1297, jailbreak_llms-890, jailbreak_llms-941, jailbreak_llms-799, jailbreak_llms-1244, jailbreak_llms-938, jailbreak_llms-1355, jailbreak_llms-1061, jailbreak_llms-1255, jailbreak_llms-1034, jailbreak_llms-1345, jailbreak_llms-318, jailbreak_llms-1295, jailbreak_llms-1071, jailbreak_llms-1236, jailbreak_llms-809, jailbreak_llms-974
jailbreak_llms | benign | jailbreak_llms-14539, jailbreak_llms-13292, jailbreak_llms-5416, jailbreak_llms-3453, jailbreak_llms-1952, jailbreak_llms-9527, jailbreak_llms-9945, jailbreak_llms-5217, jailbreak_llms-2907, jailbreak_llms-12253, jailbreak_llms-14002, jailbreak_llms-12191, jailbreak_llms-13733, jailbreak_llms-7010, jailbreak_llms-4169, jailbreak_llms-3921, jailbreak_llms-13977, jailbreak_llms-7100, jailbreak_llms-4456, jailbreak_llms-2557, jailbreak_llms-9682, jailbreak_llms-4443, jailbreak_llms-2023, jailbreak_llms-15051, jailbreak_llms-13369, jailbreak_llms-12178, jailbreak_llms-3612, jailbreak_llms-3346, jailbreak_llms-11433, jailbreak_llms-7215
jb_class | attack | jb_class-1056, jb_class-793, jb_class-1187, jb_class-1248, jb_class-51, jb_class-1253, jb_class-704, jb_class-574, jb_class-194, jb_class-444, jb_class-1106, jb_class-1583, jb_class-1577, jb_class-251, jb_class-366, jb_class-1368, jb_class-949, jb_class-402, jb_class-9, jb_class-1004, jb_class-618, jb_class-1189, jb_class-578, jb_class-823, jb_class-371, jb_class-655, jb_class-1397, jb_class-677, jb_class-530, jb_class-1524
jb_class | benign | jb_class-1284, jb_class-313, jb_class-666, jb_class-1375, jb_class-697, jb_class-1, jb_class-218, jb_class-801, jb_class-1408, jb_class-806, jb_class-1275, jb_class-318, jb_class-916, jb_class-1468, jb_class-1371, jb_class-499, jb_class-526, jb_class-122, jb_class-255, jb_class-738, jb_class-55, jb_class-716, jb_class-930, jb_class-707, jb_class-953, jb_class-887, jb_class-139, jb_class-177, jb_class-1027, jb_class-118
llmail | attack | llmail-7481, llmail-6785, llmail-12424, llmail-10607, llmail-12428, llmail-9709, llmail-10840, llmail-10897, llmail-8819, llmail-10751, llmail-9322, llmail-11243, llmail-11273, llmail-8635, llmail-9544, llmail-11694, llmail-294, llmail-9272, llmail-8046, llmail-12164, llmail-9405, llmail-12057, llmail-6810, llmail-7781, llmail-7587, llmail-8207, llmail-9167, llmail-8359, llmail-11198, llmail-164
spml | attack | spml-1530, spml-11454, spml-3827, spml-10504, spml-9766, spml-8918, spml-15399, spml-9781, spml-15236, spml-10119, spml-11648, spml-11359, spml-15390, spml-11483, spml-10769, spml-3570, spml-81, spml-15673, spml-2226, spml-7441, spml-15071, spml-8571, spml-13126, spml-9253, spml-9367, spml-711, spml-15747, spml-5418, spml-1440, spml-12243
spml | benign | spml-11680, spml-6800, spml-2944, spml-1682, spml-2814, spml-2656, spml-3532, spml-8022, spml-10964, spml-7045, spml-6691, spml-6572, spml-11704, spml-11070, spml-25, spml-801, spml-15843, spml-9208, spml-11859, spml-14271, spml-13283, spml-13248, spml-4726, spml-3228, spml-12346, spml-2802, spml-13103, spml-1480, spml-3463, spml-14292

Potential label issues requiring human review:

- `jailbreak_llms-14002`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-3346`: Benign row contains an explicit jailbreak cue; review source label.

## SPML

4704 selected rows use `text` = User Prompt as classifier input; `system_prompt` stores the paired System Prompt. `orig_label` 1 maps to attack and 0 to benign.
The source label is context dependent, so prompt-only training can introduce label noise.

## Leakage

Shared split groups across public train/dev: 0. Normalized exact text overlaps: 0.
Embedding cosine results are recorded separately when multilingual-e5-small is available.
The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.
