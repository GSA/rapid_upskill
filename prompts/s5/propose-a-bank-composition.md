---
id: "P-S5-04"
title: "Propose a bank composition"
stage: "S5"
sub_stage: "S5.5"
purpose: "Propose how many items a bank needs per domain and per difficulty, from a blueprint's own weights and the reference implementation's difficulty split."
placeholders: ["BLUEPRINT_EXCERPT", "BANK_SIZE"]
capabilities: ["llm", "file-read"]
inputs: "A blueprint excerpt (each domain's id, name and weight), and a target bank size (a count of test items)."
outputs: "A per-domain, per-difficulty item-count table, with each domain's own target checked against its weight."
---
````text
You are proposing a bank composition: how many test items a bank
needs from each domain, and at each difficulty, before any of those
items is drafted.

Blueprint excerpt (domain id, name, weight):
{{BLUEPRINT_EXCERPT}}

Target bank size: {{BANK_SIZE}} test items.

Do this:
1. For each domain, compute its target item count as its weight,
   times the bank size, divided by 100. Round to a whole number.
2. Split each domain's own target across three difficulties, easy,
   medium and hard, so the bank-wide total lands close to 30 percent
   easy, 50 percent medium and 20 percent hard. This is the reference
   implementation's own difficulty split, that project's choice, not a
   universal rule; state the split you actually used if a program
   asks for a different one.
3. Report the result as a table: one row per domain, with its weight,
   its target item count, and its easy, medium and hard counts.
4. Flag any domain whose target does not land on, or close to, a
   whole number, so a person can decide whether to adjust the bank
   size or accept the nearest whole count.

Report the table as JSON: an object with one key per domain id, each
holding "target", "easy", "medium" and "hard".
````
Written for this guide and not run against any model in this build; treat it
as a starting point and adapt it.

Filled example, using the running example's values (synthetic): `BLUEPRINT_EXCERPT`
lists four domains, "Snapshots and history" (weight 25), "Branching and
merging" (weight 30), "Working with remotes" (weight 25) and "Recovering and
collaborating safely" (weight 20), and `BANK_SIZE` is 20. A plausible reply
proposes targets of 5, 6, 5 and 4, and splits each into easy, medium and hard
counts that sum to a bank-wide 6, 10 and 4 (30, 50 and 20 percent).

Check the output by dropping the "target" column, converting the remaining
easy, medium and hard counts into a `composition.json`-shaped entry per
domain, and running the bank composition check script on the result against
the blueprint file, confirming each domain's own real count is within 1 of
its target and the bank-wide split is within 10 percentage points of
30/50/20.
