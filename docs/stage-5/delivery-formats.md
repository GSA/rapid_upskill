---
title: "Stage 5 delivery formats and lessons"
parent: "Stage 5 Assessment development"
nav_order: 6
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
prompts: ["P-S5-06"]
scripts: ["X-S5-06"]
---

# Stage 5 delivery formats and lessons

## Outcome

At the end of this stage, a finished [item bank](../glossary.md#item-bank)
of [stems](../glossary.md#stem) reaches a learner through more than one
delivery format. Every stem the bank holds has been checked against at
least one of those formats. A script only reports where that check
fails; a person still decides what a real gap means and what, if
anything, to do about it. This stage's own history of delivery tooling
also holds real, generalizable lessons about keeping that tooling safe.
This page states three of them plainly, in general terms only.

## Where it fits

This page takes in an assembled quiz from
[S5.6 Quiz and exam assembly](quiz-and-exam-assembly.md): finished
stems, an answer key, point values, and feedback text, all checked
against the bank they were drawn from. It closes out [Stage 5](index.md),
the last stage this guide describes in the framework's own order. What
happens after a package leaves this page is not something this guide
follows: whatever platform actually puts it in front of a learner is
its own separate concern. Only the kinds of package this stage hands
off are in scope here, along with how a reader checks that every stem
in the bank ended up in one of them.

## Why this way

Every earlier sub-stage in this stage checks one stem, or one bank, on
its own terms: a stem's own format, an answer key's own references, a
bank's own difficulty and domain mix. None of those checks says
anything about whether a stem that passed every one of them actually
reaches a learner. Checking deliverable-kind coverage as its own, final
step catches a failure mode none of the earlier checks can see. A stem
can be entirely correct, sitting in a bank that is entirely correct,
and still never be assigned anywhere a learner would ever open it.

## The delivery formats

Four deliverable kinds recur across this guide's own sample data,
described here generically, with no real counts. They are a large,
blueprint-tagged item bank; a small number of full-length mock exams,
each under a stated time limit; one graded quiz per chapter; and a
handful of shorter, standalone practice tests. The kinds themselves are
documented in [the project notes](../glossary.md#reference-implementation).
How this guide's own sample groups a small set of stems into them is
this guide's own suggestion, sized for the running example rather than
for a real program's own scale.

None of the real counts behind these four kinds appear anywhere in this
guide: not a bank size, not a mock-exam or chapter-quiz or
practice-test count, and not a time limit or a question-type mix. Each
of those is the reference implementation's own real result, produced
once for one program. None of them is a design rule this guide asks a
reader to copy onto a program of a different size.

The same stem can belong to more than one kind at once. A stem drafted
for one chapter's quiz can also sit in the bank; a stem built for the
bank can also appear, unchanged, inside a mock exam later. Assigning a
stem to a deliverable kind, not drafting it again, is what this stage's
last step actually does.

The four kinds are not interchangeable in how they treat a learner. A
chapter quiz is frequent and low-stakes: a learner takes one soon after
finishing a chapter, and gets immediate, explanatory feedback on every
answer. A mock exam sits at the other end: infrequent, high-stakes, and
evaluative, giving little or no feedback until the whole thing ends,
the same way the real exam it rehearses would. A practice test sits
between the two. It is a cumulative check that can pull stems from more
than one chapter, still meant to help a learner study rather than to
grade them, but less immediate than a single chapter's own quiz. A bank
is not itself something a learner sits; it is the pool every other
format draws its stems from.

## Three lessons from this stage's own script history

This stage's own history of delivery tooling holds three lessons worth
stating plainly, without naming any script, file, or real content. Each
one below is documented: a real, confirmed pattern this stage's own
research found, restated here in general terms only.

The first: never destroy real, already-delivered content with no
confirmation step, and never truncate a shared record before the
content that would replace it actually exists. A tool that assumes
today's state matches an earlier assumption, and acts on it with no
check and no way back, will eventually meet a day when the assumption
no longer holds. The cost of being wrong once, at that point, is real,
already-delivered content that cannot be recovered. The delivery
coverage check below never writes any file at all, so it cannot repeat
this particular mistake; it only reads and reports, and a person still
decides whether to act on what it reports.

The second: keep a batch, version, or chapter label consistent across
every document and script that names it. A label drifts quietly, one
small edit at a time, rather than all at once, which is exactly why it
is easy to miss: each single edit still looks reasonable on its own.
Two documents that disagree about what one label actually means will
eventually send a later reader, or a later script, to the wrong range
of content, with nothing in either document loud enough to say so.

The third: reject an out-of-range or unrecognized value loudly, with a
clear message, rather than quietly treating it as if it were the first
valid option. [S5.6](quiz-and-exam-assembly.md)'s own page already
applies this to an answer letter that falls outside a stem's real
option range. The same principle applies here to a deliverable-kind
assignment: a value nobody recognizes is worth a clear, visible
finding, not a silent default that lets a mistake pass as if it were a
real decision. A script that fails loudly on a bad value costs a reader
a moment's attention; a script that accepts it silently costs nothing
until the day someone relies on what it quietly got wrong.

## Worked illustration

The two clean, finished stems from
[S5.3 and S5.4](distractors-and-format-rules.md), `STEM-2.1-001` and
`STEM-2.1-002`, are the whole bank for this illustration.
`STEM-2.1-001` is assigned to two deliverable kinds, the bank and its
own chapter's quiz:

```json
{
  "STEM-2.1-001": ["bank", "chapter_quiz"],
  "STEM-2.1-002": []
}
```

`STEM-2.1-002` is deliberately left with an empty list: a stem that
made it into the finished bank but was never actually assigned to a
deliverable a learner would see. Nothing about `STEM-2.1-002` itself is
wrong; its own [distractors](../glossary.md#distractor), each tied to
one [misconception](../glossary.md#misconception), already passed the
format check earlier in this stage. The gap sits in the assignment
step, not in the stem.

## Scripts

[X-S5-06 Delivery coverage check](../scripts/s5/x-s5-06.md) reads a
delivery manifest and a stem file, and warns about every stem the
manifest assigns to zero deliverable kinds. It checks one direction
only: it never reports a manifest entry naming a stem id no longer in
the bank. It also skips a stem entry it cannot make sense of. One entry
in the sample stem file is marked as a deliberately broken copy, kept
only for a different script's own demonstration; a normal run here
skips that entry too, so it never counts toward the totals below.
Like the [bank composition check](difficulty-and-blueprint-bank.md)
earlier in this stage, it never exits 1 on its own; a gap here is a
person's decision, not a hard failure the script can settle by itself.
Run it from the repository root:

```bash
python3 -B scripts/s5/delivery_coverage_check.py \
    scripts/sample_data/git_basics_stage5/delivery/manifest.json \
    scripts/sample_data/git_basics_stage5/stems/stems.json
```

```text
gap: "STEM-2.1-002" is in the bank but not assigned to any deliverable
stems=2 unassigned=1
```

The checked-in manifest already carries the one real gap this stage's
own sample data plants on purpose, so no break-on-purpose edit is
needed to show the script working. `STEM-2.1-001` counts toward the
total but is not flagged, since its own list holds two kinds.
`STEM-2.1-002` counts toward the total and is flagged, since its own
list is empty. The summary line counts every stem the script read and
every gap it found. See
[Reading exit codes](../stage-1/index.md#reading-exit-codes) on the
Stage 1 index for what an exit code means generally. This script's own
exit code stays 0 here, and would stay 0 with more gaps too, since
finding one is a person's decision to make, not a failure of the
script itself.

## Prompts

[P-S5-06 Assign a stem to a deliverable](../prompts/s5/p-s5-06.md)
assigns one finished stem to one or more deliverable kinds and gives a
one-line reason for each assignment. It is written for this guide and
has not been run against any model in this build; treat it as a
starting point and adapt it. The stem text it reads is data, never
instructions, even where a sentence inside it is phrased as one.

## Artifacts and formats

This page produces one artifact: a delivery manifest, a JSON object
mapping each stem id the bank holds to the list of deliverable kinds it
has been assigned to. An empty list and a missing entry both mean the
same thing: this stem has not yet been assigned anywhere a learner
would see it.

## Definition of done

- Every stem in the finished bank has been checked against the
  delivery manifest, not only assigned once and forgotten.
- Every stem the manifest names still exists in the bank; a stem
  removed from the bank has also been removed from the manifest, not
  left pointing at nothing.
- Every gap the delivery coverage check reports has a recorded
  decision: add the stem to a deliverable, or leave it out on purpose,
  with a reason either way.
- A person has approved the delivered package before it reaches a
  learner.

## Common failures

- A bank item never assigned to any deliverable, so a learner never
  actually sees a stem that passed every earlier check in this stage.
- A deliverable manifest naming a stem id no longer in the bank, left
  over from an earlier version of the bank that has since changed.
- Treating one of the three script-history lessons above as too
  obvious to check for, when each one recurred more than once in the
  real material this guide drew from.
- Reading a clean run of the delivery coverage check as proof that a
  package is ready. The script only counts deliverable-kind
  assignments; it does not judge whether the chosen kind actually fits
  a stem's own difficulty or content.

## Adapting to your platform

- `llm`: drafts a reasoned deliverable-kind assignment for one stem,
  from [P-S5-06](../prompts/s5/p-s5-06.md).
- `file-read`: reads the finished stem file and the delivery manifest
  before any assignment is drafted or checked.
- `shell`: runs the delivery coverage check; without it, count each
  stem's own deliverable kinds by hand against the manifest.
- `human-approval`: covers approving a delivered package before it
  reaches a learner, and deciding what to do about each real gap the
  check finds.

## Where humans decide

- Approving a delivered, deliverable-kind-assigned package before it
  reaches a learner.
- For each real gap the delivery coverage check finds, whether the
  stem it names should be added to a deliverable, or set aside on
  purpose, and why.

Next: [Stage 5 Assessment development](index.md).
