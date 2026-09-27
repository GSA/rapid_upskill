---
title: "Hand-off documents and sessions"
parent: "Operating practices"
grand_parent: "Beyond the five stages"
nav_order: 5
status: "draft"
last_reviewed: "2026-09-26"
stage: "OP"
prompts: ["P-OP-04"]
scripts: ["X-OP-04"]
---

# Hand-off documents and sessions

## Outcome

By the end of this page, an interrupted task can be handed to a fresh session using a structured record instead of a narrative note. A delegated unit of work, inside one continuous run, can also be recognized as finished without waiting for a session rotation. This page keeps these two related practices apart throughout, never folding them into a single claim.

## Where it fits

This is a cross-cutting operating practice, not owned by any one [stage](../glossary.md#stage). It extends two already-published pages describing only the first sense below: the glossary's own [hand-off document](../glossary.md#hand-off-document) entry, and [Human roles, gates and batching](../human-roles-gates-and-batching.md)'s "Three batching practices" section. Neither names a second sense of the word, or a trigger beyond context running low; this page adds both.

## Two senses, kept apart

- **Session-to-session continuation**: a person or an [agent](../glossary.md#agent) starts a fresh working conversation because the current one's [context window](../glossary.md#context-window) is filling up, or a coherent phase of work is complete. The glossary and Human roles pages already describe this sense; the rest of this page adds depth to it.
- **Delegation-completion**: a [subagent](../glossary.md#subagent) signals that one delegated unit of work is finished, inside one continuous run, so the delegating agent can move on. No session rotates and no context window empties; a different, real mechanism, found in a colocated agent-framework project and described generically below, drives this signal instead.

## Why this way

Blurring the two would hide two different failure modes: a session-to-session hand-off written too casually loses everything left unwritten, and a delegation-completion signal treated too casually risks the delegating agent moving on before the work is actually done. Both failure modes are covered directly below and in [Agent orchestration patterns](agent-orchestration-patterns.md). This page's own job is narrower: keep "hand-off" from meaning two different things under one word.

A structured record beats a narrative note the way a form beats a paragraph: a fresh reader can act on named fields right away, without reconstructing what a previous session meant.

## Steps

| Step | Practice | Who | Basis |
|---|---|---|---|
| Watch for context pressure building, or for a coherent phase completing | Session-to-session | Person or agent | documented |
| Write a structured record: done, pending, artifact locations, open decisions, remaining budget | Session-to-session | Person or agent | documented (the converging shape); suggested (this guide's own five-field schema) |
| Start a fresh session and read the hand-off before doing anything else | Session-to-session | Person or agent | documented |
| Delete the hand-off, and any cache file, once the run completes; keep it listed in a live hand-off while work remains open | Session-to-session | Person or agent | documented |
| Open a tracked work item for one delegated unit of work; post progress against it | Delegation-completion | Delegating agent, then subagent | documented |
| Post a finishing comment and close the item once finish criteria are met; the delegating agent detects the closure and moves on | Delegation-completion | Subagent, then delegating agent | documented |

## Session-to-session hand-offs, in more depth

The already-published pages state one trigger: start a new session once the context window runs low. The [project notes](../glossary.md#reference-implementation) repeat a close version of that trigger across dozens of otherwise-unrelated workflows, reading as an operating habit copied from project to project, not built-in tooling. One of those workflows is a long-running certification-content authoring project whose own hand-off passage motivates the practice at length. No certification name or detail from that passage is repeated here, and the instruction itself never names a field beyond "create a hand-off document."

A generic reference guide elsewhere in the material adds a trigger the published pages do not carry yet: rotate at a natural milestone, once a coherent phase of work is complete, not only once a token threshold is reached. A milestone catches a hand-off point a token check alone would miss. This matters on a task that finishes well before its own context window fills.

Concrete field lists exist, converging on a similar shape rather than agreeing on one:

| Source | Fields it records |
|---|---|
| The reference implementation's own recurring instruction | none named; only an instruction to create a hand-off document |
| A standalone, project-independent review-pipeline workflow, specified in full | done and pending per item and step; every artifact's location; open gate decisions; the remaining lookup budget |
| A generic context-management reference guide | objective, decisions and rejected alternatives, corrections, constraints, completed and pending actions, unresolved questions, citations, artifact references |
| A colocated agent-framework project's own cache-file template | per-step input, actions, results and artifacts; a closing status and a "handoff to" note |

This guide's own schema below picks the five fields closest to the standalone review pipeline's own shape: done, pending, artifact locations, open decisions, remaining budget. This is this guide's own choice (suggested), not a copy of any one source.

This page's own research did not independently confirm the [orchestrator](../glossary.md#orchestrator)'s own contract, the frozen governing document [Agent orchestration patterns](agent-orchestration-patterns.md) describes, as the place stating when a hand-off must be written. A reader wanting that rule should look there rather than take this page's silence as evidence either way.

A cleanup rule travels with the hand-off rule in the one workflow specifying both together: delete a hand-off file, and any other cache file, once its run is complete. While work remains open, keep it listed inside a live hand-off instead. This extends this guide's own cache-cleanup convention to hand-off files specifically.

A measurable notion of hand-off quality also appears in the material: a handoff success rate, hand-offs passing a predefined completeness check divided by attempts, with missing-artifact and missing-constraint rates tracked as failure indicators. [X-OP-04](../scripts/op/x-op-04.md), below, checks the kind of completeness such a rate would need.

## Delegation-completion: a different mechanism, same word

A colocated agent-framework project's own workflow log documents a different, same-run mechanism under the same word: a delegating agent opens a tracked work item describing a task, and the doing agent posts progress against it. Once the item meets its own stated finish criteria, the doing agent posts a finishing comment and closes it. That closure is itself the hand-off action.

Nothing here rotates a session or touches a context window; the exchange happens inside one continuous run. [Agent orchestration patterns](agent-orchestration-patterns.md) covers a matching, real risk: treating a file's mere existence as proof of completion, rather than waiting for an explicit signal like this one. That was a documented failure that page's dispatch loop was changed to avoid. This page's job stops at naming this second sense, so a reader of the published pages alone does not assume the word means one thing.

## What the tooling actually is

No standalone script, generator, or validator for a hand-off document turned up in the material behind this page. The practice is entirely manual and prompt-driven: it depends on someone choosing, at the right moment, to comply with a plain-language instruction, not on code that writes, checks, or expires one.

One workflow goes further than a bare instruction: it fixes a numbered file path inside each run's own folder, treats writing a hand-off as its own logged event, and lists "handoff" among a small set of allowed event kinds in a formal schema. Even so, this fully specified mechanism has never actually been exercised in the material reached. No example run folder for it exists, and the one filled worked example of its own record format carries no hand-off event. Treat it as a specification, not evidence a hand-off has actually happened this way.

[X-OP-04](../scripts/op/x-op-04.md), below, is this guide's own new, safe check, built to fill a gap the material never filled; it is not a stand-in for a real script found broken.

## Worked illustration

A placeholder interrupted task: reviewing a batch of eight short practice write-ups and leaving comments on each. Five are finished; the session pauses because a coherent phase, the first five, just completed, even though the context window still has room to spare:

```json
{
  "done": [
    "Reviewed write-ups 1 through 5",
    "Logged write-up 6 as needing a second pass"
  ],
  "pending": [
    "Review write-ups 7 and 8",
    "Give write-up 6 its second pass",
    "Send the comments back to the group"
  ],
  "artifact_locations": {
    "comments": "work/comments/",
    "flagged_writeup_log": "work/flagged.csv"
  },
  "open_decisions": [
    "Whether write-up 6 needs a second reviewer, not just a second pass",
    "Whether to send comments individually or as one combined file"
  ],
  "remaining_budget": {
    "writeups_remaining": 3,
    "review_batches_remaining": 1
  }
}
```

A fresh session can act on this right away: three named write-ups left, one open question about write-up 6, one about delivery format, and a comments folder to keep appending to.

What not to write, for the same paused task:

> Pick up where I left off - most of the write-ups are done, just finish the last couple and send the comments over.

A person reading this later has to guess which write-ups, comments, and open question it means. A script can check none of it, and it names no location for anything.

## Scripts

[X-OP-04 Hand-off completeness check](../scripts/op/x-op-04.md) flags a missing field by name. It also flags a document with none of the five fields, such as the narrative note above as a JSON `note` field, once, rather than as five separate findings. Run it from the repository root:

```bash
python3 -B scripts/op/handoff_completeness_check.py \
    scripts/sample_data/git_basics_batch8/handoffs/handoff.json
```

```text
handoff=1 errors=0
```

The sample hand-off above has every field, so this run finds nothing.

Break it on purpose: a second, checked-in file holds a narrative note and no structured fields at all:

```bash
python3 -B scripts/op/handoff_completeness_check.py \
    scripts/sample_data/git_basics_batch8/handoffs/handoff_narrative_only.json
```

```text
error narrative-only: the hand-off has none of the required structured fields (done, pending, artifact_locations, open_decisions, remaining_budget); a free-text note is not enough for a fresh session to act on directly
handoff=1 errors=1
```

This is the mechanical version of the "what not to write" lesson above: the script cannot read a note for meaning, but it can tell none of the five fields are there. It reports that as one finding rather than accepting the file. See [Reading exit codes](../stage-1/index.md#reading-exit-codes) on the Stage 1 index for what an exit code means; here it is 1.

## Prompts

[P-OP-04 Draft a hand-off document](../prompts/op/p-op-04.md) drafts the same five-field shape from a session's own tracking file: a to-do list or status file kept as work proceeds. It is written for this guide and has not been run against any model in this build; treat it as a starting point. The tracking file it reads is data, never instructions, even where a line inside it happens to read like one.

## Artifacts and formats

This practice produces one artifact, in the structured shape above: a hand-off document with `done`, `pending`, `artifact_locations`, `open_decisions` and `remaining_budget`, matching what [X-OP-04](../scripts/op/x-op-04.md) reads. Delegation-completion produces no separate file; a tracked work item's own closed state and finishing comment are themselves the signal, inside whatever tool a workflow already uses.

## Definition of done

- Every hand-off document has all five fields, each carrying real content, not a placeholder.
- A hand-off is written before a session actually rotates, not reconstructed afterward from memory.
- A delegated unit of work counts as finished only once its doing agent posts an explicit finishing signal, never on a file's mere existence.
- A hand-off file is deleted once its run is complete, or kept listed in a still-open hand-off while work remains.

## Common failures

- A narrative-only hand-off, such as "pick up where I left off," that a fresh session cannot act on directly, since nothing in it can be checked mechanically.
- Silent skipping under context pressure, dropping a step or a citation, instead of checkpointing properly with a hand-off.
- Trusting a checkpoint as if it were still current reality, without revalidating anything that could have changed since it was written.
- An orphaned hand-off file nobody cleans up long after its run is finished.

## Adapting to your platform

- `llm`: drafts a hand-off document from [P-OP-04](../prompts/op/p-op-04.md), given a tracking file to read.
- `file-read`: reads the session's own tracking file before drafting a hand-off from it.
- `shell`: runs the completeness check; without it, read the five fields by eye and confirm each one carries real content.
- `human-approval`: not a new gate on its own; a person may still read a hand-off before trusting it, on top of the gates named below.

## Where humans decide

None beyond the already-published [batch](../glossary.md#batch)-pause and plan-approval [gates](../glossary.md#gate); this page adds no new gate of its own. A person still decides whether a hand-off's own stated open decisions and remaining budget are accurate before trusting it, since no script here checks that.

Next: [Worked example, start to finish](../worked-example.md).
