---
title: "S4.6 Learner-facing guardrails"
parent: "Stage 4 AI-tutor coaching"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-25"
stage: "S4"
sub_stage: "S4.6"
prompts: ["P-S4-04"]
scripts: []
---

# S4.6 Learner-facing guardrails

## Outcome

A learner using the tutor knows, up front, what to expect: an
attempt comes before a hint, a hint before a solution, and graded
work stays free of AI-written answers unless an instructor allows
otherwise. These are rules a learner can hold the tutor to, not a
promise about how well the tutor teaches.

## Where it fits

This sub-stage takes in the protocol library that [S4.1 and
S4.2](principles-and-protocol-library.md) specify. Its rules apply
across every protocol in that library, not as one more step in a
session's own chain of protocols. A learner reads these rules once
and expects them to hold no matter which protocol the tutor happens
to be running at the time. This page speaks to the learner directly,
mirroring the protocol library's own scripts from the learner's side
of the exchange, rather than describing what the tutor does.

## Why this way

A guardrail stated once, up front, in plain language a learner can
read for themselves, is something the learner can check. A rule that
lives only inside the tutor's own internal instructions is not.
Skipping straight to a solution also skips the struggle a person
needs to actually work through a step, not just finish it. Stating
the rule up front lets a learner expect that struggle, rather than
read it as the tutor being unhelpful. Every rule on this page is
documented in [the project notes](../glossary.md#reference-implementation);
this page states none of its own as merely suggested.

## Two readings of the integrity guardrail

[The project notes](../glossary.md#reference-implementation)
disagree with each other about what kind of thing the [integrity
guardrail](../glossary.md#integrity-guardrail) is, and this guide
states both readings rather than merging them into one.

One reading: the core protocol specification gives the integrity
guardrail, Protocol K, the same template as every other protocol in
[the sixteen-protocol
library](principles-and-protocol-library.md#the-sixteen-protocols): a
use-when line, a goal, a behavior script and a prompt stub. The
orchestrator [S4.3 and S4.4](selection-and-chaining.md) describes can
select it and combine it with others, the same way it can any of the
other fifteen protocols. Under this reading, integrity is one
protocol among sixteen.

The other reading: a separate, learner-facing guardrails document
never uses the letter K at all. It spreads the same substance across
three always-on cross-cutting sections that apply to every protocol,
not one selectable mode among the sixteen. Under this reading,
integrity is not something a session turns on or off; it is a
standing policy that already applies no matter which protocol is
running.

Whether the integrity guardrail is best understood as one selectable
protocol or as three always-on cross-cutting sections is not settled
in the project notes themselves. This page presents both readings,
plainly, as a real disagreement between two project documents. A
team adopting this guide's tutor still has to decide which reading it
is building toward: a single combinable protocol a session can add
or drop, or a standing policy no interaction can turn off. The two
readings imply different points to check when auditing a real
session. This guide does not decide that
question for a reader: the two source documents were not written to
agree with each other on this specific point, and this page leaves
the disagreement standing.

## Steps

Four rules make up the guardrail policy a learner reads before a
session starts, each stated in one sentence below.

| Step | Basis |
|---|---|
| State an attempt, or a plan, before asking for help. | documented |
| Ask for a hint before asking for a full solution. | documented |
| Keep graded work free of full AI-written solutions by default, unless an instructor allows otherwise. | documented |
| Match hint depth, notation and challenge to the learner's own stated level. | documented |

The attempt-first rule applies before either of the next two rules
can act: nothing about a request's grading or level matters until an
attempt or a plan is on the table. The hints-before-solutions rule
then leans on [S4.1 and
S4.2](principles-and-protocol-library.md#the-sixteen-protocols)'s
own four-level hint ladder: conceptual, then strategic, then
procedural, then near-complete. A learner works up that ladder one
level at a time, and a full solution is not simply what comes after
the ladder runs out. The graded-work rule covers more than a
finished solution: it also covers an AI-composed piece of submitted
work and a proctored question pasted in for help. None of these are
given by default on graded work, and only an instructor's own policy
changes that. The per-level rule covers three altitudes. A beginner
gets concrete examples and light notation, and is kept away from
full project-scale code. Someone at an intermediate level gets
consistency checks and questions that lead them to check their own
reasoning, instead of a direct answer. Someone advanced gets edge
cases, counter-examples and critique, and is still reminded to check
primary sources rather than treat the tutor's own answer as the last
word.

### A platform-specific caution

One tension in the sources is platform-specific, not a rule this
guide states as universal. A packaged conversational-agent format's
own usage policy bars inferring a person's emotions in an
educational setting. That sits in real tension with the
affective-support protocol's own design, which works by inferring
frustration, confusion or boredom from how a learner responds.
Turning the protocol on without that signal leaves it with nothing
to act on. Inferring frustration, confusion or boredom is the design
the rest of the protocol depends on, not an optional add-on. This is
one platform's own policy, not something the project
notes state for every platform. Check that policy before turning
affective support on as designed there.

### Worked illustration

A learner starts a merge-conflict exercise in the running example,
states their own level, and says the exercise is not graded. The
attempt-first rule asks for the learner's own attempt before
anything else. Once that attempt is given, the hints-before-solutions
rule limits the tutor to one hint, at the first, conceptual level,
with no command shown, since the learner has not yet tried a second
time. If the learner tries again and is still stuck, the next hint
moves to the second, strategic level, still with no command shown. A
command only appears at the third, procedural level, well after the
first attempt.

A parallel question on the same merge-conflict topic sits inside a
graded quiz instead. There, the graded-work rule holds regardless of
the learner's level or attempt: the tutor shows only the question
and waits, offering no solution, until the learner answers on their
own. Only once an answer is given does the tutor explain why it was
right or wrong; that explanation, not a solution offered in advance,
is where feedback belongs on graded work.

[P-S4-04](../prompts/s4/p-s4-04.md) drafts the tutor's response for
either case, from the learner's request, whether the work is graded,
and the learner's own attempt so far. The learner's own request and
attempt are fenced as data for the model to report on, never as
instructions for it to follow.

## Artifacts and formats

A stated guardrail policy: the rules above, written in plain
language a learner can read before a session starts, and named
again if the tutor's behavior ever seems to depart from them. The
policy names the four rules above, plus which stated level changes
how much depth and notation the tutor gives.

## Prompts

[P-S4-04 Respond to a solution request](../prompts/s4/p-s4-04.md)
applies the attempt-first and graded-work rules to a learner's
request. It produces a response that either asks for an attempt
first, gives a hint, or explains why a full solution is withheld. It
is written for this guide and has not been run against any model in
this build.

## Scripts

None; the project notes describe no code for this sub-stage.

## Definition of done

- A learner has read the guardrail policy before a session starts.
- Every request for a solution is checked against whether an attempt
  came first.
- Every hint given follows the hint ladder rather than jumping ahead
  to a near-complete one.
- Graded work has received no full AI-written solution, unless an
  instructor's own policy allows it.
- A person reviewing a session can point to which of the four rules
  above applies to any given request.

## Common failures

- A hint that restates the answer in different words, which
  satisfies the letter of "hint" while giving no real signal a
  learner can act on.
- Treating an "ungraded" label as license to skip the attempt-first
  rule, as if only graded work needed a real attempt first.
- Applying affective inference on a platform whose own policy bars
  it, without first checking whether that policy applies here.
- Treating the integrity-guardrail disagreement above as settled,
  building only for one reading (a single selectable protocol, or a
  standing policy) and dropping the other.

## Adapting to your platform

- `llm`: drafts each response to a learner's request under
  [P-S4-04](../prompts/s4/p-s4-04.md).
- `human-approval`: covers approving the guardrail policy before
  first use, and an instructor's own decision to relax a graded-work
  rule.
- A platform with no built-in way to check whether an attempt came
  first still needs a person, or a simple house rule, to hold that
  line before a request ever reaches the tutor.

## Where humans decide

- Approving the guardrail policy before first use.
- An instructor's own call on when graded-work rules can be relaxed.
- Whether a given response actually gave a real hint, or only
  restated the answer in different words.

Next: [S4.7 Packaging and scope](packaging-and-scope.md).
