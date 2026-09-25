---
title: "Stage 1 Knowledge acquisition"
nav_order: 10
status: "draft"
last_reviewed: "2026-09-24"
stage: "S1"
---

# Stage 1 Knowledge acquisition

## Outcome

[Stage 1](../glossary.md#stage) builds a [knowledge base](../glossary.md#knowledge-base) ordered by a [prerequisite hierarchy](../glossary.md#prerequisite-hierarchy), and an approved [blueprint](../glossary.md#blueprint), before any teaching text is written. People keep [blueprint design and weighting, and admitting evidence](../human-roles-gates-and-batching.md); the AI is meant to speed exploration and extraction (a design aim). See the [Pipeline overview](../pipeline-overview.md) for what the framework claims and does not claim; this page does not restate it.

## Where it fits

Stage 1 takes in a program goal and domain material. It hands on the knowledge base and the blueprint to Stage 2 and to the rest of this guide's sub-stages.

## Sub-stages

Each part of Stage 1 has a **[sub-stage](../glossary.md#sub-stage)** id. This guide numbers them 1.1 to 1.8, following an earlier survey of [the project notes](../glossary.md#reference-implementation); the project notes' own method documents describe the same activities without this numbering. This guide also splits 1.4 and 1.5 each across more than one page.

| ID | Name | What it does | Page |
|---|---|---|---|
| 1.1 | Frame the domain | Draft a boundary statement: what the program covers, and what it leaves out | [S1.1 and S1.2](frame-and-tasks.md) |
| 1.2 | List the tasks | Draft a job-task analysis: duties, tasks, and the knowledge, skills and abilities each needs | [S1.1 and S1.2](frame-and-tasks.md) |
| 1.3 | Draft the blueprint | Group tasks into weighted domains and objectives, with a rationale for each weight | [S1.3](blueprint.md) |
| 1.4 | Find and admit sources | Plan and run searches, screen and convert candidates, and scan them for hidden instructions | [S1.4a search](search-planning-and-execution.md), [S1.4b screening](screening-and-conversion.md), [S1.4c injection scan](injection-screening.md) |
| 1.5 | Extract from each source | Pull out concepts, then write a distillate with a quote bank | [S1.5a extraction](concept-extraction.md), [S1.5b distillate](distillate-and-quote-bank.md) |
| 1.6 | Knowledge items | Turn each source's concepts and distillate into atomic knowledge items, deduplicated across sources | [S1.6](knowledge-items.md) |
| 1.7 | Concept map and prerequisite hierarchy | Consolidate typed relations into one concept map; assign each concept a prerequisite tier; check for cycles and dangling references | [S1.7](concept-map-and-hierarchy.md) |
| 1.8 | Coverage and gaps | Check the blueprint for under-supported objectives; run a closing search round for any gap worth filling | [S1.8](coverage-and-gaps.md) |

All eight sub-stages are now published. The [Stage 1 checklist and failure modes](checklist-and-failure-modes.md) page gives a single, page-ordered checklist and gate list, plus failure patterns that recur across more than one sub-stage.

## Order of work

1. The blueprint (S1.3) needs the boundary statement and the task list from S1.1 and S1.2.
2. Search plans (S1.4a) need an approved blueprint; no query runs before the plan set is approved.
3. Screening and conversion (S1.4b) and the injection scan (S1.4c) work on the candidates S1.4a finds.
4. Extraction (S1.5) reads only sources that have cleared S1.4b and S1.4c.
5. Knowledge items (S1.6) read each source's distillate; the concept map and hierarchy (S1.7) read the knowledge items; coverage and gaps (S1.8) reads the concept map and blueprint together, and can loop back to more searching when a gap remains.

## Basis labels

Every sub-stage page's step table has a Basis column with one of three labels: `documented` (the project notes describe it), `inferred` (this guide's reading of the project notes, where they describe the activity but not this exact detail), or `suggested` (this guide's own method, where the project notes are silent). Where the project notes disagree with each other, the row says so and names the value this guide's page or script uses, and why.

## How Stage 1 is run

Agents do the volume work: collecting reference decompositions, drafting tasks and objectives, searching, screening, converting and extracting. People make each judgment call: the boundary, the ratings, the weights, which sources to admit, and every approval below. This is a [human-in-the-loop](../glossary.md#human-in-the-loop) design: work pauses at set points for a person to look before it continues.

## Approvals

| After | What the person approves | Human roles gate kind | Basis |
|---|---|---|---|
| S1.1 | The boundary statement | Plan approval | inferred |
| S1.3 | The weighted blueprint | Plan approval | suggested; the project notes approve a skeleton and a gap list, without weights |
| S1.4a | The search plan set, before any query runs | Plan approval | documented |
| S1.4a, the runner | What to do when the circuit breaker opens (it stops the search queue after too many queries fail in a row; see [S1.4a](search-planning-and-execution.md#steps)) | Stop | suggested |
| S1.4b and S1.4c | The selected sources, the flagged list and the blocked-document list | Plan approval | documented; the project notes approve selected sources and a flagged list, after conversion |
| S1.5 | Each batch of distillations | Batch pause | suggested; the project notes ask only for a batch "continue" here, not a review of the content, so treat this row as this guide's own recommendation to add a real look |
| S1.6 | A batch of sources' draft items | Batch pause | documented |
| S1.6 | The consolidated, deduplicated item set | Plan approval | suggested |
| S1.7 | The concept map and hierarchy, which fills in the `tier` field the blueprint reserves for this sub-stage | Plan approval | suggested |
| S1.8 | The expansion plan | Expansion-loop approval | documented |

See [Human roles, gates and batching](../human-roles-gates-and-batching.md) for what each gate kind means and who can fill each role.

## Reading exit codes

Every script in this guide exits 0 when it ran and found nothing that fails, 1 when a check failed, and 2 for a usage or input error. Read the exit code right after running a command: `echo $?` on macOS and Linux, `echo $LASTEXITCODE` in PowerShell. Each sub-stage page says what an exit code means for its own script.

## Recording an approval

Write who approved, what file, and when. A hash is optional: run `shasum -a 256 FILE` on macOS and Linux, or `certutil -hashfile FILE SHA256` on Windows, and record the result with the approval.

## Artifacts

- Boundary file: what the program covers and excludes. Defined on [S1.1 and S1.2](frame-and-tasks.md).
- Task list: duties, tasks, and knowledge, skills and abilities. Defined on [S1.1 and S1.2](frame-and-tasks.md).
- Blueprint: weighted domains and objectives. Defined on [S1.3](blueprint.md).
- Search plan: one plan per blueprint objective. Defined on [S1.4a](search-planning-and-execution.md).
- Candidate list: the deduplicated search results. Defined on [S1.4a](search-planning-and-execution.md).
- Admitted sources: converted, checked and scanned documents. Defined on [S1.4b](screening-and-conversion.md) and [S1.4c](injection-screening.md).
- Concept lists: one per source. Defined on [S1.5a](concept-extraction.md).
- Distillates: one per source, with a quote bank. Defined on [S1.5b](distillate-and-quote-bank.md).
- Knowledge items: atomic, typed claims, deduplicated across sources. Defined on [S1.6](knowledge-items.md).
- Concept map and hierarchy: typed edges and a prerequisite tier per concept. Defined on [S1.7](concept-map-and-hierarchy.md).
- Gap list: blueprint objectives this guide's own bar finds under-supported. Defined on [S1.8](coverage-and-gaps.md).

## What is documented versus suggested

S1.1 to S1.3 have no prompt in the project notes. Every prompt on those three pages is this guide's own sample: a starting point, not something the project notes provide.

## First actions for a new team

Suggested:

- Decide who approves at each gate above, and where approvals will be recorded, before Stage 1 starts.
- Gather a goal, an audience, and two or three reference decompositions of the field before drafting the boundary statement.
- Run S1.1 through S1.3 in order; every later sub-stage needs the approved blueprint they produce.

This page states, once for all of Stage 1: the prompts here are samples, written for this guide and not run against any model in this build; the scripts were tested offline on synthetic data; every threshold is a starting value, not a rule. See [Platform requirements](../platform-requirements.md) for what a platform must offer at this stage.

Next: [S1.1 and S1.2 Frame the domain and list the tasks](frame-and-tasks.md).
