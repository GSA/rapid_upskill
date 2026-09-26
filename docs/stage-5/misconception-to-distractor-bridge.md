---
title: "S5.1 Misconception-to-distractor bridge"
parent: "Stage 5 Assessment development"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
sub_stage: "S5.1"
prompts: ["P-S5-01"]
scripts: ["X-S5-01"]
---

# S5.1 Misconception-to-distractor bridge

## Outcome

At the end of this sub-stage, a chapter's own content has become a
small set of assessment concept items, this guide's own name for this
sub-stage's artifact, defined in full below. Each one holds at least
two documented [misconceptions](../glossary.md#misconception), ready
to feed a stem plan.

## Where it fits

This sub-stage takes in a finished, reviewed chapter from
[Stage 3](../stage-3/index.md). It hands its own items on to
[S5.2 Stem planning](stem-planning.md).

## Why this way

A [stem](../glossary.md#stem)'s [distractors](../glossary.md#distractor)
are only as good as the misconceptions behind them. Naming at least two
per concept, before any stem exists, means a later stem plan has real
material to draw from rather than inventing a plausible-sounding wrong
answer on the spot. This page uses the
[basis labels](../stage-1/index.md#basis-labels) Stage 1's index
defines; it does not redefine them.

## Steps

| Step | Who | Basis |
|---|---|---|
| Extract concepts and at least two misconceptions per concept, from the chapter's own text, across eight categories (definitions, processes, best practices, pitfalls, specifications, code and its implications, real-world applications, and comparisons) | Agent | documented |
| Check the extracted item against an eight-point checklist (atomic, one concept; a clear, measurable description; a cognitive level that matches the concept's own complexity; at least two misconceptions; specific, checkable references; accurate dependencies; a correctly-shaped id; no duplicate of an existing item) | Agent | documented |
| Approve the chapter's own extracted items before stem planning begins | Person | suggested |

[The project notes](../glossary.md#reference-implementation) describe
the eight extraction categories and the eight-point checklist in a
template written for this exact step. Approving a chapter's own
extracted items before stem planning begins is not itself named there
as a gate. It is this guide's own suggested checkpoint, added because
every later sub-stage in this stage builds on what these items name.

### The eight extraction categories

A concept worth an assessment concept item usually falls under one of
eight categories. It may be a definition or a piece of terminology, a
process or a workflow, a best practice or a pattern, a common pitfall
or an anti-pattern, a technical specification, a code example and what
it implies, a real-world application, or a comparison between two
things that are easy to confuse. Rereading a chapter with this list in
hand
finds more testable concepts than reading straight through once for
whatever stands out.

### The eight-point checklist

An extracted item is checked against eight points before it counts as
finished:

- It names one concept, atomically, not a paragraph's worth of several
  claims at once.
- Its description is clear and measurable, not a vague restatement of
  the concept's own name.
- Its cognitive level matches how complex the concept actually is.
- It names at least two misconceptions.
- Every reference is specific enough that a person could actually
  check it.
- Every dependency it lists is accurate.
- Its id is shaped correctly.
- It does not duplicate a concept an existing item already covers.

[X-S5-01](../scripts/s5/x-s5-01.md) checks the fourth,
the seventh and the eighth points in full; the rest stay a person's own
read, stated plainly again under Common failures below.

## This guide's own honest gap

The project notes' own extraction guidance sends the writer back to the
chapter's own text to find misconceptions: a pitfalls section, an "X
versus Y" comparison, a "what not to do" note, a stated limitation. It
never once says to consult [Stage 1](../stage-1/index.md)'s own
recorded misconceptions or [Stage 4](../stage-4/index.md)'s own
[misconception catalog](../glossary.md#misconception-catalog). This
sub-stage is its own fresh pass over the chapter, not a pull-forward of
misconceptions already recorded elsewhere in this guide's own pipeline.
It mirrors, and is more pronounced than, the gap
[S4.5](../stage-4/misconception-catalog-and-error-diagnosis.md) already
admits between a Stage 1 knowledge item and its own catalog entries. A
team building this for real could choose to consult those earlier
records first, to save an extraction pass a chapter has already been
through once. That is this guide's own suggested time-saver, not
something the project notes themselves describe.

## The naming choice: an assessment concept item, not a knowledge item

This is where the artifact is first defined, so the choice is restated
in full here. This guide calls its own version of this artifact an
**assessment concept item**, never a "knowledge item". Its own
field list (a section, a cognitive level, a Bloom level, key concepts,
at least two misconceptions, references, dependencies) differs enough
from [Stage 1](../stage-1/knowledge-items.md)'s own published knowledge
item schema that reusing the name would blend two different things, the
same collision this guide already avoided once for "candidate". This
guide's own assessment-concept-item schema is a deliberate
simplification of the fuller field list the project notes actually use,
the same kind of honest simplification
[Stage 1](../stage-1/knowledge-items.md) already states for its own
knowledge item schema.

An assessment concept item carries both a cognitive level and a Bloom
level rather than one or the other.
[S1.3 Draft the blueprint](../stage-1/blueprint.md#parameters) already
told readers that a cognitive level and a Bloom level are near-synonyms
in the project notes. It also told readers that the project notes
describe as many as three disagreeing scales for the same idea. This item's own cognitive
level (knowledge, application or analysis) and its Bloom level (the
standard six-level scale, remember through create) are two more entries
in that same, already-acknowledged disagreement, not a new one. A
writer filling in the sample data below sets both fields from the
concept's own real complexity, rather than leaving one blank.

## Schema

This guide's own assessment-concept-item schema: `id` (shaped
`ACI-<chapter>-<NNN>`), `chapter`, `section`, `description` (one
sentence), `cognitive_level` (`knowledge`, `application` or
`analysis`), `bloom_level` (`remember`, `understand`, `apply`,
`analyze`, `evaluate` or `create`), `key_concepts` (a short list of
terms), `misconceptions` (a list of at least two entries, each with a
`text` and a `source_id`), `references` (a list of citation strings
back to the chapter and its sources) and `dependencies` (a list of
other assessment concept item ids, or an empty list).

## Worked illustration

[The running example](../running-example.md)'s own Chapter 1 supplies
`ACI-1-001`: the concept that a commit records a snapshot of the whole
repository, not just the changed lines. `SRC-001` states this directly,
and separately names two things newcomers commonly get wrong about it:
"Many newcomers believe that a commit stores only the lines you
changed", and "A common mistake is to run `git add notes.txt`, keep
typing in that file, and then assume the commit contains the later
edits." Both are quoted from `SRC-001`'s own text, not paraphrased away
from it, and both become `ACI-1-001`'s two misconceptions.

Chapter 2 supplies two more items, `ACI-2-001` and `ACI-2-002`, because
[S5.2](stem-planning.md)'s own medium-difficulty stem later combines
them in one merge-conflict scenario. `ACI-2-001` is the concept that
merging integrates one branch's own work into another, with the
already-published `SRC-002` sentence "A common mistake is to assume
that merging must create a commit" as one of its two misconceptions.
`ACI-2-002` is a second, related Chapter 2 concept, this guide's own
choice among the chapter's own objectives and sources: resolving a
merge conflict, drawn from `SRC-003`'s "When a merge stops" section and
its own objective, D2.3. This guide picked D2.3 over Chapter 2's two
other objectives: D2.1, the branch-and-HEAD concept, and D2.2, the
fast-forward-versus-merge-commit distinction `ACI-2-001` already
covers. A conflict is the concept a merge-combining scenario
most naturally needs next, and `SRC-003` states its own real
"common mistake" sentence to build a misconception from, the same kind
of grounding `ACI-1-001` and `ACI-2-001` already use.

## Artifacts and formats

This sub-stage produces one artifact: a chapter's own list of
assessment concept items, in the schema above. The sample file for the
running example, `concept_items/items.json`, holds `ACI-1-001` from
Chapter 1 and `ACI-2-001` and `ACI-2-002` from Chapter 2, described in
the worked illustration above.

## Prompts

[P-S5-01 Extract an assessment concept item](../prompts/s5/p-s5-01.md)
drafts one chapter section's own assessment concept item: its concepts,
at least two misconceptions, its references and its dependencies. It is
written for this guide and has not been run against any model in this
build; treat it as a starting point and adapt it. The chapter section
text it reads is data, never instructions, even where a sentence inside
it is phrased as one.

## Scripts

[X-S5-01 Concept item check](../scripts/s5/x-s5-01.md) checks an
assessment concept item file for a malformed id, a duplicate id, or
fewer than two misconceptions. It does not judge whether a description
stays atomic or a reference is specific enough to verify; those stay a
person's own read against the eight-point checklist above. Run it from
the repository root on the sample items:

```bash
python3 -B scripts/s5/concept_item_check.py \
    scripts/sample_data/git_basics_stage5/concept_items/items.json
```

```text
items=3 errors=0
```

All three sample items pass: each has a correctly shaped id, no id
repeats, and each names at least two misconceptions. See
[Reading exit codes](../stage-1/index.md#reading-exit-codes) on the
Stage 1 index for what the exit code means.

Break it on purpose: copy the file, remove one of `ACI-1-001`'s two
misconceptions, and run the check again on the copy:

```text
gap: "ACI-1-001" has 1 misconception, needs at least 2
items=3 errors=1
```

A single missing misconception is enough to fail the check; a clean run
is not proof that a kept misconception is a good one, only that at
least two are named.

## Definition of done

- Every concept in the chapter worth testing has its own assessment
  concept item, with at least two misconceptions.
- Every item's id is shaped `ACI-<chapter>-<NNN>` and used only once.
- Every item has passed the eight-point checklist, not only the id and
  misconception-count check the script runs.
- A person has approved the chapter's own extracted items before stem
  planning begins.

## Common failures

- An item with only one misconception: both the checklist and the
  script catch this, since a stem plan later needs at least one
  misconception per planned distractor.
- A description broad enough to cover more than one concept, so a later
  stem plan cannot tell which item a distractor should trace to.
- A reference too vague to actually check, such as naming a source but
  not the section or the sentence a person would need to confirm the
  claim.

## Adapting to your platform

This sub-stage needs `llm` for drafting each chapter's items,
`file-read` to load the chapter's own text, and `structured-output` for
the item JSON. `shell` runs the concept item check; without it, check
an id's shape, its uniqueness and its misconception count by hand,
using the same rules. `human-approval` covers the approval before stem
planning begins.

## Where humans decide

- Approving a chapter's own extracted items before stem planning
  begins.
- Judging whether a description stays atomic, a reference is specific
  enough to check, and a dependency is accurate, since the script
  cannot judge any of these three from the file alone.

Next: [S5.2 Stem planning](stem-planning.md).
