---
title: "S2.5 Closing templates and the prerequisite check"
parent: "Stage 2 Content development"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-25"
stage: "S2"
sub_stage: "S2.5"
prompts: ["P-S2-04"]
scripts: ["X-S2-04"]
---

# S2.5 Closing templates and the prerequisite check

## Outcome

At the end of this sub-stage, a finished chapter has a **chapter
summary**: the chapter's concepts grouped by
[tier](../glossary.md#prerequisite-hierarchy), an exam-skill mapping,
and links to other chapters. Before each section, it also has a
**prerequisite-review block** a learner can check against. A script
has checked every section's stated requirements against what the
chapter has actually taught by that point, and a person has approved
the result.

## Where it fits

This sub-stage takes in the revised chapter from
[S2.3 and S2.4](readability-and-revision.md). It hands on a chapter
ready for [Stage 3](../stage-3/index.md) review.

## Why this way

A summary and a prerequisite-review block are the two places a chapter
states what it assumes and what it connects to. Writing them last means
they describe the chapter as it actually ended up, not as it was
planned when drafting started. Checking each section's stated
requirements against what came before it catches a stale assumption
while it is still cheap to fix. This happens before a person approves
the chapter, rather than leaving a learner to discover the gap partway
through a section. This page uses the
[basis labels](../stage-1/index.md#basis-labels) defined on the Stage 1
index.

## Steps

| Step | Who | Basis |
|---|---|---|
| Draft the chapter summary: sort the chapter's concepts by tier, map its content to exam skills, and link it to other chapters | Agent | documented for the mapping and the link idea; suggested that an agent drafts it, since [the project notes](../glossary.md#reference-implementation) do not say who does |
| Draft a prerequisite-review block before each section: which concepts a learner needs already, and where to review one they lack | Agent | suggested for authorship; documented for the content |
| Run the prerequisite check across the chapter's sections | Script | suggested |
| Check the summary and every prerequisite-review block against the blueprint and the concept map | Person | suggested |
| Approve the chapter | Person | suggested |

## Chapter summary

The chapter summary (documented) has four parts. An overview names the
chapter's exam weight and complexity mix. The chapter's concepts are
grouped by tier, and an exam-skill mapping shows which
[exam skill](../glossary.md#exam-skill) each part of the chapter
prepares a learner for, and how well. Links to other chapters close it
out. The project notes describe that last part in three different
formats (narrative bullets, a table, an arrow diagram); this guide
keeps to one: a short table of chapter, concept and why it matters.

Concepts are grouped using [S1.7](../stage-1/concept-map-and-hierarchy.md)'s
own tier scheme, spelled exactly as that page spells it: 1 foundational,
2 building blocks, 3 integrated, 4 applied. The project notes use two
other tier vocabularies for this template elsewhere, one of them close
enough in wording to Stage 1's own scheme to blend with it by accident.
This guide reuses Stage 1's scheme without change, for the same reason
S1.7 picked one mapping over the project's own inconsistent tier
language. It says plainly that the project notes are not consistent
with themselves on this point.

Length and content are the reference implementation's parameters:
roughly 150 to 300 words, or about 10 to 15% of the chapter's own
length; 4 to 7 main concepts; written at around an 8th-grade reading
level. That reading-level target reuses the Grade Level meaning
[S2.2](condensation.md) defines at its first use. It is a lower,
separate number from the 9-to-11 grade level
[S2.3 and S2.4](readability-and-revision.md) sets for the chapter body
itself, so do not confuse the two.

Content mix inside the summary is 60/30/10, the reference
implementation's parameters, defined here, on this page, rather than on
[S2.3 and S2.4](readability-and-revision.md), which only names it to
tell it apart from its own numbers. That is about 60% of the summary's
own length on the chapter's main concepts, 30% on secondary points, and
10% on how the chapter connects to others. This is not the same figure
as [S2.3 and S2.4](readability-and-revision.md)'s 70/20/10
cumulative-review question mix; the two numbers look alike but cover
different things.

## Prerequisite-review block

The prerequisite-review block (documented) sits before each section. It
lists the concepts that section needs, each marked required or
optional. It also gives a short self-check question per concept, for a
learner to test whether they already have it, and, for any concept a
learner does not have, where to go and review it. Required means the
section will not make sense without the concept; optional means the
section reads more smoothly with it, but a learner without it can
still follow along. The self-check question is meant for the learner
to answer quietly, before starting the section, not as a graded
question the chapter scores.

## Artifacts and formats

- Chapter summary: Markdown, one per chapter. Defined on
  [Chapter summary](#chapter-summary).
- Prerequisite-review blocks: Markdown, one per section. Defined on
  [Prerequisite-review block](#prerequisite-review-block).
- Links to other chapters: a short table with three columns, chapter,
  concept and why it matters, one row per link. This guide's own
  choice, kept to one format instead of the project notes' three.
- Taught-so-far record (`taught_so_far.json`, the format
  `prerequisite_check.py` reads): a list of objects, each with
  `section` (a dotted section id, such as `"1.2"`) and
  `concepts_taught` (a list of concept ids taught by that section). The
  sample lists two sections, `"1.1"` and `"1.2"`.
- Section-requires record (`section_requires.json`): a list of
  objects, each with `section` and `requires` (a list of
  `{"concept": ..., "min_tier": ...}` objects). The sample checks
  section `"1.2"`, which passes, and section `"1.3"`, which does not.

## Prompts

[P-S2-04 Chapter summary and prerequisite review](../prompts/s2/p-s2-04.md)
drafts a chapter summary and a prerequisite-review block for one
section, from the chapter's concepts by tier, a list of exam skills and
the section's own stated requirements. It is written for this guide and
has not been run against any model in this build.

## Scripts

[X-S2-04 Prerequisite check](../scripts/s2/x-s2-04.md) reads a
concept-map catalog, a taught-so-far record and a section-requires
record. It checks, section by section, whether every required concept
was already taught, and at a tier no higher than the catalog's own
tier for it.

Unlike the other scripts in this batch, this one reads across two
different sample-data folders: this page's own `taught_so_far.json` and
`section_requires.json`, plus
[S1.7](../stage-1/concept-map-and-hierarchy.md)'s own, already-published
`catalog.json`, read-only and not copied here. Run it from the
repository root, with all three paths:

```bash
python3 -B scripts/s2/prerequisite_check.py \
    scripts/sample_data/git_basics_stage1/concept_map/catalog.json \
    scripts/sample_data/git_basics_stage2/prerequisites/taught_so_far.json \
    scripts/sample_data/git_basics_stage2/prerequisites/section_requires.json
```

```text
pass: section "1.2" requires "commit", satisfied
gap: section "1.3" requires "branch" at tier 1, catalog has it at tier 2
sections=2 gaps=1
```

Two sections checked: section 1.2 requires "commit" at tier 1 or lower,
and by then the chapter has already taught "commit", which the catalog
also places at tier 1, so it passes. Section 1.3 requires "branch" at
tier 1 or lower. By then the chapter has taught "branch" too, but the
catalog places "branch" at tier 2, higher than the section's own stated
minimum, so the check flags it. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 2 index
for what the exit code means.

A tier mismatch like this one is a signal, not a proof of a mistake. It
means the section's own assumption about how deep a learner needs to
understand a concept does not match where the concept map places it.
That mismatch is worth a person's second look before the chapter is
approved. No break-on-purpose edit is needed here: the sample already
carries one real pass and one real flag, unlike a catalog file that
starts clean and needs an edit to show a failure. A clean run of this
check is not proof that a section's own requires list names the right
concepts, only that what it does name lines up with what came before
it.

## Definition of done

- The chapter summary states the chapter's exam weight and complexity
  mix, groups its concepts by tier, maps at least one exam skill, and
  links to other chapters in the one table format this guide uses.
- Every section has a prerequisite-review block: required and optional
  concepts, a self-check question for each, and where to review any
  concept a learner may lack.
- The prerequisite check has run, and every flagged section has been
  read and resolved or explained.
- A person has checked the summary and every prerequisite-review block
  against the blueprint and the concept map.
- A person has approved the chapter.

## Common failures

- A chapter summary using a tier name that does not match Stage 1's own
  four names, which breaks the one prerequisite vocabulary this guide
  uses across every stage.
- A prerequisite-review block naming a concept the learner has no way
  to review, because no earlier chapter or section actually covers it.
- An exam-skill mapping with no certification outline to map against,
  so the mapping has nothing real behind it.
- A prerequisite check that runs clean while the chapter summary and
  the section text still disagree about which concepts a section
  actually uses. The check only compares stated requirements against
  what was taught, not the chapter's own prose.

## Adapting to your platform

- `llm`: drafts the chapter summary and each prerequisite-review block.
- `file-read`: reads the chapter's own text, the concept map and, for
  the exam-skill mapping, the certification outline.
- `structured-output`: ask for the tier groups and the required or
  optional lists directly in a fixed shape, or convert a plain-text
  reply by hand.
- `shell`: runs the prerequisite check; without it, work out by hand
  which concepts a chapter has taught by a given section, and compare
  each one's catalog tier to what the section states.
- `human-approval`: covers the check against the blueprint and the
  concept map, and the final approval.

## Where humans decide

- Whether the summary and each prerequisite-review block fit the
  blueprint and the concept map.
- Which flagged section, if any, from the prerequisite check needs a
  fix rather than a note.
- Approval of the chapter; see the Stage 2 index's
  [Approvals table](index.md#approvals) for what kind of approval this
  is and how to record it.

Next: [Stage 3 Review and verification](../stage-3/index.md).
