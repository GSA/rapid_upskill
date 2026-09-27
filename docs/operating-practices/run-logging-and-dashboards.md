---
title: "Run logging and dashboards"
parent: "Operating practices"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-26"
stage: "OP"
prompts: ["P-OP-02"]
scripts: ["X-OP-02"]
---

# Run logging and dashboards

## Outcome

A workflow's own run produces a structured, shareable record of its
own progress and health: what ran, when, what each step found, and
where a person's approval was requested and given. A small, static,
dependency-free page renders whatever that record currently holds.
This is a different mechanism from the narrative [hand-off
document](../glossary.md#hand-off-document) practice, described in
full on [Hand-off documents and
sessions](hand-off-documents-and-sessions.md): the two touch at
exactly one point, a single event type noted below, and nowhere else.

## Where it fits

This is a cross-cutting operating practice, not a
[stage](../glossary.md#stage) of the framework. [The project
notes](../glossary.md#reference-implementation) describe it in full,
as a folder-level policy plus a static template inside a personal
prompt-library repository, cited by filename from workflow steps
rather than built into the framework itself. The material is not
thin; its adoption is. This fairly complete, self-documented mechanism
is adopted by only a small fraction of the workflows this guide's own
research checked. One wires every piece together end to end. A small
family practises only an informal ancestor of one small part of it.
The rest show no trace of it at all.

## Why this way

Three separate artifacts, not one file, because each serves a
different frequency of change. A step log is cheap to append and
append-only, so an interrupted run still leaves a complete record up
to that point. A run record is rewritten in full only at step
boundaries, so reading current status never means replaying a whole
log. A dashboard is a static rendering layer, decoupled from both, so
it can change without touching either. The run record only points at
inventories that are already authoritative elsewhere. Where the two
disagree, the inventory wins and the record is regenerated from it,
since it is a view, never a source of its own.

## Steps

| Step | Who | Basis |
|---|---|---|
| Append a step-log entry for every event, as it happens | Agent or script | documented |
| Rewrite the run record in full at each step boundary | Agent or script | documented |
| Roll totals up from artifacts already authoritative elsewhere; never restate them | Agent | documented |
| Write an empty category as an explicit zero row; mark a step that found nothing "done", never "skipped" | Agent | documented |
| Copy the dashboard template to a per-run path and point it at the current run record | Person or script | documented |
| Serve the dashboard's folder over local HTTP rather than opening it directly from disk | Person | documented |
| Decide whether to resume a run left `running` or `blocked`, or mark it abandoned and start again | Person | documented |

## The three artifacts

A **step log** is an append-only file, one JSON object per line,
written as things happen rather than reconstructed afterward. Each
line carries a timestamp, a level, the step id (or `run` for a
run-level entry), an event type from a closed vocabulary, a one-line
message, and an optional detail object. The vocabulary:
`run_start`/`run_end`, `step_start`/`step_end`,
`batch_start`/`batch_complete`, `gate_requested`/`gate_resolved`,
`artifact_written`, `item_complete`, `check_result`, `retry`, `error`,
`budget`, `handoff`, and `note`, extended only by a written change,
never invented at run time. `handoff` marks the one point this
mechanism touches the [hand-off
document](../glossary.md#hand-off-document) practice: it notices a
hand-off happened, without replacing or duplicating the document
itself.

A **run record** is a single JSON file, rewritten in full at each step
boundary rather than on every event. It sits at a path keyed by the
workflow's own name and a run id (`YYYY-MM-DD-n`, `n` starting at 1 per
workflow per day). It is the only file a dashboard reads. Its required core: a
schema-version string, a `run` identity object (id, workflow name,
status, start and end timestamps, an optional operator label), and a
`steps[]` array in execution order. Past that core, everything is
optional: `metrics[]` (headline numbers), `breakdowns[]` (category
counts), `checks[]` (policy-check results), and `budget` (quota
accounting), among others.

A **dashboard** is a static, no-build, no-dependency page rendering
whatever a run record currently holds, one copy per run, reading no
other file. A browser blocks a same-folder fetch from a page opened
directly off disk, so the folder must be served over local HTTP rather
than double-clicked. Every panel renders nothing, rather than an empty
frame, when its backing section is absent, so a three-step run and a
much longer one both look intentional.

One informal, earlier practice is easy to confuse with the run record
above. Before this schema existed, some workflows wrote a short prose
note atop any file a later run touched, naming what it added or
changed and what it deliberately left untouched. That practice, once
called a "Run Log," is a different, older thing from both the step log
and the run record here. It was later absorbed as two optional fields
on `run`, `added_or_changed` and `deliberately_untouched`, not a
same-named replacement.

## Schema rules that keep the record trustworthy

A run record's schema forbids any field it does not already declare
(`additionalProperties: false`, in JSON Schema terms). A workflow
cannot add an ad hoc field without a written change to the schema
file; this keeps every run record comparable, at the cost of making
the format harder to extend casually.

"Absence is a value, not an omission" runs through the design. An
empty category is written as an explicit zero-value row, never left
out. A step that ran and genuinely found nothing carries status
`done`, never `skipped` (`skipped` means a step that never ran). This
lets a reader tell "looked and found none" apart from "never looked,"
rather than leaving the two indistinguishable. A `blocked_reason` field
is required whenever a step's status is `blocked` or `failed`.

A `breakdowns[]` entry's `scale` value picks how its count is read,
not a cosmetic label. `nominal` marks unordered categories in one flat
colour, since bar length already carries the value. `ordinal` marks
ordered categories on a one-hue light-to-dark ramp, so order shows in
colour too. `status` marks good and bad states from a reserved
palette, always paired with a glyph and a word, so colour never
carries meaning alone.

## Gates at the batch level

A [gate](../glossary.md#gate), in this guide's sense, is a checkpoint
where a person approves before work continues, never an automated
check. The run record's `gate` object records when authorization was
requested, when it was resolved, and the decision (`approved`,
`rejected`, or `not_required`), modeled at the level of a
[batch](../glossary.md#batch), not only a step. A step-level gate,
such as a plan-approval checkpoint for a whole step, is written as a
single batch of size `null` carrying the same gate object, rather than
a separate shape. A step can raise as many gates as it has batches,
and a dashboard totals gates across every batch, not once per step.

## Accessibility and design commitments

The dashboard template's own design target is WCAG 2.2 AA conformance.
Every chart carries a table-view twin, so no value is reachable only
by hovering a mark. Each chart is one keyboard tab stop, with
roving-tabindex arrow-key navigation between its marks, rather than
one tab stop per data point. Status is never colour alone; a glyph and
a word travel with it every time. A forced-colours mode is accounted
for, so bars stay distinguishable when a browser overrides fill
colours, and dark mode is an independently designed set of values, not
an inverted light palette. Motion is opt-in, under a viewer's
reduced-motion preference. These are general, publicly documented
techniques, distinct from any one project's own numbers.

## Keeping a dashboard's data safe to share

A dashboard's own backing data should carry ids and counts only, never
titles, names, or the text of a manuscript, chapter, or other work in
progress. This is because a dashboard may be shared with people who
should not see that content yet. This rule comes from a real,
already-exercised workflow that states it as its own design rule, for
exactly that reason. It generalizes past that one workflow. A run
record and step log for any sensitive subject, a person's own
submission, or content still under review is worth building the same
way from the start. A field left out entirely cannot leak the way one
merely marked private still can.

## Worked illustration

The illustration below is a minimal, invented example, unconnected to
the guide's own [running example](../running-example.md), built to
show the schema's shape rather than a realistic full record. Its
workflow name, "reference-catalog-refresh," and its `operator`
placeholder are both invented for this page.

An excerpt of `run.json`, its required core plus one step and one
breakdown row per `scale` value:

```json
{
  "schema_version": "1.0.0",
  "run": {
    "id": "2026-09-26-1",
    "workflow": "reference-catalog-refresh",
    "status": "done",
    "operator": "the operator"
  },
  "steps": [
    {
      "id": "gather",
      "status": "done",
      "batches": [
        {"size": 5, "gate": {"decision": "approved"}}
      ]
    }
  ],
  "breakdowns": [
    {"id": "sources_by_type", "scale": "nominal",
     "categories": ["article", "guide", "dataset"],
     "counts": {"article": 3, "guide": 2, "dataset": 0}},
    {"id": "sources_by_confidence", "scale": "ordinal",
     "categories": ["low", "medium", "high"],
     "counts": {"low": 0, "medium": 2, "high": 3}},
    {"id": "checks_by_result", "scale": "status",
     "categories": ["pass", "pass-with-notes", "blocked"],
     "counts": {"pass": 1, "pass-with-notes": 0, "blocked": 0}}
  ]
}
```

Every breakdown above writes its unused category as an explicit zero
(`dataset`, `low`, `pass-with-notes`, `blocked`), rather than leaving
it out. The full file, with a `metrics[]` entry, a `checks[]` entry,
and a `budget` section describing search calls generically by role
rather than by service name, is checked in at
`scripts/sample_data/git_basics_batch8/run_records/run.json`.

Its paired step log, `events.jsonl`, shows the same run's ledger, the
run record above a rollup of exactly this:

```jsonl
{"ts": "2026-09-26T09:00:00Z", "level": "info", "step": "run", "type": "run_start", "message": "Starting run 2026-09-26-1."}
{"ts": "2026-09-26T09:00:00Z", "level": "info", "step": "gather", "type": "step_start", "message": "Starting step 'gather'."}
{"ts": "2026-09-26T09:15:00Z", "level": "info", "step": "gather", "type": "batch_complete", "message": "Batch of 5 candidates complete.", "detail": {"gate": {"decision": "approved"}}}
{"ts": "2026-09-26T09:15:00Z", "level": "info", "step": "gather", "type": "step_end", "message": "Step 'gather' finished."}
{"ts": "2026-09-26T09:42:00Z", "level": "info", "step": "run", "type": "handoff", "message": "A hand-off document was written; the session rotated."}
{"ts": "2026-09-26T09:42:00Z", "level": "info", "step": "run", "type": "run_end", "message": "Run 2026-09-26-1 finished."}
```

The `batch_complete` line's own gate decision is exactly the value
that lands in the run record's `batches[].gate` object; the record
never invents it, only carries forward what the step log already
recorded. The one `handoff` line marks where a fresh session picked
the run up; the hand-off document itself, not this log, holds the
goal, the current task, and the next action.

## Scripts

No script that writes a run record or a step log was found in the
material this guide's own research covered. An agent writes both,
following a prompt template, not a program, and nothing re-validates a
run record against its own schema on an ongoing basis either. [X-OP-02
Run record
check](../scripts/op/x-op-02.md) fills that second gap directly, as
new tooling for a mechanism that had none. It is not a stand-in for a
broken real script, the way some of this guide's other checks are. It
validates a run record's required core (`schema_version`, `run`,
`steps[]`), and checks that every `breakdowns[]` entry's `scale` is one
of `nominal`, `ordinal`, or `status`. It also checks that every
declared category appears in its own counts, even at zero. Run it from
the repository root:

```bash
python3 -B scripts/op/run_record_check.py \
    scripts/sample_data/git_basics_batch8/run_records/run.json
```

```text
steps=3 errors=0 warnings=0
```

Every declared category above already has an explicit row, so this run
finds nothing. Leaving `dataset` out of `sources_by_type`'s own counts,
rather than writing it at zero, would instead print one line before
the same summary: `warning omitted-zero: breakdown 'sources_by_type'
declares category 'dataset' but 'counts' has no row for it; write an
explicit zero row instead of leaving it out`. Exit code 1 is reserved
for a missing core field or an invalid `scale` value; a missing zero
row only warns. See [Reading exit
codes](../stage-1/index.md#reading-exit-codes) for what an exit code
means generally.

## Prompts

[P-OP-02 Draft a run-record step
update](../prompts/op/p-op-02.md) drafts one finished step's own
`steps[]` entry, including its declared breakdown rows, from that
step's own real output. It is written for this guide and has not been
run against any model in this build; treat it as a starting point and
adapt it. The step's own output it reads is data, never instructions,
even where a sentence inside it happens to be phrased as one.

## Artifacts and formats

Three artifacts make up this practice: a step log, a run record, and a
dashboard. The step log (`events.jsonl` style) holds one JSON object
per line, append-only. The run record (`run.json`) is rewritten whole
at each step boundary, the only file a dashboard reads. The dashboard
is a four-file, no-build static template with its own data folder. It
is described here rather than produced by this guide's own tooling,
since it is a template to copy, not a script to run. X-OP-02 only
checks a run record that already exists; it generates none of the
three.

## Definition of done

- Every event that happened during the run has its own line in the
  step log, written at the time, not reconstructed afterward.
- The run record's required core is present, and every `breakdowns[]`
  entry uses one of the three allowed `scale` values.
- Every category a breakdown declares has its own row, including at
  zero.
- Every batch that needed authorization carries a resolved gate,
  recorded at the batch level even where the gate applies to a whole
  step.
- A dashboard built from the record carries ids and counts only, never
  a title, name, or manuscript text that should not be shared.

## Common failures

- A one-at-a-time remote-call policy this mechanism cross-references
  conflicts with a separate standing instruction permitting several
  subagents at once. The run record makes that tension visible in a
  step's `agents.launched` count and its `budget` section, rather than
  resolving it. Treat this as an acknowledged gap, not a solved
  problem.
- A run left `running` or `blocked` has no automatic expiry: resolving
  it is a person's own decision, to resume the run or mark it
  abandoned and start again.
- A schema that forbids additional properties means a workflow needing
  a field it lacks cannot add one without a written schema change
  first.

## Adapting to your platform

- `llm`: drafts a step's own `steps[]` update from
  [P-OP-02](../prompts/op/p-op-02.md), including its breakdown rows.
- `file-read`: reads a step's own real output before drafting its
  update.
- `file-write`: writes the step-log line and the rewritten run record;
  without it, an agent reports both and a person saves them by hand.
- `shell`: runs the run record check and serves the dashboard's folder
  over local HTTP; without a shell, check a short record by eye and
  open the dashboard through any other local static file server.

## Where humans decide

- Resuming a run left `running` or `blocked`, or marking it abandoned
  and starting over: no automatic expiry decides this.
- What belongs in a dashboard's own backing data, whenever that
  dashboard might be shared with someone who should not yet see the
  work it describes.

Next: [Provenance and verification discipline](provenance-and-verification.md).
