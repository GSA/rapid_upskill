---
title: "S3.4 and S3.5 Source tiering and remediation"
parent: "Stage 3 Review and verification"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-25"
stage: "S3"
sub_stage: "S3.4"
prompts: ["P-S3-04"]
scripts: ["X-S3-04"]
---

# S3.4 and S3.5 Source tiering and remediation

## Outcome

At the end of this sub-stage, every admitted source carries a
**credibility tier**, a number from 1 to 4, recorded separately from
the five-point checklist that judged whether to admit the source at
all. A flagged defect from anywhere earlier in this stage is sorted
into an escalation matrix, so it carries a type, a severity, an
action, an owner and a response-time target instead of sitting in an
undifferentiated list.

## Where it fits

This sub-stage takes in the recorded, checked chapter from
[S3.3](layer-3-audit-trail.md). Tiering a source can happen any time
the source is admitted, as early as [Stage 1](../stage-1/index.md).
This page places the check at the end of Stage 3 because that is where
this guide's own sample script runs it, against a chapter that is
about to move on. This sub-stage hands on a checked, tiered chapter to
the planned Stage 4 (AI-tutor coaching).

## Why this way

A source's own credibility and whether it passed the five-point
admission checklist are two different questions. Keeping them as two
separate fields, checked separately, lets a person ask either one
later without re-deriving it from the other. An individual's blog post
can hold a low tier and still pass the checklist: it exists, has a
real author, and matches the claim it supports. A source's tier can
also change with no new checklist result at all, if the venue's own
standing changes later.

