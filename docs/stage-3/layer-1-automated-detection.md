---
title: "S3.1 Layer 1 automated detection"
parent: "Stage 3 Review and verification"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-25"
stage: "S3"
sub_stage: "S3.1"
prompts: ["P-S3-01"]
scripts: ["X-S3-01"]
---

# S3.1 Layer 1 automated detection

## Outcome

A chapter's claims are scanned for a missing or invalid citation and
classified by a four-type [hallucination](../glossary.md#hallucination)
taxonomy, quickly and before a person's much more expensive review
time is spent on the same chapter. A claim, here, is any statement in
the chapter's own text that names or implies a fact a source is meant
to back up, from a definition to a described command's behavior.

## Where it fits

This sub-stage takes in a finished, revised chapter from
[Stage 2](../stage-2/index.md), already closed out with a chapter
summary and a passed prerequisite check. It hands on flagged claims to
[S3.2](layer-2-expert-review.md), where a subject-matter expert gives
each one a closer look. A chapter with no flagged claims still moves
on to Layer 2, since Layer 1 only screens for a missing or invalid
citation, not for whether every well-cited claim is actually correct.

## Why this way

Layer 1, the first of this stage's three
[verification layers](../glossary.md#verification-layer), is meant to
catch the cheapest, most mechanical class of problem: a claim with no
real source behind it, or one whose cited source is not actually
admitted. Sorting that out first means Layer 2's much more expensive
review time goes to claims that genuinely need a person's judgment,
not to ones a script could have caught. This page uses the
[basis labels](../stage-1/index.md#basis-labels) defined on the Stage 1
index.

## Steps

| Step | Who | Basis |
|---|---|---|
| Run the claim source check across the chapter's claims | Script | suggested |
| Classify any claim the check could not resolve, or that a person flags on a quick read, by the four-type taxonomy | Agent | documented for the taxonomy; suggested for who classifies, since [the project notes](../glossary.md#reference-implementation) do not say |
| Do a category-by-category manual pass on the kinds of claims a script cannot judge, such as a specific quoted number or a named process step | Person | documented |
| Decide which flagged claims are handed off to Layer 2 | Person | suggested |

This guide calls the person who does the manual pass above the
**content quality lead**. The project notes describe the activity, a
pass through the kinds of claims a script cannot judge, but not this
role name; this guide gives it one for clarity.

Only the first of these steps is automated tooling in the sense this
page means it: a script doing fixed, rule-based work. Classifying a
flagged claim by the taxonomy below is agent work, guided by a
person's own quick read where the check could not resolve something
by itself. The category-by-category manual pass and the decision on
what gets handed off are done by a person outright. Calling this
sub-stage "automated detection" names its fastest, cheapest step, not
everything that happens in it.

## The four automated-detection checks

The project notes describe four automated-detection checks, adapted
from a third-party evaluation method this guide does not name. Each
checks one property of a claim against the source it is meant to rest
on (documented):

- **Faithfulness**: whether the claim's text matches what the
  retrieved source actually says.
- **Context precision**: whether it uses only the relevant detail,
  without over-generalizing.
- **Answer relevancy**: whether it actually addresses the learning
  objective it sits under.
- **Harmfulness**: whether it could mislead a learner or create a
  safety or compliance risk. A claim that fails this check is rejected
  outright, not corrected.

This guide's own sample script only automates a narrow slice of the
first check: whether a claim's citation resolves to an admitted source
at all, not whether that source's own words actually back the claim.
Context precision, answer relevancy and harmfulness, and a closer read
of faithfulness itself, stay an agent's or a person's own judgment call
in this guide's sample, the same way the manual category pass above
already covers the kinds of claims a script cannot judge.

## The four-type hallucination taxonomy

The project notes also document a four-type taxonomy for classifying
any claim that a check or a quick read flags (documented):

- **Factual**: a specific claim stated more strongly than its source
  supports, the most common type.
- **Reasoning**: true premises that lead to an invalid conclusion.
- **Contextual**: a true statement placed in the wrong context.
- **True fabrication**: an invented number or claim with no source at
  all, the most serious type.

## A caution about a validator that goes quiet

A pattern worth carrying into any automated check like this one:
confirmed by reading one validator's own code together with the real
directory listing it was meant to match, a check whose file-matching
pattern goes stale after files are renamed can find zero files to
check, and still silently overwrite its own tracked results with empty
data, instead of failing loudly. A similar pattern, inferred from
reading two more scripts but not run to confirm, appears to affect
them as well. Left uncaught, a failure like that prints a clean-looking
summary line with nothing real behind it, and a person who checks only
the exit code, not what the check actually printed, could easily read
that as every claim having passed. `claim_source_check.py` is designed
to fail loudly instead of taking that path: pointed at a source folder
with zero admitted sources, it exits with a usage error rather than
quietly reporting every claim as a gap.

## Artifacts and formats

- Claims list (`claims.json`, the format `claim_source_check.py`
  reads): a list of objects, each with `claim_id`, `text` (the claim's
  own wording) and `source_id` (the source it cites). The sample lists
  four claims paraphrasing Chapter 1's own content.
- Flagged-claims list: the claims the check or a person's quick read
  raised, each with a taxonomy type and a one-line reason. Prompt
  P-S3-01 drafts it as a short labelled list; the script only prints a
  pass or gap line per claim to standard output. Neither writes a
  file.

## Prompts

[P-S3-01 Claim scan and classify for one chapter](../prompts/s3/p-s3-01.md)
scans a chapter's own text for a claim with no citation or one outside
the admitted list, and classifies each flagged claim by the four-type
taxonomy above. It is written for this guide and has not been run
against any model in this build.

## Scripts

[X-S3-01 Claim source check](../scripts/s3/x-s3-01.md) reads a small
claims file and the running example's own admitted-sources folder. For
each claim, it checks whether the claim's cited source id names a
source file actually present in that folder.

Run it from the repository root, with the claims file and the
admitted-sources folder as its two arguments:

```bash
python3 -B scripts/s3/claim_source_check.py \
    scripts/sample_data/git_basics_stage3/claims/claims.json \
    scripts/sample_data/git_basics/sources
```

```text
pass: claim "C1" cites "SRC-001", admitted
pass: claim "C2" cites "SRC-002", admitted
pass: claim "C3" cites "SRC-006", admitted
gap: claim "C4" cites "SRC-009", no such source is admitted
claims=4 gaps=1
```

Four claims paraphrase [Chapter 1](../stage-2/structural-drafting.md)'s
own content. Three cite a source that is genuinely admitted, so they
pass. The fourth, C4, cites `SRC-009`, a source id that does not exist
among the running example's seven admitted sources, so the check flags
it as a gap. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 3 index
for what the exit code means; here it is 1, since one claim failed. No
break-on-purpose edit was needed to show this: the sample already
carries the one real flag.

A clean run of this check is not proof that a claim is true, only that
its citation resolves to an admitted source. It cannot tell you
whether that source's own text actually says what the claim states;
that is a person's job, described in
[Common failures](#common-failures) below.

The caution above asks for a second, short demonstration: what this
script does when it finds no admitted sources at all, rather than a
missing one. Pointed at an empty folder instead of the real sources
folder:

```bash
mkdir empty-sources
python3 -B scripts/s3/claim_source_check.py \
    scripts/sample_data/git_basics_stage3/claims/claims.json empty-sources
rmdir empty-sources
```

```text
claim_source_check.py: error: no admitted sources found in SOURCES_DIR
```

The exit code here is 2, a usage or input error, not 1. The script
never reports every claim in `claims.json` as a gap just because the
folder it was pointed at happens to be empty; an empty admitted-sources
folder is a setup problem to fix, not a finding about the claims.

## Definition of done

- The claim source check has run against the chapter's claims and the
  admitted-sources folder, and every gap it found has been looked at.
- Every claim the check could not resolve, or that a quick read
  flagged, has a taxonomy type and a one-line reason.
- The content quality lead has done the category-by-category manual
  pass.
- A person has decided which flagged claims are handed off to Layer 2.

## Common failures

- A claim whose citation resolves to a real, admitted source, but that
  source does not actually say what the claim states. This script only
  checks that the source exists; it cannot read the claim against the
  source's own text.
- The stale-check pattern described above: a source folder that looks
  populated but, because of a rename or a bad path, holds zero files
  the check recognizes.
- Treating context precision and answer relevancy as the same check.
  The first asks whether a claim over-generalizes past what the source
  supports; the second asks whether it addresses the learning
  objective it sits under. A claim can pass one and fail the other.
- Reading a clean run (`gaps=0`) as proof the chapter has no citation
  problem left. It only shows that every claim currently names an
  admitted source; the manual category pass below still has to look at
  the kinds of claims the check cannot judge on its own.

## Adapting to your platform

- `llm`: classifies a flagged claim by the four-type taxonomy, using
  P-S3-01.
- `file-read`: reads the chapter's own text and the admitted-sources
  folder.
- `structured-output`: ask for each flagged claim's taxonomy type and
  reason in a fixed shape, or convert a plain-text reply by hand.
- `shell`: runs the claim source check; without it, check each claim's
  cited source id against the admitted list by hand.
- `human-approval`: covers the manual category-by-category pass and
  the decision on which flagged claims are handed off.

## Where humans decide

- What the category-by-category manual pass covers, and which claims
  in it need a closer look.
- Which flagged claims, if any, are handed off to Layer 2 rather than
  resolved here.
- Whether a flagged claim's citation is simply missing, in which case
  a person can often add the right source id directly, or whether the
  claim itself needs Layer 2's closer read.

Next: [S3.2 Layer 2 expert human review](layer-2-expert-review.md).
