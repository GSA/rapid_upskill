---
title: "Evidence and limitations"
nav_order: 76
status: "draft"
last_reviewed: "2026-09-26"
prompts: []
scripts: []
---

# Evidence and limitations

## Outcome

By the end of this page, a reader can name exactly what evidence backs
this guide's own claims about how the [reference
implementation](glossary.md#reference-implementation) actually
performed, and exactly what has not been shown. The page states three
results this guide is approved to report about the reference
implementation's own certification-facing work. It also states the
source material's own admitted limits on all of its evidence, and a
plain statement that the source material reports further results this
guide does not state anywhere.

## Where it fits

This page sits at the top level, cross-cutting every stage and
workstream rather than belonging to any one of them. Several
already-published pages already carry an evidentiary caveat of their
own. [Pipeline overview](pipeline-overview.md#what-the-framework-does-not-claim)
lists what the framework's own design does not claim.
[S3.2 Layer 2 expert human review](stage-3/layer-2-expert-review.md#this-stages-own-honest-gap)
states that expert review and the audit trail are specified, but no
completed record of either was found. [Human roles, gates and
batching](human-roles-gates-and-batching.md#what-the-framework-says-people-do)
makes a close point about the people-facing roles the framework
assigns, adding that no record found is not evidence that the
assigned work did not happen. This page does not restate any of that;
it links back to each instead. It adds a narrower set of facts none
of those pages covers: three specific results about the reference
implementation's own certification-facing work, and the limits the
source material states on all of its evidence. A reader who
wants the whole evidentiary picture in one place, rather than
gathered from four pages by hand, can start here and follow the three
links above for the rest.

## Why this way

Most of this guide describes the framework as it is specified: a
design, laid out stage by stage, that a team can adopt and run for
itself. Specifying a design is not the same as showing that a run of
it produced a given result. Keeping that line visible matters for a
reader deciding how much weight to place on any one part of the
method before adopting it. This page draws that line in one place, so
a reader does not have to gather every stage page's own caveat into
one picture alone.

A basis label such as `documented` or `suggested`, used throughout the
rest of this guide, states whether a design detail traces to a real
source or to this guide's own reading of a gap. It says nothing about
whether the design, once run, produced a given outcome. This page is
the one place the two questions meet. It takes the same basis
vocabulary and applies it to results rather than to design details.
That lets a reader tell, for any one claim, whether it describes what
the framework specifies or what a run of it actually showed.

## Steps

This page's own Basis column uses a narrower label than the rest of
the guide, alongside the usual `documented`. **The manuscript's own
self-report** marks a claim that comes from the unpublished source
manuscript's own account of its work. It is stated here in the exact
substance this guide is approved to use, and not checked further by
this guide beyond that approval. `documented` keeps its usual meaning
in the row it appears in below: traceable to a real source. It states
this guide's own observation about scope, not a result the source
manuscript reports about itself.

| Step | Who | Basis |
|---|---|---|
| State three results about the reference implementation's own certification-facing work, in the exact substance this guide is approved to state | This guide | the manuscript's own self-report |
| State the source manuscript's own admitted limits on all of its evidence, paraphrased rather than quoted | This guide | the manuscript's own self-report |
| State plainly that the source manuscript reports further results beyond the three above, without naming or counting any of them | This guide | documented |

### The three approved results

Each of the three results below is a different kind of evidence: a
real institutional record, a real institutional review, and a stated
absence. None stands in for either of the other two, and none is
read here as adding up to more than what it states on its own.

- A certification's own exam records, cited in the source material,
  show three attempts that have passed to date, with fourteen further
  attempts in progress when the source material was prepared. This
  guide states these two counts and no rate.
- An accrediting body assessed the program against its own
  administrative and structural standards. That assessment did not
  cover the accuracy of the program's content.
- No psychometric pilot with live examinees has tested the test
  questions this framework produces. [Pipeline
  overview](pipeline-overview.md#what-the-framework-does-not-claim)
  already states this design gap for the framework generally; it is
  stated again here because a reader of this page needs the reference
  implementation's own three results together, not spread across two
  pages.

### The source manuscript's own stated limits

The source manuscript states several limits on its own evidence.
Paraphrased here, never quoted:

- Its evidence is design work, the artifacts it produced, and outside
  checks such as the two results above, not a controlled comparison
  against an alternative approach.
- No claim it makes reaches beyond what its own observed numbers show.
- The certification exam's own content, and how it is graded, sit
  outside the framework's control; the certification's own owner sets
  both.
- The subject-matter-expert sign-off layer [Stage 3](stage-3/index.md)
  specifies is described in full, but the source manuscript does not
  show a complete, evidenced execution record for it.
- One remediation item found during the work stays tracked, not
  resolved.
- Each of the three validation signals carries a limit taken alone.
  The source manuscript states that their evidentiary weight comes
  from all three pointing the same way together, not from any one
  signal by itself.

### Beyond this page's scope

This guide's own research into the source material found further
results beyond the three stated above. None of them is named,
counted, or described here, or anywhere else in this guide: they sit
outside what this guide is approved to report. Treat that boundary as
a fact about this guide's own scope, not as a hint about what a wider
report on the reference implementation might show, in either
direction. This guide's own standing practice is to add an
evidentiary claim only once it is explicitly cleared for a page. The
boundary named here follows that same practice, not a one-off
decision made for this page alone.

## Worked illustration

None. This page states a consolidated evidentiary position, not a
procedure with a run to demonstrate. [Stage 4's own
index](stage-4/index.md) and [Operating practices' own
index](operating-practices/index.md) set the same precedent: a
synthesis page whose own material does not call for one.

## Artifacts

None new. This page produces no file; it states a position, and links
back to where each supporting page already lives.

## Prompts

None. This page synthesizes and cross-references evidence already
gathered for this guide rather than drafting new content, so no
prompt drives any part of it.

## Scripts

None, for the same reason as Prompts. No sample data accompanies this
page.

## Definition of done

- Every claim on this page carries the evidentiary tier stated beside
  it.
- No claim on this page reaches beyond what its own tier supports.
- A reader can name, from this page alone, the three approved
  results, the source manuscript's own stated limits, and the fact
  that further results exist outside this guide's approved scope.
- A reader can point to the three already-published pages this page
  cross-links, and can tell that this page adds new facts rather than
  repeating theirs.

## Common failures

- Treating a design specification, described throughout the rest of
  this guide, as if it were a demonstrated result.
- Treating an in-progress or preprint citation, elsewhere in the
  guide, as an established finding.
- Reading the fact that further results exist outside this guide's
  scope as a hint about what those results show, in either direction.
- Reading "no completed record was found," stated on the pages this
  page links back to, as evidence that a role or a check did not
  happen. Those pages already state plainly that it is not.
- Assuming the three results on this page describe every
  certification-facing claim the source material makes, when this
  page states plainly that further results exist outside its own
  scope.

## Adapting to your platform

None. This page describes the reference implementation's own
evidentiary state as the source manuscript reports it. It names no
step for a reader's own team to run, so nothing here changes with
platform.

## Where humans decide

Whether a reader's own team needs a stronger evidentiary bar than the
reference implementation has cleared, before adopting any part of the
method. The reference implementation's own team decided what evidence
to gather and report. A reader's own team decides separately how much
of that evidence justifies adopting any one part of the method for
its own use. This guide states the evidentiary record above; it does
not set a bar for what counts as enough, and it states plainly that
it cannot make that judgment for the reader.

Next: [Glossary](glossary.md).
