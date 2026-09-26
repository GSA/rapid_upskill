---
title: "Stage 4 AI-tutor coaching"
nav_order: 40
status: "draft"
last_reviewed: "2026-09-25"
stage: "S4"
---

# Stage 4 AI-tutor coaching

## Outcome

[Stage 4](../glossary.md#stage) tutors a learner one to one. A chapter is tutored by a set of named coaching protocols, chosen by a fixed priority order and chained across a session, checked against a misconception catalog when a learner errs, kept within learner-facing guardrails, and packaged to fit a target platform.

## Where it fits

Stage 4 takes in finished, reviewed chapters from [Stage 3](../stage-3/index.md). This stage's own output, a tutoring package, is designed to reach a learner directly, outside the chapter-production pipeline the earlier stages describe.

## Sub-stages

Each part of Stage 4 has a **[sub-stage](../glossary.md#sub-stage)** id, continuing Stage 1 through Stage 3's own numbering.

| ID | Name | What it does | Page |
|---|---|---|---|
| 4.1 | Principles | Six principles that apply to every protocol and every interaction | [S4.1 and S4.2](principles-and-protocol-library.md) |
| 4.2 | Protocol library | Sixteen named coaching protocols (A through P), each covering one recurring kind of interaction | [S4.1 and S4.2](principles-and-protocol-library.md) |
| 4.3 | Selection | A fixed priority order picks which protocol runs next for a given interaction | [S4.3 and S4.4](selection-and-chaining.md) |
| 4.4 | Chaining | A documented sequence moves a session through more than one protocol in order | [S4.3 and S4.4](selection-and-chaining.md) |
| 4.5 | Misconception catalog and error diagnosis | Classify a wrong answer by kind, then check it against a per-chapter catalog | [S4.5](misconception-catalog-and-error-diagnosis.md) |
| 4.6 | Learner-facing guardrails | Attempt-first, hints before solutions, graded work AI-free by default, per-level adaptation | [S4.6](guardrails.md) |
| 4.7 | Packaging | Bundle a chapter, its catalog and the protocol library to fit a target platform | [S4.7](packaging-and-scope.md) |

All five sub-stage pages are now published.

## Order of work

1. Principles and the protocol library ([S4.1 and S4.2](principles-and-protocol-library.md)) are specified once, for the whole program, before any chapter is tutored.
2. Selection and chaining ([S4.3 and S4.4](selection-and-chaining.md)) apply the protocol library to a given interaction and, where a documented arc calls for it, to a whole session.
3. Misconception catalog and error diagnosis ([S4.5](misconception-catalog-and-error-diagnosis.md)) build a chapter's own catalog and use it once a learner's answer is wrong.
4. Guardrails ([S4.6](guardrails.md)) apply across every protocol, and packaging ([S4.7](packaging-and-scope.md)) bundles the whole of the above once a chapter's own material is ready.

This stage's own five pages do not chain in one straight line the way earlier stages' pages did. The principles-and-protocol-library page is a stage-wide specification, set once, not built from any one chapter. Both the misconception catalog and the guardrail policy it names are built or read on other pages, and more than one later page reads directly from it. Expect several pages here to reference each other out of page order, not only forward, and read a page's own "Where it fits" section closely rather than assuming a strict pipeline.

## Basis labels

This page and every Stage 4 sub-stage page use the same three [basis labels](../stage-1/index.md#basis-labels) Stage 1's index defines: `documented`, `inferred` and `suggested`. This page does not redefine them.

Unlike Stage 1 through Stage 3, the project notes describe no code anywhere in this stage. Every page here has one prompt and no script, stated plainly on each page's own Scripts section, not omitted.

## How Stage 4 is run

Agents do the volume work: drafting each protocol's script, drafting a session's own selection and chaining decisions, classifying a wrong answer and drafting a diagnosis, drafting each response under the guardrail rules, and drafting a packaged bundle. People make each judgment call: approving the specification before first use, judging whether a real session followed it, approving a chapter's own catalog entries, and approving a packaged bundle before it reaches a learner. This is the same [human-in-the-loop](../glossary.md#human-in-the-loop) design every earlier stage uses.

## Approvals

| After | What the person approves | Human roles gate kind | Basis |
|---|---|---|---|
| S4.1 and S4.2 | The protocol library and the six principles, before first use | Plan approval | suggested |
| S4.5 | A chapter's own misconception-catalog entries, before they diagnose a real learner's errors | Plan approval | suggested |
| S4.6 | The guardrail policy, before first use | Plan approval | suggested |
| S4.7 | A packaged bundle, before it reaches a learner | Plan approval | suggested |

The project notes describe no explicit human-approval gate for this stage's own design-time work, unlike the per-chapter gates Stage 1 through Stage 3 describe. Every row above is this guide's own suggested checkpoint, stated as such. See [Human roles, gates and batching](../human-roles-gates-and-batching.md) for what each gate kind means and who can fill each role.

## Artifacts

- The protocol library and the six principles: one written specification. Defined on [S4.1 and S4.2](principles-and-protocol-library.md).
- A selected-protocol decision and a session's own chain of protocols. Defined on [S4.3 and S4.4](selection-and-chaining.md).
- A per-chapter misconception catalog and a per-answer diagnosis. Defined on [S4.5](misconception-catalog-and-error-diagnosis.md).
- A stated guardrail policy a learner can read. Defined on [S4.6](guardrails.md).
- Bundle files and a package manifest. Defined on [S4.7](packaging-and-scope.md).

## What is documented versus suggested

Several points in Stage 4 are this guide's own call, not [the project notes](../glossary.md#reference-implementation)'. Two real disagreements between project documents are stated as open, not resolved: whether the selection layer can ever be reached by a learner directly ([S4.3 and S4.4](selection-and-chaining.md)), and whether the integrity guardrail is one selectable protocol or three always-on cross-cutting sections ([S4.6](guardrails.md)). The link between a Stage-1-recorded misconception and this stage's own catalog is this guide's own suggested reading, illustrated with one worked example built fresh for this batch, not something the project notes demonstrate ([S4.5](misconception-catalog-and-error-diagnosis.md)). Every approval row above is this guide's own suggested checkpoint, since the project notes describe no explicit gate for this stage's design-time work.

## First actions for a new team

Suggested:

- Decide who approves the protocol library and the six principles before any real session runs against them.
- Confirm a chapter has cleared Stage 3's own closing checks before tutoring on it begins.
- Decide, for your own build, which reading of the selection layer's reachability and the integrity guardrail's own framing you are building toward, since the project notes do not settle either question.

This page states, once for all of Stage 4: the prompts here are samples, written for this guide and not run against any model in this build. Every threshold is a starting value, not a rule. See [Platform requirements](../platform-requirements.md) for what a platform must offer at this stage.

Next: [S4.1 and S4.2 Principles and protocol library](principles-and-protocol-library.md).
