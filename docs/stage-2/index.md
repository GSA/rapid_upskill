---
title: "Stage 2 Content development"
nav_order: 20
status: "draft"
last_reviewed: "2026-09-25"
stage: "S2"
---

# Stage 2 Content development

## Outcome

[Stage 2](../glossary.md#stage) turns Stage 1's knowledge base and blueprint into finished chapters. A chapter is drafted from its objectives, condensed, polished for beginner readability, and closed out with a summary and a prerequisite check, before it is considered finished.

## Where it fits

Stage 2 takes in the approved blueprint, admitted sources' knowledge items, and the checked concept map and hierarchy from [Stage 1](../stage-1/index.md). It hands on finished chapters to [Stage 3](../stage-3/index.md) (review and verification).

## Sub-stages

Each part of Stage 2 has a **[sub-stage](../glossary.md#sub-stage)** id, continuing Stage 1's own numbering.

| ID | Name | What it does | Page |
|---|---|---|---|
| 2.1 | Structural drafting | Draft a chapter on the fixed skeleton, with objectives, worked examples in the I Do, We Do, You Do pattern, and a lab or formative check | [S2.1](structural-drafting.md) |
| 2.2 | Condensation | Shorten the draft with five named techniques, meaning intact, checked against a word-count target and two readability deltas | [S2.2](condensation.md) |
| 2.3 | Readability polish | Rework each section for beginner readability, one new complexity dimension at a time, with cumulative review distributed through the chapter | [S2.3 and S2.4](readability-and-revision.md) |
| 2.4 | Six-pass revision | Check the polished chapter through six fixed passes, ending with a non-expert reading it aloud | [S2.3 and S2.4](readability-and-revision.md) |
| 2.5 | Closing templates and the prerequisite check | Add a chapter summary and a prerequisite-review block, then check each section's stated requirements against what the chapter has actually taught | [S2.5](closing-templates.md) |

All five sub-stages are now published.

## Order of work

1. Structural drafting (S2.1) needs the chapter's own objectives, knowledge items and concept-map slice, all from Stage 1.
2. Condensation (S2.2) needs the approved draft from S2.1.
3. Readability polish and six-pass revision (S2.3 and S2.4) need the approved condensed chapter from S2.2.
4. Closing templates and the prerequisite check (S2.5) need the approved revised chapter from S2.3 and S2.4, and hand on a finished chapter to [Stage 3](../stage-3/index.md).

## Basis labels

This page and every Stage 2 sub-stage page use the same three [basis labels](../stage-1/index.md#basis-labels) Stage 1's index defines: `documented`, `inferred` and `suggested`. This page does not redefine them.

## How Stage 2 is run

Agents do the volume work: drafting each chapter section, applying the condensation techniques, drafting each revision pass's changes, and drafting the chapter summary and prerequisite-review blocks. People make each judgment call: whether a draft fits the blueprint, whether a cut kept the chapter's meaning, the beginner-validation read-aloud, and every approval below. This is the same [human-in-the-loop](../glossary.md#human-in-the-loop) design Stage 1 uses: work pauses at set points for a person to look before it continues.

## Approvals

| After | What the person approves | Human roles gate kind | Basis |
|---|---|---|---|
| S2.1 | The chapter draft, against the blueprint and the 12-item checklist | Plan approval | suggested |
| S2.2 | The condensed chapter | Plan approval | documented |
| S2.4 | The chapter, after the sixth revision pass | Plan approval | documented |
| S2.5 | The chapter summary, every prerequisite-review block, and the chapter itself | Plan approval | suggested |

See [Human roles, gates and batching](../human-roles-gates-and-batching.md) for what each gate kind means and who can fill each role.

## Reading exit codes

Every script in this guide exits 0 when it ran and found nothing that fails, 1 when a check failed, and 2 for a usage or input error. Read the exit code right after running a command: `echo $?` on macOS and Linux, `echo $LASTEXITCODE` in PowerShell. Each sub-stage page says what an exit code means for its own script. One exception in this stage: [X-S2-03](readability-and-revision.md#scripts) always exits 0 unless its own input is unusable, since it only reports two scores and never fails a check by itself.

## Artifacts

- Chapter draft: the first draft on the fixed skeleton. Defined on [S2.1](structural-drafting.md).
- Condensed chapter: shortened with named techniques, meaning intact. Defined on [S2.2](condensation.md).
- Revised chapter and read-aloud note: reworked for beginner readability, checked by six passes. Defined on [S2.3 and S2.4](readability-and-revision.md).
- Chapter summary and prerequisite-review blocks: concepts by tier, an exam-skill mapping, links to other chapters. Defined on [S2.5](closing-templates.md).

## What is documented versus suggested

Three points in Stage 2 are this guide's own call, not [the project notes](../glossary.md#reference-implementation)'. The objective count per chapter: the project notes state no fixed count at any grain, so [S2.1](structural-drafting.md) gives the running example's own count as one concrete instance, not a rule to copy for every chapter. The tier vocabulary the chapter summary uses: [S2.5](closing-templates.md) picks Stage 1's own four-name, 1-to-4 scheme over two other vocabularies the project notes use inconsistently for the same template. Keeping the Grade Level and Reading Ease scales separate: [S2.2](condensation.md) defines both scales at their first use, and [S2.3 and S2.4](readability-and-revision.md) reuse them without mixing them, unlike one project script that mixes the two scales in its own pass or fail logic.

## First actions for a new team

Suggested:

- Decide who checks a chapter against the blueprint at each of S2.1, S2.2, S2.4 and S2.5, before Stage 2 starts.
- Confirm that Stage 1's blueprint, knowledge items and concept map are already approved before drafting the first chapter.
- Draft, condense, polish and close one chapter fully before starting a second, so the fixed skeleton and the six-pass order are familiar before they run at scale.

This page states, once for all of Stage 2: the prompts here are samples, written for this guide and not run against any model in this build; the scripts were tested offline on synthetic data; every threshold is a starting value, not a rule. See [Platform requirements](../platform-requirements.md) for what a platform must offer at this stage.

Next: [S2.1 Structural drafting](structural-drafting.md).
