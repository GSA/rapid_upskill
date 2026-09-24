---
title: "S1.4a Search planning and execution"
parent: "Stage 1 Knowledge acquisition"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-22"
stage: "S1"
sub_stage: "S1.4a"
prompts: ["P-S1-04"]
scripts: ["X-S1-02", "X-S1-03"]
---

# S1.4a Search planning and execution

## Outcome

At the end of this sub-stage you have an approved search plan set, a
deduplicated **candidate** list (a search result recorded for a person to
judge; being found is not the same as being admitted), and a manifest of
every query that ran. Nothing is downloaded here; that starts in
[S1.4b](screening-and-conversion.md).

## Where it fits

This sub-stage takes in the weighted objectives from
[S1.3 Draft the blueprint](blueprint.md). It hands on the deduplicated
candidate list and the query manifest to
[S1.4b Screening and conversion](screening-and-conversion.md).

## Why this way

A plan approved before any query runs keeps search spending inside a
person's decision, not an agent's. Two ideas guide what happens next, in
this order. First, search calls to one service run one at a time, in this
guide's runner (below); see
[Platform requirements](../platform-requirements.md#risks-to-plan-for)
(Risks) for why. Second, once candidates exist, subagents can grade their
abstracts in waves; this page sets no wave size or worker cap of its own
(see
[Human roles, gates and batching](../human-roles-gates-and-batching.md#three-batching-practices)
for both).

This page uses the documented and suggested
[basis labels](index.md#basis-labels) defined on the Stage 1 index. Most of
the plan-and-queue method is documented in
[the project notes](../glossary.md#reference-implementation); running the
queue as a script, and the web-address rule used when deduplicating, are
this guide's own suggestions. The project notes plan search per blueprint
section; this guide's sample prompt and script plan per objective instead
(see the plan-count row below for what that changes).

## Steps

An **anchor** is a document already known to be relevant that a plan's
queries should find; a quoted phrase is not an anchor. A **query cluster**
is a named group of related queries inside one plan, run in the plan's own
order. A **circuit breaker** stops the queue after too many queries fail
in a row, so a person can look before more calls happen.

| Step | Who | Basis |
|---|---|---|
| Draft one plan per blueprint objective with P-S1-04 | Agent | documented |
| List anchors for each plan, from a tool or a person; never invent one | Person | documented |
| Check the plan against its anchors on a small test set | Script or person | documented |
| Approve the plan set before any query runs | Person | documented |
| Run the queries one at a time with `run_queue.py` | Script | suggested |
| Read the manifest after each query | Person or agent | documented |
| Deduplicate with `dedupe_candidates.py` | Script | documented |
| Decide what to do when the breaker opens | Person | suggested |

Checking a plan against its anchors is documented; aim for **recall**
(the share of a plan's expected anchors that its queries actually find)
of 0.8 or more within two revisions (a parameter). Running the queue as a script
is this guide's own suggestion, since the notes describe a one-at-a-time
queue without naming a tool. Deduplicating candidates by identifier first
is documented; the web-address rule and the title-author-year rule that
follow it are both this guide's own choice, offered as starting values
to calibrate on your own material.

## Parameters

The first four rows are limits a person tracks across a blueprint's whole
set of plans; `run_queue.py` enforces only the per-plan query cap.

| Parameter | Value used in this guide | Basis |
|---|---|---|
| Plans for one blueprint section | at most 8 | the reference implementation's parameters; at this guide's finer, per-objective grain, treat 8 as a starting cap and raise it for a blueprint with many objectives |
| Queries in one plan (`query_cap`) | at most 10 | the reference implementation's parameters |
| Queries across all plans | at most 60 | the reference implementation's parameters |
| Queries per search **venue** (one search service or site) | at most 5; going over needs a written reason | the reference implementation's parameters |
| Query text and result counts | quote a multi-word phrase, or an unquoted, over-broad query floods the results; this guide's script does not enforce a result-count band | documented; the notes give three disagreeing bands (5-60; 15-60; "over 200 is too many"), so judge match counts yourself |
| Gap between calls (`--min-gap`) | 3 seconds | a starting value chosen for this guide |
| Retries after a temporary failure (`--retries`) | 2 | the project notes disagree: one place caps retries at 2, a client library in the same notes retries up to 5, and wait schedules differ; this guide keeps 2 |
| Wait before a retry (`--wait`, `--max-wait`) | 5 seconds, doubling each retry, up to 60 seconds | starting values chosen for this guide |
| Circuit breaker (`--breaker`) | 2 consecutive exhausted queries | the reference implementation's parameters |

## Artifacts and formats

- **Search plan** (JSON): `plan_id`, `objective_id`, `objective_text`,
  `query_cap`, a list of `anchors` (each an `anchor_id`, a `title`, and an
  optional `identifier`), and a list of `clusters` (each a `cluster` name
  and a list of `queries`, each a `query_id` and `text`).
- **Query log**: a table kept by hand from the plan and the manifest, one
  row per query: plan, cluster, query id, query text, filters, result
  count, anchors expected, anchors hit, status, notes. No script here
  writes it; it simplifies a richer log the project notes describe.
- **Manifest** (JSON Lines, one line per finished query, in this key
  order): `query_id`, `start`, `finish` (seconds since the run began),
  `attempts`, `matches`, `new_candidates`, `stage` (always `listed`),
  `state`, `anchors_expected`, `anchors_hit`. `state` is one of `done` (at
  least one match), `empty` (zero matches, still finished, not a
  failure), `failed` (every attempt exhausted), `blocked` (the service
  refused outright; no retry), or `breaker_open` (this query's failure
  opened the breaker; the run stops after this line).
- **Candidate record**: `title`, `url`, `year`, and the optional fields
  `identifier`, `authors`, `summary`, `source_type`.

## Prompts

[P-S1-04 Search plan for one learning objective](../prompts/s1/p-s1-04.md)
drafts one plan's clusters and queries from the objective text and a list
of known anchors, treating the anchor list as data, never as
instructions, since anchors can come from a tool rather than a person. It
is written for this guide and not run against any model in this build;
treat it as a starting point and adapt it.

## Scripts

[X-S1-02 Deduplicate search candidates](../scripts/s1/x-s1-02.md) groups
candidate records that likely describe the same document and keeps the
fullest one from each group. Run it from the repository root on the mock
search index, with a duplicate title and an old, unrelated record on
purpose:

```bash
python3 -B scripts/s1/dedupe_candidates.py \
    scripts/sample_data/git_basics_stage1/search/mock_index.json \
    --min-year 2020
```

```text
merge: kept 'Branches are just names' dropped 'branches are just names' rule=title-author-year
flag: 'Quick cheat sheet: sending and getting changes' too_old (year=2019 < 2020)
flag: 'Distributed version control before Git: a 1998 retrospective' too_old (year=1998 < 2020)
dedupe_candidates: 9 in, 8 out, 1 merged
```

The two titles differ only in case, so the title-author-year rule catches
what identifier and web-address matching miss. `--min-year` flags both old
records but drops neither. Exit code 0: this script only fails on a bad
input.

Break it on purpose: copy the mock index to a scratch file, delete its
final `]` character (the file ends with `]` on its own line, so delete
the whole line), and run the script on the broken copy:

```text
dedupe_candidates.py: error: Expecting ',' delimiter: line 81 column 1 (char 3406)
```

Exit code 2, no traceback: a usage error, not a finding about the
candidates.

[X-S1-03 Run a search plan's queries one at a time](../scripts/s1/x-s1-03.md)
runs a plan's queries in order, one call in flight at a time, printing one
manifest line per finished query. Its backend is a mock search backend
(never the model provider the glossary defines), answering from an index
file by simple word matching; this script never reaches a network. Run it
on the sample plan and index:

```bash
python3 -B scripts/s1/run_queue.py \
    scripts/sample_data/git_basics_stage1/search/plan.json \
    --index scripts/sample_data/git_basics_stage1/search/mock_index.json
```

```text
{"query_id": "Q1", "start": 0.0, "finish": 0.0, "attempts": 1, "matches": 1, "new_candidates": 1, "stage": "listed", "state": "done", "anchors_expected": 2, "anchors_hit": 1}
{"query_id": "Q2", "start": 3.0, "finish": 3.0, "attempts": 1, "matches": 1, "new_candidates": 0, "stage": "listed", "state": "done", "anchors_expected": 2, "anchors_hit": 1}
{"query_id": "Q3", "start": 6.0, "finish": 6.0, "attempts": 1, "matches": 1, "new_candidates": 0, "stage": "listed", "state": "done", "anchors_expected": 2, "anchors_hit": 1}
{"query_id": "Q4", "start": 9.0, "finish": 9.0, "attempts": 1, "matches": 0, "new_candidates": 0, "stage": "listed", "state": "empty", "anchors_expected": 2, "anchors_hit": 1}
queries=4 done=3 empty=1 failed=0 candidates=1 anchors=1/2 recall=0.50
```

`Q1` to `Q3` all match the same candidate, already known after `Q1`, so
`new_candidates` is 0 for the repeats; still `done`, not `empty`, since a
match happened. `Q4` finds nothing, which is `empty`. Only one of the two
anchors ever turns up, so recall stops at 0.50; exit code 0, since every
query is `done` or `empty`. A real plan at 0.50 recall is below the 0.8
bar above and needs another revision before anyone approves it; this
small sample plan is left as it is only to show the runner and the
manifest, not as an approved plan.

The virtual clock, on by default, only advances when the runner waits;
nothing actually sleeps, so this run finishes at once. `--real-time` swaps
in `time.monotonic()` and `time.sleep()` for a run against a real backend.

`--fail` scripts a query failing and recovering. `--fail Q1:2` raises a
transient error on `Q1`'s first two calls, so the runner retries and
succeeds on the third:

```text
{"query_id": "Q1", "start": 0.0, "finish": 15.0, "attempts": 3, "matches": 1, "new_candidates": 1, "stage": "listed", "state": "done", "anchors_expected": 2, "anchors_hit": 1}
```

`attempts` is 3 and `finish` later, since the runner waited 5 then 10
seconds between attempts; the rest of the run has the same states and
counts as the one above, only shifted later in time.
`--fail`, given twice, can script two queries failing outright: `--fail
Q1:3 --fail Q2:3` exhausts every retry on both:

```text
{"query_id": "Q1", "start": 0.0, "finish": 15.0, "attempts": 3, "matches": 0, "new_candidates": 0, "stage": "listed", "state": "failed", "anchors_expected": 2, "anchors_hit": 0}
{"query_id": "Q2", "start": 18.0, "finish": 33.0, "attempts": 3, "matches": 0, "new_candidates": 0, "stage": "listed", "state": "breaker_open", "anchors_expected": 2, "anchors_hit": 0}
queries=2 done=0 empty=0 failed=1 candidates=0 anchors=0/2 recall=0.00
```

Two exhausted queries in a row reach the breaker's default of 2; `Q2`'s
line is the one that opens it, and the run stops before `Q3` and `Q4` run.
Exit code 1.

Break it on purpose: copy the plan to `plan.extra-query.json`, add one more
query to a cluster without raising `query_cap`, and run it:

```text
run_queue.py: error: plan.extra-query.json: 5 queries exceed query_cap 4
```

Exit code 2: the plan is invalid before any query runs, the failure a
person approving the plan set should catch first. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 1 index for
what each exit code means.

To replace the mock, write a class with a `search(text)` method that calls
your own service, raising a transient error worth retrying or a blocked
error that is not; give the queue that class instead. With no such class,
run one query at a time by hand and copy each result into a manifest
line.

## Definition of done

- Every plan has at least one anchor that came from a tool or a person,
  never one the agent itself confirmed. The project notes ask for at
  least five anchors per plan for real search work; the sample plan
  here, covering one small objective, uses two.
- The plan set is approved, with a record of who approved it and when,
  before any query ran.
- Every query in the manifest reached a final state: `done`, `empty`,
  `failed`, `blocked`, or `breaker_open`.
- The candidate list has no two records sharing an identifier, a
  normalized web address, or a normalized title, author and year.
- A person has decided what to do about any candidate flagged too old,
  and about a run where the breaker opened.

## Common failures

- Throttling: too many calls too quickly draw a refusal, which can look
  like "no results" rather than "try again later".
- A cached answer masking a refusal: stale results keep returning on
  retry, so the run looks fine while nothing new is found.
- Anchors the agent itself confirmed, not ones from a tool or a person:
  recall then measures the agent grading its own plan.
- Overlap between plans: two plans for related objectives search the same
  ground, doubling review work without adding coverage.

## Adapting to your platform

- `llm`: drafts each plan's clusters and queries from the objective text
  and the known anchors.
- `web-search`: the real calls behind the mock in this guide's runner;
  without it, look up each query by hand and copy results into a manifest
  line.
- `shell`: runs `dedupe_candidates.py` and `run_queue.py`; without it, run
  them on another machine with Python 3.10 or newer and paste the output
  back in.
- `human-approval`: approves the plan set before any query runs, and
  decides what to do when the breaker opens.

No other [capability](../glossary.md#capability) is needed for this
sub-stage.

## Where humans decide

- Which anchors count as known-relevant for each plan, and whether the
  plan finds them well enough to approve.
- Approval of the plan set, before any query runs.
- What to do when the breaker opens: raise the breaker, fix the query, or
  stop for the day.
- Whether a plan that goes over one of the caps above has a good enough
  written reason.

Next: [S1.4b Screening and conversion](screening-and-conversion.md).
