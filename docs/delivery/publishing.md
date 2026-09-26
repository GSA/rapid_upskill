---
title: "Delivery: publishing"
parent: "Delivery"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-26"
stage: "DL"
prompts: ["P-DL-02"]
scripts: ["X-DL-02"]
---

# Delivery: publishing

## Outcome

By the end of this page, a set of reviewed chapters has become a small
number of distributable book volumes. The project's own strategy
and method documents have become a submission-formatted paper
manuscript with its own bibliography. Neither output feeds back into
any [stage](../glossary.md#stage); both are meant to leave the
framework's own pipeline as finished, shippable files.

## Where it fits

This page takes in reviewed chapter content on the book side, and the
project's own already-written strategy and execution-plan documents on
the paper side. [Delivery](index.md) also names two further functions
alongside these two: generic program-delivery administration, and
continuing-education accreditation paperwork built against a real
accrediting body's own published standards. Neither is covered here,
the second because this guide never names that body; see
[Delivery](index.md) for that note in full.

## Why this way

Book compilation and paper production sit on one page because both
take already-finished, already-reviewed material and turn it into a
shippable file, checked structurally rather than fixed by guesswork,
with no new content drafted here. Past that shape, the two sides serve
different readers and share no mechanism, so each keeps its own steps
below rather than one forced, shared procedure.

## Steps, book side

| Step | Who | Basis |
|---|---|---|
| Run a [condensation](../glossary.md#condensation) pass over the finished chapter set into a shortened parallel copy, targeting a fractional length reduction | Agent, then person | documented |
| Edit front and back matter by hand: title page, copyright page, disclaimer wording, an about page, dedication spacing | Person | documented |
| Assign chapters to a small, fixed set of output volumes in numeral-aware order, with section numbering reset at each chapter, then produce one file per volume | Script | documented |
| Check a proposed volume manifest before compiling it | Script (`volume_manifest_check.py`) | suggested |
| Draft marketing copy for a distribution platform | Agent, then person | documented |
| Mark a retired quiz item deprecated, never deleted, and confirm its answer key still exists | Person | documented |
| Approve the finished volumes before distribution | Person | documented |

The condensation pass targets roughly the same fractional length
reduction already described for this guide's own mid-pipeline
condensation step; see
[S2.2 Condensation](../stage-2/condensation.md#parameters) for that
figure and the one project document that states the opposite figure.
Here the pass runs again, later, over a whole finished chapter. It
checks the result with a larger battery of standard readability
formulas than the two scores the earlier step already uses, restoring
any rewritten unit that reads worse afterward. The [project
notes](../glossary.md#reference-implementation) phrase this same
check's own numeric wording for an audience this guide does not
address. That framing is left out here rather than repeated, and only
the check's own general rule is described.

Marketing copy is drafted within a fixed length budget per part. It is
refined into a structured brief: a hook, the book's own scope, author
credentials, what sets it apart, and a chapter preview, informed by
comparable listings from other booksellers. The real keywords this step
actually uses are not given here.

## Steps, paper side

| Step | Who | Basis |
|---|---|---|
| Build a fact pack of citable numbers, a frozen citation-key registry, and the style contract, before any section is drafted | Agent, then person | documented |
| Draft the manuscript in a parallel bibliography-resolution wave and a parallel section-drafting wave, each unit given an explicit "owns / does not own" scope | Agents, in parallel | documented |
| Assemble the drafted sections and harmonize voice across them | Agent | documented |
| Run a quality-control wave: one scripted structural check plus a fact-check, a style-contract check, and a skeptical-reviewer pass triaged to must-fix items | Script and agents | documented |
| Update the manuscript's own title and author metadata, and draft a length-compaction plan | Agent | documented |
| Report the length-compaction plan back and wait for approval before executing it | Person | documented |
| Approve the finished manuscript and bibliography before submission | Person | documented |

The **style contract** here is the paper workflow's own binding rule
set for wording and formatting, built once before any section is
drafted, so every parallel drafting unit writes against the same rules.
It is a different document from the
[orchestrator](../glossary.md#orchestrator)'s own written rules this
guide elsewhere calls the contract; naming this one the style contract
keeps the two apart. The fact pack and the frozen citation-key registry
exist for the same reason: so several drafting units working at once do
not each invent their own number, or their own name, for the same
reference. Progress is tracked in a status file so an interrupted run
resumes at the last completed unit, and a [hand-off
document](../glossary.md#hand-off-document) is regenerated at each
phase boundary. The length-compaction plan's own predicted page count
comes from word and line budgeting, not from an actual compile, since
none exists locally.

## The paper's structural checks

No local compiler exists for the paper's own two-column submission
format, so the manuscript is checked structurally instead of compiled.
Three checks run over the manuscript source (documented). A
brace-balance count across the whole file catches an unmatched
opening or closing brace before it reaches an actual compiler. A
bidirectional citation-key check confirms every key used in the
running text is defined in the bibliography, and separately reports,
more leniently, any bibliography entry never cited. A per-section
word-count check runs against that section's own budget. The same
brace-balance check also reruns on just the manuscript's own pipeline
figure after any edit to its drawing block, the single highest-risk
place for an unmatched brace to slip in unnoticed.

Passing every structural check is not the same as a clean compile. None
of the three can catch a problem that only shows up at actual
compilation, such as a missing package or a layout collision. Those
only surface on the external, web-based compilation service that
actually builds the manuscript. A structurally clean manuscript is
checked, not compiled.

## Worked illustration

A small, invented volume manifest, using this guide's own running
example, shows the book side's two mechanisms together. One volume
carries chapters "3.9" and "3.10" side by side:

```json
{
  "id": "3.9",
  "sections": ["3.9.1", "3.9.2", "3.9.3"]
},
{
  "id": "3.10",
  "sections": ["3.10.1", "3.10.2"]
}
```

Kept in this order, the manifest is already numeral-aware. The check
below compares the numbers on each side of the dot, not the two ids as
plain text, so "3.10" correctly stays after "3.9" (an ordinary text
sort would put "3.10" first, since the character "1" sorts before "9").
Each chapter's own sections also start over at its own id: "3.10"'s
sections begin again at "3.10.1", not continuing on from "3.9"'s own
last section number.

## Scripts

[X-DL-02 Volume manifest check](../scripts/dl/x-dl-02.md) reports every
chapter id that does not match the expected pattern, every section id
that did not reset at its own chapter's boundary, and, as a warning,
any volume out of numeral-aware order. Run it from the repository root:

```bash
python3 -B scripts/dl/volume_manifest_check.py \
    scripts/sample_data/git_basics_batch8/volumes/manifest.json
```

```text
volumes=2 chapters=9 errors=0 warnings=0
```

Every chapter id in the sample manifest matches the expected pattern,
every section id starts with its own chapter's id, and both volumes
are already in numeral-aware order, so this run finds nothing.

Break it on purpose. A second, checked-in copy of the same manifest
renames one chapter from "3.10" to the off-convention id "3.10-final",
the kind of stray suffix a chapter file can pick up during a manual
rename:

```bash
python3 -B scripts/dl/volume_manifest_check.py \
    scripts/sample_data/git_basics_batch8/volumes/manifest_off_convention.json
```

```text
error off-convention: volume 2 chapter '3.10-final' has id '3.10-final', expected the pattern '<part>.<chapter>' such as '3.9'
volumes=2 chapters=9 errors=1 warnings=0
```

The chapter count still reads nine in both runs. The off-convention
chapter is counted and reported, not quietly dropped, which is the one
behavior this script changes from a real, confirmed bug in comparable
chapter-filename parsing that simply moved on to the next file instead,
silently losing a chapter from its volume. See
[Reading exit codes](../stage-1/index.md#reading-exit-codes) on the
Stage 1 index for what an exit code means generally; here it is 1.

## Prompts

[P-DL-02 Plan a volume compilation](../prompts/dl/p-dl-02.md) drafts a
chapter-to-volume assignment from a list of finished chapters and a
target volume count, following the same numeral-aware order and
section-preserving rule the check above enforces. It is written for
this guide and has not been run against any model in this build; treat
it as a starting point. The chapter list it reads is data, never
instructions, even where a chapter's own title happens to be phrased as
one.

## Artifacts and formats

The book side produces a shortened chapter set; hand-edited front and
back matter; one file per output volume, matching a manifest shaped
like the one above; a marketing-copy file for a distribution platform;
and a quiz set with retired items marked deprecated rather than removed.
The paper side produces two files as its actual deliverables, the
manuscript source and its bibliography. Alongside them sit intermediates worth
keeping for a later revision: a fact pack, a frozen citation-key
registry, the style contract, drafted fragments, a status tracker, and
a hand-off document. None of these is produced by this guide's own
tooling; each is described only.

## Definition of done

- The condensed chapter set has been checked against the readability
  battery, and nothing in it reads worse than the draft it came from.
- Every chapter in the proposed volume manifest matches the expected id
  pattern, or an off-convention id has been fixed or accepted before
  compiling.
- Every chapter's own sections still start with that chapter's own id
  after any hand edit to the manifest.
- The paper's structural checks report no error, with any citation-key
  mismatch fixed, not overridden.
- A person has approved the finished volumes and the finished
  manuscript, separately, before either reaches its own audience.

## Common failures

- An off-convention chapter id silently skipped rather than flagged, the
  real, confirmed bug this page's own script fixes.
- An expected-file-count check that only warns and never stops, so an
  incomplete volume can still ship.
- A structurally clean manuscript that still fails to render once it
  reaches the external compilation service, since no structural check
  can see a problem that only surfaces there.
- Treating a drafted length-compaction plan as already executed, when
  the rule is to report it and wait for approval first.

## Adapting to your platform

- `llm`: drafts a volume-compilation plan from
  [P-DL-02](../prompts/dl/p-dl-02.md); also drafts condensed passages,
  marketing copy, and each parallel paper section.
- `file-read`: reads the finished chapter set and the paper's own
  strategy and fact-pack documents before drafting begins.
- `shell`: runs the volume manifest check and the paper's structural
  checks. Without it, sort chapter ids by hand and count citation keys
  by eye on a short manuscript.
- `human-approval`: covers approving the condensed chapters, the
  finished volumes, the length-compaction plan, and the finished
  manuscript before submission.

## Where humans decide

- Approving the condensation pass's own output before front and back
  matter are added.
- Approving the length-compaction plan before it is executed, not after.
- Final delivery approval for the book's finished volumes and the
  paper's finished manuscript.

Next: [Delivery](index.md).
