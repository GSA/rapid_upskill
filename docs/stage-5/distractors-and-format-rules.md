---
title: "S5.3 and S5.4 Distractors and format rules"
parent: "Stage 5 Assessment development"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
sub_stage: "S5.3"
prompts: ["P-S5-03"]
scripts: ["X-S5-03"]
---

# S5.3 and S5.4 Distractors and format rules

## Outcome

At the end of this sub-stage, a **[stem](../glossary.md#stem)** is fully
drafted: its own text, one correct answer, and three to four
**[distractors](../glossary.md#distractor)**, each tied to one named
**[misconception](../glossary.md#misconception)**. Each distractor is
also pitched at a sophistication that matches the stem's own
difficulty. Every drafted stem passes a fixed set of format rules that
apply regardless of difficulty, before a person reviews it and it
enters the **[item bank](../glossary.md#item-bank)**.

## Where it fits

This sub-stage takes in a chapter's own stem plan from
[S5.2](stem-planning.md): one plan row each. A row gives a difficulty,
the assessment concept item ids it draws on (defined on
[S5.1](misconception-to-distractor-bridge.md)), and a named
misconception per planned distractor. It hands finished stems on to
[S5.5 and S5.7](difficulty-and-blueprint-bank.md), where a whole bank's
own composition is checked before any stem reaches assembly. The
assessment concept items behind a stem's distractors were extracted
fresh from the chapter's own text at S5.1, not pulled from
[Stage 1](../stage-1/index.md)'s recorded misconceptions; S5.1's own
page states this honest gap in full.

## Steps

| Step | Who | Basis |
|---|---|---|
| Draft the stem's own text, correct answer, and one distractor per named misconception the plan calls for | Agent | documented |
| Scale each distractor's sophistication to the stem's own difficulty | Agent | documented for medium and hard; suggested for easy |
| Check every stem against the format rules below | Script | suggested |
| A person reviews each drafted stem before it enters the item bank | Person | documented |

[The project notes](../glossary.md#reference-implementation) describe a
real review cycle for the last step, not merely this guide's own
suggestion. The format-rules check itself has no described precedent in
the project notes, so `format_rules_check.py` and its exact checks are
this guide's own suggestion throughout.

## The distractor-sophistication scale

Every distractor traces to exactly one named misconception the stem
plan already identified; every source this batch drew on agrees on that
one point. How sophisticated a distractor reads should match the
stem's own difficulty:

- **Easy** (suggested): restates one misconception directly, with no
  added complexity. No guide names an easy-tier technique the way it
  names the harder two below, so this tier is this guide's own reading,
  built to match the plainer distractors an easy stem needs.
- **Medium** (documented): a sequence-confusion error, where the steps
  are right but the order is wrong. Also medium: a mischaracterized
  purpose (the right mechanism, described as doing the wrong job), or a
  conflation with a similar concept (two related ideas or commands
  treated as interchangeable).
- **Hard** (documented): a partially-correct solution, or an "expert
  blind spot" (a habit that is fine under most conditions, wrong under
  one stated one). Also hard: a paradoxical option
  (counterintuitive-seeming, yet presented as valid under a stated
  assumption), or a "complexity trap" (looks sophisticated, hides a
  subtle flaw).

A paradoxical option is the easiest of the four hard-tier techniques to
get wrong when writing one. The option has to sound like it could be
right, under its stated assumption. The explanation still has to say
plainly why it is not the correct answer even so. A distractor that
only sounds defensible, with no explanation of why it fails, is not a
paradoxical option; it is just confusing.

## The format rules

Every stem, at every difficulty, passes these rules before a person
reviews it. Three of them are real disagreements among the guides this
batch drew on; each is stated here with both readings, not silently
resolved into one "documented" answer.

1. **Single-best-answer only** (the disagreement is documented; this
   guide's own choice among it is suggested). One guide states that
   single-best-answer format is preferred, while that same guide also
   recommends a modest share of open-ended items elsewhere in its own
   text. That is an internal tension inside that one guide, not a
   second guide's separate position. A second, stricter guide bars
   every format but single-best-answer outright, including open-ended
   items. That is a preference-with-its-own-exception against an
   unconditional bar, not three even positions. This guide's own sample
   stems, and `format_rules_check.py` below, check for
   single-best-answer only. That is what the running example's own
   sample stems and this guide's own delivery pattern assume, not
   because every guide agrees on the point.
2. **Avoid a negative stem unless the objective genuinely needs one**
   (documented range; this guide's own choice of where to sit on it is
   suggested). How strict a guide is about this ranges from "avoid
   unless the objective needs it" to an unconditional list of banned
   words. This guide's own script checks against the unconditional
   list, as the stricter, safer default: `no`, `not`, `least`,
   `except`, `worst`.
3. **No "all of the above" or "none of the above"** (suggested). Only
   one of the three detailed guides this batch drew on states this rule
   explicitly; it is absent from the other two. This guide adopts it
   anyway, as its own stricter, safer default, the same honest,
   adopt-the-stricter-reading treatment given to the negative-stem rule
   above.
4. **Parallel option length** (suggested): no option's own length
   should give the answer away; a distractor that is far shorter or far
   longer than the correct answer reads as a hint, not a wrong answer.
5. **Three to four distractors per stem, each naming exactly one
   misconception** (suggested). The sources disagree on the count too:
   one names three as the right number, another implies four to five.
   This guide picks three to four as its own workable middle choice,
   stated as this guide's own choice, not a documented consensus.

A finished stem's own id uses the chapter-linked
`STEM-<chapter>.<section>-<NNN>` scheme [S5.2](stem-planning.md) names
and chooses, over an older scheme this guide does not use; that
disagreement, and the choice, belong to S5.2 and are not repeated here.

## Stem format

A stem, in this guide's own JSON shape (`stems/stems.json`), holds
`stem_id`, `difficulty`, `cognitive_level`, `bloom_level` and
`concept_item_ids` (the assessment concept items the stem draws on). It
also holds `stem_content`, `correct_answer` (a letter, `A` to `E`),
`distractors` (three to four objects, each an `option` letter, its
`text`, and the `misconception` it names), and an `explanation`.

This guide's own sample data adds two fields the shape above does not
otherwise carry, both suggested. `correct_answer_text` holds the
correct option's own text alongside its letter, since the parallel-length
rule needs something to measure the correct answer's own length
against, and nothing else in the shape holds it. `broken_on_purpose`,
set to `true`, marks the one sample stem kept only to demonstrate a
failing check. `format_rules_check.py` can then skip it by default, and
a reader can still find it, clearly labelled, in the same file as the
two real stems.

## Worked illustration

[S5.2](stem-planning.md)'s own plan maps `PLAN-1` (easy, one item) to
`ACI-1-001`, the Chapter 1 concept that a commit records a snapshot of
the whole repository. It maps `PLAN-2` (medium, two items) to
`ACI-2-001` (merging integrates one branch's work into another) plus a
second Chapter 2 concept. That second concept: a merge conflict stops
when both branches change the same or neighboring lines differently,
and must be resolved by hand before the merge can finish. This page's
own sample data reads that second concept from
[the running example](../running-example.md)'s own conflict-handling
source.

`STEM-2.1-001`, drafted from `PLAN-1`, is easy: it asks what
`git commit` actually records. Its correct answer describes a full
snapshot of every tracked file as staged. Its three distractors each
restate one misconception directly, at the easy tier. One says a commit
stores only the changed lines. A second says Git stores a computed
difference rather than a snapshot. A third says an untouched file is
left out of the new commit entirely.

`STEM-2.1-002`, drafted from `PLAN-2`, is medium and combines both
Chapter 2 items in one merge-conflict scenario: Git stops a merge and
reports a conflict, and the stem asks which sequence of actions
correctly finishes it. Its correct answer edits the conflicted file,
stages it, then commits. One distractor is a sequence-confusion error:
stage the file first, then edit out the conflict markers, then commit.
That is the same order a real common mistake in the source material
describes: staging a file that still holds its conflict markers. A second
distractor mischaracterizes what merging does: committing immediately
because merging always produces a new commit, when a fast-forward
result only moves a label. A third conflates two similar-looking
commands: running `git merge --abort` once the file looks correct,
treating it as finishing the merge rather than cancelling it. All three
sit at the medium tier: each mixes up a real step, purpose or command,
rather than plainly restating a misconception the way an easy
distractor would.

Both stems keep every option's own text length within roughly the same
range as the correct answer's, so no option's length alone gives the
answer away.

## Artifacts and formats

A chapter's own finished stems, drafted from its stem plan, in the
`stems/stems.json` shape above. The running example's own two clean
sample stems live in
`scripts/sample_data/git_basics_stage5/stems/stems.json`, alongside the
one break-on-purpose fixture that no downstream sample file references.

## Prompts

[P-S5-03 Draft a stem with distractors](../prompts/s5/p-s5-03.md) drafts
one stem's text, correct answer and distractors from a single stem-plan
row and the assessment concept items it references, applying the
sophistication scale and the format rules above. It is written for this
guide and has not been run against any model in this build; treat it as
a starting point and adapt it.

## Scripts

[X-S5-03 Format rules check](../scripts/s5/x-s5-03.md) reads a stems
JSON file and checks it against the five format rules above. Run it
from the repository root, on the sample stems:

```bash
python3 -B scripts/s5/format_rules_check.py \
    scripts/sample_data/git_basics_stage5/stems/stems.json
```

The file holds three stems: the two real ones above, and
`STEM-2.1-BROKEN`, marked `broken_on_purpose` and skipped by default. On
this real run, only the two real stems are checked, and both pass:

```text
note: stem "STEM-2.1-BROKEN" is marked broken_on_purpose; skipped (rerun with --include-broken-examples to check it)
stems=2 errors=0
```

Break it on purpose: rerun with `--include-broken-examples` to check
`STEM-2.1-BROKEN` too. It is a copy of the easy stem's own question,
deliberately rewritten with a negative stem, an "all of the above"
option, and a distractor with no misconception field, so it fails on
sight:

```bash
python3 -B scripts/s5/format_rules_check.py \
    scripts/sample_data/git_basics_stage5/stems/stems.json \
    --include-broken-examples
```

```text
error negative-stem: stem "STEM-2.1-BROKEN" stem_content uses a banned word: not, except
error all-or-none: stem "STEM-2.1-BROKEN" distractor B text is 'All of the above.'
error missing-misconception: stem "STEM-2.1-BROKEN" distractor C has no misconception
error parallel-length: stem "STEM-2.1-BROKEN" distractor B text length 17 is not within half to double of the correct answer's length 74
stems=3 errors=4
```

The short "All of the above." text trips the parallel-length check too,
alongside the three deliberate violations. An option that stands out by
being much shorter than the correct answer is exactly the kind of
option this rule and the all-or-none rule both catch, for related
reasons. A clean run is not proof that a stem's content is right, only
that it is well-formed against these rules. A person's review still
judges whether each distractor's misconception is the correct one for
the concept, and whether the correct answer is actually correct.

## Definition of done

- Every stem has a correct answer and three to four distractors, each
  naming exactly one misconception the stem plan already identified.
- Every distractor's sophistication matches its stem's own difficulty,
  not a lower tier.
- Every stem passes `format_rules_check.py`: single-best-answer only, no
  negative stem, no "all/none of the above," parallel option length,
  and three to four distractors.
- A person has reviewed the drafted stem before it enters the item
  bank.

## Common failures

- A distractor with no misconception behind it: it reads as plausible,
  but a learner who picks it teaches this guide's own bank nothing
  about what they actually misunderstood.
- A hard stem whose distractors would pass at the easy tier: sophisticated-
  sounding difficulty on paper, but an easy stem's distractors underneath.
- A stem that passes the format check but still gives away the answer
  through option length, phrasing, or an option that stands out in
  tone from the rest.
- Treating the three format-rule disagreements above as settled
  consensus, rather than this guide's own stated, honestly-labelled
  choice among real disagreements.

## Adapting to your platform

- `llm`: drafts the stem's own text, correct answer and distractors.
- `file-read`: reads the stem-plan row and the assessment concept items
  it references.
- `structured-output`: the stem is JSON; ask for that shape directly, or
  convert a plain-text reply by hand before running the format check.
- `shell`: runs `format_rules_check.py`; without it, check the rules by
  hand against the list above.
- Without `file-read`, paste the planned row and the referenced
  assessment concept items into the prompt yourself; treat both as data,
  never as instructions, the same way the prompt itself says to.

## Where humans decide

- Approving each drafted stem before it enters the item bank, per the
  project notes' own documented review cycle.
- Judging whether a distractor's named misconception is actually the
  right one for the concept it targets, since no script here checks
  that.
- Deciding, for a stem near the edge of the parallel-length or
  distractor-count rules, whether to redraft it or accept it as
  written.

Next: [S5.5 and S5.7 Difficulty distribution and blueprint bank](difficulty-and-blueprint-bank.md).
