---
title: "S1.5a Concept extraction"
parent: "Stage 1 Knowledge acquisition"
nav_order: 6
status: "draft"
last_reviewed: "2026-09-22"
stage: "S1"
sub_stage: "S1.5a"
prompts: ["P-S1-06"]
scripts: ["X-S1-06"]
---

# S1.5a Concept extraction

## Outcome

At the end of this sub-stage, every admitted source has a concept list: the
terms it uses, a short definition for each, and how the terms relate to
one another. Each list passes the concept lint script before a person
reviews a sample.

## Where it fits

This sub-stage takes in the approved corpus from
[S1.4c](injection-screening.md). It hands on one concept list per source to
[S1.5b](distillate-and-quote-bank.md), which reads the same source again to
write a fuller distillate. The concept lists this sub-stage produces come
before the knowledge items of S1.6, which is planned and not published
yet.

## Why this way

Naming and defining a source's concepts before writing anything longer
about it keeps later passes anchored to what the source actually says,
rather than to a paraphrase of a paraphrase. This page uses the
[basis labels](index.md#basis-labels) defined on the Stage 1 index: the
four extraction passes and the review step are documented in
[the project notes](../glossary.md#reference-implementation); the lint
script and its exact thresholds are this guide's own suggestion, because
the project notes describe the checks without giving one script for them.

## Steps

| Step | Who | Basis |
|---|---|---|
| Build a brief for the source | Script or person | documented |
| Count the source's words and choose a reading plan: read the whole source when it is under 6,000 words, otherwise read it by heading | Agent | documented |
| Identify the source's concepts (pass 1) | Agent | documented |
| Define each concept in one sentence (pass 2) | Agent | documented |
| Add typed relations from trigger phrases, each with a quote from the source (pass 3) | Agent | documented |
| Link prerequisite and downstream-use relations (pass 4) | Agent | documented |
| Remove near-duplicate concepts after every pass | Agent | documented |
| Run the concept lint | Script | suggested |
| Review a sample of the concept lists | Person | documented |

A **brief** is a short packet built for the agent before extraction
starts, so it does not have to guess what a bare source id means. It
holds the source's id and file path, a word count, the objective or seed
claims the source is meant to support, a short reading plan, and a note
if the source's own page numbers are missing or unreliable.

Passes 1 to 4 run as separate calls over the same source, each one
building on the prior pass's output; [P-S1-06](#prompts) below carries
one pass per call. Removing near-duplicate concepts after every pass
keeps the list from growing a second entry for the same idea under a
slightly different name. The project notes remove a near-duplicate at
0.85 similarity measured on text embeddings (numeric representations of
meaning); this guide's script uses word overlap as a stand-in, which
finds only names or definitions that are near-identical in wording, so
comparing both the name and the definition catches more than comparing
names alone.

The concept lint checks that every relation carries a quote; it does not
check that the quote is true, or that it supports the relation it is
attached to. [S1.5b](distillate-and-quote-bank.md#scripts) applies the
same limit to a fuller quote bank.

## Parameters

| Parameter | Value used in this guide | Basis |
|---|---|---|
| Name length | 2 to 5 words | documented; the project notes give 1 to 5, 2 to 5 and 2 to 8 words in different places, and this guide's script defaults to 2 to 5 |
| Definition length | 15 to 50 words | documented; most of the project notes agree on this range, though one asks for one sentence and another for one or two |
| Relations per concept | about 1.5 to 2.5 on average (a warning, not an error) | documented |
| Relation types | five: `depends-on`, `part-of`, `implemented-by`, `contrasts-with`, `example-of` | suggested; this guide's own list |
| Near-duplicate threshold | 0.85 word-set overlap | inferred from the project notes' 0.85 embedding-similarity threshold, applied here to a word-overlap stand-in |
| Reading plan cutoff | read the whole source under 6,000 words, otherwise read it by heading | documented |

Joining each source's concept list into the fuller distillate of
[S1.5b](distillate-and-quote-bank.md) is inferred: the project notes
describe both activities but not how one feeds the other, so this guide
treats the concept list as the agent's own working notes for writing
the distillate that follows.

## Artifacts and formats

Each source gets one concept list, a JSON file: a list of objects, each
with a `name`, a `definition`, an optional `type`, and a `relations` list.
Each relation has a `type` (one of the five above), a `target` (another
concept's `name` in the same file) and a `quote`. The project notes hold
this record as Markdown; this guide uses JSON so a script can read it
directly.

## Prompts

[Concept extraction](../prompts/s1/p-s1-06.md) (P-S1-06) runs one pass at
a time: `PASS_NUMBER` says which of the four passes to run, and
`PRIOR_OUTPUT` carries the previous pass's JSON forward, written as the
word `none` on pass 1. It is written for this guide and has not been run
against any model in this build; treat it as a starting point and adapt
it.

## Scripts

[Concept lint](../scripts/s1/x-s1-06.md) (X-S1-06) checks a concept
file's name and definition lengths, relation types, relation targets and
quotes, and warns on near-duplicate concepts and an unusual average
relation count. A passing run means every relation carries a quote; it
never checks whether that quote is true.

Run it from the repository root on the sample concept list:

```bash
python3 -B scripts/s1/concept_lint.py \
    scripts/sample_data/git_basics_stage1/extraction/SRC-002.concepts.json
```

```text
concepts=6 relations=11 errors=0 warnings=0
```

Six concepts, no errors and no warnings: every name and definition falls
inside its length range, every relation names one of the five types and
an existing concept as its target, and the average of 11 relations over
6 concepts, about 1.83, falls inside the warning band. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 1 index
for what the exit code means.

Break it on purpose: copy the file, then change the one relation with
type `part-of` to an invented type, and run the lint again on the copy:

```text
error bad-relation-type: concept 'Detached HEAD' relation #1 has type 'contains', not in depends-on, part-of, implemented-by, contrasts-with, example-of
concepts=6 relations=11 errors=1 warnings=0
```

The relation count and the average are unchanged; only the one renamed
type is flagged, by name, against the five this guide allows.
`--name-words`, `--def-words` and `--similar` replace the three default
ranges with your own. A clean run is not proof that a concept's
definition is accurate, only that the file is well formed and every
relation carries a quote.

## Definition of done

- Every admitted source has a concept list.
- Every concept's name and definition fall inside the length ranges.
- Every relation names one of the five types, an existing concept as its
  target, and carries a quote from the source.
- No concept name is used twice in the same file.
- The concept lint reports no errors.
- A person has reviewed a sample of the concept lists.

## Common failures

- An overlong definition that reads like a small paragraph instead of
  one sentence; the length check catches this, but a person still has to
  judge whether a short definition is also a clear one.
- A relation added without a quote, or with a quote copied from the
  wrong sentence; the lint only checks that a quote is present, not that
  it is the right one.
- A name that is a full sentence instead of a term, which the length
  check flags but does not explain; look at the source's own wording for
  a shorter name.
- An invented relation between two concepts that never appear near each
  other in the source; a quote drawn from unrelated sentences is a sign
  this happened.

## Adapting to your platform

This sub-stage needs `llm` for the four passes, `file-read` to load the
source and the brief, and `structured-output` for the concept JSON.
`shell` runs the lint; without it, check name and definition lengths and
relation targets by hand, using the same ranges. `human-approval` covers
the sample review. Without a model that can run four passes in sequence,
run one pass per chat turn and paste each output back in as the next
turn's prior output.

## Where humans decide

- Which sources continue to [S1.5b](distillate-and-quote-bank.md) after
  the sample review.
- What the sample review looks for, and how large a sample is enough.

Next: [S1.5b Distillate and quote bank](distillate-and-quote-bank.md).
