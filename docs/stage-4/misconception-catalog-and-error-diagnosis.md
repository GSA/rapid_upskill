---
title: "S4.5 Misconception catalog and error diagnosis"
parent: "Stage 4 AI-tutor coaching"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-25"
stage: "S4"
sub_stage: "S4.5"
prompts: ["P-S4-03"]
scripts: []
---

# S4.5 Misconception catalog and error diagnosis

## Outcome

At the end of this sub-stage, a wrong answer is classified by kind,
then checked against a per-chapter catalog of known misconceptions. A
tutor's response then addresses the actual gap, rather than just
marking the answer wrong. The catalog itself, and the classify-then-check
habit this sub-stage builds, both persist beyond any one answer: the
same catalog serves every learner who reaches this chapter.

## Where it fits

This sub-stage takes in a finished, reviewed chapter from
[Stage 3](../stage-3/index.md). It hands the resulting [misconception
catalog](../glossary.md#misconception-catalog) on to two later pages. [S4.1 and S4.2](principles-and-protocol-library.md)'s
Error Diagnosis protocol reads the catalog whenever a learner's wrong
answer calls for it. [S4.7](packaging-and-scope.md) bundles the
catalog for a target platform, alongside the chapter's own text. This
sub-stage's own diagnosis step is one destination
[S4.3 and S4.4](selection-and-chaining.md)'s selection layer can route
an interaction to, once a learner's answer is wrong.

## Why this way

A script or a person can already tell that an answer is wrong. Only a
classification by kind, checked against what the catalog already
knows learners tend to get wrong on this material, lets a response
target the actual misunderstanding instead of repeating the correct
answer louder. Marking an answer wrong without diagnosing why tells a
learner nothing they did not already suspect. Naming the gap, and
matching it against a known, chapter-specific misconception, is what
turns a wrong answer into a useful teaching moment.

## Steps

| Step | Who | Basis |
|---|---|---|
| Classify the wrong answer as conceptual, procedural, factual or careless | Agent | documented |
| Check the classified error against the chapter's own misconception catalog | Agent | documented |
| Respond by type: Socratic questioning back toward the principle, a pointer to the exact step that diverged, the correct fact restated with its source, or a flag for the learner to recheck | Agent | documented |
| Re-test the same idea once the response has been given | Agent | documented |

[The project notes](../glossary.md#reference-implementation) describe
this four-step sequence as a single named protocol.
[S4.1 and S4.2](principles-and-protocol-library.md#the-sixteen-protocols)
lists it, under the library's own letter, as Error Diagnosis: one of
sixteen protocols in the library this sub-stage's catalog feeds. The
project notes illustrate the classify-and-check steps only with
generic examples, not with one of the catalog's own ids. The second
step's own worked example on this page is this guide's own
construction instead, fitted to the documented four-step shape (see
the suggested illustration below).

## The four-type taxonomy

The taxonomy matters because a script or an untrained tutor tends to
treat every wrong answer the same way: mark it wrong, show the right
answer. The four types split "wrong" into kinds that call for
different help. Each type gets its own kind of response, matched one
to one with the step above:

- **Conceptual**: the learner misunderstands a principle behind the
  material, such as believing a mechanism works one way when it
  actually works another. Response: Socratic questioning back toward
  the principle, rather than stating the correct rule outright.
- **Procedural**: the learner has the right idea, but the execution
  goes wrong, such as applying a correct method in the wrong order or
  with the wrong input. Response: a pointer to the exact step that
  diverged, not a restatement of the whole method.
- **Factual**: a plain recall error, such as naming the wrong term or
  command for a thing the learner otherwise understands. Response: the
  correct fact, restated with its source.
- **Careless**: a slip, not a real misunderstanding, such as a typo or
  a rushed answer that does not reflect what the learner actually
  believes. Response: flagged for the learner to recheck, not
  re-taught, since re-teaching a slip wastes a moment that needed only
  a second look.

Getting the type right matters more than getting a fast response: a
conceptual error re-taught as though it were a slip leaves the same
misunderstanding in place for the next question.

## Catalog format

One entry per known misconception, documented as an id shaped
`MC-<chapter>-<NNN>`, a short label, and one to two sentences stating
the wrong belief and the correction. The project notes' own catalog
nests each entry under a chapter heading that itself carries a
sub-chapter number, inside a still larger, part-level grouping. That
scheme does not fit a three-chapter running example with no parts and
no sub-chapters. The worked illustration below drops the sub-chapter
piece and uses a plain chapter number instead, giving an id such as
`MC-1-001`. This is this guide's own adaptation of a documented
format, not a different format the project notes describe.

## This guide's own honest gap

The project notes describe two things without showing one becoming
the other. [Stage 1](../stage-1/index.md)'s own
[knowledge-item](../glossary.md#knowledge-item) schema, already
published, allows [misconception](../glossary.md#misconception) as one
value of a knowledge item's `type` field, not a field of its own (see
[Stage 1's schema](../stage-1/knowledge-items.md#schema)). An item of
that type carries a quote and a locator back to a specific source. The
catalog's own entries carry no such field. They read as chapter-level
observations, not items traceable to one specific source's own
sentence, and the error-diagnosis protocol's own worked examples never
reference the catalog's id format at all.

Presenting the [misconception catalog](../glossary.md#misconception-catalog)
as "compiled from" Stage-1-recorded misconceptions is this guide's own
suggested reading, not something the project notes demonstrate. The
two records could line up in practice; nothing in the project notes
shows that they do.

## A suggested illustration, built for this guide

[The running example](../running-example.md)'s own `SRC-002` already
states, verbatim: "A common mistake is to assume that merging must
create a commit."

That sentence sits under `SRC-002`'s own "How do I combine two
branches?" heading, two paragraphs after the one that describes the
two ways a merge can finish: a fast-forward, or a merge commit.

Suggested, to show what the missing link above would look like if it
existed: a Stage 1 knowledge item of this kind could exist. It would
be of type `misconception`, quoting that sentence with its real
locator: source `SRC-002`, under the heading named above. That
knowledge item could then feed one catalog entry:

> `MC-1-001: Merging always creates a commit` - correction: a
> fast-forward merge only moves a label; no new commit is made.

A learner who answers a "does merging always create a new commit"
question incorrectly would be diagnosed as a **conceptual** error and
shown this entry. [P-S4-03](../prompts/s4/p-s4-03.md) works through
this same scenario.

This illustration is this guide's own construction, built fresh for
this page and this prompt. It does not exist in Stage 1's own
published knowledge-item file, and building it added nothing to that
file.

## Artifacts and formats

- **Misconception catalog**: one file per chapter, entries
  `### MC-<chapter>-<NNN>: <label>`, each with one to two sentences
  stating the wrong belief and the correction.
- **Per-answer diagnosis**: an error type (conceptual, procedural,
  factual or careless), a one-line diagnosis, and a catalog entry id
  when one applies.

Neither artifact records who classified an error or when. A team
adopting this sub-stage still has to decide, on its own, how to keep a
record of a diagnosis beyond the single reply a learner sees. Earlier
stages ask a team to build its own record the same way, for an
approval the project notes do not themselves leave a trail for.

## Prompts

[P-S4-03 Diagnose a wrong answer](../prompts/s4/p-s4-03.md) classifies
a wrong answer by the four-type taxonomy and checks it against a small
excerpt of the misconception catalog. It is written for this guide and
has not been run against any model in this build; treat it as a
starting point and adapt it.

## Scripts

None; the project notes describe no code for this sub-stage.

## Definition of done

- Every wrong answer this sub-stage handles has an error type from the
  four-type taxonomy, not left unclassified.
- A classified error has been checked against the chapter's own
  misconception catalog before a response is given.
- The response given matches the type: a question for a conceptual
  error, a step pointer for a procedural one, a restated fact for a
  factual one, a recheck flag for a careless one.
- Anyone reading a diagnosis can tell whether the Stage-1-to-catalog
  link behind a cited entry is documented or this guide's own
  suggestion.

## Common failures

- Treating every wrong answer as the same error type, which sends
  every learner the same kind of response regardless of what actually
  went wrong.
- Citing a catalog entry that does not actually match the learner's
  own mistake, which teaches the wrong lesson at the wrong moment.
- Skipping the catalog check because the wrong answer looks obviously
  careless, which misses the cases where a slip was actually a
  conceptual gap in disguise.
- Treating this guide's own suggested Stage-1-to-catalog link as if it
  were documented, not suggested. Citing a catalog entry's id as
  though it traced back to a specific Stage 1 record, when the project
  notes do not show that connection being made.

## Adapting to your platform

- `llm`: classifies the wrong answer and drafts the one-line
  diagnosis.
- `file-read`: reads the chapter's own misconception catalog, or the
  excerpt of it a person supplies.
- Without `file-read`, paste the relevant catalog entries into the
  prompt by hand before running it. A chapter's whole catalog can grow
  large; passing only the excerpt a diagnosis actually needs keeps the
  request small and keeps the model from guessing at entries it was
  never shown.
- `human-approval`: covers the catalog-approval step below; a platform
  with no built-in approval step still needs a person to read and
  record it somewhere, such as a shared document.

## Where humans decide

- Approving a chapter's own misconception-catalog entries before they
  are used to diagnose a real learner's errors.
- Confirming that this guide's own illustrative Stage-1-to-catalog
  link is only a suggestion, not something to copy as if the project
  notes required it.
- Judging, for any real diagnosis a tutor gives, whether the cited
  catalog entry actually matches the learner's own mistake, since
  neither artifact above records that judgment automatically.

Next: [S4.6 Learner-facing guardrails](guardrails.md).
