---
title: "Stage 3 Review and verification"
nav_order: 30
status: "draft"
last_reviewed: "2026-09-25"
stage: "S3"
---

# Stage 3 Review and verification

## Outcome

[Stage 3](../glossary.md#stage) turns a finished Stage 2 chapter into a reviewed one. A chapter's claims are scanned automatically and handed off to a person where the scan cannot resolve them. What was found is recorded in an audit trail, and the chapter's own sources are classified by credibility, before the chapter is considered ready for [Stage 4](../stage-4/index.md).

## Where it fits

Stage 3 takes in a finished, revised chapter from [Stage 2](../stage-2/index.md). It hands on a reviewed chapter to [Stage 4](../stage-4/index.md) (AI-tutor coaching).

## Sub-stages

Each part of Stage 3 has a **[sub-stage](../glossary.md#sub-stage)** id, continuing Stage 1 and Stage 2's own numbering.

| ID | Name | What it does | Page |
|---|---|---|---|
| 3.1 | Layer 1 automated detection | Scan a chapter's claims for a missing or invalid citation, and classify any flagged claim by a four-type hallucination taxonomy | [S3.1](layer-1-automated-detection.md) |
| 3.2 | Layer 2 expert human review | A subject-matter expert gives every flagged claim a closer look, then signs off against a seven-item checklist | [S3.2](layer-2-expert-review.md) |
| 3.3 | Layer 3 audit trail | Record what Layers 1 and 2 found, at several levels of detail, and check the chapter's own citations for fidelity | [S3.3](layer-3-audit-trail.md) |
| 3.4 | Source tiering | Classify each admitted source's credibility into one of four tiers, kept separate from whether it was admitted at all | [S3.4 and S3.5](tiering-and-remediation.md) |
| 3.5 | Remediation | Sort a flagged defect into an escalation matrix by type, severity, the action it calls for, an owner role, and a response-time target | [S3.4 and S3.5](tiering-and-remediation.md) |

All five sub-stages are now published.

## Order of work

1. Layer 1 automated detection (S3.1) needs a finished, revised chapter from Stage 2.
2. Layer 2 expert human review (S3.2) needs the flagged-claims list S3.1 hands off.
3. Layer 3 audit trail (S3.3) needs Layer 2's signed-off findings.
4. Source tiering and remediation (S3.4 and S3.5) need the recorded, checked chapter from S3.3; tiering a source can itself happen any time it is admitted, not only at this last step.

## Basis labels

This page and every Stage 3 sub-stage page use the same three [basis labels](../stage-1/index.md#basis-labels) Stage 1's index defines: `documented`, `inferred` and `suggested`. This page does not redefine them.

## How Stage 3 is run

Agents do the volume work: running each automated check, drafting each deep-verification note, drafting each per-claim and per-chapter record, and proposing a tier for each candidate source. People make each judgment call: every status a subject-matter expert assigns, every disagreement resolution, every signature, and every approval below. This is the same [human-in-the-loop](../glossary.md#human-in-the-loop) design Stage 1 and Stage 2 use: work pauses at set points for a person to look before it continues.

## Approvals

| After | What the person approves | Human roles gate kind | Basis |
|---|---|---|---|
| S3.1 | Which flagged claims are handed off to Layer 2 | Plan approval | suggested |
| S3.2 | The subject-matter expert's sign-off against the seven-item checklist, the main approval of this stage | Plan approval | documented |
| S3.4 | A source's proposed tier, before it is relied on in a citation | Plan approval | suggested |

There is no separate approval row for S3.3. Layer 3 records what S3.2 already approved, rather than adding a further sign-off of its own; Stage 1's index uses this same pattern for S1.4b and S1.4c sharing one row. See [Human roles, gates and batching](../human-roles-gates-and-batching.md) for what each gate kind means and who can fill each role.

## Reading exit codes

Every script in this guide exits 0 when it ran and found nothing that fails, 1 when a check failed, and 2 for a usage or input error. Read the exit code right after running a command: `echo $?` on macOS and Linux, `echo $LASTEXITCODE` in PowerShell. Each sub-stage page says what an exit code means for its own script. One exception in this stage: [X-S3-04](tiering-and-remediation.md#scripts) always exits 0 unless its own input is unusable, since a source's tier distribution is a judgment call for a person, not a hard failure.

## Artifacts

- Flagged-claims list: claims a citation check or a person's quick read raised. Defined on [S3.1](layer-1-automated-detection.md).
- Deep-verification notes and a signed-off chapter: a subject-matter expert's per-claim judgment and final sign-off. Defined on [S3.2](layer-2-expert-review.md).
- A change log, per-claim records, per-chapter metadata, a per-reference matrix, and a version-history entry: what Layers 1 and 2 found, recorded. Defined on [S3.3](layer-3-audit-trail.md).
- A per-source tier record and an escalation-matrix row: a source's credibility, and a flagged defect's triage. Defined on [S3.4 and S3.5](tiering-and-remediation.md).

## What is documented versus suggested

Three points in Stage 3 are this guide's own call, not [the project notes](../glossary.md#reference-implementation)'. What the project notes describe for source tiering's own companion sub-stage reads, on inspection, as an escalation matrix: a defect's type, severity, the action it calls for, an owner role, and a response-time target. It is not the ranked, hour-estimated backlog an earlier reading of the source material assumed. [S3.4 and S3.5](tiering-and-remediation.md) states this correction plainly and uses the escalation matrix as the sourced content instead. The review-record status vocabulary (`accurate`, `needs-review`, `reject`, `unverifiable`) is another: the project notes describe the Content Audit pass itself, but not this exact four-word list, so [S3.2](layer-2-expert-review.md) states one. The third is `source_tier_check.py`'s own warning threshold, no more than a quarter of admitted sources at Tier 3 or below. The project notes give no such number, so this guide picks one as a starting value, not a rule.

## First actions for a new team

Suggested:

- Decide who fills the [content quality lead](layer-1-automated-detection.md#steps) and [subject-matter expert](layer-2-expert-review.md#outcome) roles before Stage 3 starts.
- Confirm a chapter has cleared Stage 2's own closing checks before running Layer 1 automated detection against it.
- Tier each source as it is admitted, rather than waiting until this stage's own check runs at the end.

This page states, once for all of Stage 3: the prompts here are samples, written for this guide and not run against any model in this build. The scripts were tested offline on synthetic data. Every threshold is a starting value, not a rule. See [Platform requirements](../platform-requirements.md) for what a platform must offer at this stage.

Next: [S3.1 Layer 1 automated detection](layer-1-automated-detection.md).
