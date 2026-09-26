---
title: "S4.1 and S4.2 Principles and protocol library"
parent: "Stage 4 AI-tutor coaching"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-25"
stage: "S4"
sub_stage: "S4.1"
prompts: ["P-S4-01"]
scripts: []
---

# S4.1 and S4.2 Principles and protocol library

## Outcome

At the end of this sub-stage, a tutor's behavior is specified in
advance rather than left to emerge from one general-purpose prompt.
Six principles apply to every interaction a learner has with the
tutor. A library of sixteen named **[coaching
protocols](../glossary.md#protocol-tutor)** (lettered A through P)
each cover one recurring kind of interaction, such as explaining a
term, hinting at a stuck step, or diagnosing a wrong answer. A person
can check a real tutoring session against this written specification,
rather than trusting an unconstrained prompt to improvise well every
time. Neither the six principles nor the sixteen protocols name a
chapter, a learner, or a topic. They describe a kind of move a tutor
can make, to be filled in with real material once a session starts.

## Where it fits

This specification is written once, for the whole program, not built
from any one chapter's own content. A specific chapter enters the
picture only once [Stage 3](../stage-3/index.md) hands one on, so
that chapter's own tutoring can begin. Once a chapter's
[misconception catalog](../glossary.md#misconception-catalog) exists
([S4.5](misconception-catalog-and-error-diagnosis.md) builds it),
this page's own Error Diagnosis protocol (M) reads it.

This page hands the protocol library on to three later pages, not
one. [S4.3 and S4.4](selection-and-chaining.md) chooses among the
protocols for a given interaction. [S4.6](guardrails.md) applies its
own rules across every protocol in the library, not as one protocol
among the sixteen. [S4.7](packaging-and-scope.md) bundles the whole
library, alongside a chapter and its misconception catalog, for a
target platform.

## Why this way

Specifying pedagogy as a fixed set of named moves, checkable against
a written spec, is what lets a person judge whether the tutor is
doing the right kind of thing in a given moment. A single,
unconstrained prompt has no such check: whether it behaves well
depends on trusting it to improvise well every time, session after
session, with nothing written down to compare it against. A named
protocol also gives a reviewer a shared vocabulary for a disagreement:
"the tutor should have used Step-by-Step Hinting here" is a claim
someone can check against a written script, while "the tutor should
have been more helpful" is not.

## Steps

| Step | Who | Basis |
|---|---|---|
| Write the six principles that apply across every protocol | Agent, from [the project notes](../glossary.md#reference-implementation) | documented |
| Write each of the sixteen protocols' use-when, goal and script | Agent, from the project notes | documented |
| Note where a protocol has no learner-facing worked example, and why | Agent | documented for the gap itself; inferred for the likely reason |
| Approve the specification before any real session runs against it | Person | suggested |

## The six principles

These six principles are documented in the project notes as applying
across every protocol. They are reported here as design choices, not
as findings this guide has checked itself.

- **Knowledge grounding**: answer from the course's own material, not
  a model's general knowledge (see
  [grounding](../glossary.md#grounding)). The project notes cite
  external research for this design choice; this guide does not
  restate a figure from that research as its own finding.
- **Learner modeling**: keep a running sense of what a learner has,
  and has not yet, mastered, topic by topic.
- **Verify before trusting**: never accept an unchecked answer as
  settled; check it before building the next step on it.
- **Ask, don't tell**: prefer a question that leads a learner toward
  an answer over stating that answer outright.
- **Calibrated intervention**: step in only when the moment calls for
  it, not on a fixed schedule regardless of need.
- **Step-level feedback**: respond to a flaw in one reasoning step,
  not only to a wrong final answer. Here too, the project notes cite
  external research for this design choice, not restated as a figure
  on this page.

None of the six stands alone. A tutor that grounds its answers in the
course material but never verifies a learner's own claim before
building on it has only half of what these principles ask for. The
same is true of a tutor that asks good questions but intervenes on
every turn, regardless of whether the moment calls for it.

## The sixteen protocols

Every protocol below follows the same shape: a name, a trigger for
when to use it, a goal and a short script of moves; all but one also
carry a worked example. The table names each with one clause; several
are described further, or reused, on a later page.

| Letter | Protocol | What it does |
|---|---|---|
| A | Direct Explanation | Gives a concise, direct explanation of a term or idea. |
| B | Socratic Definition | Sharpens a definition through questions asked from more than one angle. |
| C | Elenchus | Cross-examines a learner's own reasoning to surface a contradiction in it. |
| D | Dialectic/Counterfactual | Explores a trade-off through a "what if" question. |
| E | Self-Explanation | Has the learner explain, in their own words, why each step holds. |
| F | Worked Example (fading) | Shows a full worked model, then fades the scaffolding across further examples. |
| G | Step-by-Step Hinting | Gives one hint at a time from a four-level ladder; see the worked illustration below. |
| H | Drills | Runs spaced, interleaved retrieval practice. |
| I | Quiz/Exam Coaching | Runs exam-style items and tracks mastery over time. |
| J | Reflection | Closes a session with a plan-monitor-evaluate review. |
| K | [Integrity Guardrail](../glossary.md#integrity-guardrail) | Withholds a full solution on graded work; see [S4.6](guardrails.md) for a real disagreement over what kind of thing K is. |
| L | Auto Protocol Selection | Orchestrator-only decision logic, with no learner-facing prompt of its own; see [S4.3 and S4.4](selection-and-chaining.md). |
| M | Error Diagnosis | Classifies a wrong answer by type and points a response at it; see [S4.5](misconception-catalog-and-error-diagnosis.md). |
| N | Productive Failure | Has the learner attempt a problem first, then contrasts the attempt with the canonical solution. |
| O | Affective Support | Responds differently to confusion, frustration and boredom. |
| P | Collaborative Facilitation | Makes light-touch moves across five stages of a group discussion. |

One project document gives a worked example for fifteen of these
sixteen protocols, leaving out Auto Protocol Selection (L). The
likely reason is that L has no learner-facing prompt to begin with,
since it only ever runs as orchestrator-only decision logic. No
source states this reason outright, so this guide's own reading of it
is labelled `inferred`, not `documented`.

How fully each protocol is written up also varies. Step-by-Step
Hinting, Affective Support, Collaborative Facilitation and Error
Diagnosis carry the most detailed scripts of the sixteen; Integrity
Guardrail and Auto Protocol Selection carry the least, each reduced
to a short, generic set of moves. This guide has not checked why the
level of detail differs across the sixteen, so treat it as an
observation about the project notes, `inferred`, not a claim about
which protocol matters most.

## Worked illustration: the hint ladder in a merge conflict

[The running example](../running-example.md)'s Chapter 2 covers
objective D2.3: resolve a merge conflict by editing the conflict
markers, staging the file and completing the merge. A learner working
through that chapter runs a merge, and Git stops with a file marked
"both modified." The learner asks the tutor for help. Protocol G
answers with one hint at a time, from a four-level ladder, and never
reveals the resolving command outright before the learner has tried
each earlier level.

1. **Conceptual**: name the general idea only. A merge conflict means
   Git could not combine both sides on its own, because both branches
   changed the same lines, or one deleted a file the other edited.
   The learner has to decide the final result.
2. **Strategic**: name the kind of move, not the exact step. Look at
   the file `git status` marks as "both modified," and decide, block
   by block, whether to keep one side, the other, or a combination of
   both.
3. **Procedural**: name the concrete step, without carrying it out.
   Find the block between the `<<<<<<<` and `>>>>>>>` markers, edit
   it down to the exact text wanted, and delete all three marker
   lines.
4. **Near-complete**: show almost the whole path, holding back only
   the very last action. Once the markers are gone and the file reads
   the way it should, stage that file, then finish the merge; running
   those commands, and confirming the result, is still the learner's
   own last step.

Each level moves the learner one step closer without handing over the
finished answer at an earlier one. If a hint does not unstick the
learner after a real attempt, the tutor raises to the next level
rather than repeating the same hint. That is the one-line note
[P-S4-01](../prompts/s4/p-s4-01.md) adds after every hint it gives.

The ladder is one place several of the six principles meet at once.
Ask, don't tell shows up as a hint, not a stated answer. Calibrated
intervention shows up as one level per turn, not the whole ladder at
once. Verify before trusting shows up as checking the learner's next
attempt before raising the level again.

## Artifacts and formats

- The protocol library and the six principles: one written
  specification a person can check a real tutoring session against,
  covering what a tutor should do in a given kind of moment, not what
  any one interaction actually said.

## Prompts

[P-S4-01 One hint from the step-by-step ladder](../prompts/s4/p-s4-01.md)
gives one hint at a time from Protocol G's four-level ladder, without
revealing the solution outright, for a learner's own attempt and the
topic it concerns. It is written for this guide and has not been run
against any model in this build.

## Scripts

None; the project notes describe no code for this sub-stage.

## Definition of done

- Every one of the six principles is written down and stated as
  applying to every protocol, not to some.
- Every one of the sixteen protocols has a use-when, a goal and a
  script, except Auto Protocol Selection (L), which is
  orchestrator-only decision logic.
- The worked-example gap around Auto Protocol Selection is stated
  plainly, not left for a reader to notice on their own.
- A person has approved the specification before any real session
  runs against it.

## Common failures

- Treating one of the six principles as optional once a protocol is
  already running, rather than as a constraint that applies to every
  protocol, every time.
- Letting Protocol G's ladder skip straight to a near-complete hint,
  which defeats the point of an escalating ladder and can hand over
  the answer before the learner has tried anything.
- Citing one of the two research-backed principles, knowledge
  grounding or step-level feedback, by the specific figure the cited
  research reports, rather than stating only the design choice it
  supports.

## Adapting to your platform

- `llm`: drafts every explanation, question, hint and reflection
  prompt the sixteen protocols call for.
- `human-approval`: covers approving the specification itself before
  first use, and any point where a session's own record needs a
  person's sign-off. A platform with no built-in approval step still
  needs a person to read and record that approval somewhere, such as
  a shared document.

## Where humans decide

- Approving the protocol library and the six principles before first
  use.
- Judging, after the fact, whether a given real session actually
  followed the specification it was supposed to.

Next: [S4.3 and S4.4 Selection and chaining](selection-and-chaining.md).
