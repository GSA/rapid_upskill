---
title: "Pipeline overview"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-21"
---

# Pipeline overview

## The shape of the framework

The framework has five [stages](glossary.md#stage) that run in order. Each stage pairs a job for AI, a mechanism aimed at the learner, and a quality check. The description follows the [reference implementation](glossary.md#reference-implementation), the project this guide draws on. This guide calls that project's own working documents the project notes. Stage 1 through Stage 3, and Stage 5, are published as a worked sequence of sub-stage pages with sample prompts and scripts, and Stage 4 with sample prompts; all five stages are now published.

![Five stages in a row, Knowledge acquisition to Assessment development, with human judgment above and possible external checks below. The figure shows the framework as specified; no results are reported. Certification alignment and delivery sit apart, outside the stages.](assets/images/pipeline-overview.svg)

## The figure in words

- Five boxes run left to right, joined by solid arrows. Table A names them.
- The top band lists [blueprints](glossary.md#blueprint), expert review, [misconceptions](glossary.md#misconception) and question ratings (ratings of test questions). Dashed arrows run to Stages 1, 3, 4 and 5, and none to Stage 2, although people also judge fit there. "As specified" means the framework assigns this work, not that it was done.
- The bottom band, Possible external checks, names four kinds of check that could apply: a vendor-scored certification exam, an analysis built on the [knowledge base](glossary.md#knowledge-base), review by an adopting institution's experts, and standards-body review. Dotted arrows leave Stages 1, 3 and 5; the figure does not say which check applies where. A note in the band says the figure is not affiliated with or endorsed by any certifying body.
- The learner-facing stages draw on the Stage 1 knowledge base; no arrows show this.
- The two bottom boxes are not stages. Certification alignment is a parallel workstream. Delivery is outside the framework and not assessed here.

## Two design aims

One aim is to shorten the time to produce learning materials, using AI at every stage. The other is to shorten the time a learner takes to reach competence. Both are design aims, not measured effects: there is no timing baseline.

## Table A: what stages produce

Table A shows what the framework specifies for each stage.

| Stage | Produces | What AI does |
|---|---|---|
| Stage 1: Knowledge acquisition | A knowledge base ordered by a [prerequisite hierarchy](glossary.md#prerequisite-hierarchy) | Explores the domain, extracts [knowledge items](glossary.md#knowledge-item) |
| Stage 2: Content development | Chapters with objectives, labs and exam-style test questions | Drafts chapters and shortens them |
| Stage 3: Review and verification | Validation reports (designed to be scored against numeric targets; agents wrote the reports in the reference implementation) | Automated checks for [hallucination](glossary.md#hallucination) are specified. The [verification layers](glossary.md#verification-layer) are Layer 1 automated checks, Layer 2 expert review and Layer 3 [audit trail](glossary.md#audit-trail) |
| Stage 4: AI-tutor coaching | Named [coaching protocols](glossary.md#protocol-tutor), a [misconception catalog](glossary.md#misconception-catalog) per chapter, learner guardrails | Is designed to tutor one to one, following a protocol |
| Stage 5: Assessment development | An [item bank](glossary.md#item-bank) of blueprint-tagged test questions, mock exams, quizzes, practice tests | Writes test questions and [distractors](glossary.md#distractor) (wrong answer options) |

## Table B: checks and learner help

The people who act at each stage are listed on [Human roles, gates and batching](human-roles-gates-and-batching.md), so this table leaves them out.

| Stage | Quality check (as specified) | Designed to help learners by |
|---|---|---|
| Stage 1: Knowledge acquisition | Checks that the content covers the blueprint; higher levels of the hierarchy must refer to lower levels | Prerequisite order, so each lesson builds on ideas already learned |
| Stage 2: Content development | Fixed templates; revising the draft in six successive passes | One new element at a time; review that revisits earlier material |
| Stage 3: Review and verification | Automated checks, expert review and an audit trail | Catching defects before learners study the content |
| Stage 4: AI-tutor coaching | [Integrity guardrails](glossary.md#integrity-guardrail); answers [grounded](glossary.md#grounding) in course material | Coaching protocols that adapt to the learner's intent and feelings; diagnosing a wrong answer from the misconception catalog |
| Stage 5: Assessment development | Blueprint tagging; difficulty fixed in advance, with a 30/50/20 split across easy, medium and hard test questions | Distractors written from recorded misconceptions; low-stakes quizzes; practice tests |

The last column lists design intents, not measured effects. The 30/50/20 split is one of the reference implementation's parameters, that project's choice and not a universal rule. The tables show what the framework specifies, not that any step was completed.

## The parallel workstream and delivery

[Certification alignment](glossary.md#certification-alignment) compares each chapter with a [certification outline](glossary.md#certification-outline), the list of skills a certifying body publishes. Its output is an [alignment matrix](glossary.md#alignment-matrix): a grid that rates how well each chapter prepares learners for each [exam skill](glossary.md#exam-skill), one entry in that list. The ratings are high, medium, low or none, and they are meant to show learners where to spend study time. Agents produced the ratings in the reference implementation. One certification was the design target. This is a parallel workstream, not a stage.

Delivery is outside the framework and not assessed here. This guide makes no claims about it.

## How the stages connect

| Stage | Takes in | Hands on |
|---|---|---|
| Stage 1: Knowledge acquisition | Sources admitted by people | The knowledge base, with misconceptions recorded for each knowledge item; the blueprint |
| Stage 2: Content development | Knowledge base, blueprint | Chapters |
| Stage 3: Review and verification | Stage 2 chapters | Validation reports on them |
| Stage 4: AI-tutor coaching | Chapter text; a misconception catalog this guide's own S4.5 page builds, with a suggested (not sourced) link back to Stage 1's own misconception-typed knowledge items | Tutoring for learners; a per-chapter misconception catalog, which the tutor uses to diagnose learner errors |
| Stage 5: Assessment development | Blueprint; a finished chapter's own text, from which it extracts its own misconceptions afresh | Test questions for learners |

The figure assigns misconception authoring to people at Stage 4. The project notes also record misconceptions at Stage 1. Stage 5's own extraction step records a further, separate set of misconceptions directly from each chapter's own text, and builds wrong answers from those, not from the Stage 1 records.

## Checks you do not control

The figure's bottom band lists checks that could apply. Some are outside the framework's control: a certifying body sets its own exam's content and grading. In this guide's assessment, a framework that produces its own measure of success cannot show by itself that it works, so outside checks matter. This guide reports no results from them.

## What the framework does not claim

- No controlled comparison and no timing baseline, so no claim of time saved.
- This guide does not report how the Layer 1 checks performed. Expert review (Layer 2) and the audit trail (Layer 3) are specified; no completed record was found. No record found is not evidence that something did not happen.
- The framework assigns question ratings and misconception authoring to people. This guide does not claim that either was done.
- No pilot with live examinee data, so test-question quality is a design goal, not a result.
- The tutor's design cites published research for its design choices. This guide does not claim that the finished tutor achieves those effects.
- The name of Stage 3 states its purpose, not its achievement.

Next: [How to use this guide](how-to-use-this-guide.md).
