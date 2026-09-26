---
title: "Stage 5 Assessment development"
nav_order: 50
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
---

# Stage 5 Assessment development

## Outcome

[Stage 5](../glossary.md#stage) turns a chapter's own finished text into
a blueprint-tagged bank of test questions, each one traceable back to a
documented misconception. A chapter's content becomes a small set of
assessment concept items; those items become planned, then drafted,
stems; a whole bank's own difficulty mix and domain coverage are
checked against the blueprint; and finished stems are assembled into a
deliverable quiz and assigned to one or more delivery formats.

## Where it fits

Stage 5 takes in a finished, reviewed chapter from
[Stage 3](../stage-3/index.md) and the blueprint
[Stage 1](../stage-1/index.md) approved. This stage's own output, an
item bank and its delivered formats, is designed to reach a learner
directly, outside the chapter-production pipeline the earlier stages
describe.

## Three names, three artifacts

[Stage 1](../stage-1/knowledge-items.md) already publishes a knowledge
item: `id`, `type`, `body`, `relations`, `evidence`, `tags`, `status`.
This stage's own extraction step, S5.1, produces a different,
structurally distinct artifact. This guide calls it an **assessment
concept item**, never a "knowledge item", because its own field list
does not match Stage 1's. A third, further artifact appears from S5.2
onward: a **stem**, the finished, assembled question. An assessment
concept item feeds one or more stems; a stem is not itself a bigger or
smaller assessment concept item. Read this paragraph once before any
sub-stage page below, since every one of them assumes it: knowledge
item (Stage 1) to assessment concept item (S5.1, this guide's own
name) to stem (S5.2 onward). [S5.1](misconception-to-distractor-bridge.md)
restates the choice in full, where the artifact is first defined.

## Sub-stages

| ID | Name | What it does | Page |
|---|---|---|---|
| 5.1 | Misconception-to-distractor bridge | Extract a chapter's own assessment concept items, each with at least two documented misconceptions | [S5.1](misconception-to-distractor-bridge.md) |
| 5.2 | Stem planning | Map assessment concept items to a planned set of stems by difficulty, before any stem is drafted | [S5.2](stem-planning.md) |
| 5.3 | Distractors | Draft a stem's own distractors, scaled in sophistication to its difficulty | [S5.3 and S5.4](distractors-and-format-rules.md) |
| 5.4 | Format rules | Check every stem against a fixed set of format rules | [S5.3 and S5.4](distractors-and-format-rules.md) |
| 5.5 | Difficulty distribution | Fix a whole bank's own difficulty mix, mapped to Bloom's levels | [S5.5 and S5.7](difficulty-and-blueprint-bank.md) |
| 5.6 | Quiz and exam assembly | Assemble finished stems into an answer key, with points and feedback | [S5.6](quiz-and-exam-assembly.md) |
| 5.7 | Blueprint-aligned bank | Weight a bank's own domain coverage against the blueprint | [S5.5 and S5.7](difficulty-and-blueprint-bank.md) |

S5.5 and S5.7 are not adjacent sub-stage numbers. S5.6 sits between
them in the project notes' own numbering, but its own content is
different enough, and rich enough, that this guide gives it two pages
of its own instead: [S5.6](quiz-and-exam-assembly.md) and
[Stage 5 delivery formats and lessons](delivery-formats.md), a closing
synthesis page with no sub-stage number of its own, covering a
deliverable-kind coverage check and three generalizable lessons from
this stage's own script history.

## Order of work

1. Extract a chapter's own assessment concept items
   ([S5.1](misconception-to-distractor-bridge.md)).
2. Plan a chapter's own stems by difficulty, before drafting any
   ([S5.2](stem-planning.md)).
3. Draft each stem and its distractors, under the format rules
   ([S5.3 and S5.4](distractors-and-format-rules.md)).
4. Check the whole bank's own difficulty mix and domain composition
   against the blueprint
   ([S5.5 and S5.7](difficulty-and-blueprint-bank.md)).
5. Assemble finished stems into a deliverable quiz
   ([S5.6](quiz-and-exam-assembly.md)) and assign each one to a
   delivery format ([delivery formats](delivery-formats.md)).

## Basis labels

This page and every Stage 5 sub-stage page use the same three
[basis labels](../stage-1/index.md#basis-labels) Stage 1's index
defines: `documented`, `inferred` and `suggested`. This page does not
redefine them.

## Approvals

| After | What the person approves | Human roles gate kind | Basis |
|---|---|---|---|
| S5.1 | A chapter's own extracted assessment concept items, before stem planning begins | Plan approval | suggested |
| S5.2 | A chapter's own stem plan, before any stem is drafted | Plan approval | suggested |
| S5.3 and S5.4 | Each drafted stem, before it enters the item bank | Plan approval | documented |
| S5.5 and S5.7 | A finished bank's own composition against the blueprint, before assembly | Plan approval | suggested |
| S5.6 | An assembled quiz, before delivery | Plan approval | suggested |
| Delivery formats | A delivered, deliverable-kind-assigned package, before it reaches a learner | Plan approval | suggested |

The project notes describe a real review cycle only for approving a
drafted stem before it enters the item bank; every other row above is
this guide's own suggested checkpoint. See
[Human roles, gates and batching](../human-roles-gates-and-batching.md)
for what each gate kind means and who can fill each role.

## Artifacts

- A chapter's own assessment concept items. Defined on
  [S5.1](misconception-to-distractor-bridge.md).
- A chapter's own stem plan. Defined on [S5.2](stem-planning.md).
- A chapter's own finished stems. Defined on
  [S5.3 and S5.4](distractors-and-format-rules.md).
- A bank-composition record. Defined on
  [S5.5 and S5.7](difficulty-and-blueprint-bank.md).
- An answer key. Defined on [S5.6](quiz-and-exam-assembly.md).
- A delivery manifest. Defined on
  [delivery formats](delivery-formats.md).

## What is documented versus suggested

Several points in Stage 5 are this guide's own call, not
[the project notes](../glossary.md#reference-implementation)'. The
name "assessment concept item", and every field this guide's own
schema for it leaves out of the fuller field list the project notes
actually use, are this guide's own choice, stated as such on
[S5.1](misconception-to-distractor-bridge.md). The chapter-linked
`STEM-<chapter>.<section>-<NNN>` id scheme is this guide's own choice
between two disagreeing project schemes, stated in full on
[S5.2](stem-planning.md). The easy-tier distractor technique is this
guide's own inference, since no project guide names one; the medium
and hard tiers are documented, both on
[S5.3 and S5.4](distractors-and-format-rules.md). Every default value
this guide's own sample scripts use, such as a point value or a
bank-composition figure, is this guide's own illustration, not a
project result. A further honest gap, mirroring the ones
[Stage 4](../stage-4/index.md)'s own index states plainly: S5.1's own
extraction pass never consults Stage 1's recorded misconceptions or
Stage 4's own misconception catalog. It is a fresh pass over the
chapter's text, by design, not an oversight; a team building this for
real could choose to consult those earlier records first, as this
guide's own suggested time-saver.

## First actions for a new team

Suggested:

- Decide who approves a chapter's own extracted assessment concept
  items before stem planning begins.
- Confirm a chapter has cleared Stage 3's own closing checks, and that
  its blueprint is approved, before Stage 5 begins on it.
- Pick this guide's own id scheme, or your own, before any stem is
  drafted, and hold to it across every chapter.

This page states, once for all of Stage 5: the prompts here are
samples, written for this guide and not run against any model in this
build. Every threshold is a starting value, not a rule. See
[Platform requirements](../platform-requirements.md) for what a
platform must offer at this stage.

Next: [S5.1 Misconception-to-distractor bridge](misconception-to-distractor-bridge.md).
