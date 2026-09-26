---
title: "S2.2 Condensation"
parent: "Stage 2 Content development"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-25"
stage: "S2"
sub_stage: "S2.2"
prompts: ["P-S2-02"]
scripts: ["X-S2-02"]
---

# S2.2 Condensation

## Outcome

At the end of this sub-stage the drafted chapter has been through
**[condensation](../glossary.md#condensation)**: shortened with named
techniques, its meaning intact, and checked against a word-count target
and two readability deltas.

## Where it fits

This sub-stage takes in the approved chapter draft from
[S2.1 Structural drafting](structural-drafting.md). It hands on the
condensed chapter to
[S2.3 and S2.4 Readability polish and six-pass revision](readability-and-revision.md).

## Why this way

A chapter drafted for completeness usually reads longer than a beginner
needs. Cutting loosely, sentence by sentence, leaves a person nothing to
check afterward beyond whether the result feels shorter. Naming the
techniques instead keeps a record of what was done, so a person can
check the work and reverse a cut that went too far. This page uses the
same [basis labels](../stage-1/index.md#basis-labels) Stage 1's index
defines. Most of the technique list and the condensation target are
documented in [the project notes](../glossary.md#reference-implementation).
Running the check and comparing the result to the original is this
guide's own suggestion.

Condensation also waits until the chapter's structure is stable. A
structural edit made afterward, such as merging two sections or adding
one, would throw away shortening work already done. Sentences that get
rewritten or moved lose that work, so this sub-stage starts only once
[S2.1](structural-drafting.md)'s draft is approved.

## Steps

| Step | Who | Basis |
|---|---|---|
| Read the whole chapter and note what is essential and what is supplementary | Agent | documented |
| Apply the five named techniques to each passage that needs shortening | Agent | documented |
| Confirm the meaning survived the cut | Person | documented |
| Reassemble the chapter, run the condensation check, and compare the result to the original | Script | suggested |
| Fix anything that reads worse than the original, then run the check again | Agent and person | documented |
| Approve the condensed chapter | Person | documented |

The five named techniques, one sentence each:

1. Minimalist documentation: write action first, cut prose the reader
   does not need in order to act, and treat an error message as part
   of the lesson.
2. A five-rule concise-writing framework: cut filler words, redundant
   pairs and anything the reader can infer; simplify wording; state
   things positively.
3. Information Mapping: sort the content into small, labelled blocks by
   kind, and keep only what the reader needs right now.
4. Worked-example fading: replace most practice problems with fully
   worked examples, then thin the guidance across a few more until the
   learner works alone.
5. A four-stage condensation process: read for the overall theme, split
   the passage into small labelled units, rewrite each unit concisely,
   then reassemble into one text.

These five are documented in the project notes. The project notes also
give a per-technique estimate of how much each one tends to shorten a
passage. Those figures are the project's own working notes, not a
general rule, so this page does not repeat them.

### A small worked example

One sentence from the sample passage below shows the five-rule
framework at work. The draft reads: "It is not only a record of the
lines that changed since the previous commit; it is a snapshot of the
state of every file that Git is tracking." The condensed version cuts
the redundant "it is ... it is" construction and drops "only". It
states the point once: "It records the state of every file Git
tracks, not just the lines that changed since the previous commit."
The meaning is the same. The second sentence says it in fewer words
and in the active voice, and a person checking the cut can trace
exactly which rule removed which word.

## Parameters

Condensation target (the reference implementation's parameters): the
project notes mostly agree the target is roughly a fifth shorter than
the draft, keeping about 80% of the original length. One project
document states the opposite figure, "80% shorter, keeping 20%";
treat that document as an outlier if you meet it elsewhere, not as
this guide's own rule. Do not average the two figures into a
compromise number.

Checking whether a condensed passage still reads as well as the draft
it came from needs two readability scales. Both are defined here, at
their first use in this guide, before either one is used in a number
below:

- **Grade Level** is roughly the school-grade reading level a text
  needs; a lower number is easier to read.
- **Reading Ease** is a score from 0 to 100; a higher number is easier
  to read.

Readability delta bands (the reference implementation's parameters),
checked between the condensed passage and the draft it came from, not
against a fixed target:

| Delta | Band |
|---|---|
| Word count | 15% to 25% shorter |
| Reading Ease | falls by no more than 5 points |
| Grade Level | rises by at most 1 |

These are deltas, not fixed targets: this sub-stage only checks how far
the condensed passage moved from the draft it came from.
[S2.3 and S2.4](readability-and-revision.md) checks the finished
chapter's Grade Level and Reading Ease against an absolute band, once
the six-pass revision is done. That later check reuses the same two
scale meanings defined above and does not redefine them.

## Artifacts and formats

This sub-stage produces one file: the condensed chapter, in the same
structure as the draft (front matter, then the fixed skeleton's
headings).

## Prompts

[P-S2-02 Condense a passage](../prompts/s2/p-s2-02.md) applies the named
techniques to one passage at a time and returns a condensed version. A
person names which techniques to apply before the call, since not every
technique fits every passage. The prompt lists all five again inside
itself, so a model given only the names still knows what each one
means. The passage text is fenced as data before it is sent, the same
as every other prompt in this guide that reads earlier sub-stage
output. The prompt is written for this guide and not run against any
model in this build.

## Scripts

[X-S2-02 Condensation check](../scripts/s2/x-s2-02.md) checks a
condensed passage's word-count ratio against the original, and how far
each of the two readability scores moved between the two. It does not
fix anything and does not judge meaning; it only measures the numbers
above. Run it from the repository root:

```bash
python3 -B scripts/s2/condensation_check.py \
    scripts/sample_data/git_basics_stage2/condensation/original.md \
    scripts/sample_data/git_basics_stage2/condensation/condensed.md
```

On the sample pair, a short passage about what a Git commit holds, it
prints three checks and a summary line, all pass:

```text
word-ratio 0.80, band 0.75-0.85: pass
reading-ease +3.88, limit -5: pass
grade-level -1.95, limit +1: pass
checks=3 hard=0
```

The condensed passage is 80% of the original's word count, a fifth
shorter, and both readability scores moved toward being easier to read,
not away from it. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 2 index
for what the exit code means; here it is 0.

Break it on purpose: copy the condensed passage, then keep only its
first paragraph. This is what happens if an editor cuts the whole
second half instead of condensing it passage by passage with the named
techniques:

```bash
head -n 9 scripts/sample_data/git_basics_stage2/condensation/condensed.md > condensed.broken.md
python3 -B scripts/s2/condensation_check.py \
    scripts/sample_data/git_basics_stage2/condensation/original.md condensed.broken.md
rm condensed.broken.md
```

```text
word-ratio 0.31, band 0.75-0.85: hard
reading-ease +6.87, limit -5: pass
grade-level -3.06, limit +1: pass
checks=3 hard=1
```

The `word-ratio` line is now `hard`, so the exit code is 1. The copy is
far shorter than the band allows, because it lost the whole second
paragraph rather than being condensed with the named techniques. Both
readability scores still look fine on their own, and that is the trap a
word-count check alone cannot see: a much shorter passage often reads
easier by these two scores, even when it dropped content a reader
needed. The check and a person's own read of the result are testing
different things. `--word-low` and `--word-high` widen or narrow the
word-count band; `--re-drop` and `--grade-rise` do the same for the two
readability limits.

## Definition of done

- The condensed chapter keeps the same fixed-skeleton headings as the
  draft.
- Every cut traces to one of the five named techniques, not to
  guesswork.
- A person has confirmed the chapter's meaning survived the cut.
- The condensation check reports no hard result at the default band.
- A person has approved the condensed chapter.

## Common failures

- A cut that removes meaning, not just words: a worked example
  stripped down until the steps no longer make sense, or a warning cut
  along with the sentence that carried it.
- Condensing before the draft's structure is stable, so a later
  structural edit throws away work this sub-stage already did, and the
  chapter has to be condensed again.
- A technique applied to the wrong kind of passage: worked-example
  fading used on a passage with no worked example to fade, or
  Information Mapping used on one short paragraph that did not need
  sorting into blocks.
- A chapter that passes the condensation check while a person can tell
  it lost something the check cannot see. The break-on-purpose run
  above shows this: the numbers alone are not a stand-in for reading
  the result.

## Adapting to your platform

- `llm`: applies the named techniques to a passage, one at a time or
  several at once, from the prompt above or your own equivalent.
- `shell`: runs the condensation check. Without it, count words by
  hand with a word processor's own count, and read the passage aloud
  for the same two impressions the two scores approximate: how long
  the sentences feel, and how familiar the words are.
- `human-approval`: a person confirms the meaning survived, reads any
  check result, and approves the condensed chapter before the next
  sub-stage begins. Without a platform that pauses for this step, hold
  the approval as a written note next to the chapter file.

## Where humans decide

- Which passages need condensing, and which technique fits each one.
- Whether the chapter's meaning survived the cut.
- Approval of the condensed chapter before readability polish begins.

Next: [S2.3 and S2.4 Readability polish and six-pass revision](readability-and-revision.md).
