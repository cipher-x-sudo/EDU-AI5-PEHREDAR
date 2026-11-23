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
jailbreak_llms | benign | none | en | 3852
jb_class | attack | jailbreak | en | 509
jb_class | benign | none | en | 145
llmail | attack | injection | en | 1233
llmail | attack | injection | mixed | 2
spml | attack | injection | en | 1234
spml | benign | none | en | 3372

## Label review

Deterministic random sample: 300 rows, up to 30 per source and label (seed 42).
The sample IDs are listed below for manual review. Automated cue checks are triage, not label adjudication.

Source | Label | Sample IDs
---|---|---
deepset_pi | attack | deepset_pi-516, deepset_pi-250, deepset_pi-126, deepset_pi-542, deepset_pi-379, deepset_pi-368, deepset_pi-361, deepset_pi-270, deepset_pi-541, deepset_pi-224, deepset_pi-526, deepset_pi-81, deepset_pi-493, deepset_pi-191, deepset_pi-504, deepset_pi-441, deepset_pi-136, deepset_pi-131, deepset_pi-213, deepset_pi-354, deepset_pi-364, deepset_pi-474, deepset_pi-507, deepset_pi-87, deepset_pi-497, deepset_pi-334, deepset_pi-519, deepset_pi-543, deepset_pi-44, deepset_pi-359
deepset_pi | benign | deepset_pi-347, deepset_pi-53, deepset_pi-253, deepset_pi-100, deepset_pi-203, deepset_pi-344, deepset_pi-288, deepset_pi-74, deepset_pi-198, deepset_pi-22, deepset_pi-355, deepset_pi-312, deepset_pi-52, deepset_pi-141, deepset_pi-132, deepset_pi-217, deepset_pi-458, deepset_pi-205, deepset_pi-303, deepset_pi-272, deepset_pi-193, deepset_pi-105, deepset_pi-233, deepset_pi-431, deepset_pi-351, deepset_pi-336, deepset_pi-435, deepset_pi-273, deepset_pi-148, deepset_pi-9
gandalf | attack | gandalf-67, gandalf-915, gandalf-894, gandalf-432, gandalf-631, gandalf-276, gandalf-749, gandalf-162, gandalf-14, gandalf-709, gandalf-309, gandalf-811, gandalf-366, gandalf-171, gandalf-888, gandalf-313, gandalf-899, gandalf-192, gandalf-45, gandalf-355, gandalf-517, gandalf-685, gandalf-869, gandalf-435, gandalf-249, gandalf-440, gandalf-426, gandalf-292, gandalf-717, gandalf-345
jailbreak_llms | attack | jailbreak_llms-957, jailbreak_llms-935, jailbreak_llms-898, jailbreak_llms-1077, jailbreak_llms-857, jailbreak_llms-884, jailbreak_llms-1191, jailbreak_llms-774, jailbreak_llms-985, jailbreak_llms-1270, jailbreak_llms-1182, jailbreak_llms-695, jailbreak_llms-192, jailbreak_llms-1297, jailbreak_llms-890, jailbreak_llms-941, jailbreak_llms-799, jailbreak_llms-1244, jailbreak_llms-938, jailbreak_llms-1355, jailbreak_llms-1061, jailbreak_llms-1255, jailbreak_llms-1034, jailbreak_llms-1345, jailbreak_llms-318, jailbreak_llms-1295, jailbreak_llms-1071, jailbreak_llms-1236, jailbreak_llms-809, jailbreak_llms-974
jailbreak_llms | benign | jailbreak_llms-14452, jailbreak_llms-13213, jailbreak_llms-5198, jailbreak_llms-3271, jailbreak_llms-1817, jailbreak_llms-8991, jailbreak_llms-9576, jailbreak_llms-5009, jailbreak_llms-2765, jailbreak_llms-12198, jailbreak_llms-13856, jailbreak_llms-12136, jailbreak_llms-13624, jailbreak_llms-6525, jailbreak_llms-4021, jailbreak_llms-3783, jailbreak_llms-13828, jailbreak_llms-6552, jailbreak_llms-4306, jailbreak_llms-2392, jailbreak_llms-9280, jailbreak_llms-4288, jailbreak_llms-1867, jailbreak_llms-14990, jailbreak_llms-13305, jailbreak_llms-12110, jailbreak_llms-3427, jailbreak_llms-3197, jailbreak_llms-11378, jailbreak_llms-6766
jb_class | attack | jb_class-1056, jb_class-793, jb_class-1187, jb_class-1248, jb_class-51, jb_class-1253, jb_class-704, jb_class-574, jb_class-194, jb_class-444, jb_class-1106, jb_class-1583, jb_class-1577, jb_class-251, jb_class-366, jb_class-1368, jb_class-949, jb_class-402, jb_class-9, jb_class-1004, jb_class-618, jb_class-1189, jb_class-578, jb_class-823, jb_class-371, jb_class-655, jb_class-1397, jb_class-677, jb_class-530, jb_class-1524
jb_class | benign | jb_class-1304, jb_class-276, jb_class-622, jb_class-1401, jb_class-673, jb_class-1, jb_class-193, jb_class-789, jb_class-1430, jb_class-790, jb_class-1292, jb_class-281, jb_class-90, jb_class-1466, jb_class-139, jb_class-440, jb_class-1403, jb_class-946, jb_class-856, jb_class-93, jb_class-17, jb_class-1027, jb_class-1186, jb_class-694, jb_class-1438, jb_class-634, jb_class-573, jb_class-561, jb_class-8, jb_class-1308
llmail | attack | llmail-10607, llmail-12428, llmail-9709, llmail-10840, llmail-10897, llmail-8819, llmail-10751, llmail-9322, llmail-11243, llmail-11273, llmail-8635, llmail-9544, llmail-11694, llmail-294, llmail-9272, llmail-8046, llmail-12164, llmail-9405, llmail-12057, llmail-6810, llmail-7781, llmail-7587, llmail-8207, llmail-9167, llmail-8359, llmail-11198, llmail-164, llmail-12317, llmail-10700, llmail-7029
spml | attack | spml-10504, spml-9748, spml-8883, spml-15381, spml-9749, spml-15177, spml-10231, spml-11543, spml-1131, spml-15361, spml-11461, spml-10773, spml-3550, spml-8053, spml-15547, spml-2213, spml-7372, spml-15043, spml-8425, spml-13152, spml-9205, spml-9374, spml-7095, spml-15652, spml-5389, spml-14467, spml-12189, spml-12244, spml-6019, spml-4204
spml | benign | spml-3026, spml-2847, spml-3730, spml-8371, spml-10994, spml-7411, spml-7014, spml-689, spml-11785, spml-11140, spml-2726, spml-8356, spml-1627, spml-9560, spml-11922, spml-1445, spml-13394, spml-13372, spml-5005, spml-3465, spml-12414, spml-3008, spml-13238, spml-14955, spml-3667, spml-14455, spml-11422, spml-3380, spml-9683, spml-5216

Potential label issues requiring human review:

- `jailbreak_llms-14452`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-5198`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-2765`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-12198`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-3783`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-4306`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-4288`: Benign row contains an explicit jailbreak cue; review source label.
- `jailbreak_llms-3197`: Benign row contains an explicit jailbreak cue; review source label.

## SPML

4606 selected rows use `text` = User Prompt as classifier input; `system_prompt` stores the paired System Prompt. `orig_label` 1 maps to attack and 0 to benign.
The source label is context dependent, so prompt-only training can introduce label noise.

## Leakage

Shared split groups across public train/dev: 0. Normalized exact text overlaps: 0.
Embedding cosine results are recorded separately when multilingual-e5-small is available.
The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.
