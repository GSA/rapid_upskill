---
title: "S4.7 Packaging and scope"
parent: "Stage 4 AI-tutor coaching"
nav_order: 5
status: "draft"
last_reviewed: "2026-09-25"
stage: "S4"
sub_stage: "S4.7"
prompts: ["P-S4-05"]
scripts: []
---

# S4.7 Packaging and scope

## Outcome

At the end of this sub-stage, a chapter's finished text, its
misconception catalog, and its protocol library exist as two kinds of
package. One is a set of bundle files a person can upload to a plain
chat session. The other is a package sized and shaped for one target
platform's own current limits. Neither package changes what the
chapter says; packaging only chunks and arranges material that earlier
sub-stages have already produced and, where needed, already had a
person approve.

## Where it fits

This sub-stage takes in a finished, reviewed chapter from
[Stage 3](../stage-3/index.md), the misconception catalog from
[S4.5](misconception-catalog-and-error-diagnosis.md), and the protocol
library from [S4.1 and S4.2](principles-and-protocol-library.md). This
sub-stage's own output is a package meant to reach a learner directly,
outside the chapter-production pipeline the earlier stages describe.

## Why this way

A platform's own size limits are real, and they vary by platform.
Packaging as its own, separate step means a chapter's own content does
not have to be redesigned every time a target platform changes. Only
the chunking and the reference files built around it need to change.

Keeping the two jobs in a fixed order also matters. Producing the
bundle files first, and only then reading a target platform's own
current limits, means the second job always starts from a platform's
own present-day figures, not from whatever limit an earlier build
happened to assume.

## Steps

| Step | Who | Basis |
|---|---|---|
| Produce size-bounded bundle files: combine a chapter's own drafted parts into files kept under a stated character cap, splitting an oversized range across more than one file so no single file exceeds the cap | Agent | documented |
| Prepare the content for a target platform: read that platform's own current size limits, then build whatever configuration and reference files it expects | Agent drafts; a person confirms the platform's current limits | documented |

