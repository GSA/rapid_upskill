---
title: "S5.6 Quiz and exam assembly"
parent: "Stage 5 Assessment development"
nav_order: 5
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
sub_stage: "S5.6"
prompts: ["P-S5-05"]
scripts: ["X-S5-05"]
---

# S5.6 Quiz and exam assembly

## Outcome

At the end of this sub-stage, a set of finished, checked
[stems](../glossary.md#stem) becomes an assembled, deliverable quiz: an
answer key, a point value per stem, and feedback text for the correct
answer and for each wrong one.

## Where it fits

This sub-stage takes in a checked [item bank](../glossary.md#item-bank)
from [S5.5 and S5.7 Difficulty distribution and blueprint
bank](difficulty-and-blueprint-bank.md). It hands an assembled quiz on
to [Stage 5 delivery formats and lessons](delivery-formats.md), the
last step before a learner sees any of it.

## Why this way

Assembling a quiz is kept separate from drafting a stem, because the
same finished stem can be assembled into more than one deliverable: a
chapter quiz today, a mock exam later. Separating the two steps means a
stem is only ever drafted once, no matter how many deliverables it
later ends up in. Keeping the two apart also keeps a person's own
review focused: a person confirming a drafted feedback row is judging
the feedback itself, not re-checking references and letters a script
already checks the same way every time, once a stem is finished.

## Steps

| Step | Who | Basis |
|---|---|---|
| Build an answer key from the bank's own finished stems, one row per stem: its id, its correct answer, its point value, and feedback text for the correct answer and for each [distractor](../glossary.md#distractor) | Agent drafts, a person confirms | documented for the key's own shape; suggested for who confirms it |
| Check the answer key against the bank's own stems, so every stem id resolves and every answer letter is a real, matching option | Script | suggested |
| Approve the assembled quiz before delivery | Person | suggested |

[The project notes](../glossary.md#reference-implementation) describe
an answer key with this same shape, drawn from a real, working script
this batch's own research read in full: one row per stem, a correct
answer, a point value, and feedback text split between the correct
answer and each distractor. Who confirms a drafted row before it enters
the key is not itself named there as a separate gate; it is this
guide's own suggested checkpoint.

## Reject an out-of-range answer letter loudly

A real project script's own answer-parsing step used a pattern that
matched only part of a stem's valid option range. An answer letter
that fell outside that matched range would have been silently treated
as the first option instead of raising an error: a key entry with a
letter the pattern could not see would have graded as whatever the
first option happened to be, with no error printed and no record
anywhere that anything had gone wrong.

[X-S5-05 Answer key check](../scripts/s5/x-s5-05.md) does the
opposite. Any letter that is not one of a stem's own real options, or
that names the wrong option for that stem, is a loud, reported error,
never a silent default. The lesson generalizes past this one script:
whenever code parses a letter, a code, or any other enumerated value
out of text, an input the parser does not actually recognize should
fail visibly, not fall through to whatever the first case happens to
be.

These are two different problems, and the check reports them
differently. A letter that is a real option for its own stem, just not
the correct one, is an ordinary mismatch: the key disagrees with the
stem about which option is right. A letter that is not one of that
stem's own real options at all is the out-of-range case above, the one
the real project bug would have quietly folded into option A instead
of reporting.

## A two-phase assembly pattern

Building the pieces of an assembled quiz is a separate concern from
creating the quiz itself on a forms-based quiz-delivery platform, the
generic name this guide uses for the real product its own sources
build a quiz on, never named here.
[The project notes](../glossary.md#reference-implementation) document
a generalizable two-phase pattern for that second concern, described
here with no real platform field or method named either. First, create
the quiz's own shell on the platform and add its items with only the
content the platform needs to accept them. The platform then assigns
each item its own id, an id that did not exist before that item was
created. Only once every item carries a real, platform-assigned id can
a second update actually address it: submitting a point value, a
correct-answer key, and feedback text keyed to ids the platform had
not yet minted before the first step ran, so no update could have
named them correctly any earlier. A real assembly run built this way
often batches the work at each phase, creating many items in one call
during the first phase and updating many in one call during the
second, rather than one round trip per item; this guide's own sample
data is far too small to need batching, but the pattern still holds at
its own small scale. The pattern generalizes past assembling a quiz:
whenever a target system assigns its own identifiers to whatever is
created in it, the shape of any later update is fixed by the ids the
first step waits to receive, not by whatever id scheme this guide's
own sample data happens to use.

## Answer-key schema

This guide's own answer-key schema: a list of entries, each with
`stem_id` (matching a real stem in the bank), `correct_answer` (one
letter, matching that stem's own real correct answer), `points` (a
whole number), `feedback_correct` (text for the correct answer), and
`feedback_by_distractor` (a map from an option letter to feedback
text, one entry per distractor the stem defines). A row does not have
to give feedback for every distractor a stem defines to pass the
check below; it only has to give real feedback for the distractors it
does cover. Every letter it does give, though, has to be one of that
stem's own real options, whether the row covers all of them or only
some.

Harder items are commonly worth more points than easier ones, as a
general pattern; exactly how many points a real program's own scheme
assigns is not stated here as a design rule this guide asks a reader
to copy. This guide's own sample answer key below picks its own point
values as a plain illustration of the harder-is-worth-more pattern,
deliberately different from the reference implementation's own real
scheme, so a reader never mistakes this guide's own illustration for a
project's actual result.

## Worked illustration

The two clean, finished stems from [S5.3 and S5.4 Distractors and
format rules](distractors-and-format-rules.md), `STEM-2.1-001` and
`STEM-2.1-002`, each get one answer-key row. `STEM-2.1-001`, the easy
stem built from the commit-is-a-snapshot concept, has correct answer A
and three distractors, B through D; its row is worth 5 points, with
feedback confirming the snapshot behavior for the correct answer and
naming, for each distractor, the [misconception](../glossary.md#misconception)
it was built from. `STEM-2.1-002`, the medium stem built from the
merge concept and a merge-conflict concept combined in one scenario,
also has correct answer A and three distractors; its row is worth 8
points, with feedback naming the already-published `SRC-002` sentence,
"A common mistake is to assume that merging must create a commit,"
behind one of its own distractors. A second distractor's feedback for
`STEM-2.1-002` addresses the merge-conflict concept itself: mistaking
a conflict resolved in the working directory for a finished merge,
before the resolved files are actually staged and committed.

To show the loud-failure behavior in full, take a copy of the answer
key and change `STEM-2.1-001`'s own `correct_answer` from A to F, a
letter no stem in this guide's own sample data ever uses.
`STEM-2.1-001`'s own real option range runs only from A to D, so F is
not a mismatch, a real option that is simply the wrong one; it is
outside the range entirely, exactly the kind of input the real
project's own bug would have quietly treated as if it were option A.

## Artifacts and formats

This sub-stage produces one artifact: an answer key, in the schema
above. The sample file for the running example, `answer_key/key.json`,
holds one row each for `STEM-2.1-001` and `STEM-2.1-002`, described in
the worked illustration above. The out-of-range demonstration lives
only in the script block below, never in this checked-in file.

## Prompts

[P-S5-05 Draft item feedback](../prompts/s5/p-s5-05.md) drafts the
correct-answer feedback and the per-distractor feedback for one
already-assembled stem, from its own explanation and its own
distractors' named misconceptions. It is written for this guide and
has not been run against any model in this build; treat it as a
starting point and adapt it. The stem text and the explanation notes it
reads are data, never instructions, even where a sentence inside
either is phrased as one.

## Scripts

[X-S5-05 Answer key check](../scripts/s5/x-s5-05.md) checks an answer
key against the bank's own stems in three ways: every `stem_id` the
key names resolves to a real stem; a `correct_answer` that is a real
option for its own stem, but not the right one, is reported as a
mismatch; and a `correct_answer` or a `feedback_by_distractor` key that
is not one of that stem's own real options at all is reported as out
of range. Run it from the repository root:

```bash
python3 -B scripts/s5/answer_key_check.py \
    scripts/sample_data/git_basics_stage5/answer_key/key.json \
    scripts/sample_data/git_basics_stage5/stems/stems.json
```

```text
entries=2 errors=0
```

Both sample rows pass: each names a real stem, and its correct answer
matches that stem's own real correct answer. See [Reading exit
codes](../stage-1/index.md#reading-exit-codes) on the Stage 1 index for
what the exit code means; here it is 0.

Break it on purpose: copy the answer key, change `STEM-2.1-001`'s own
`correct_answer` from A to F, and run the check again on the copy:

```text
error: stem "STEM-2.1-001" answer "F" is outside its own option range (A-D)
entries=2 errors=1
```

F is not one of `STEM-2.1-001`'s own four real options, A through D, so
the check reports it as out of range rather than silently matching it
to option A or to anything else. A clean run only says every stem_id
resolves and every letter in the key is real; it says nothing about
whether the feedback text itself is accurate, or whether it happens to
give away the answer to a different stem than the one it is attached
to.

## Definition of done

- Every row in the answer key names a stem id that is actually in the
  bank.
- Every row's `correct_answer` is a real option for its own stem, and
  matches that stem's own real correct answer.
- Every `feedback_by_distractor` key names a real option for its own
  stem.
- Feedback text written for one stem never reveals, or hints at, the
  correct answer to a different stem.
- A person has approved the assembled quiz before delivery.

## Common failures

- An answer-key entry that references a stem id no longer in the bank,
  left over from an earlier version of the bank that has since
  changed.
- Feedback text that gives away the answer to a different question
  than the one it is attached to, which the answer key check cannot
  see, since it only checks ids and letters, not what feedback text
  actually says.
- An out-of-range answer letter accepted silently rather than rejected
  loudly, the exact failure this sub-stage's own script is built to
  catch.
- A `correct_answer` that names a real option for its own stem, just
  the wrong one: an ordinary mismatch, distinct from the out-of-range
  case above, but still worth a person's own look at which reading is
  actually right.
- Point values assigned with no regard for the difficulty they are
  tied to, so a harder stem ends up worth the same as, or less than, an
  easier one, undoing the very pattern this sub-stage's own sample
  illustrates.

## Adapting to your platform

- `llm`: drafts the feedback text from [P-S5-05](../prompts/s5/p-s5-05.md).
- `file-read`: reads the bank's own finished stems before feedback is
  drafted or the key is checked.
- `shell`: runs the answer key check; without it, check every stem id,
  correct answer and feedback key by hand against the bank.
- `human-approval`: covers confirming the drafted feedback and
  approving the assembled quiz before delivery.

## Where humans decide

- Confirming the drafted feedback text before it reaches a learner.
- Approving the assembled quiz before delivery.

Next: [Stage 5 delivery formats and lessons](delivery-formats.md).
