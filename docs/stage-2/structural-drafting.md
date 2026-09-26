---
title: "S2.1 Structural drafting"
parent: "Stage 2 Content development"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-25"
stage: "S2"
sub_stage: "S2.1"
prompts: ["P-S2-01"]
scripts: ["X-S2-01"]
---

# S2.1 Structural drafting

## Outcome

At the end of this sub-stage, a chapter has a first draft on a
**fixed skeleton**: Overview, Learning Objectives, Content, Key
Concepts, Assessment, in that order. The draft carries a Markdown list of
objectives, at least one worked example in the I Do, We Do, You Do
pattern, at least one lab or formative check, and practice items whose
right answer and every wrong answer both carry an explanation.

## Where it fits

This sub-stage takes in a chapter's objectives from [S1.3 Draft the
blueprint](../stage-1/blueprint.md), its knowledge items from [S1.6
Knowledge items](../stage-1/knowledge-items.md), and the relevant slice
of the concept map from [S1.7 Concept map and prerequisite
hierarchy](../stage-1/concept-map-and-hierarchy.md), all from [Stage
1](../stage-1/index.md), already published. It hands on the draft to
[S2.2 Condensation](condensation.md).

## Why this way

A fixed skeleton is what lets a person's review focus on whether the
content fits the blueprint, not on judging a new shape every chapter.
[The project notes](../glossary.md#reference-implementation) describe
this work through two different projects' own drafting workflows. The
two differ in particulars, such as how a task is scoped and handed to
an agent, but they agree on the same fixed skeleton below. This page
presents one method, drawn from what both agree on, rather than
walking through both chains side by side. This page uses the [basis
labels](../stage-1/index.md#basis-labels) defined on the Stage 1
index.

## Steps

| Step | Who | Basis |
|---|---|---|
| Draft the chapter on the fixed skeleton, one section per objective or small group of objectives | Agent | documented |
| Write each section's worked example as I Do, then We Do, then You Do, fading the scaffolding across the three | Agent | documented |
| Write at least one formative check or lab per chapter | Agent | documented |
| Write each practice item's stem with an explanation for the correct option and for every wrong option | Agent | documented |
| Run the chapter structure check | Script | suggested |
| A person checks the draft against the blueprint and the 12-item checklist | Person | suggested for the checklist's use here, documented for the checklist's own content |
| Approve the draft | Person | suggested |

Drafting on the fixed skeleton, the I Do, We Do, You Do pattern, the
formative check or lab, and the fully explained practice items are all
documented in the project notes' own chapter and section templates.
Running an automated structure check and approving the draft have no
described precedent in the project notes, so both are marked
suggested. The person checking a draft against the blueprint is this
guide's [judging fit to the blueprint](../human-roles-gates-and-batching.md)
role; the check itself is suggested, but the checklist it reads from,
below, is documented.

### I Do, We Do, You Do

The project notes describe this pattern the same way across both
drafting workflows, documented. Each worked example fades its own
scaffolding across three steps, rather than jumping straight from a
demonstration to independent practice:

- **I Do**: a narrated worked example, with the reasoning behind each
  step written out, not only the step itself.
- **We Do**: the same kind of task, done together. The learner sees
  the scaffolding still present, such as a hint that is only partly
  revealed, and a test they can run to check their own work.
- **You Do**: the learner works from the task alone, with no hints and
  no scaffolding left, and checks the result against a rubric.

A You Do step that still shows a hint has not finished fading the
scaffolding; see Common failures below.

### The 12-item checklist

The project notes give a single checklist for a finished chapter draft.
This guide restates it in plain language, documented, unchanged in
substance:

1. Exam skills covered.
2. Prerequisites stated.
3. Connection boxes present.
4. I Do, We Do, You Do kept.
5. Code tested.
6. Platform integration included.
7. Misconceptions addressed.
8. Practice questions aligned.
9. Cumulative review present.
10. Learning checks throughout.
11. Self-assessment present.
12. Solutions in appendices.

A person reads the draft against this list before approving it. The
chapter structure check below covers a narrower, mechanical slice of
the same list: the skeleton's headings, the objectives list, and the
lab or formative-check heading. It does not read code, misconceptions
or cross-chapter links, so a clean run is a starting point for the
checklist, not a substitute for reading it.

### How many objectives

The SMART framework is documented in the project notes: an objective
should be specific, measurable, achievable, relevant, and time-bound,
meaning it says by when in the chapter a learner reaches it. The
project notes state no fixed count of objectives for every chapter.
Real counts vary by grain, whether you are writing for a whole chapter,
one section, or one lab, and by the size of the program itself. The
[running example](../running-example.md) gives one concrete instance:
its Chapter 1 uses four objectives, D1.1, D1.2, D1.3 and D2.1, drawn
from its blueprint. Read that as one program's own count at the
chapter grain, not as a rule to copy for every chapter you draft. [S1.3
Draft the blueprint](../stage-1/blueprint.md)'s own Parameters table
already points a reader here for this same correction, so the two
pages agree: neither states a fixed objective count as a rule for
every chapter.

## Artifacts and formats

This sub-stage produces one file per chapter, the chapter draft, in
Markdown:

- Front matter with two keys: `chapter` (a number) and `title`.
- Five H2 headings, in this exact order: `Overview`, `Learning
  Objectives`, `Content`, `Key Concepts`, `Assessment`.
- Under `Learning Objectives`, a Markdown list of at least one item:
  the chapter's own objectives, in the blueprint's words.
- Under `Content`, at least one `### Lab` or `### Formative Check`
  heading, alongside the worked example and any other subsections the
  chapter needs.

Every field above is a starting point for the chapter structure check
below: the script reads the same five headings, the same objectives
list, and the same lab or formative-check heading, and nothing else.
Fields the checklist above also asks for, such as connection boxes or
solutions in appendices, sit inside the Content or Key Concepts
sections as ordinary Markdown; this sub-stage does not fix their exact
shape, only where the fixed skeleton places them.

## Prompts

[P-S2-01 Chapter structural draft](../prompts/s2/p-s2-01.md) drafts one
chapter's content on the fixed skeleton, from its objectives, its
admitted sources' knowledge items, and a concept-map excerpt. It is
written for this guide and has not been run against any model in this
build; treat it as a starting point and adapt it.

## Scripts

[X-S2-01 Chapter structure check](../scripts/s2/x-s2-01.md) reads one
chapter draft and reports a missing or out-of-order required heading,
an empty objectives list, or a Content section with no lab or
formative-check heading, then prints a summary line. It never writes a
file, and a clean run is not proof that the content itself is right,
only that the skeleton, the objectives list and the lab or formative
check are in place.

Run it from the repository root on the sample chapter draft, which is
clean:

```bash
python3 -B scripts/s2/chapter_structure_check.py \
    scripts/sample_data/git_basics_stage2/chapter-1/draft.md
```

```text
headings=5 objectives=4 errors=0
```

Five required headings found, four objectives listed under Learning
Objectives, no errors. See [Reading exit
codes](index.md#reading-exit-codes) on the Stage 2 index for what the
exit code means.

Break it on purpose: copy the sample chapter draft, remove its `##
Key Concepts` heading line, and run the check again on the copy:

```bash
grep -v '^## Key Concepts$' \
    scripts/sample_data/git_basics_stage2/chapter-1/draft.md \
    > draft.broken.md
python3 -B scripts/s2/chapter_structure_check.py draft.broken.md
rm draft.broken.md
```

```text
missing-heading: "Key Concepts"
headings=4 objectives=4 errors=1
```

The missing heading is reported by name, and the headings count drops
from five to four; the objectives count is unaffected, because the
Learning Objectives section itself is untouched. The exit code is 1.

## Definition of done

- The chapter draft has all five required H2 headings, in order.
- The Learning Objectives section holds a Markdown list of the
  chapter's own objectives.
- At least one worked example follows the I Do, We Do, You Do pattern.
- At least one lab or formative check appears under Content.
- Every practice item's stem has an explanation for the correct option
  and for every wrong option.
- The chapter structure check reports no errors.
- A person has checked the draft against the blueprint and the
  12-item checklist, and approved it.

## Common failures

- A chapter missing a required section: the structure check names it,
  but a person still has to judge whether the missing content matters
  here.
- A You Do step that still carries hints: the fading from I Do to We
  Do to You Do stalls, and the learner never works alone.
- A practice item with no explanation for a wrong option: a learner who
  picks that option learns nothing about why it is wrong.
- An objective count wildly out of scale for the chapter's own size:
  neither the structure check nor the SMART criteria catch this by
  themselves, so a person has to judge it against the chapter's actual
  content.
- A term introduced here that later drifts from what [S2.3 and
  S2.4](readability-and-revision.md)'s terminology pass settles on:
  this sub-stage's draft is a first attempt at wording, not the final
  word on a term's definition.

## Adapting to your platform

- `llm`: drafts the chapter content from the objectives, the knowledge
  items and the concept-map excerpt.
- `file-read`: loads the objectives, knowledge items and concept-map
  excerpt before drafting.
- `structured-output`: the chapter draft is Markdown on a fixed
  skeleton; ask for that shape directly, or convert a plain-text reply
  by hand.
- `shell`: runs the chapter structure check; without it, walk the
  headings, the objectives list and the Content section by hand, using
  the same rules.
- `human-approval`: covers the check against the blueprint and the
  12-item checklist, and the approval that follows it.

## Where humans decide

- Whether the draft fits the blueprint's objectives for this chapter,
  not only whether it mentions them.
- Whether the draft meets every item on the 12-item checklist, and
  what to do about an item the checklist calls out.
- How many objectives this particular chapter needs, since no fixed
  count applies.
- Approval of the draft before [S2.2](condensation.md) condenses it.

Next: [S2.2 Condensation](condensation.md).
