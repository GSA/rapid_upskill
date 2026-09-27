---
title: "Worked example, start to finish"
parent: "Beyond the five stages"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-27"
prompts: []
scripts: []
---

# Worked example, start to finish

## Outcome

A reader can trace one continuous thread — the same running example, Git Basics for New Team Members — through every [stage](glossary.md#stage) and workstream this guide publishes, from the earliest source gathered to the last artifact produced. Each step below names a real, already-established artifact id and links to the real page that defines it in full. A reader leaves this page able to point at one artifact from every stage of the pipeline and say exactly where its own schema lives, without re-deriving that schema from this page.

## Where it fits

Top level, cross-cutting. [The running example](running-example.md) introduces the example's own setup — its domains, objectives, sources and blueprint. [Pipeline overview](pipeline-overview.md) describes the framework's shape in the abstract. This page instead narrates the example's own journey in pipeline order. It links to the real page and the real artifact id at each step, and never restates a schema either of those two pages, or a stage page, already defines. A reader arriving here without having read anything else should read [The running example](running-example.md) first; this page assumes that setup and moves straight into what happens to it, stage by stage and workstream by workstream. A reader who already knows one stage well can also start there and follow only the ids that stage hands forward, without reading every row above it.

## Why this way

Every earlier page in this guide already proves its own step works in isolation: [S1.3 Draft the blueprint](stage-1/blueprint.md) shows a blueprint passing its own check, [S5.6 Quiz and exam assembly](stage-5/quiz-and-exam-assembly.md) shows an answer key passing its own check, and so on for every sub-stage in between. None of those pages, on its own, shows the same artifact surviving unchanged from one stage into the next. A source admitted in Stage 1 might be the same source a citation check reads in Stage 3; a misconception drafted from a chapter in Stage 5 might trace back to the same objective and source pairing Stage 4 already worked through — but no single page shows that continuity. Reading the whole site stage by stage leaves that continuity to a reader's own memory, carried across dozens of pages read at different times, on different days. One linear page, keyed to real ids from start to finish, makes the continuity checkable instead of assumed. A reader can follow one id, such as `D2.3` or `SRC-003`, all the way from the blueprint that first names it to the answer key that eventually scores it. Neither end has to be trusted on faith that they actually line up.

## Steps

The table below is this page's own worked illustration: one row per major pipeline point the example actually passes through, linking to the real page that covers each in full. It assumes [The running example](running-example.md)'s own setup and does not repeat it. Each row says only what carries forward from the row above, or what a later stage does with an artifact an earlier row already named; no row restates a schema, which stays defined once, on its own owning page.

| Pipeline point | What carries forward |
|---|---|
| [Stage 1: Knowledge acquisition](stage-1/index.md) | The seven sources and the [blueprint](glossary.md#blueprint) [The running example](running-example.md) introduces are the exact ones every row below actually uses. [S1.8 Coverage and gaps](stage-1/coverage-and-gaps.md) is where the planted gap, `D4.2`, first surfaces as a finding a script produced, not just a fact stated about the blueprint. |
| [Stage 2: Content development](stage-2/structural-drafting.md) | [S2.1 Structural drafting](stage-2/structural-drafting.md) turns Stage 1's own blueprint objectives into Chapter 1's actual text. Neither [S2.2 Condensation](stage-2/condensation.md) nor [S2.3 and S2.4](stage-2/readability-and-revision.md) introduces a new artifact; both keep working on that same draft. |
| [Stage 3: Review and verification](stage-3/tiering-and-remediation.md) | The same sources Stage 1 gathered are what get checked and tiered here: `SRC-001`, `SRC-002` and `SRC-006` become the sources behind a sample claim and citation in [S3.1](stage-3/layer-1-automated-detection.md) and [S3.3](stage-3/layer-3-audit-trail.md), and all seven sources are assigned a credibility tier, with the older, conflicting `SRC-005` and the promotional `SRC-007` landing lowest for the same reasons Stage 1's own descriptions already gave. |
| [Stage 4: AI-tutor coaching](stage-4/principles-and-protocol-library.md) | Chapter 2's own `D2.3`/`SRC-003` merge-conflict pairing, already named in Stage 1's blueprint, is what [S4.1 and S4.2](stage-4/principles-and-protocol-library.md)'s own hint ladder actually walks through — the first of two stages below that reuse this exact pairing. |
| [Stage 5: Assessment development](stage-5/misconception-to-distractor-bridge.md) | The same `D2.3`/`SRC-003` pairing Stage 4 just used reappears a second time: [S5.1](stage-5/misconception-to-distractor-bridge.md) builds its own second Chapter 2 item, `ACI-2-002`, from it, fresh from the chapter's own text, never from Stage 1's or Stage 4's own records. From there the bank of 20 [stems](glossary.md#stem) the blueprint calls for is built and assembled into an answer key — the last new artifact before the chapter leaves the five-stage framework. |
| [Certification alignment](certification-alignment.md) | The finished chapters Stages 2 through 5 produced are rated here against a certification's own outline for the first time. The mismatch [The running example](running-example.md) already promises — one skill no chapter covers, one chapter no skill covers — is where that promise is actually kept, in [certification-alignment.md](certification-alignment.md#worked-illustration)'s own worked illustration. |
| [Delivery](delivery/index.md) | Delivery turns a finished chapter into a slide deck or a compiled volume, among other outputs. Its own sample data is intentionally unrelated to Git Basics for New Team Members; nothing on a Delivery page continues this running example, and this page makes no claim otherwise. |
| [Operating practices](operating-practices/index.md) | Carried out by an agent team, this same run would sit alongside several already-published practices, none of them a new claim about the framework: coordinating an [orchestrator](glossary.md#orchestrator)'s own dispatch of Stage 1's search and extraction work is an [agent orchestration](operating-practices/agent-orchestration-patterns.md) concern; recording each stage's own progress is a [run logging](operating-practices/run-logging-and-dashboards.md) concern; screening `SRC-006` for a hidden instruction is the same principle [prompt-injection screening](operating-practices/prompt-injection-screening.md) names once, cross-cutting; and carrying this run across more than one session is a [hand-off documents and sessions](operating-practices/hand-off-documents-and-sessions.md) concern. |

## Worked illustration

This page carries no worked illustration separate from the table above. The Steps table is itself the worked illustration, keyed to real ids across the whole pipeline rather than to one sub-stage's own sample. Reading down that one table, in pipeline order, rather than reading one page at a time and holding the connections in memory, is the whole point of building this page at all. A second, separate illustration built fresh for this page would only compete with the one already sitting in the Steps table above, so none is added.

## Prompts

None. This page introduces no new prompt. Every prompt behind a step named above already lives on that step's own page. Two examples: [P-S1-03 Blueprint domains, objectives and weights](prompts/s1/p-s1-03.md) behind the blueprint, and [P-S5-01 Extract an assessment concept item](prompts/s5/p-s5-01.md) behind the assessment concept items. This page links to the page that names each one rather than repeating any of them here. Writing a fresh prompt for this page would either duplicate one of those already-published prompts or step on a chapter's own content, neither of which this page's own job calls for.

## Scripts

None, for the same reason. [X-S1-01 Blueprint check](scripts/s1/x-s1-01.md) checks the blueprint, [X-S5-05 Answer key check](scripts/s5/x-s5-05.md) checks the answer key, and every other script this page's steps mention already has its own page. This page runs none of them and adds no new one. A reader who wants to run a check against the running example's own files follows the link to the sub-stage that owns that check, not this page.

## Artifacts

Every real artifact id this page touches, with its role in this run and the page that defines it in full.

| Artifact id | Role in this run | Defined on |
|---|---|---|
| `SRC-001` through `SRC-007` | The seven sources supplying every chapter's content | [The running example](running-example.md) |
| `D1.1` through `D4.3` | The blueprint's twelve objectives across four domains | [The running example](running-example.md), [S1.3 Draft the blueprint](stage-1/blueprint.md) |
| The blueprint (Git Basics for New Team Members) | The program's own weighted plan | [S1.3 Draft the blueprint](stage-1/blueprint.md) |
| `D4.2` | The planted coverage gap, no supporting source | [S1.8 Coverage and gaps](stage-1/coverage-and-gaps.md) |
| The concept map and hierarchy (`staging-area`, `commit`, `branch` and others) | Tiered concepts underlying the twelve objectives | [S1.7 Concept map and prerequisite hierarchy](stage-1/concept-map-and-hierarchy.md) |
| `KI-001` through `KI-004` | Sample canonical knowledge items drawn from `SRC-001` and `SRC-003` | [S1.6 Knowledge items](stage-1/knowledge-items.md) |
| `MC-1-001` | A suggested misconception-catalog entry, built from `SRC-002`'s own sentence | [S4.5 Misconception catalog and error diagnosis](stage-4/misconception-catalog-and-error-diagnosis.md) |
| `ACI-1-001`, `ACI-2-001`, `ACI-2-002` | Assessment concept items for Chapters 1 and 2 | [S5.1 Misconception-to-distractor bridge](stage-5/misconception-to-distractor-bridge.md) |
| `PLAN-1`, `PLAN-2` | Chapter 2's own planned stem rows | [S5.2 Stem planning](stage-5/stem-planning.md) |
| `STEM-2.1-001`, `STEM-2.1-002` | The two finished stems carried into the answer key | [S5.2 Stem planning](stage-5/stem-planning.md), [S5.3 and S5.4 Distractors and format rules](stage-5/distractors-and-format-rules.md), [S5.6 Quiz and exam assembly](stage-5/quiz-and-exam-assembly.md) |
| `CB-1.1` through `CB-3.2` | The fictional certification's own eight exam skills | [Certification alignment](certification-alignment.md) |

## Definition of done

- A reader can name, for the running example, one artifact from each stage and workstream, and point to the page that defines it.
- Every id named on this page matches a real id already established on [The running example](running-example.md) or on the stage page that owns it.
- No row above restates a schema; each one only says what happened to an artifact whose shape is defined elsewhere.

## Common failures

- Treating this page as a second source of truth for a schema. It is not: every schema stays defined once, on its own owning page, and this page only narrates and links.
- Assuming Delivery's own sample data continues the running example, when the two are intentionally unrelated by design.
- Reading one row here as a substitute for the stage page it links to, rather than as a pointer toward it: a row names what happened, not the full method behind it.
- Copying an id from this page into a reader's own program without also reading the owning page's own definition of that id's schema. A reader who never opens the linked page still has to guess at what the id's own fields mean.

## Adapting to your platform

This page adapts nothing of its own. It narrates a run that is already adaptable through each linked page, and every capability a reader would need for a given step is already named on that step's own "Adapting to your platform" section.

## Where humans decide

This page states no new gate. It only narrates where the already-published gates fall along this one thread. In order: the blueprint's approval before search planning begins, the batch pauses across Stage 1, the draft approval before condensation, the tiering and escalation decisions in Stage 3, the protocol-library approval before any tutoring session runs, the stem-plan approval and the assembled-quiz approval in Stage 5, and the rating and schedule approvals in certification alignment. A reader who wants the full list of who can fill each role, and what each gate kind requires, still has to read [Human roles, gates and batching](human-roles-gates-and-batching.md) and each stage's own approvals table. This page only points at where each one sits along one worked thread.

Next: [Evidence and limitations](evidence-and-limitations.md).
