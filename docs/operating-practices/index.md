---
title: "Operating practices"
parent: "Beyond the five stages"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-26"
stage: "OP"
---

# Operating practices

## Outcome

A reader understands five practices that apply across every
[stage](../glossary.md#stage) of the framework, owned by none of them.
Each is a piece of how a run is actually operated day to day. One
covers how an [orchestrator](../glossary.md#orchestrator) dispatches
and recovers. One covers how a run's own progress is logged and
rendered. One covers how a claim or a citation is traced back to where
it came from. One covers how untrusted text is kept from being read as
an instruction. One covers how work is handed from one session, or one
agent, to another.

## Where it fits

None of the five pages this page links to belongs to the five-stage
framework or to the parallel [certification-alignment](../certification-alignment.md)
and [Delivery](../delivery/index.md) workstreams. Each sub-page
extends, and does not duplicate, an already-published page. Agent
orchestration extends [Human roles, gates and
batching](../human-roles-gates-and-batching.md). Run logging and
dashboards is new material with only a light connection to that same
page. Provenance and verification extends [Stage
1](../stage-1/index.md) and [Stage 3](../stage-3/index.md).
Prompt-injection screening extends [S1.4c](../stage-1/injection-screening.md)
and [S4.6](../stage-4/guardrails.md). Hand-off documents and
sessions extends the glossary's own [hand-off
document](../glossary.md#hand-off-document) entry and that same Human
roles page. Read a sub-page's own "Where it fits" section for the
exact relationship. This page only names the five and says how rich or
thin each one's own source material turned out to be.

## Why this way

A cross-cutting practice, by definition, does not belong to one
stage's own page. Five pages, gathered under one parent here, keep
each practice separately linkable and separately sized to its own
material. This spares a thin topic from padding out a stage page it
does not belong to, and spares a rich topic from being compressed past
what its own detail deserves.

## Five practices, and how rich each one's own material is

- [Agent orchestration patterns](agent-orchestration-patterns.md) —
  the session-level procedure an orchestrator follows: what it reads
  before acting, how it dispatches and waits, how it validates and
  merges a wave's results, how it fails and recovers. **Rich**: this
  page goes considerably deeper than what [Human roles, gates and
  batching](../human-roles-gates-and-batching.md) already publishes.
- [Run logging and dashboards](run-logging-and-dashboards.md) — a
  step log, a run record, and a static dashboard that together turn a
  run's own progress into a structured, shareable record. **Rich**: a
  real, fully-designed mechanism this guide's own research found
  mostly undocumented anywhere else.
- [Provenance and verification discipline](provenance-and-verification.md)
  — a citation-key check, a document-derivation-chain concept, and a
  short list of integrity rules for tracing a claim or a number back
  to where it came from. **Thin**: mostly a cross-reference to what
  [Stage 1](../stage-1/index.md) and [Stage 3](../stage-3/index.md)
  already cover in full, plus a handful of rules those two pages do
  not.
- [Prompt-injection screening, as a cross-cutting
  practice](prompt-injection-screening.md) — one rule, already applied
  in three separate places under three different names, named once as
  a single principle. **Thin**: a naming and cross-reference exercise,
  with no new mechanism of its own.
- [Hand-off documents and sessions](hand-off-documents-and-sessions.md)
  — two related but distinct practices. One is writing a structured
  record for a fresh session to continue a task. The other is a
  subagent signalling that one delegated unit of work is finished
  inside a single run. **Mixed**: the first sense is a real, deeper
  mechanism than the already-published pages state; the second is a
  different, real mechanism under the same word, found separately.

## What is documented versus suggested

Every rule and script default on these five pages carries its own
[basis label](../stage-1/index.md#basis-labels), stated on its own
page. Two scripts are worth naming here because their own gap is
unusual: [X-OP-02](../scripts/op/x-op-02.md) (run record check) and
[X-OP-04](../scripts/op/x-op-04.md) (hand-off completeness check).
Both check a mechanism that the underlying material describes in full
but never backed with any script at all. [X-OP-05](../scripts/op/x-op-05.md)
(completion signal check, on agent orchestration patterns) is the same
situation: a documented lesson, a `suggested` script written for this
guide to encode it, not a stand-in for a broken real one.
[X-OP-03](../scripts/op/x-op-03.md) (citation key check) instead
replaces short, unpackaged text-processing one-liners with one safe,
tested script that does the same bidirectional check.

## Artifacts across these five pages

- A governing document (the contract), a tracking file, a hand-off
  file, and a per-item worker output file, all described on [Agent
  orchestration patterns](agent-orchestration-patterns.md).
- A step log, a run record, and a dashboard, all described on [Run
  logging and dashboards](run-logging-and-dashboards.md).
- A reference list with evidence annotations, described on
  [Provenance and verification
  discipline](provenance-and-verification.md).
- Nothing new on [Prompt-injection
  screening](prompt-injection-screening.md); its own artifacts belong
  to the pages it cross-references.
- A hand-off document with five structured fields, described on
  [Hand-off documents and
  sessions](hand-off-documents-and-sessions.md). This is distinct from
  the tracking file named on the orchestration page above. It is the
  same practice as that page's own hand-off file; the two pages
  cross-reference one artifact, not two.

## First actions for a new team

Suggested:

- Read [Agent orchestration patterns](agent-orchestration-patterns.md)
  and [Run logging and dashboards](run-logging-and-dashboards.md)
  first if your own team is already running parallel agents; both
  describe real, adoptable mechanisms in depth.
- Read [Hand-off documents and
  sessions](hand-off-documents-and-sessions.md) before your own team's
  first session rotation; the two-sense distinction it draws is easy
  to blur without a page stating it plainly.
- Treat [Provenance and verification
  discipline](provenance-and-verification.md) and [Prompt-injection
  screening](prompt-injection-screening.md) as short reads. Neither
  introduces a large new mechanism. Both point back to fuller
  material your own team may already be applying without a name for
  it.

Next: [Agent orchestration patterns](agent-orchestration-patterns.md).
