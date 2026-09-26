---
title: "S3.3 Layer 3 audit trail"
parent: "Stage 3 Review and verification"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-25"
stage: "S3"
sub_stage: "S3.3"
prompts: ["P-S3-03"]
scripts: ["X-S3-03"]
---

# S3.3 Layer 3 audit trail

## Outcome

At the end of this sub-stage, what Layers 1 and 2 found is recorded at
several levels of detail: an immutable change log, a per-claim record,
a per-chapter summary with its own per-reference matrix, and a
version-history entry. A citation-fidelity check also runs across the
whole chapter's own citations.

## Where it fits

This sub-stage takes in Layer 2's signed-off findings from
[S3.2](layer-2-expert-review.md). It hands on a recorded, checked
chapter to [S3.4 and S3.5](tiering-and-remediation.md), the last step
before the planned Stage 4.

## Why this way

A finding that is not written down the same way every time cannot be
compared across chapters later. A citation nobody re-checks at the
finished-chapter stage can also drift from its source, even after
[Layer 2](../glossary.md#verification-layer) approved it. This page
uses the same
[basis labels](../stage-1/index.md#basis-labels) Stage 1's index
defines. Logging every action, the per-claim record's own fields, and
the per-chapter and per-reference shapes are documented in
[the project notes](../glossary.md#reference-implementation). Who
actually writes to the log, and who compiles the per-chapter summary,
are this guide's own suggestion, where the project notes are silent.

The citation-fidelity check reuses
[quote_check.py](../stage-1/distillate-and-quote-bank.md)'s (S1.5b,
already published) own idea, at a later stage's larger scale. Both
check that a quoted phrase is a real substring of a named source file;
this one checks many claims in a finished chapter against a shared
folder of several admitted sources, instead of one distillate's quote
bank against one source.

## Steps

| Step | Who | Basis |
|---|---|---|
| Log every action immutably, as it happens | Script or person | documented for the log's own shape, suggested for who writes to it |
| Roll each claim's findings into a per-claim record, including a signature field for whoever verified it | Agent drafts, person signs | documented for the record's shape |
| Roll every chapter's claims into a per-chapter summary and a per-reference matrix | Agent | suggested for who compiles it, documented for the shape |
| Run the citation fidelity check across the chapter's own citations | Script | suggested |
| Record a version-history entry for the chapter | Agent drafts, person confirms | documented for the entry's own shape, suggested for who records it |

The project notes state no more than each artifact's own shape; the
same hedge applies to every "documented" row above.

## Artifacts and formats

Four shapes make up this sub-stage's record, each given below as a
compact field table rather than a full example, to keep this page
inside its word budget.

The **change log** is an immutable, append-only record of every action
taken on the chapter:

| Field | Meaning |
|---|---|
| timestamp | When the action happened |
| chapter and section | Where in the chapter the action applies |
| before / after | The text before and after a correction |
| reason | Why the change was made |
| verified by | Who checked it |
| evidence | The source or detail backing the entry |
| status | The entry's current state |

The **per-claim record** rolls up one claim's own findings, including
who signed it:

| Field | Meaning |
|---|---|
| id | The record's own identifier |
| timestamp | When the claim was checked |
| chapter and section | Where the claim sits |
| claim | The claim's own text |
| source location | Where in the source the claim's support sits |
| method | How the claim was checked |
| result | The outcome of that check |
| findings | Nested detail on what the check found |
| resolution | How a problem was resolved, if one was found |
| verified by | Who checked the claim, with a signature field |
| references checked | Which sources were checked against the claim |
| approved | Whether the record has been signed off |
| notes | Any other detail worth keeping |

The **per-chapter metadata** summarizes one chapter's own audit state,
and the **per-reference matrix** tracks each source across every
chapter that cites it:

| Per-chapter field | Meaning |
|---|---|
| chapter id and title | Which chapter the summary covers |
| sections | The chapter's own section list |
| claims checked / verified / modified / rejected | Counts for each outcome |
| status | The chapter's overall audit status |
| date | When the summary was compiled |
| reviewers | Who did the checking |

| Per-reference field | Meaning |
|---|---|
| reference | The source being tracked |
| chapters | Which chapters cite it |
| status | Whether it is still admitted |
| confidence | How strongly it is trusted |
| verifier | Who checked it |

The **version-history entry** is a commit-style record of a change to
the chapter:

| Field | Meaning |
|---|---|
| id | The entry's own identifier |
| date | When the entry was recorded |
| author | Who made the change |
| message | A short summary of the change |
| before / after | The text before and after the change |
| reason | Why the change was made |
| sources verified against | Which sources back the change |
| approval status | Whether the change is approved |

### A worked example

One filled per-claim record for a claim from the running example's own
Chapter 1, using the same claim id as the citation-fidelity sample
below:

```json
{
  "id": "PCR-C1",
  "timestamp": "2026-04-02T09:00:00Z",
  "chapter_section": "1.1",
  "claim": "A commit records a snapshot of the tracked files, not a list of edits.",
  "source_location": "SRC-001.md, section \"A commit is a snapshot\"",
  "method": "citation fidelity check",
  "result": "pass",
  "findings": [],
  "resolution": "none needed",
  "verified_by": {"name": "Author A", "signature": "AA-2026-04-02"},
  "references_checked": ["SRC-001"],
  "approved": true,
  "notes": "matches Chapter 1's first objective"
}
```

This record's `references_checked` and `result` fields line up with
`quote-C1` in the script block below; a real per-claim record would
also link to the change-log entry it rolled up from, and to the
per-chapter summary it rolls into.

### Two checklists, not one

This sub-stage keeps a **citation-verification checklist**: a longer
list, used when checking a finished chapter's own citations, running to
roughly fifteen items. The project notes group its items into clusters
wherever they refer to a subset of the list: item 1 on its own; items 2
and 3; items 4 and 5; items 6 through 10; items 12 through 14. Items 11
and 15 are not named in any source read for this guide. This guide does
not print an invented fifteen-item list to fill that gap; the grouping
above is everything this guide can confirm about its shape.

This is a different, shorter list from the **five-point
source-admission checklist** that decides whether to admit a source at
all. That checklist belongs to
[S3.4 and S3.5](tiering-and-remediation.md#the-five-point-checklist),
which owns it and lists its five points; it is named here only so the
two are not confused.

### This stage's own honest gap

Layer 3 shares Layer 2's own gap.
[S3.2's own honest-gap section](layer-2-expert-review.md#this-stages-own-honest-gap)
already quotes the one sentence that covers both layers; it is not
restated here in different words.

## Prompts

[Audit record from review](../prompts/s3/p-s3-03.md)
(P-S3-03) turns one claim's completed review, its note and its
resolution, into a per-claim audit record. It is written for this guide
and has not been run against any model in this build; treat it as a
starting point and adapt it.

## Scripts

[Citation fidelity check](../scripts/s3/x-s3-03.md) (X-S3-03) reads a
manifest of claim id, source id and quoted phrase, and checks each
quote against the named file in a folder of admitted sources.

This script is a plainer version of
[quote_check.py](../stage-1/distillate-and-quote-bank.md)'s idea: a
bare exact-substring check only. That script normalizes typography on
both sides, offers a `--ignore-case` option, and splits a quote into
fragments at a bracketed insertion, failing any fragment under three
words. `citation_fidelity_check.py` does none of this. A quote either
sits in the named source file's text unchanged, or it does not; a
reader arriving from S1.5b's page should expect nothing more here. It
writes no files; its printed lines are a record to copy elsewhere, not
a saved file.

Run it from the repository root on the sample citations manifest, which
carries one quote written as a paraphrase on purpose:

```bash
python3 -B scripts/s3/citation_fidelity_check.py \
    scripts/sample_data/git_basics_stage3/citations/citations.json \
    scripts/sample_data/git_basics/sources
```

```text
pass quote-C1: found in SRC-001.md
pass quote-C2: found in SRC-001.md
pass quote-C3: found in SRC-002.md
pass quote-C4: found in SRC-002.md
fail quote-C5: not found verbatim in SRC-001.md
quotes=5 pass=4 fail=1
```

Four quotes pass. The fifth fails because claim C5 restates a source
sentence about an untouched file's stored content in different words
instead of quoting it. The check does not know whether the underlying
claim is right; it only knows that this exact wording is not in
`SRC-001.md`. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 3 index
for what the exit code means.

Fix it by editing a copy of the manifest to quote the source's own
words instead of paraphrasing them, then run the check again:

```text
pass quote-C1: found in SRC-001.md
pass quote-C2: found in SRC-001.md
pass quote-C3: found in SRC-002.md
pass quote-C4: found in SRC-002.md
pass quote-C5: found in SRC-001.md
quotes=5 pass=5 fail=0
```

If `SOURCES_DIR` holds zero `SRC-*.md` files, the check exits 2 with a
clear message instead of reporting every quote as a mismatch, the same
loud-failure rule [S3.1](layer-1-automated-detection.md)'s script
follows.

## Definition of done

- Every action on the chapter is logged immutably; nothing is
  overwritten in place.
- Every claim carries a per-claim record, including a signature field
  for whoever verified it.
- The chapter carries a per-chapter summary and a per-reference matrix.
- The citation fidelity check reports no failures.
- The chapter carries a version-history entry, confirmed by a person.

## Common failures

- A per-claim record with no signature field, which breaks the one
  place this guide records who actually checked a claim.
- A citation whose source file was renamed after the check ran, so a
  later run cannot find what an earlier one did.
- Skipping the version-history entry because nothing in the chapter's
  own text changed, when the record itself, not the text, is the
  point.

## Adapting to your platform

This sub-stage needs `llm` for drafting each per-claim record, the
per-chapter summary and the version-history entry. It needs
`file-write` to save the change log and these records, and `file-read`
to load Layer 2's findings and the chapter's own admitted sources.
`shell` runs the
citation fidelity check; without it, check each citation by opening
its named source file and searching for the quoted phrase by hand.
`human-approval` covers signing a per-claim record and confirming a
version-history entry; without a platform that pauses for this step,
hold each signature and confirmation as a written note next to the
record.

## Where humans decide

- Who signs a per-claim record, and on what evidence.
- What counts as an approved status on a record or a chapter summary.
- Confirming a version-history entry once an agent has drafted it.

Next: [S3.4 and S3.5 Source tiering and remediation](tiering-and-remediation.md).
