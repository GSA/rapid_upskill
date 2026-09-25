---
title: "S1.8 Coverage and gaps"
parent: "Stage 1 Knowledge acquisition"
nav_order: 10
status: "draft"
last_reviewed: "2026-09-24"
stage: "S1"
sub_stage: "S1.8"
prompts: []
scripts: ["X-S1-10"]
---

# S1.8 Coverage and gaps

## Outcome

At the end of this sub-stage you have a gap list naming every
[blueprint](../glossary.md#blueprint) objective this guide's own bar
finds under-supported. For each gap a person chooses to close, you
also have one more targeted round of search, screening and extraction.
A person still decides which gaps matter and when coverage is good
enough to move on; the script only points at where to look.

## Where it fits

This sub-stage takes in the blueprint from
[S1.3 Draft the blueprint](blueprint.md) and the concept map and
[prerequisite hierarchy](../glossary.md#prerequisite-hierarchy) from
[S1.7 Concept map and prerequisite hierarchy](concept-map-and-hierarchy.md).
It loops back into
[S1.4a Search planning and execution](search-planning-and-execution.md)
for a closing round on each gap a person chooses to close. Otherwise,
it hands the admitted [knowledge base](../glossary.md#knowledge-base)
on to the planned later stages, once a person decides coverage is
good enough to move on.

## Why this way

Checking coverage against the blueprint, rather than reading the
material and guessing, is what lets a small gap surface before it
becomes a chapter with nothing to teach from.
[The project notes](../glossary.md#reference-implementation) treat a
gap as a judgment call across several signs at once: too few
independent sources, an unresolved contested point, only low-quality
material, or a stated evidence gap, among others. No single
source-count number appears there. This guide's script checks one of
those signs only, the source count recorded in each objective's own
`supported_by` list, because that is the one a small program can check
by counting rather than judging. The rest still need a person's read
of the gap list.

The concept map and hierarchy from S1.7 also give a closing round a
broader query to try. When the objective's own wording already ran
dry, the project notes widen the next query to a parent concept in the
hierarchy rather than only repeating the same text.

## Steps

A **closing round** is this guide's name for one targeted pass back
through [S1.4a](search-planning-and-execution.md) to
[S1.6](knowledge-items.md), scoped to a single gap, rather than a fresh
pass over the whole blueprint.

| Step | Who | Basis |
|---|---|---|
| Run the gap check against the blueprint | Script | suggested |
| Read the gap list and decide which gaps to close now, later, or not at all | Person | documented |
| Scope a new search plan to one objective, reusing [the search-plan prompt](search-planning-and-execution.md#prompts) | Agent | documented |
| Approve the new plan | Person | Plan approval; the same gate as [S1.4a](search-planning-and-execution.md) |
| Run the closing round through S1.4a to S1.6 again | Script and agent | documented |
| Decide whether to run another round | Person | Expansion-loop approval |

Running the gap check as a script is this guide's own suggestion. The
project notes describe gap-finding and the closing round as a person
and an agent judging the concept map and the knowledge-item records
together, not as an automated check. Reading the gap list, scoping a
new plan and running the closing round are documented in the project
notes' own expansion procedure; deciding whether to run another round
follows the loop cap below.

## Parameters

These numbers set how far one gap-driven expansion can go before a
person must approve it again.

| Parameter | Value used in this guide | Basis |
|---|---|---|
| Gap threshold (`--min-sources`) | flag an objective with fewer than 1 supporting source | suggested; the project notes flag a gap on several criteria together, with no single source-count number; this guide's script checks the source count alone, with its own lower default sized for a small program. Calibrate your own bar to your program's size. |
| Expansion-loop cap | at most 2 closing rounds without a person's explicit approval to run a third | the reference implementation's parameters; see [Expansion-loop approval](../human-roles-gates-and-batching.md#five-kinds-of-gate-in-the-reference-implementation) for what to do once the cap is reached |
| Re-query budget | caps how many of [S1.4a](search-planning-and-execution.md)'s original plan queries may be reissued in one closing round | the reference implementation's parameters; this sits alongside S1.4a's own per-plan query cap and retry limit, not in place of either one |

## Artifacts and formats

This sub-stage produces a gap list and, for each gap closed, a new
closing round's own artifacts.

- **Gap list**: one row per flagged objective, holding the objective
  id, why it was flagged, and its status (open, closed, or accepted as
  open). Kept by hand from the script's printed lines, the same way
  [S1.4a](search-planning-and-execution.md#artifacts-and-formats)'s
  query log is kept by hand from its runner; no script here writes it
  to a file.
- **Closing-round search plan and outputs**: the same formats
  [S1.4a](search-planning-and-execution.md#artifacts-and-formats)
  already defines (search plan, manifest, candidate record), produced
  again for one objective.

For example, the row for the running example's own flagged objective
might read: objective `D4.2`, flagged because the gap check found 0
supporting sources against a bar of 1, status open. That status stays
open until a closing round finds a source, or a person accepts the
gap as open.

## Prompts

S1.8 adds no new prompt. Closing a gap reuses
[S1.4a's search-plan prompt](search-planning-and-execution.md#prompts),
scoped to the one objective with the gap. The project notes reuse
their own search-and-screen steps unchanged for an expansion round,
rather than defining a second procedure. Draft the new plan with that
prompt, list its anchors, and carry it through the same approval and
run steps [S1.4a](search-planning-and-execution.md) already describes.

## Scripts

[X-S1-10 Gap check](../scripts/s1/x-s1-10.md) counts the entries in
each objective's `supported_by` list and prints one line for every
objective below the minimum. It never reads a blueprint's weights, ids
or cognitive levels; [the blueprint check](blueprint.md#scripts)
already does that. A domain or an objective that is not well formed is
skipped here, not reported. Run the blueprint check first to catch
that kind of problem. Run the gap check from the repository root, on
the running example's blueprint:

```bash
python3 -B scripts/s1/gap_check.py scripts/sample_data/git_basics/blueprint.json
```

```text
gap D4.2: 0 source(s), need at least 1
objectives=12 gaps=1
```

At the default bar, fewer than one supporting source, only `D4.2` is
flagged: the recovering-a-lost-commit objective the running example
planted with no source at all. The summary line counts every
objective the script read and every gap it found. Exit code 0: a gap
list is information a person reads, not a failure of the script
itself.

Raising the script's own bar to two sources shows what a stricter bar
finds on the same data, as a demonstration of the flag, not a claim
about any other program's scale:

```bash
python3 -B scripts/s1/gap_check.py scripts/sample_data/git_basics/blueprint.json --min-sources 2
```

```text
gap D1.1: 1 source(s), need at least 2
gap D1.3: 1 source(s), need at least 2
gap D2.1: 1 source(s), need at least 2
gap D2.2: 1 source(s), need at least 2
gap D2.3: 1 source(s), need at least 2
gap D3.1: 1 source(s), need at least 2
gap D3.3: 1 source(s), need at least 2
gap D4.1: 1 source(s), need at least 2
gap D4.2: 0 source(s), need at least 2
objectives=12 gaps=9
```

Every objective with only one source, not only the one with none, is
now a gap; the objective count stays the same, since that counts what
the script read, not what it flagged. Set `--min-sources` back to the
default, or leave it unset, once you are done checking a bar's effect.
A program's real bar should match its own material, judged on its own
terms; it should not stay at a value chosen only to show the flag.

## Definition of done

- The gap check runs against the approved blueprint with no usage
  error.
- Every flagged objective has a person's decision recorded: close now,
  close later, or accept as open.
- Every closing round's new plan is approved before any query runs,
  the same gate as [S1.4a](search-planning-and-execution.md).
- No more than two closing rounds have run without a person's explicit
  approval for a third.
- A person has decided, in plain words, that coverage is good enough
  to move on, or that work continues.

## Common failures

- A gap that stays open because no source exists to fill it: record
  that plainly rather than fabricating a fill or quietly dropping the
  objective. Spot it by an objective still flagged after more than one
  closing round with no new candidate found.
- An expansion round that only turns up near-duplicates of what the
  knowledge base already holds: recall does not rise, even though the
  query count does. Spot it by a closing round's manifest showing
  every match already in the candidate list before the round began.
- A loop-cap breach nobody notices, because nothing enforces the cap
  automatically: a person still has to check how many closing rounds
  have already run before approving another. Spot it only by reading
  the approval record; the script itself does not track how many
  rounds have run.

## Adapting to your platform

- `llm`: drafts the new, gap-scoped search plan from the same prompt
  [S1.4a](search-planning-and-execution.md) uses.
- `web-search`: runs the closing round's queries; without it, look
  them up by hand as
  [S1.4a](search-planning-and-execution.md#scripts) already describes.
- `shell`: runs the gap check; without it, count each objective's
  `supported_by` entries by hand against the same bar.
- `human-approval`: reads the gap list, approves the new plan, and
  decides whether to run another closing round.

## Where humans decide

- Which gaps to close now, which to leave for later, and which to
  accept as open.
- Approval of each closing round's new plan, before any query runs.
- Whether to run another closing round past the loop cap, or stop
  there.
- When coverage is good enough to move on to the planned later stages.

Next: [Stage 1 checklist and failure modes](checklist-and-failure-modes.md).
