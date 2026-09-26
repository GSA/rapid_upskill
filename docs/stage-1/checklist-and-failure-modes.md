---
title: "Stage 1 checklist and failure modes"
parent: "Stage 1 Knowledge acquisition"
nav_order: 11
status: "draft"
last_reviewed: "2026-09-24"
---

# Stage 1 checklist and failure modes

## Outcome

This page is a single place to work from when running all of [Stage 1](index.md), from framing the domain to closing the last gap. It does not repeat any sub-stage page's own conditions or failures; it links to them. Its own added value is two lists this guide keeps nowhere else: every Stage 1 gate in page order, and a short set of failure patterns that show up on more than one sub-stage.

## Checklist by sub-stage

Each row links to that sub-stage's own "Definition of done" and "Common failures" sections. Work through the pages in this order; a later sub-stage assumes the ones above it are done.

| Sub-stage | Definition of done | Common failures |
|---|---|---|
| S1.1 and S1.2, frame the domain and list the tasks | [Definition of done](frame-and-tasks.md#definition-of-done) | [Common failures](frame-and-tasks.md#common-failures) |
| S1.3, draft the blueprint | [Definition of done](blueprint.md#definition-of-done) | [Common failures](blueprint.md#common-failures) |
| S1.4a, search planning and execution | [Definition of done](search-planning-and-execution.md#definition-of-done) | [Common failures](search-planning-and-execution.md#common-failures) |
| S1.4b, screening and conversion | [Definition of done](screening-and-conversion.md#definition-of-done) | [Common failures](screening-and-conversion.md#common-failures) |
| S1.4c, injection screening | [Definition of done](injection-screening.md#definition-of-done) | [Common failures](injection-screening.md#common-failures) |
| S1.5a, concept extraction | [Definition of done](concept-extraction.md#definition-of-done) | [Common failures](concept-extraction.md#common-failures) |
| S1.5b, distillate and quote bank | [Definition of done](distillate-and-quote-bank.md#definition-of-done) | [Common failures](distillate-and-quote-bank.md#common-failures) |
| S1.6, knowledge items | [Definition of done](knowledge-items.md#definition-of-done) | [Common failures](knowledge-items.md#common-failures) |
| S1.7, concept map and prerequisite hierarchy | [Definition of done](concept-map-and-hierarchy.md#definition-of-done) | [Common failures](concept-map-and-hierarchy.md#common-failures) |
| S1.8, coverage and gaps | [Definition of done](coverage-and-gaps.md#definition-of-done) | [Common failures](coverage-and-gaps.md#common-failures) |

## Gates in order

A trimmed, page-ordered view of the [Stage 1 index](index.md#approvals)'s own Approvals table. That table stays the source of truth; read it for the human-roles gate kind and the basis label behind each row.

| After | What the person approves | Where it is defined |
|---|---|---|
| S1.1 | The boundary statement | [Approvals](index.md#approvals) |
| S1.3 | The weighted blueprint | [Approvals](index.md#approvals) |
| S1.4a | The search plan set, before any query runs | [Approvals](index.md#approvals) |
| S1.4a, the runner | What to do when the circuit breaker opens | [Approvals](index.md#approvals) |
| S1.4b and S1.4c | The selected sources, the flagged list and the blocked-document list | [Approvals](index.md#approvals) |
| S1.5 | Each batch of distillations | [Approvals](index.md#approvals) |
| S1.6 | A batch of sources' draft items | [Approvals](index.md#approvals) |
| S1.6 | The consolidated, deduplicated item set | [Approvals](index.md#approvals) |
| S1.7 | The concept map and hierarchy | [Approvals](index.md#approvals) |
| S1.8 | The expansion plan | [Approvals](index.md#approvals) |

## Failure patterns that recur

Each pattern below shows up more than once across Stage 1. The link goes to a page where a concrete instance is described in full; the pattern itself is not repeated there.

- **A check that passes on a small, synthetic sample but says nothing about a reader's own material.** A clean run of a sample script only shows that the script works on this guide's own data; see [S1.4c's tripwire note](injection-screening.md#why-this-way) and [S1.5b's quote-check limits](distillate-and-quote-bank.md#what-the-quote-check-does-and-does-not-do) for two stated instances.
- **A pause satisfied by a standing instruction to continue, which no longer shows that anyone looked.** See [Human roles, gates and batching](../human-roles-gates-and-batching.md#five-kinds-of-gate-in-the-reference-implementation) for the general point, and the [S1.5 batch-pause row](index.md#approvals) for where this guide flags it as a real risk rather than a formality.
- **A later step using an artifact before its own approval has actually landed.** [S1.4a](search-planning-and-execution.md#steps) requires the search plan set approved before any query runs; [S1.7](concept-map-and-hierarchy.md#steps) similarly holds the map and hierarchy for approval before [S1.8](coverage-and-gaps.md#steps) reads it. Skipping ahead defeats the point of the gate.
- **A cap or threshold that nothing enforces automatically, so a person has to remember to check it.** [S1.4a's own recall target](search-planning-and-execution.md#steps), [S1.7's relation-density band](concept-map-and-hierarchy.md#parameters), and [S1.8's expansion-loop cap](coverage-and-gaps.md#steps) are each a number this guide's own scripts do not stop the reader from exceeding; a person has to look. (The circuit breaker on S1.4a's own runner is the opposite case: it does stop the queue by itself, and only the decision of what to do next needs a person.)

## Before you start Stage 2

Confirm each of these exists and has a recorded approval before moving on:

- A dated boundary file and a task list ([S1.1 and S1.2](frame-and-tasks.md)).
- A blueprint that passes its check, with a weight rationale for every domain ([S1.3](blueprint.md)).
- Admitted sources: converted, checked, and scanned for hidden instructions ([S1.4a](search-planning-and-execution.md) through [S1.4c](injection-screening.md)).
- Canonical knowledge items, deduplicated across sources ([S1.6](knowledge-items.md)).
- A checked concept map and prerequisite hierarchy, with every concept's tier filled in ([S1.7](concept-map-and-hierarchy.md)).
- A gap list with a decision recorded for every open row: closed, deferred, or accepted as a known gap ([S1.8](coverage-and-gaps.md)).

Next: [Stage 2 Content development](../stage-2/index.md).
