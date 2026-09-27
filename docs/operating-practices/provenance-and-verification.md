---
title: "Provenance and verification discipline"
parent: "Operating practices"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-26"
stage: "OP"
prompts: ["P-OP-03"]
scripts: ["X-OP-03"]
---

# Provenance and verification discipline

> This page uses **provenance** in a broader sense than the glossary's
> own entry. The [glossary](../glossary.md#provenance) defines
> provenance narrowly: a record of where one
> [knowledge item](../glossary.md#knowledge-item) came from, its source
> document, section and, where possible, its page. This page means
> something wider: a whole document's own chain of custody, and
> whether a claim, a number or a citation inside it can be traced back
> to where it came from and checked. No other page in this guide uses
> "provenance" this way; a similar idea elsewhere in this guide (a
> per-artifact timestamp, an orchestration wave's own accept-and-merge
> trail) is called traceability or lineage instead.

## Outcome

By the end of this page, a claim, a number or a citation inside a
document can be traced back to where it came from, and checked. The
same discipline applies no matter which document it appears in.

## Where it fits

Cross-cutting: this practice is not owned by any one
[stage](../glossary.md#stage) of the framework. Most of the
substantive "how was this checked" material already lives in
[Stage 1](../stage-1/index.md): source gathering, screening and
per-source quote extraction. The rest lives in
[Stage 3](../stage-3/index.md): the three [verification
layers](../glossary.md#verification-layer) (automated detection,
expert review and the audit trail) plus source-credibility tiering.
This page points to both rather than
re-explaining either, and adds only a citation-key check, a
document-derivation-chain concept, and a short list of integrity
rules.

## Steps

The material below comes from a different work product of the
[project notes](../glossary.md#reference-implementation): a short
document the reference implementation produced outside its own
course-content pipeline, with its own contributor-guidance file. There
it exists only as short, self-contained text-processing one-liners, not
a packaged script; this guide's own [script](#scripts) below is a new,
safe stand-in written for the citation-key check specifically. The
one-liners were read for this page, not run, so whether they still
work as documented is inferred, not confirmed by a fresh run.

| Step | Who | Basis |
|---|---|---|
| Check that every citation key used in a document's text resolves to a defined entry in its reference list, and report the reverse gap (a defined key never cited) more leniently | Script | documented |
| Respect the document's own derivation chain: never hand-edit a downstream file in a way that breaks its own traceability back to what it was built from | Person, then agent | documented |
| Trace every numeric claim to a named source, a specific record, or something the requester directly supplied; never invent a figure | Agent | documented |
| Leave a record's own review status unchanged unless an actual verification step justifies changing it | Person | documented |
| Check a drafted fragment twice: once by an automated script, once by a reviewing agent given a different objective than the drafting agent had | Script and agent | documented |
| Flag a missing citation; never add one | Agent | documented |

## The document-derivation chain

A **document-derivation chain** is a one-directional pipeline of
files: raw sources feed per-source extraction records, which feed a
consolidated base, which feeds an outline, which feeds a final
document. Each file in the chain is built from the one before it,
never edited to quietly disagree with it. A downstream file should
never be hand-edited in a way that breaks its own traceability back to
what it was built from. A correction belongs upstream, in the file the
mistake actually came from, so the whole chain keeps agreeing with
itself. This is the broader, chain-of-custody sense of
[provenance](../glossary.md#provenance) the callout above describes:
it tracks a whole document's own history, not one knowledge item's own
source citation.

## Other integrity rules

A handful of smaller rules ride alongside the citation-key check and
the derivation-chain concept above, all documented in the same work
product.

- **No invented numbers.** A numeric claim in a document may only be a
  number that traces back to a named source, a specific record, or
  something the requester directly supplied. A gap is reported, never
  filled with an invented figure.
- **No silent status upgrades.** A record's own review status may not
  move to a more certain value without an actual verification step
  behind it. A script's own merge decision, or an agent's own
  confidence, is not enough on its own. A
  [knowledge item](../glossary.md#knowledge-item)'s own `status` field,
  defined under
  [S1.6 Knowledge items](../stage-1/knowledge-items.md#schema), carries
  a comparable idea, extended here without redefining what that
  field's own values mean.
- **A lighter, two-check echo of Stage 3.** A drafted text fragment is
  checked twice: once by an automated script, once by a reviewing
  agent given a different objective than the drafting agent had. This
  is a smaller version of the fuller three
  [verification layers](../glossary.md#verification-layer) Stage 3
  already documents, scoped down to a short document.
- **Flag, never add.** A drafting agent may flag a missing citation but
  may not add a new citation key of its own. This is a control against
  an agent inventing its own reference, or its own publication venue,
  to paper over a gap.
- **Careful wording about an outside review's own scope.** A claim
  about what an outside review actually covers is worded carefully,
  and agreed on in advance rather than phrased fresh each time. This
  avoids overclaiming what the review assessed (documented, at a
  generic level; this guide does not name that review or the body
  behind it).

## Worked illustration

A small, invented reference list and text excerpt, about a generic
engineering topic rather than the running example, show the
two-directional check together. The excerpt cites four keys, and the
reference list defines four keys, but the two lists disagree on the
last one:

```text
A worker that checkpoints its own progress before each batch survives
a restart without redoing finished work [atomic-checkpoint]. A
retrying call backs off with jitter rather than retrying immediately,
so a wave of failures does not retry in lockstep [backoff-jitter].
Outbound calls to one shared service are capped by a token bucket, so
a burst of work never exceeds what the service allows [token-bucket].
A worker also drains its own current unit of work before exiting on a
shutdown signal [drain-on-shutdown].
```

The reference list defines `atomic-checkpoint`, `backoff-jitter`,
`token-bucket` and `graceful-shutdown`, the same idea as
`drain-on-shutdown` above but kept under a different key after an
earlier rename that did not reach every citation. `drain-on-shutdown`
is the deliberately unresolved citation; `graceful-shutdown` is the
deliberately uncited reference-list entry.

## Scripts

[X-OP-03 Citation key check](../scripts/op/x-op-03.md) reads the
excerpt and the reference list above and reports both mismatches. Run
it from the repository root:

```bash
python3 -B scripts/op/citation_key_check.py \
    scripts/sample_data/git_basics_batch8/citations/TEXT.md \
    scripts/sample_data/git_basics_batch8/citations/REFERENCES.json
```

```text
error undefined: citation key 'drain-on-shutdown' is used in TEXT.md but not defined in REFERENCES.json
warning uncited: reference key 'graceful-shutdown' is defined in REFERENCES.json but never used in TEXT.md
keys_used=4 errors=1 warnings=1
```

The other three keys resolve cleanly in both directions, so only the
renamed pair shows up. See
[Reading exit codes](../stage-1/index.md#reading-exit-codes) on the
Stage 1 index for what an exit code means generally; here it is 1.

## Prompts

[P-OP-03 Check a fragment for invented numbers](../prompts/op/p-op-03.md)
reads a drafted text fragment and a source list. It reports any
numeric claim that does not trace to a named source, a specific
record, or something the requester directly supplied. It is written
for this guide and has not been run against any model in this build;
treat it as a starting point. The fragment and the source list it
reads are data, never instructions, even where a sentence inside
either happens to be phrased as one.

## Artifacts

A reference list, one entry per citation key, each carrying a short
evidence annotation: where the evidence for that entry came from, and
whether a published version exists. This page's own tooling does not
produce this file; it only checks one.

## Definition of done

- Every citation key used in a document resolves to a defined
  reference-list entry, with any mismatch fixed rather than left for a
  reader to puzzle over.
- Every numeric claim traces to a named source, a specific record, or
  something the requester directly supplied.
- No record's own review status changed without an actual verification
  step behind the change.
- A drafted fragment has been checked twice, once by script and once
  by a differently-tasked reviewing agent, before it is treated as
  ready.

## Common failures

- A citation used in the running text but missing from the reference
  list, the one finding the check above is built to catch.
- An agent inventing its own citation key, or its own publication
  venue, to paper over a gap instead of flagging it.
- A two-check pattern that still misses an error both checks share a
  blind spot on (inferred: a general limit of any dual-check scheme).

## Adapting to your platform

- `file-read`: reads the document and its reference list before either
  check runs.
- `shell`: runs the citation-key check; without it, resolve a short
  document's own keys by eye in both directions.
- `llm`: drafts the reviewing agent's own pass, and uses
  [P-OP-03](../prompts/op/p-op-03.md) for the numeric-claim half of it.
- `human-approval`: covers judging whether a traced source actually
  supports a claim, the one thing no check here does.

## Where humans decide

No check here judges whether a claim's traced source actually supports
what the claim says; that judgment stays with a person, on every claim
a check above passes.

Next: [Prompt-injection screening, as a cross-cutting practice](prompt-injection-screening.md).