[The project notes](../glossary.md#reference-implementation) describe
these as one builder prompt's two ordered jobs, not two separate
prompts. [P-S4-05](../prompts/s4/p-s4-05.md), below, follows the same
order.

A 500,000-character cap per bundle file is documented as one stated
cap among [the reference implementation](../glossary.md#reference-implementation)'s
parameters. This guide's own scripts and pages elsewhere use character
or word counts of their own, unrelated to this figure, so do not
confuse the two. Treat the 500,000-character figure exactly as what it
is: one project's own working number, useful as an example of the
shape a per-file cap takes. It is not a rule this guide asks a reader
to copy onto a different platform.

A target platform's own real limits should always be checked at build
time, never assumed from a printed number anywhere, including the
500,000-character figure just given. The project notes' own
platform-limit documents disagree with themselves in more than one
place, and at least one figure among them is stated as unverified even
by its own source. A number that looked settled when a project's own
documentation was written can already be out of date by the time a
reader builds against it. Two of that project's own documents can even
disagree with each other about the same platform on the same day. Read
a platform's own current documentation immediately before a build, not
once at the start of a project and never again.

## A caution before citing a file's name or size

More than one project document cites a companion file by a name that
does not match any real file on disk. One of those documents names the
same file two different wrong ways within its own text. A packaged
conversational-agent format's own description of one of its own files
understates that file's real, current size by roughly a fifth. None of
this is unusual on purpose: it is the kind of drift that happens
whenever a document is written once and the file it names keeps
changing underneath it.

Two habits guard against this drift in a reader's own package
manifest. Re-measure a file's size before citing it, rather than
trusting an inherited number forward from an older document. Confirm a
cited filename actually exists, under the exact name given, before
naming it in a manifest, rather than assuming a plausible-sounding name
is the real one. Neither check takes long, and both are cheap next to
the cost of a learner-facing package that points at a file the
platform cannot find, or that quietly runs larger than the manifest
claims.

## Worked illustration

Chapter 2 of [the running example](../running-example.md) (Branching
and merging), once Stage 3 has reviewed it, supplies the sample
chapter text for this illustration. An author picks a size limit for
chunking that is deliberately small: 2,000 characters per bundle file.
This limit is clearly labelled as this guide's own arbitrary choice for
the illustration, not the reference implementation's own cap and not a
limit to copy. Chapter 2's own drafted text runs longer than that, so it
is combined and split into two bundle files, `part1.md` and `part2.md`,
each measured and confirmed to fall under the chosen limit.

A minimal package for a hypothetical target platform then draws on
those two bundle files. The package holds a short **behavior file**: a
few sentences telling the tutor to answer only from the chapter text
supplied, and to apply the protocol library's named protocols rather
than improvise. Alongside it sits a small set of reference files: the
two bundle files, the chapter's own misconception-catalog file, and a
short excerpt of the protocol library.

Before building this same kind of package for a real target platform,
a reader would read that platform's own current documentation for its
own file-count, file-size, and prompt-length limits. A platform's own
published limits change over time and, in the project notes' own
experience, sometimes disagree with themselves. Nothing above, including the
2,000-character illustration limit and the 500,000-character
reference-implementation figure earlier on this page, should be
assumed to still hold for any real platform without checking it fresh.
Prompt [P-S4-05](../prompts/s4/p-s4-05.md) works through this same
scenario.

## Artifacts and formats

- **Bundle files**: a chapter's own drafted parts, combined and split
  so that each file stays under a stated character cap. A chapter that
  fits under the cap needs only one bundle file; a longer chapter
  needs as many as it takes to keep every file under the cap.
- **Package manifest**: a short list naming every file a package
  needs, one line per file. Each line gives the file's name exactly as
  written on disk, its role in the package (a bundle file, the
  misconception catalog, the protocol library, or a behavior file),
  and its freshly measured size. That size is never copied forward
  from an earlier version of the same manifest.

## Prompts

[P-S4-05 Package a chapter bundle](../prompts/s4/p-s4-05.md) chunks a
chapter's finished text into size-bounded bundle files, then drafts
the reference files a target platform's own package needs. It is
written for this guide and has not been run against any model in this
build; treat it as a starting point and adapt it.

## Scripts

None; the project notes describe no code for this sub-stage.

## Definition of done

- Every bundle file measures under the stated character cap, confirmed
  by an actual count, not an estimate.
- An oversized range is split across more than one bundle file, never
  truncated to fit inside one file.
- The target platform's own current size limits have been read
  immediately before this build, not carried over from an earlier
  build or from this page's own reference-implementation figure.
- Every file named in the package manifest exists on disk under the
  exact name given.
- Every file size in the package manifest is freshly measured, not
  copied forward from an earlier citation.

## Common failures

- Trusting an inherited file-size citation without re-measuring it, so
  a manifest states a size the real file no longer has.
- Citing a companion file that does not exist under the name cited,
  leaving a reader to search for a file that was never there.
- Packaging content for a platform's limit that has since changed, so
  a package that fit when it was built no longer fits when it is used.
- Treating one project's own stated cap, such as the
  500,000-character figure on this page, as a rule that applies to
  every platform, rather than one project's own working number.

## Adapting to your platform

- `llm`: drafts the split bundle-file text, the behavior file, and the
  package manifest a target platform's package needs.
- `file-read`: reads the chapter's finished text, the misconception
  catalog, the protocol library, and a target platform's own current
  limit documentation before any file is built.
- Without `file-read`, paste the chapter text and the platform's own
  current limits into the prompt by hand before running it.
- `human-approval`: pauses before a packaged bundle reaches a learner,
  and before a build proceeds on any target platform's current limits.
  A platform with no built-in approval step still needs a person to
  read and record each one, such as in a shared document or a
  version-control commit message.

## Where humans decide

- Approving a packaged bundle before it reaches a learner, the same
  way an earlier gate approves a chapter, a guardrail policy, or a
  chapter's own misconception-catalog entries before first use.
- Confirming the target platform's own current limits before every
  build, not only the first one, since a platform's own published
  limits can change between one build and the next.
- Deciding what to do when a platform's own documentation disagrees
  with itself about a limit. No script can settle a genuine
  disagreement in a platform's own published figures; a person picks
  the more conservative reading and records why.

Next: [Stage 4 AI-tutor coaching](index.md).
