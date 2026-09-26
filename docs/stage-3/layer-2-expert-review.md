---
title: "S3.2 Layer 2 expert human review"
parent: "Stage 3 Review and verification"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-25"
stage: "S3"
sub_stage: "S3.2"
prompts: ["P-S3-02"]
scripts: ["X-S3-02"]
---

# S3.2 Layer 2 expert human review

## Outcome

At the end of this sub-stage, every claim [S3.1](layer-1-automated-detection.md)
could not resolve has a **subject-matter expert**'s judgment: a
deep-verification note, a status, and, once the chapter clears a
seven-item checklist, a sign-off. A subject-matter expert is the
specialist who does this checking work, named in the
[verification layers](../glossary.md#verification-layer) as Layer 2,
expert review. A signed-off chapter's findings, not its raw text, are
what the next sub-stage records.

## Where it fits

This sub-stage takes in the flagged-claims list that
[S3.1](layer-1-automated-detection.md) hands off. It hands on a
signed-off chapter's findings to [S3.3](layer-3-audit-trail.md).

## Why this way

A script can find a missing citation. Only a person with real
subject-matter depth can judge whether a claim that does cite
something is actually right, current, and appropriately hedged. A
fixed checklist and a fixed disagreement-resolution order exist for
the same reason a chapter's other checks are fixed. Without them, one
subject-matter expert's sign-off could mean something different from
another's. A disagreement between two experts could also stall the
chapter indefinitely, with no agreed way to move it forward. This page
uses the [basis labels](../stage-1/index.md#basis-labels) defined on
the Stage 1 index.

## Steps

| Step | Who | Basis |
|---|---|---|
| Draft a deep-verification note for each flagged claim: a status, the issue, supporting evidence and a suggested correction | Agent | suggested for who drafts; documented for the note's own shape |
| Do the Content Audit pass: one pass over the whole chapter, marking each passage accurate, needs-review, reject or unverifiable | Subject-matter expert | documented for the pass itself; suggested for this exact four-word vocabulary |
| Do Deep Verification on every flagged item, producing a per-claim report | Subject-matter expert | documented |
| Sign off against the seven-item approval checklist | Subject-matter expert | documented |
| Resolve a disagreement between two subject-matter experts with the five-step protocol below | Subject-matter expert | documented |

Three phases make up this workflow, each with a rough timebox that is
[the reference implementation](../glossary.md#reference-implementation)'s
parameters, not a rule to copy: **Content Audit** (roughly 2 to 4
hours per chapter) is the pass above that covers the whole chapter;
**Deep Verification** (roughly 4 to 6 hours per chapter) is the closer,
per-claim pass on every flagged item; **Approval** (about a day) is
where a subject-matter expert signs off against the checklist below.
The same or a different subject-matter expert can do Content Audit and
Deep Verification. The two passes cover different ground: Content
Audit reads the whole chapter fresh, including passages
[S3.1](layer-1-automated-detection.md) never flagged, while Deep
Verification works only through the flagged-claims list this sub-stage
took in. A chapter can pass Content Audit with no flagged claims left
unresolved. It can still fail Deep Verification on one claim whose
citation looked fine to a script but does not hold up under a closer
read.

The four status words a subject-matter expert marks a passage with
carry a plain, working meaning:

- **accurate**: the claim checks out as stated.
- **needs-review**: the claim is uncertain, overstated, or missing a
  hedge, and a person should look again before it ships.
- **reject**: the claim is wrong and should be corrected or removed.
- **unverifiable**: no admitted source settles the claim either way,
  so it is neither confirmed nor denied.

## The seven-item approval checklist

A subject-matter expert signs off only once every item below is true
for the chapter:

1. Every claim has been verified or corrected.
2. Every unsourced metric has been cited or removed.
3. Every procedure or command has been verified.
4. Every reference actually exists.
5. No cross-chapter contradiction remains.
6. Terminology is consistent with the rest of the guide.
7. The chapter's complexity is appropriate for its place in the
   sequence.

## Disagreement resolution

When two subject-matter experts read the same passage differently,
this sub-stage's protocol runs in this order:

1. Document both positions, each with its own reasoning.
2. Each reviewer cites the sources behind their position.
3. If the sources disagree on a testable fact, prefer the newer
   publication.
4. If both readings are equally well supported, present both in the
   text rather than picking one.
5. Take it outside the pair of reviewers if the point is central to
   one of the chapter's own learning objectives.

The last step is deliberately not called "escalate" on this page: this
guide reserves that word for the escalation matrix at
[S3.4 and S3.5](tiering-and-remediation.md), a different mechanism for
a different kind of problem. The project notes do not name who a
disagreement goes to once it leaves the original pair. This guide's own
suggestion, where the project notes are silent: bring in a third
subject-matter expert, or whoever holds this program's own final
sign-off authority, to make the call.

## The batch-and-pause pattern

Beyond the steps above, several of
[the project notes](../glossary.md#reference-implementation)' own review
workflows share one shape. A person supplies written feedback, and the
work is chunked into small [batches](../glossary.md#batch). A capped
number of parallel agents each take one batch, and findings are logged
per item. The same person's explicit permission is then needed before
the next batch starts. This is the general shape a review round can
take, documented across more than one of the reference
implementation's own workflows. It is not a step this sub-stage's own
numbered steps above add.

## This stage's own honest gap

[Pipeline overview](../pipeline-overview.md#what-the-framework-does-not-claim)
already states the limit that applies here and at the next sub-stage:
"Expert review (Layer 2) and the audit trail (Layer 3) are specified;
no completed record was found. No record found is not evidence that
something did not happen." This page does not restate that finding in
different words. The checklist, the protocol and the script run below
describe what this sub-stage specifies, not a record that a real
chapter went through it. A team adopting this sub-stage still has to
build its own record of who reviewed what, and when, since the
sourced design does not by itself leave that trail behind.

## Artifacts and formats

- Deep-verification notes: one per flagged claim, each with a status,
  the issue, supporting evidence and a suggested correction. Drafted
  with the prompt below.
- Signed-off chapter: a chapter whose subject-matter expert has
  checked every item on the seven-item checklist above and approved
  it.
- Review-flags record (`flags.json`, the format the script below
  reads): a list of objects, each with `claim_id`, `status` (one of
  `accurate`, `needs-review`, `reject`, `unverifiable`), `reason`, and,
  when the status is `needs-review` or `reject`, `suggestion`. The
  sample lists four claims, one of each status, paraphrasing the
  running example's own Chapter 1 content.

## Prompts

[P-S3-02 Deep-verification note](../prompts/s3/p-s3-02.md)
drafts a deep-verification note for one flagged claim, from the
claim's text, the reason it was flagged, and an excerpt from the
source it cites. It is written for this guide and has not been run
against any model in this build.

## Scripts

[X-S3-02 Review record check](../scripts/s3/x-s3-02.md) reads a
review-flags file. It checks that every flag's status is one of the
four allowed values, that every flag gives a reason, and that a flag
whose status is `needs-review` or `reject` also gives a suggestion. It
does not judge whether a status, a reason or a suggestion is actually
right. That stays a subject-matter expert's own call. It writes no
file; its printed lines are a record to copy elsewhere, not a saved
file.

Run it from the repository root:

```bash
python3 -B scripts/s3/review_record_check.py \
    scripts/sample_data/git_basics_stage3/review/flags.json
```

```text
claims=4 errors=0
```

All four sample flags pass: one `accurate`, one `needs-review` and one
`reject` each carry a `suggestion`, and the `unverifiable` flag needs
none. Break it on purpose by copying the file and removing the
`reject` flag's `suggestion` field, then running the check again on
the copy:

```text
missing-suggestion: claim "C3" status "reject" needs one
claims=4 errors=1
```

See [Reading exit codes](index.md#reading-exit-codes) on the Stage 3
index for what the exit code means. A clean run only shows that every
flag has the shape this sub-stage requires. It is not proof that a
status, a reason or a suggestion is actually correct, only that the
record around it is complete.

## Definition of done

- Every claim [S3.1](layer-1-automated-detection.md) flagged has a
  deep-verification note.
- A subject-matter expert has completed the Content Audit pass over
  the whole chapter.
- A subject-matter expert has completed Deep Verification on every
  flagged item.
- `review_record_check.py` runs clean on the chapter's `flags.json`.
- Every disagreement between two subject-matter experts is documented
  under the five-step protocol above.
- A subject-matter expert has signed off against the seven-item
  checklist.

## Common failures

- A flag whose status is `needs-review` or `reject` with no
  suggestion, which leaves a person nothing to act on. This is the
  finding `review_record_check.py` catches.
- A disagreement between two subject-matter experts left undocumented,
  so the chapter's sign-off hides a real, unresolved difference of
  opinion.
- Treating a batch's pause as itself a review. The
  [Stage 1 index](../stage-1/index.md#approvals)'s own S1.5 approval
  row names this same risk: a person saying "continue" is not the same
  as a person having looked.
- A Content Audit pass that only rereads the claims
  [S3.1](layer-1-automated-detection.md) already flagged, skipping the
  rest of the chapter. Content Audit's job is a pass over the whole
  chapter; Deep Verification is where the flagged-claims list narrows
  the work.

## Adapting to your platform

- `llm`: drafts each deep-verification note.
- `file-read`: reads the flagged-claims list, the chapter text and
  each cited source's excerpt.
- `structured-output`: ask for the four-part note directly in a fixed
  shape, or convert a plain-text reply by hand.
- `shell`: runs the review record check; without it, read
  `flags.json` by hand and check the same three things: a status from
  the four-word list, a reason, and a suggestion where the status
  calls for one.
- `human-approval`: covers every subject-matter-expert phase above and
  the final sign-off; a platform with no built-in approval step still
  needs a person to read and record each one somewhere, such as a
  shared document or a version-control commit message.

## Where humans decide

- Every status a subject-matter expert assigns, at either phase, since
  a script never assigns one of the four status words itself.
- Every issue, evidence line and suggested correction an agent drafts
  into a deep-verification note, before it is treated as settled.
- Every disagreement between two subject-matter experts, and whether
  it needs to be taken outside the pair.
- The sign-off itself; see the
  [Stage 3 index](index.md#approvals) for what kind of approval this
  is and how to record it.

Next: [S3.3 Layer 3 audit trail](layer-3-audit-trail.md).
