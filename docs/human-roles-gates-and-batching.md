---
title: "Human roles, gates and batching"
nav_order: 5
status: "draft"
last_reviewed: "2026-09-21"
---

# Human roles, gates and batching

This page covers who decides, where work pauses, and how work is sized. It describes a design and how the reference implementation, the project this guide draws on, ran it as of September 2026. It makes no claim about results.

## The premise

The framework rests on one idea. AI absorbs the volume work, such as drafting, condensing and cross-referencing. People keep the judgment calls, such as [blueprint](glossary.md#blueprint) design, expert review, [misconception](glossary.md#misconception) authoring and test-question rating. This is a [human-in-the-loop](glossary.md#human-in-the-loop) design. Its authors call it an interpretation, not a measured result.

## What the framework says people do

| Role | What it covers | Where |
|---|---|---|
| Blueprint design and weighting | Framing the program's plan and weighting its parts | Stage 1 |
| Evidence admission | Deciding which sources count as evidence | Stage 1 |
| Expert review | Checking accuracy through audit, deeper checks and approval | Stage 3 |
| Misconception authoring | Naming the wrong ideas learners tend to hold | Stage 4 |
| Test-question rating | Rating test questions | Stage 5 |
| Approval at gates | Deciding at each gate whether work goes on | All stages |
| Graded-work policy | Graded work is AI-free unless an instructor says otherwise | Stage 4 (a tutor rule) |

The table shows what the framework assigns, not what was done. In the reference material, expert review is specified, but no completed sign-off was found. [Agents](glossary.md#agent) wrote the test questions, and no record shows a person writing the misconception catalogs. A coordinating [orchestrator](glossary.md#orchestrator) session made the accept and merge decisions. It is not a person. No record found is not evidence that something did not happen.

## The five gates

A [gate](glossary.md#gate) is a checkpoint where the work stops until a person decides.

| Gate | When it stops the work | What you do |
|---|---|---|
| Batch pause | After every item in a batch is processed | Say whether to continue |
| Plan approval | Before an irreversible step, such as cutting content | Approve the plan or reject it |
| Search-cycle approval | When a search cycle would repeat past 2 rounds | Approve another round or decline |
| Search cap decision | When the cap on searches runs out | Raise the cap, continue with what was found, or pause |
| Stop | When a check fails or an approved file changes | Fix the cause; approve again if a file changed |

Two notes:

- A standing "continue" can satisfy a batch pause. So a pause alone is not evidence that anyone checked the work.
- An approval can be tied to one version of a file by a hash, a fingerprint of its contents. In the reference design, plan approvals (the step gates) are tied this way and the other gates are not. A tied approval lapses when the file changes.

## Three batching practices

These are the reference design's parameters, project practice rather than rules for every project.

1. **Work in small [batches](glossary.md#batch).** The design uses 3 to 8 items per batch, chosen by item size, with a pause after each. An item is one unit of work, such as one source.
2. **Cap parallel workers.** The caps varied by workflow, from about 4 to 8.
3. **Write a [hand-off document](glossary.md#hand-off-document) when context (working memory) runs low.** This is a short file that lets a fresh session continue the task. Then start a new session.

A later part of this guide covers other practices.

## Parallel workers and rate limits

Two facts:

- The reference design runs work in parallel. The orchestrator can start several [subagents](glossary.md#subagent) at once.
- Outside services apply a [rate limit](glossary.md#rate-limit). The project's notes record limits such as one request per second, or a wait of a few seconds between calls.

The sources we read do not say how these fit together. Our inference: the workers split the items, but a service's limit still covers all of them together. If so, adding workers does not raise the number of calls a service will accept.

## Decide before you start

Write down your answers before Stage 1.

1. Who fills each role in the table, and how will you record that they did?
2. Which gates will you keep, and will a standing "continue" cover any of them?
3. What batch size and worker cap will you use?
4. What will you do when a service limits your calls?
5. Where will you keep hand-off documents and approval records?

Next, see [Platform requirements](platform-requirements.md). Stage numbers refer to the [Pipeline overview](pipeline-overview.md).