A flagged defect with no severity or owner attached becomes a queue
nobody actually prioritizes: whichever item a person notices first
gets fixed first, regardless of how serious it is. Sorting a defect by
its type and severity into a fixed set of response-time targets fixes
this. A problem in a published chapter then gets attention on a clock
that matches how serious it actually is, rather than the order it
happened to surface in. This page uses the same
[basis labels](../stage-1/index.md#basis-labels) Stage 1's index
defines.

## Steps

| Step | Who | Basis |
|---|---|---|
| Propose a tier for each candidate source against the four tier definitions and the five-point checklist | Agent | suggested for who proposes, documented for the tier definitions and the checklist |
| Confirm or correct the proposed tier | Person | suggested |
| Run the source tier check across the chapter's admitted sources | Script | suggested |
| Assign a flagged defect a severity, an action, an owner role and a response-time target from the escalation matrix | Person | documented for the matrix's shape, suggested for who assigns it |

[The project notes](../glossary.md#reference-implementation) state no
more than the tier definitions, the checklist and the matrix's own
shape; the same hedge applies to every "documented" row above.

## Parameters

### The four tiers

This guide's four credibility tiers classify a source by venue type,
not by a numeric score (documented, the project notes). Tier 1,
Tier 2 and Tier 4 each list five kinds of source; Tier 3 lists four.

| Tier | Source types |
|---|---|
| 1 | Official vendor or standards documentation; a peer-reviewed venue; a whitepaper; a standards body; a university-press textbook |
| 2 | Recognized-expert writing; an established venue's proceedings; a major organization's own documentation; a transparent analyst report; an established course's tutorial content |
| 3 | Individual writing; community question-and-answer content with visible voting; verified-professional social discussion; a non-peer-reviewed preprint used only as a supplement |
| 4 | A crowd-sourced general encyclopedia, for a basic definition only; an uncredentialed how-to page; AI-generated content; an unverifiable paywalled source; a site with an undisclosed bias |

A source's tier and its checklist result, below, are recorded as two
separate fields side by side, never merged into one score.

### The five-point checklist

Before a source is admitted at all, it is checked against a five-point
checklist (documented):

- The source exists and is reachable.
- Its stated author is real.
- Its publication or venue is credible.
- Its content actually matches the claim citing it.
- Its date is still relevant to the claim.

This is a different, shorter list from
[Layer 3](layer-3-audit-trail.md#two-checklists-not-one)'s own
citation-verification checklist, which runs to roughly fifteen items
and checks a finished chapter's own quoted citations. The two must not
blend: this page's five points decide whether a source is admitted at
all, and Layer 3's longer list checks a citation already sitting in a
chapter's text.

### The escalation matrix

No primary source read for this guide describes a ranked,
effort-estimated defect backlog: none names a backlog, a remediation
figure, or an hour estimate in that shape. What the project notes do
describe is an escalation matrix instead: this is this sub-stage's
actual sourced content, in place of that unsupported figure. A flagged
defect carries five fields together, recorded at once.

| Field | What it records |
|---|---|
| Type | What kind of problem the defect is |
| Severity | Critical, high, or medium |
| Action | The specific action the defect calls for |
| Owner role | Which role is responsible for taking that action |
| Response-time target | Same day, 24 hours, 48 hours, or 72 hours |

A defect's type and severity set the action it calls for and the owner
role responsible. The response-time target then sorts the defect by
urgency, instead of leaving it in an undifferentiated queue.

### Affiliation tier is a different question

One project's own source-admission code also carries a field called
**affiliation tier** (documented: the field exists in that code). It
classifies a source by its first author's country or institution, for
an admission rule specific to that project. Whether it answers a
different question from this page's own venue-type credibility tier is
`inferred`: this guide's own reading, not a primary-source statement.
This page's own tier classifies a source's credibility by venue type,
a different axis from a source's affiliation, and the two fields are
not merged.

## Artifacts and formats

Two shapes make up this sub-stage's own record.

The **per-source tier record** tracks one admitted source (documented:
the project notes' own reference-database record). Its "chapters"
field is this guide's own simplification, for tracking one chapter at
a time:

| Field | Meaning |
|---|---|
| id | The source's own identifier |
| citation | The source as cited |
| url or doi | Where to find the source |
| chapters | Which chapters cite the source |
| tier | The 1 to 4 tier from above |
| checklist result | The five-point checklist outcome, kept separate from the tier |
| date | When the record was made or last confirmed |
| verifier | Who confirmed the tier |
| notes | Any other detail worth keeping |

A per-chapter audit table also carries a Tier column, rolling every
cited source's tier into one place for the chapter (documented).

The **escalation-matrix row** records one flagged defect, using the
same five fields given above: type, severity, action, owner role, and
response-time target.

## Prompts

[Propose a source tier](../prompts/s3/p-s3-04.md) (P-S3-04)
proposes a tier for one candidate source against the four tier
definitions and the five-point checklist, from an excerpt of the
source and its metadata. It is written for this guide and has not been
run against any model in this build; treat it as a starting point and
adapt it.

## Scripts

[Source tier check](../scripts/s3/x-s3-04.md) (X-S3-04) prints each
admitted source's own tier, then warns if the share sitting at Tier 3
or below is over a limit. A source's tier is a judgment call for a
person, not a hard pass or fail, so this script never exits 1 on its
own: the warning below never changes the exit code. It exits 0
whenever it can read its input, and 2 only for a usage or input error.

Run it from the repository root. The sample below uses this guide's
own suggested reading of the running example's seven sources, tiered
against the four tier definitions above, from each source's own
description on [The running example](../running-example.md):

```bash
python3 -B scripts/s3/source_tier_check.py \
    scripts/sample_data/git_basics_stage3/tiers/source_tiers.json
```

```text
SRC-001 tier=2
SRC-002 tier=2
SRC-003 tier=2
SRC-004 tier=2
SRC-005 tier=3
SRC-006 tier=2
SRC-007 tier=4
warning low-tier: 2 of 7 sources (0.29) are Tier 3 or below, over the 0.25 limit
sources=7 low_tier=2
```

SRC-005, an older source that conflicts with a later one over what a
pull does, and SRC-007, a promotional source carrying unsupported
claims, are this guide's own suggested Tier 3 and Tier 4 reading of
those two sources' own descriptions. The other five read as
expert-level writing at the same level as one another, so all five
land at Tier 2. Two of seven is
over the default `--max-low-tier-fraction` of 0.25, this guide's own
suggested default: no more than a quarter of admitted sources at
Tier 3 or below. The warning prints for that reason, but the script
still exits 0. `--max-low-tier-fraction` changes the limit; a higher
value, such as 0.5, would let this same sample pass with no warning at
all. See [Reading exit codes](index.md#reading-exit-codes) on the
Stage 3 index for what an exit code means in general. This script's
own exit code never reflects the warning, for the reason just given.

The script writes no file. If you want a record of a run, copy its
printed lines into your own notes; the printed report is the whole of
what the script produces.

## Definition of done

- Every admitted source carries a tier from 1 to 4, recorded
  separately from its five-point checklist result.
- A person has confirmed or corrected every agent-proposed tier.
- The source tier check has run across the chapter's admitted sources,
  and its warning, if any, has a person's response.
- Every flagged defect carries all five escalation-matrix fields: type,
  severity, action, owner role, and response-time target.

## Common failures

- A tier assigned once, when a source was first admitted, and never
  revisited after the source's own venue changes credibility.
- Merging the tier field with the five-point checklist result into one
  score, instead of keeping them side by side.
- Treating the escalation matrix's response-time target as a promise
  about the outcome, rather than a target for when a person takes the
  action.

## Adapting to your platform

- `llm` and `file-read`: an agent reads a candidate source's excerpt
  and metadata and proposes a tier against the checklist and the tier
  definitions.
- `human-approval`: a person confirms or corrects a proposed tier, and
  assigns a flagged defect's severity, action, owner role and
  response-time target.
- `shell`: runs the source tier check; without it, compare each
  source's tier by hand against the four tier definitions, and count
  the low-tier share by hand.

## Where humans decide

- Confirming or correcting a proposed tier.
- Assigning a flagged defect's severity, action, owner role and
  response-time target.

Next: [Stage 3 Review and verification](index.md).
