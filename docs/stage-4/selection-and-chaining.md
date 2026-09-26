---
title: "S4.3 and S4.4 Selection and chaining"
parent: "Stage 4 AI-tutor coaching"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-25"
stage: "S4"
sub_stage: "S4.3"
prompts: ["P-S4-02"]
scripts: []
---

# S4.3 and S4.4 Selection and chaining

## Outcome

At the end of this sub-stage, which coaching protocol runs next is
chosen by a fixed priority order, not left to a model's own judgment
call each time. A session can also move through more than one
protocol in a documented sequence, rather than stopping once the
first one finishes.

## Where it fits

This sub-stage takes in the protocol library
[S4.1 and S4.2](principles-and-protocol-library.md) defines. It
selects and sequences among those protocols for
[S4.5](misconception-catalog-and-error-diagnosis.md) (when a wrong
answer needs Protocol M, Error Diagnosis) and for every other
interaction a session has.

## Why this way

A fixed order means an integrity concern is never pushed aside just
because a model judges the moment's content need as more urgent. A
learner pasting in a graded assignment and asking for it to be solved
is one example; a learner in visible distress is another.
[The project notes](../glossary.md#reference-implementation) describe
this order identically across every source that states it, which is
part of why this guide treats it as fixed rather than as one option
among several. A documented chaining sequence, in turn, means a whole
session's shape can be checked afterward, not only each individual
[coaching protocol](../glossary.md#protocol-tutor)'s own content,
taken one at a time.

The priority order and a chaining arc answer two different questions.
The priority order picks one protocol for the interaction happening
right now. An arc, described later on this page, describes how a
whole sequence of turns unfolds instead, once a topic calls for more
than one protocol in turn.

## Steps

| Step | Who | Basis |
|---|---|---|
| Check the interaction for an integrity risk first, and hand off to the Integrity Guardrail (Protocol K) if one is present | Orchestrator | documented |
| Check for a clear affective signal next, and hand off to Affective Support (Protocol O) if the learner shows confusion, frustration or boredom | Orchestrator | documented |
| Check for a group context next, and hand off to Collaborative Facilitation (Protocol P) if more than one learner is present | Orchestrator | documented |
| Match the learner's own stated intent against roughly ten interaction kinds, only once none of the checks above has fired | Orchestrator | documented |

The order runs without exception: integrity risk first, then
affective signals, then group context, and only then the learner's
own stated intent. Intent is matched against roughly ten interaction
kinds, such as asking for an explanation, showing flawed reasoning,
being stuck mid-solution, or reaching the end of a session. This
guide calls the whole decision procedure the **selection layer**: its
plain name for Protocol L, Auto Protocol Selection. It is the one
protocol in the library with no learner-facing script of its own,
only [orchestrator](../glossary.md#orchestrator)-only decision rules.
See [S4.1 and S4.2](principles-and-protocol-library.md#the-sixteen-protocols)
for where Protocol L sits among the other fifteen.

## Whether a learner can ever reach the selection layer directly

The project notes disagree with themselves on this point, and this
guide states both readings rather than choosing one.

One reading, from the core protocol specification: the selection
layer is given no learner-facing prompt of its own anywhere in that
document, only orchestrator-only decision logic. Read this way, a
learner can never invoke it directly; only an orchestrator session
runs it, as part of deciding what a learner sees next.

A different reading, from a separate project document: it tells a
learner they can request a protocol explicitly, or let the tutor
choose for them. Read this way, automatic selection is a default a
learner can override on request, not something wholly out of reach.

Neither reading resolves the other. The project notes themselves do
not settle the question, so a team adopting this sub-stage has to
decide, for its own build, whether a learner-facing surface ever
exposes a way to ask for a specific protocol by name.

The choice has a practical consequence either way. Following the
first reading, a learner-facing surface would offer no button,
command or menu naming a protocol by letter or name, since the
selection layer would run only behind the scenes, inside the
orchestrator. Following the second, that same surface could let a
learner type something close to "give me a quiz" or "just explain
it," and have the tutor honor the request directly. Automatic
selection would then apply only once the learner has not asked for
anything specific.

## Chaining across a session

A session does not have to stop once one coaching protocol finishes.
The project notes describe more than one documented sequence, called
an **arc** in this guide: a named sequence that moves a learner
through more than one protocol, in order, across a session.

### The six-step arc

One project document, the cookbook's own overview file, gives a
six-step sequence as a "typical path." The order runs: Productive
Failure (Protocol N), then Direct Explanation (Protocol A), then
Self-Explanation (Protocol E), then Step-by-Step Hinting (Protocol
G), then Quiz/Exam Coaching (Protocol I), then Reflection (Protocol
J).

State this plainly, since it is easy to read the other way around:
the core protocol specification itself does not spell out this exact
six-step sequence anywhere. It documents only the individual pairwise
transitions the arc draws on, such as Productive Failure moving into
Self-Explanation, or Direct Explanation moving into Self-Explanation.
The six-step arc is the cookbook's own downstream synthesis of those
transitions, named there as a typical path, not the protocol
library's own single canonical sequence. A reader who goes looking
for this exact six-step arc inside the core specification will not
find it spelled out as one sequence there.

### Three further named arcs

A different project document, the same cookbook's own
worked-example-prompts file, not the overview file the six-step arc
comes from, documents three further named arcs. All three matter,
because naming only two of them would leave out the one most likely
to be confused with the six-step arc above.

- **A new-concept arc** is the closest of the three to the six-step
  arc. It swaps the hinting-then-quiz pair (Protocols G and I) for a
  single drill step (Protocol H), then still closes with Reflection
  (Protocol J).
- **An exam-prep arc**, for a weak topic, starts from assessment
  rather than from struggle. It runs Quiz/Exam Coaching (Protocol I)
  first, then Error Diagnosis and Elenchus (Protocols M and C)
  against each wrong answer along the way, and ends with a fresh quiz
  and a reflection.
- **A debug-a-design arc** runs Elenchus into Dialectic/Counterfactual
  (Protocols C and D), then calls Error Diagnosis (Protocol M) only
  if the learner's reasoning needs it. It ends at Self-Explanation
  (Protocol E), with no quiz or reflection step at all.

## Worked illustration: the six-step arc in a merge-conflict session

[The running example](../running-example.md), Git Basics for New Team
Members, gives one way to see the six-step arc in order, on a
stuck-on-a-merge-conflict moment like the one
[S4.1 and S4.2](principles-and-protocol-library.md#worked-illustration-the-hint-ladder-in-a-merge-conflict)
also uses.

1. **Productive Failure**: the learner attempts to resolve the
   conflict unaided first, with no hint offered yet.
2. **Direct Explanation**: once the learner is genuinely stuck, the
   tutor explains how the conflict resolves.
3. **Self-Explanation**: the learner explains, in their own words,
   why staging the edited file and completing the merge actually
   settles it.
4. **Step-by-Step Hinting**: a second conflict, later in the same
   session, is hinted at one level at a time rather than explained
   outright.
5. **Quiz/Exam Coaching**: a short quiz then compares merging and
   rebasing, checking that the learner can now tell the two apart.
6. **Reflection**: a short reflection closes the session, asking what
   the learner would do differently on the next conflict.

The selection layer chooses each step in turn; the arc itself is what
makes the session's whole shape checkable afterward, not only whether
any single step went well.

## Artifacts and formats

- A selected-protocol decision, per interaction: the chosen
  protocol's letter, plus a one-line reason keyed to the priority
  order above, so a later reviewer can see which check fired without
  re-reading the whole interaction.
- A session's own chain of protocols, recorded in order. Its overall
  shape can be reviewed once the session ends, not only judged step
  by step while it runs, and compared against the documented arcs
  above.

## Prompts

[P-S4-02 Select the next protocol](../prompts/s4/p-s4-02.md) applies
the fixed priority order to one interaction and names which protocol
runs next. It is written for an orchestrator session to call, not for
a learner to run directly, matching the selection layer's own
orchestrator-only design. It is written for this guide and has not
been run against any model in this build.

## Scripts

None; the project notes describe no code for this sub-stage.

## Definition of done

- Every interaction is checked for an integrity risk, then an
  affective signal, then a group context, in that order, before
  learner intent is ever matched.
- A hand-off away from intent-matching records which of the first
  three checks fired, not only which protocol ran.
- A session that follows a documented arc records the resulting
  sequence of protocol letters, not only a count of protocols used.
- Both readings of the selection layer's reachability are available
  to a team building on this stage, not silently resolved into one.

## Common failures

- Treating the fixed priority order as a suggestion rather than
  fixed, so a content-need protocol runs ahead of an integrity or
  affective signal that should have taken it first. A learner in real
  distress then gets an explanation instead of support.
- Running the six-step "typical path" as though it were the only
  acceptable sequence, rather than one documented option among at
  least three named arcs. This can force a quiz and a reflection onto
  a session that fits the debug-a-design arc better instead.
- Letting an affective or group signal go unhandled because the model
  already committed to a content-need protocol before the signal
  appeared, and never re-checking once the interaction is underway.

## Adapting to your platform

- `llm`: applies the priority order to a given interaction, and
  drafts the reasoning behind each selection and each chaining
  choice.
- `human-approval`: covers approving the priority order and the
  documented arcs before first use. A platform with no built-in
  approval step still needs a person to read and record that approval
  somewhere, such as a shared document.

## Where humans decide

- Approving the priority order and the documented arcs before first
  use.
- Judging, after the fact, whether a real session's own chain of
  protocols still made sense in hindsight.

Next: [S4.5 Misconception catalog and error diagnosis](misconception-catalog-and-error-diagnosis.md).
