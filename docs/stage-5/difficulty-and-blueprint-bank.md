---
title: "S5.5 and S5.7 Difficulty distribution and blueprint bank"
parent: "Stage 5 Assessment development"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
sub_stage: "S5.5"
prompts: ["P-S5-04"]
scripts: ["X-S5-04"]
---

# S5.5 and S5.7 Difficulty distribution and blueprint bank

S5.5 and S5.7 are not adjacent sub-stage numbers. S5.6, quiz and exam
assembly, sits between them in the project notes' own numbering, but
its own content is different enough, and rich enough, that this guide
gives it two pages of its own instead: [S5.6 Quiz and exam
assembly](quiz-and-exam-assembly.md) and [the delivery-formats
page](delivery-formats.md). This page covers S5.5 and S5.7 together
because they are two tightly linked halves of one idea: fix the bank's
own difficulty mix first, then weight its domain coverage against the
blueprint.

## Outcome

At the end of these two sub-stages, a whole [item
bank](../glossary.md#item-bank)'s own difficulty mix is fixed up
front and mapped to Bloom's levels, and the bank's own domain coverage
mirrors the [blueprint](../glossary.md#blueprint)'s own weights: the
same arithmetic [S1.3 Draft the blueprint](../stage-1/blueprint.md)
already defines for its own bank of test items, applied here at Stage
5's own larger scale.

## Where it fits

These two sub-stages take in finished [stems](../glossary.md#stem)
from [S5.3 and S5.4 Distractors and format
rules](distractors-and-format-rules.md), and the blueprint
[S1.3](../stage-1/blueprint.md) approved. They hand a checked bank on
to [S5.6 Quiz and exam assembly](quiz-and-exam-assembly.md), where the
bank's own stems are assembled into a deliverable quiz.

## Why this way

Fixing the difficulty mix and the domain weighting before assembly,
rather than checking only after a bank is finished, means a gap in one
domain or one difficulty tier is caught while there is still time to
write the stems that would close it.

## Steps

| Step | Who | Basis |
|---|---|---|
| Fix the bank's own difficulty split at 30% easy, 50% medium, 20% hard, mapped to Bloom's levels | Agent | documented |
| Weight each domain's own target item count from the blueprint | Agent | documented |
| Run the bank composition check | Script | suggested |
| Approve the bank's own composition before assembly | Person | suggested |

The difficulty split and its Bloom crosswalk are documented: [the
project notes](../glossary.md#reference-implementation) fix them
exactly, and this guide has already stated the split publicly
elsewhere (see below). The blueprint arithmetic is also documented,
not this guide's own invention: the project notes describe matching a
bank's own item counts to a blueprint's weights the same way
[S1.3](../stage-1/blueprint.md)'s own Parameters table already defines
it, under its "Bank-size arithmetic" row, for the bank of test items
S1.3's own blueprint already sizes. Stage 1's blueprint sizes a bank
of stems, not concepts, at a small, toy scale; Stage 5 applies the
identical mechanism at this stage's own much larger, real scale, not a
new mechanism borrowed from a concept-count check. The bank
composition check itself, and the judgment call of approving a
finished composition, have no described precedent, so both are marked
suggested.

## The difficulty split and the Bloom crosswalk

[Pipeline overview](../pipeline-overview.md) already states: "The
30/50/20 split is one of the reference implementation's parameters,
that project's choice and not a universal rule." This page reuses that
exact split and its own crosswalk onto Bloom's six-level scale
(documented, the reference implementation's own mapping of that
already-public split onto Bloom's levels): Remember and Understand map
to easy (30 percent); Apply and Analyze map to medium (50 percent);
Evaluate and Create map to hard (20 percent).

## A separate, industry-generic range

A separate, industry-generic exam-development guide gives a wider
range for the same three-tier idea, not tied to any one certification:
roughly 20 to 30 percent foundational (Remember and Understand), 50 to
60 percent intermediate (Apply and Analyze), and 15 to 20 percent
advanced (Evaluate and Create). Keep the two figures distinct: the
industry-generic range is a general reference point, useful when no
project-specific split exists yet; the reference implementation's own
fixed 30/50/20 above is one project's chosen instance inside that kind
of range, not the same figure restated twice.

## Blueprint arithmetic applied to a bank of test items

[S1.3](../stage-1/blueprint.md)'s own Parameters table defines a
"Bank-size arithmetic" row (suggested, at that sub-stage's own small
scale): "A domain's weight, times the bank size, divided by 100,
should be a whole number." [The running example](../running-example.md)'s
own blueprint already applies this: four domains weighted 25, 30, 25
and 20, against a bank of 20 stems, gives target counts of 5, 6, 5 and
4. A real bank at Stage 5's own scale can span many more domains,
unevenly weighted, but the arithmetic does not change: multiply a
domain's weight by the bank size, divide by 100, and a domain's own
real item count should land close to that number. This is not a
mechanism first used for counting concepts and then carried over to
items; the blueprint's own bank-size field already counts stems, the
finished test items, at both scales, so Stage 5 reuses the same
mechanism, not a new one, at its own larger scale.

## Worked illustration

[The running example](../running-example.md)'s own real,
already-published blueprint
(`scripts/sample_data/git_basics/blueprint.json`, read-only, not
copied here) has four domains, weighted 25, 30, 25 and 20. Applied to
a bank of 20 items, the arithmetic above gives:

| Domain | Weight | Target (weight \* 20 / 100) |
|---|---|---|
| D1 Snapshots and history | 25 | 5.0 |
| D2 Branching and merging | 30 | 6.0 |
| D3 Working with remotes | 25 | 5.0 |
| D4 Recovering and collaborating safely | 20 | 4.0 |

A small, invented bank composition
(`bank/composition.json`, this guide's own suggested illustration)
splits each domain's own target across the three difficulties, so the
bank-wide split also lands on 30/50/20:

| Domain | Easy | Medium | Hard | Total |
|---|---|---|---|---|
| D1 | 2 | 2 | 1 | 5 |
| D2 | 2 | 3 | 1 | 6 |
| D3 | 1 | 3 | 1 | 5 |
| D4 | 1 | 2 | 1 | 4 |
| Bank-wide | 6 (30%) | 10 (50%) | 4 (20%) | 20 |

Every domain's own real count matches its target exactly, and the
bank-wide difficulty split matches 30/50/20 exactly, so
`bank_composition_check.py` reports no warnings on this file, shown
below.

## Artifacts and formats

This sub-stage's own artifact is a bank-composition record: item
counts by domain and by difficulty. Its JSON shape
(`bank/composition.json`) is a single object with one key, `domains`,
mapping each domain id to an object holding an `easy`, a `medium` and
a `hard` count (this guide's own suggested shape; the project notes
give no machine-checkable format for this record).

## Prompts

[P-S5-04 Propose a bank composition](../prompts/s5/p-s5-04.md)
proposes a per-domain, per-difficulty item-count table from a
blueprint excerpt and a target bank size, using the arithmetic above.
It is written for this guide and has not been run against any model
in this build.

## Scripts

[X-S5-04 Bank composition check](../scripts/s5/x-s5-04.md) reads a
bank composition file and the blueprint it is meant to match. For each
blueprint domain, it checks whether the composition's own real item
count is within 1 of `weight * bank_size / 100`; it also checks
whether the bank-wide easy, medium and hard split is within 10
percentage points of 30/50/20. A composition gap is a person's
judgment call, not a hard failure, the same limit [Stage 2's
readability report](../stage-2/readability-and-revision.md) already
sets for its own two scores: this script never exits 1 on its own, and
exits 0 whenever it can read both files.

Run it from the repository root, with the composition file and the
blueprint file as its two arguments:

```bash
python3 -B scripts/s5/bank_composition_check.py \
    scripts/sample_data/git_basics_stage5/bank/composition.json \
    scripts/sample_data/git_basics/blueprint.json
```

```text
domain by target and actual item count (bank_size=20):
D1  weight=25 target=5.0 actual=5
D2  weight=30 target=6.0 actual=6
D3  weight=25 target=5.0 actual=5
D4  weight=20 target=4.0 actual=4
difficulty split (bank_size=20): easy=6 (30.0%) medium=10 (50.0%) hard=4 (20.0%) target=30/50/20
domains=4 warnings=0
```

A clean run only shows that this one small, invented composition
happens to match its blueprint and its difficulty split exactly; it is
not proof that every stem behind those counts is itself sound, only
that the counts add up.

Break it on purpose: copy the file, then change domain D2's own `hard`
count from 1 to 5, so it drifts far past its own target and the
bank-wide hard share balloons past its own 10-point tolerance, and run
the check again on the copy:

```text
warning domain-count: domain D2 weight 30 gives bank_size * weight / 100 = 7.2 target, actual count is 10 (+2.8 away)
warning difficulty-split: bank-wide split is easy=25.0% medium=41.7% hard=33.3%, more than 10 points off the reference implementation's 30/50/20
domain by target and actual item count (bank_size=24):
D1  weight=25 target=6.0 actual=5
D2  weight=30 target=7.2 actual=10
D3  weight=25 target=6.0 actual=5
D4  weight=20 target=4.8 actual=4
difficulty split (bank_size=24): easy=6 (25.0%) medium=10 (41.7%) hard=8 (33.3%) target=30/50/20
domains=4 warnings=2
```

The one-domain change trips two warnings at once, the same way a
single weight edit trips two checks on [S1.3](../stage-1/blueprint.md)'s
own blueprint check: adding four items to one domain both moves that
domain away from its own target and pulls the whole bank's hard share
away from 30/50/20, since the added items were all hard. See [Reading
exit codes](../stage-1/index.md#reading-exit-codes) on the Stage 1
index for what the exit code means; here it stays 0, since a
composition gap is always a warning on this script, never a failure.

## Definition of done

- Every domain's own real item count is within 1 of its blueprint
  target.
- The bank-wide difficulty split is within 10 percentage points of
  30/50/20.
- The bank composition check has run, and a person has looked at any
  warning it printed.
- A person has approved the bank's own composition before assembly.

## Common failures

- A bank whose difficulty mix drifts from 30/50/20 as stems are added
  piecemeal, one chapter at a time, with no one checking the running
  total.
- A domain's own item count that does not divide evenly against its
  blueprint weight, the same arithmetic warning
  [S1.3](../stage-1/blueprint.md) already gives for its own bank of
  test items.
- Conflating the generic 20-30/50-60/15-20 range above with the
  reference implementation's own fixed 30/50/20, as though they were
  the same figure restated twice.

## Adapting to your platform

- `llm`: proposes the per-domain, per-difficulty table from a
  blueprint excerpt and a target bank size, using P-S5-04.
- `file-read`: reads the blueprint file the proposal, and the check,
  are both measured against.
- `shell`: runs the bank composition check; without it, compute each
  domain's target by hand and compare it to the real count.
- `human-approval`: covers the approval step below; a platform with no
  built-in approval step still needs a person to read and record it
  somewhere, such as a shared document.

## Where humans decide

- Approving a finished bank's own composition before assembly.
- Whether a domain's own item count that misses its target by more
  than 1 needs new stems, or is close enough to accept as is.
- Whether a bank-wide difficulty split more than 10 points off
  30/50/20 needs rebalancing before assembly, or reflects a deliberate
  choice for this particular program.

Next: [S5.6 Quiz and exam assembly](quiz-and-exam-assembly.md).
