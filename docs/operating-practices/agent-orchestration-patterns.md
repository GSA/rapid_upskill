---
title: "Agent orchestration patterns"
parent: "Operating practices"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-26"
stage: "OP"
prompts: ["P-OP-01"]
scripts: ["X-OP-05"]
---

# Agent orchestration patterns

## Outcome

This page states the session-level procedure an
[orchestrator](../glossary.md#orchestrator) follows underneath the
parameters [Human roles, gates and
batching](../human-roles-gates-and-batching.md) already publishes. It
covers what it reads before acting, how it decides a
[batch](../glossary.md#batch) is ready, how it dispatches and waits, how
it validates and merges a wave's results, and how it fails and recovers.
The procedure is cross-cutting. The [project
notes](../glossary.md#reference-implementation) describe it as a shared
execution layer that several stage-specific workflows are written on top
of, not a stage of its own.

## Where it fits

This page extends, and does not duplicate, [Human roles, gates and
batching](../human-roles-gates-and-batching.md). That page already
states the batch-size range, the worker-cap range, the five gate kinds,
and the one-paragraph shape of the mechanism: the orchestrator starts
several [subagents](../glossary.md#subagent) at once, up to the caps
already published. What follows is the layer underneath that paragraph,
read directly from the material behind it.

## Why this way

An orchestrating session carries no memory between sessions beyond what
it writes to disk. The order in which it reads, reconciles and
restates its own state before acting is what keeps two sessions of one
run from disagreeing about what is actually done.
In the material behind this page, an informal set of hand-written prompt
instructions already carried the same closing rules in substance: work
in capped batches, launch capped parallel workers, keep a hand-off
current. A more heavily instrumented format later emerged, once a
project's own coordination needs grow past what a plain prompt sequence
can hold safely. It reads those informal instructions and writes a
frozen, rule-bearing document from them.

Every step below carries one of the three [basis
labels](../stage-1/index.md#basis-labels) Stage 1's index defines.
Unless stated otherwise, each is `documented`, read directly from the
material this page draws on, not inferred or suggested by this guide.
The one exception is [X-OP-05](#scripts) itself. The completion-test
concept and the false-completion-signal lesson below are both
`documented`, but no script for this exact check was found in that
material, so the script is this guide's own `suggested` addition.

## Steps

| Step | Who | Basis |
|---|---|---|
| A person starts or continues a session on one step's own instructions; the session reads, in order, the governing document, the tracking file, the newest hand-off, and the step's own inputs | Person, then the orchestrator | documented |
| Reconcile the tracking file against the filesystem before computing what is ready; an item marked done whose output is missing, or fails its completion test, reverts to not-done | Orchestrator | documented |
| Write a short, dated restatement to a [hand-off file](../glossary.md#hand-off-document) before new work, checked against the previous restatement's own next step; a bare "continue where the last session left off" is disallowed | Orchestrator | documented |
| Group the ready items into one batch, sized to the item | Orchestrator | documented |
| Dispatch one worker per item as a single wave, briefing each with only its own bound inputs and an exact output path | Orchestrator | documented |
| Wait for each worker's own explicit completion notification before reading its output | Orchestrator | documented |
| Validate each result against a completion test; redispatch once on failure; do the item itself on a second failure | Orchestrator | documented |
| Decide accept, merge or remove for the whole wave, sometimes through a small deterministic script rather than an agent | Orchestrator, or a script | documented |
| Record the state change as one append-only step-log line | Orchestrator, or a script | documented |
| Close the step in one of a small fixed set of terminal states (fully verified; partially verified, with failing criteria named; blocked; escalated; or budget-exhausted); an empty to-do list is never treated as success | Orchestrator | documented |

Each step-log line holds a timestamp, the step, the state change and who
acted. [Run logging and dashboards](run-logging-and-dashboards.md) owns
this record's full schema; this page only touches the one event type the
two pages share.

## Two governance layers beyond the per-wave cap

Two further caps sit on top of the per-wave worker cap [Human roles,
gates and batching](../human-roles-gates-and-batching.md) already
publishes. Both are automated caps the orchestrator itself enforces,
never [gates](../glossary.md#gate) in this guide's sense, since neither
one pauses for a person's approval.

One layer serializes a single category of work. Per-item content
processing, such as reading or drafting from a bound input, still runs in
parallel waves, capped as already published. Outbound calls to an
external search or lookup service instead run strictly one at a time, in
one ordered queue, each finished before the next begins. A minimum
spacing separates calls, with an escalating cooldown after repeated
refusals.
Not every kind of repeated work should be parallelized; some categories
exist to respect a limit the orchestrator does not control.

The other layer is a total-running-agents ceiling, spanning every wave
and session in the run, on top of the per-wave cap. This guide treats
it as the same "capping at 10 in total" figure Human roles, gates and
batching already publishes, since the observed value falls inside that
already-published figure (inferred: the published page states the "10"
only as a bare number, and does not itself confirm the two describe the
same mechanism). Before every dispatch,
the orchestrator counts every agent currently running, including a
review agent and anything left from an earlier session. It dispatches
only when the running total plus the new wave stays under the ceiling
and under the per-wave cap. The count is logged again after every
dispatch; this ceiling takes precedence over any looser instruction
written elsewhere in the contract.

## The frozen governing document

The project notes call this document "the contract," matching the
glossary's own [orchestrator](../glossary.md#orchestrator) entry: the
orchestrator's own written rules for how its agents run the work, and for
the accept and merge decisions in particular. A **contract** is written
once, near a run's start, and held immutable afterward; nothing already
inside it is ever edited. A later lesson, such as either governance layer
above, is instead layered on as a separate, dated revision section around
the frozen block, never folded into it.

The reason is mechanical, not stylistic. At every session's start, the
orchestrator checks the tracking file's own copy of the contract's
protected constraints against the frozen block by comparing the two texts
directly, and halts on any mismatch. Editing the frozen block would break
that check on every future session, so an amendment has to live beside it
instead. A hash is used elsewhere in this same mechanism, for a different
purpose: tying a person's approval to one specific version of a
deliverable artifact, exactly as Human roles, gates and batching already
describes. The approval lapses once that artifact changes. The two
checks serve different ends: one compares text, the other computes a
hash, and each guards a different kind of drift.

This design has a real cost. A reader who trusts only the frozen block
misses any amendment recorded only around it. In two structurally similar
governing documents this page's own research compared, one had already
adopted the two governance layers above; the other, inspected at the same
time, had adopted neither. Nothing found shows whether that gap was later
closed. Read a frozen contract's own dated revision sections as part of
its current rule set, not only its opening block, for a run that has been
going for a while.

## Worked illustration

Take a neutral, invented task: a batch of four generic reference
documents needs a structural-consistency review, one worker per document.
The orchestrator reads the contract, the tracking file and the newest
hand-off. It reconciles that tracking file against the filesystem
(nothing here is done yet), and writes a fresh restatement naming this
review as the next action. It groups the four documents into one batch,
inside the published 3-to-8 range. It dispatches four workers as a
single wave, each briefed with only its own document and an exact output
path such as `outputs/doc-02.json`, following [P-OP-01](#prompts).

The orchestrator waits. Three workers send an explicit completion
notification promptly; the fourth's arrives later, and its output file
stays unread until it does, since a file appearing on disk is never a
signal on its own. Once all four have reported, the orchestrator
validates every result against the batch's own completion test: each
output must carry `document_id`, `status` and `findings`, all non-empty.
One file is missing its `status` field outright; the orchestrator
redispatches that item, with the validation failure attached, and accepts
the corrected result on the second try. With every item now valid, the
orchestrator decides accept for all four. It merges their findings into
the shared tracking file, records one step-log line per state change,
and closes the step fully verified before pausing for a person's
permission to start the next batch.

## Scripts

[X-OP-05 Completion signal
check](../scripts/op/x-op-05.md) checks a batch of worker output files
against the completion test from the illustration above: every file must
be valid JSON and must carry every required field, present and
non-empty. It never checks whether a value is actually correct, only
whether the completion signal itself is genuine, encoding the
false-completion-signal lesson in Common failures below. Run it from the
repository root:

```bash
python3 -B scripts/op/completion_signal_check.py \
    scripts/sample_data/git_basics_batch8/worker_briefs/outputs \
    scripts/sample_data/git_basics_batch8/worker_briefs/completion_test.json
```

```text
outputs=4 errors=0
```

Every file passes: four output files, no findings. A second folder keeps
the same four filenames but breaks two of them: one worker's file is
missing its `status` field outright, and another's `findings` list is
present but empty. These are two ways a file can exist, even look
complete, and still fail to prove the work behind it is finished.

```bash
python3 -B scripts/op/completion_signal_check.py \
    scripts/sample_data/git_basics_batch8/worker_briefs/outputs_broken \
    scripts/sample_data/git_basics_batch8/worker_briefs/completion_test.json
```

```text
missing-field: doc-02.json has no 'status'
empty-field: doc-03.json field 'findings' is empty
outputs=4 errors=2
```

The exit code is 1 whenever a finding is printed, 0 when every file is
clean, and 2 for a usage or input error, such as a missing folder or a
completion test with no `required_fields` list. See [Reading exit
codes](../stage-1/index.md#reading-exit-codes) on the Stage 1 index for
what an exit code means generally.

## Prompts

[P-OP-01 Draft a worker brief](../prompts/op/p-op-01.md) drafts one
dispatched worker's own brief from a ready item's id, task, bound input,
exact output path and required fields. This way the worker never has to
guess what finishing its own item actually means. It is written for this
guide
and has not been run against any model in this build; treat it as a
starting point and adapt it. The bound input it repeats inline is data,
never instructions, even where a sentence inside it is phrased as one.

## Artifacts and formats

- A governing document (the contract), described above. Its own
  contents: an objective statement, a domain-scope paragraph, a numbered
  list of protected constraints, a directory layout, an identifier and
  status vocabulary, a failure taxonomy, and the batching and hand-off
  rules, closed with a version tag. The session-entry checklist the
  Steps table follows is part of the same document.
- A tracking file: the per-step state table an orchestrator reconciles
  against the filesystem before computing what is ready, and rewrites
  after every wave.
- A hand-off file: the short, dated restatement written before any new
  work; [Hand-off documents and
  sessions](hand-off-documents-and-sessions.md) covers this artifact's
  own field shape in depth.
- A per-item worker output file, one per dispatched item, whose own
  output path doubles as its idempotency key: an item whose output
  already validates is never redispatched.

## Definition of done

- Every dispatched worker's output passes [X-OP-05](#scripts) before the
  orchestrator accepts it into the shared tracking file.
- Every state change, including a reopened item and a redispatch, has its
  own step-log line.
- The orchestrator, never a worker, has made every accept, merge and
  remove decision for the batch.
- A frozen contract's own dated revision sections, not only its opening
  block, have been checked before treating its rules as complete.

## Common failures

- **Length-cap gaming.** A worker briefed to keep its own report under a
  fixed word count spent its final effort compressing, in practice
  deleting, its own findings to fit. The adopted fix: never cap a
  worker's report file; cap only the short message it sends back as a
  pointer to that file. A length limit that is part of the actual
  deliverable, such as a fixed word count for a written definition, is
  unaffected, since that caps the product, not how much may be reported
  about it.
- **Parallel-search rate-limiting.** Running search or lookup calls in
  parallel against an external service triggered repeated throttling,
  severe enough to draw an extended block. The adopted fix is the
  serialization layer above: abandon per-wave parallelism for that one
  category of work for a strict one-call-at-a-time queue, leaving
  per-item content processing untouched.
- **False completion signal.** Treating a worker's output file merely
  existing, or being non-empty, as proof it had finished is unsafe, since
  a file can be read mid-write. The adopted fix: wait for the worker's
  own explicit completion notification before reading its output,
  encoded mechanically in [X-OP-05](#scripts) above.
- **A frozen contract going stale by design.** Because the governing
  document is never edited in place, a later lesson is recorded only
  around it, as dated addenda a reader can miss. See The frozen
  governing document above for the real gap this created.

## Adapting to your platform

- `llm`: drafts a worker's own brief, from
  [P-OP-01](../prompts/op/p-op-01.md); no other capability is needed to
  draft one.
- `shell`: runs [X-OP-05](#scripts); without it, read each worker output
  file by hand against the completion test's own required-fields list.
- `subagents`: dispatches a wave of workers at all; without it, an
  orchestrator does every item itself, one at a time, and the batch, wave
  and completion-test steps above collapse into a single-worker
  checklist.
- `human-approval`: covers every point in Where humans decide below.

## Where humans decide

- The accept, merge and remove decision after every wave, made by the
  orchestrator itself and never delegated to a worker.
- The pause for permission after every batch, a standing checkpoint that
  shows nothing if a person tells the agent in advance to keep going
  regardless.
- The hash-bound approval points named in the contract, such as after a
  named step or before a condensation cut, which lapse automatically if
  the approved artifact changes. These are a heavier kind of pause than
  the per-batch checkpoint above: a standing "continue" instruction
  never satisfies one, because each is tied to one specific version of
  an artifact, not to a point in time. The per-batch checkpoint above,
  by contrast, is satisfied by a standing "continue" instruction and is
  not tied to any file version. The published Human roles page does not
  draw this distinction, so it is worth stating here.

Next: [Run logging and dashboards](run-logging-and-dashboards.md).
