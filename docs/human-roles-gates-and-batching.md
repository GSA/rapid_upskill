---
title: "Human roles, gates and batching"
nav_order: 5
status: "draft"
last_reviewed: "2026-09-21"
---

# Human roles, gates and batching

This page covers who decides, where work pauses, and how work is sized. It describes the framework's design. Where it gives numbers, they come from the [reference implementation](glossary.md#reference-implementation), the project this guide draws on. They are that project's parameters, not rules for every project.

## The premise

The framework rests on one idea. AI does the volume work, such as drafting, [condensation](glossary.md#condensation) (shortening text) and linking related material. People keep the judgment calls, such as [blueprint](glossary.md#blueprint) design, expert review, [misconception](glossary.md#misconception) authoring and question ratings. This is a [human-in-the-loop](glossary.md#human-in-the-loop) design. The framework calls it an interpretation, not a measured result.

## What the framework says people do

Each role belongs to a [stage](glossary.md#stage). Stage numbers refer to the [Pipeline overview](pipeline-overview.md).

| Role | What it covers | Stage |
|---|---|---|
| Blueprint design and weighting | Framing the program's plan and weighting its parts | Stage 1 |
| Admitting evidence | Deciding which sources count as evidence | Stage 1 |
| Judging fit to the blueprint | Checking that drafted chapters match the blueprint | Stage 2 |
| Expert review | Experts check accuracy, make deeper checks and approve the result (Layer 2 of the [verification layers](glossary.md#verification-layer)) | Stage 3 |
| Misconception authoring | Naming the wrong ideas learners tend to hold | Stage 4 (per the figure in the Pipeline overview); sources also record them at Stage 1 |
| Graded-work policy | Instructors decide whether AI help is allowed on graded work; when it is not, the tutor's [integrity guardrail](glossary.md#integrity-guardrail) withholds full solutions and offers hints. | Stage 4 |
| Question ratings | Rating test questions | Stage 5 |
| Approval at gates | Deciding at each gate whether work goes on | All stages |

The table shows what the framework assigns, not what was done. In the project notes, expert review is specified, but no completed record of it was found. The notes show [agents](glossary.md#agent) writing the test questions, and no record shows a person writing the [misconception catalogs](glossary.md#misconception-catalog). They describe no step in which a person rates questions.

The coordinating [orchestrator](glossary.md#orchestrator) session is given the accept and merge decisions in the contract, the reference implementation's written rules for running each step. It is not a person. No record found is not evidence that something did not happen.

## Five kinds of gate in the reference implementation

A [**gate**](glossary.md#gate) is a checkpoint where a person approves before work continues. The project notes also use "gate" for automated script checks; this guide means a person's approval unless it says otherwise.

| Gate | When it stops the work | What you do |
|---|---|---|
| [Batch](glossary.md#batch) pause | After every unit of work in a batch is processed | Say whether to continue |
| Plan approval | After named planning steps, such as before condensation cuts | Approve the plan or reject it |
| Expansion-loop approval | When an expansion loop would run past 2 times | Approve another run or decline |
| Search cap decision | When the cap on searches runs out | Raise the cap, continue with what was found, or pause |
| Stop | When a required check fails or an approved file changes | Fix the cause; approve again if a file changed |

Three notes:

- If you tell the agent in advance to keep going after every batch, the pause no longer shows that anyone looked.
- In the reference implementation, an expansion loop may run at most twice without approval. That limit is one of its parameters. An expansion loop is a step that repeats to widen its results.
- An approval can be tied to one version of a file by a hash, a fingerprint of its contents. In the reference implementation, the planning-step approvals are tied this way and the other gates are not. A tied approval lapses when the file changes.

## Three batching practices

These are the reference implementation's parameters: project practice, not rules for every project.

1. Work in small batches. The reference implementation uses 3 to 8 units of work per batch, chosen by size, with a pause after each. A unit of work is one thing an agent handles at a time, such as one source.
2. Cap parallel workers. Caps differ by workflow, from about 4 up to 9 workers, with one workflow capping at 10 in total; the main step contract uses waves of 6. A wave is a group of workers started together. The agent waits for the wave to finish and checks its results before it starts the next.
3. Keep a [hand-off document](glossary.md#hand-off-document) current (in the reference implementation, after every batch). It is a short file that lets a fresh session continue the task. Start a new session when the [context window](glossary.md#context-window), the amount of text a model can take in at once, runs low.

## Parallel workers and rate limits

In the reference implementation, the orchestrator starts several [subagents](glossary.md#subagent) at once, up to the caps above. Outside services can also apply a [rate limit](glossary.md#rate-limit). Suggested: read the Risks section of [Platform requirements](platform-requirements.md) before you raise a worker cap.

## Decide before you start

Write down your answers before Stage 1.

1. Who fills each role in the table, and how will you record that they did?
2. Which gates will you keep, and which will you leave for a person to approve each time?
3. What batch size and worker cap will you use?
4. What will you do when a service limits your calls?
5. Where will you keep hand-off documents and approval records?

Next: [Platform requirements](platform-requirements.md).
