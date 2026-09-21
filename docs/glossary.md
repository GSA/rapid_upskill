---
title: "Glossary"
nav_order: 85
status: "draft"
last_reviewed: "2026-09-21"
---

# Glossary

Each term below has its own stable link, so other pages can point straight to it. A definition describes how this guide uses the word, and where it says "the framework" it means the method this guide describes.

## Agent {#agent}

An AI system that works toward a goal by using tools, such as reading files or running commands, and by taking several steps rather than answering once.

## Agentic platform {#agentic-platform}

Software in which an [agent](#agent) can use tools, read and write files and run steps. This guide describes what such a platform must offer instead of naming products.

## Alignment matrix {#alignment-matrix}

A grid that rates how closely each chapter matches each [exam skill](#exam-skill), as high, medium, low or none.

## Audit trail {#audit-trail}

In the framework, an unalterable record of every check made on the content, every problem found and every correction. It is the third [verification layer](#verification-layer).

## Batch {#batch}

A small group of items, such as sources or plan files, that are processed together in one run. Work can pause after each batch at a [gate](#gate) for a person to say whether to continue.

## Blueprint {#blueprint}

The program's own plan, which groups learning objectives (what a learner should be able to do) into content domains (major topic areas) and gives each domain a weight. A certifying body's published list is not a blueprint; it is a [certification outline](#certification-outline).

## Capability {#capability}

A feature that a platform must offer for a [prompt](#prompt) to work, such as reading files, running commands or searching the web. Each prompt names the capabilities it needs from a fixed list.

## Certification alignment {#certification-alignment}

A side workstream, not a [stage](#stage), that rates each chapter against each [exam skill](#exam-skill) in a [certification outline](#certification-outline) and uses the ratings to pace study. The ratings are kept in an [alignment matrix](#alignment-matrix).

## Certification outline {#certification-outline}

The list of skills that a certifying body, the organization that awards a certification, publishes for one of its exams. Each entry on the list is an [exam skill](#exam-skill).

## Condensation {#condensation}

Shortening text by applying a set of named techniques, instead of cutting it as you go. In the framework, AI makes condensation passes over drafted text during content development.

## Context window {#context-window}

The amount of text an AI model can take in at one time. When a long task fills it, work can continue in a fresh session with a [hand-off document](#hand-off-document).

## Distractor {#distractor}

A plausible wrong answer option in a multiple-choice test question, written from a recorded [misconception](#misconception). The question itself is the [stem](#stem).

## Dry run {#dry-run}

A script mode that shows what the script would write or delete, without doing it; a script that changes anything runs this way unless you pass `--write`. The `mock` model provider, which lets a script that calls an AI model run offline, is a different thing.

## Exam skill {#exam-skill}

One entry in a [certification outline](#certification-outline): a single skill that the exam covers. Its ID has the form `CB-d.n`, where d numbers the section of the outline and n numbers the skill within it, as in `CB-3.1`.

## Gate {#gate}

A checkpoint where a person approves before work continues. Scripts also have automated checks, which this guide does not call gates.

## Grounding {#grounding}

In the framework, making the AI tutor answer from reference text it has been given, and cite that text, instead of relying on what the model learned in training.

## Hallucination {#hallucination}

Output from an AI model that sounds confident but is false or invented. It is an error in what the AI wrote, unlike a [misconception](#misconception), which is a wrong belief a person holds.

## Hand-off document {#hand-off-document}

A file that lets a fresh session, meaning a new working conversation with an [agent](#agent), continue a task. It records the goal, the current task, any blocker and the next action.

## Human in the loop {#human-in-the-loop}

A design idea in which people keep the judgment calls, such as designing the [blueprint](#blueprint), reviewing content and rating test questions, while AI does high-volume work such as drafting. Stage pages have a section that lists where a person decides.

## Integrity guardrail {#integrity-guardrail}

In the framework, the tutor rule that withholds full solutions to graded work and points the learner to hints instead. The tutor applies it before choosing a teaching [protocol](#protocol-tutor).

## Item bank {#item-bank}

A pool of test questions, each tagged to the part of the [blueprint](#blueprint) it covers.

## Job-task analysis {#job-task-analysis}

A list of the duties and tasks of a job, with the knowledge, skills and abilities needed to do them. It is one step in mapping a topic before any content is written.

## Knowledge base {#knowledge-base}

The whole collection of [knowledge items](#knowledge-item) extracted from a program's sources, arranged in a [prerequisite hierarchy](#prerequisite-hierarchy).

## Knowledge item {#knowledge-item}

One small, self-contained idea, written in your own words, with a type, links to related items, evidence from the source and a status. A test question is not a knowledge item.

## Misconception {#misconception}

A specific wrong belief that many people hold about a topic. The framework records misconceptions with its [knowledge items](#knowledge-item), and test questions use them to write [distractors](#distractor).

## Misconception catalog {#misconception-catalog}

In the framework, a numbered list of the [misconceptions](#misconception) for one chapter. It is used to write [distractors](#distractor) and to diagnose why a learner's answer is wrong.

## Orchestrator {#orchestrator}

An [agent](#agent) that hands parts of a task to helper agents, called [subagents](#subagent), and decides which of their results to accept. It is an AI session, not a person.

## Placeholder {#placeholder}

A named gap in a [prompt](#prompt), written as a capitalised name with underscores, such as `OBJECTIVE_ID`, inside doubled curly braces. You replace it with a real value before you use the prompt.

## Prerequisite hierarchy {#prerequisite-hierarchy}

Content sorted into four levels, from foundational to applied. A higher level must build on the levels below it, so each idea comes after the ideas it depends on.

## Prompt {#prompt}

A written instruction that you give to an AI model. In this guide each prompt is a single file that lists the [capabilities](#capability) a platform needs to run it and any [placeholders](#placeholder) you fill in.

## Prompt injection {#prompt-injection}

An instruction hidden in a document or web page and aimed at the AI that reads it, not at a human reader. Treat text an AI fetches as data, never as instructions.

## Protocol (tutor) {#protocol-tutor}

A named, reusable teaching pattern for the AI tutor, with a trigger that says when to use it and a script of steps. It is a design for teaching, not the [prompt](#prompt) text that tells the AI what to do.

## Provenance {#provenance}

A record of where a [knowledge item](#knowledge-item) came from: the source document, the section and, where possible, the page.

## Rate limit {#rate-limit}

A cap that a service puts on how many requests you may make in a period. Going over it can make requests fail or be delayed.

## Reference implementation {#reference-implementation}

The original program and tooling this guide was written from. When the guide describes what was done in practice, it means this work, and its numbers are that project's choices, not universal rules.

## Stage {#stage}

A major part of the pipeline, the ordered set of steps that builds an [upskilling program](#upskilling-program). The framework has five stages, described in the [Pipeline overview](pipeline-overview.md), and this guide says stage, never phase.

## Stem {#stem}

The question part of a multiple-choice test question, written so that it makes sense without its answer options. The options are the correct answer and the [distractors](#distractor).

## Sub-stage {#sub-stage}

A numbered part of a [stage](#stage), with an ID such as `S1.4a`, where S1 is the stage.

## Subagent {#subagent}

A helper [agent](#agent) that another agent starts for one part of a task. Several can run at the same time.

## Upskilling program {#upskilling-program}

A structured course of instruction, practice and assessment that moves working professionals to competency in a topic, measured against an external standard where one exists.

## Verification layer {#verification-layer}

In the framework, one of three layers of checking applied to drafted content: automated detection of errors such as [hallucinations](#hallucination), review by an expert, and an [audit trail](#audit-trail).

## Easily confused pairs {#confused-pairs}

Each row compares terms that are easy to mix up.

| Pair | The difference |
|---|---|
| [Knowledge item](#knowledge-item) vs [knowledge base](#knowledge-base) | A knowledge item is one small idea written up as a record. The knowledge base is the whole collection of those records, arranged by prerequisites. |
| [Blueprint](#blueprint) vs [certification outline](#certification-outline) | A blueprint is the program's own plan for what to teach and how much weight each area gets. A certification outline is a list of exam skills written by the certifying body, not by the program. |
| [Certification outline](#certification-outline) vs [exam skill](#exam-skill) | The certification outline is the whole published list. An exam skill is one entry on that list. |
| [Misconception](#misconception) vs [distractor](#distractor) | A misconception is a wrong belief, recorded with the knowledge items. A distractor is a wrong answer option in a test question, written from a misconception. |
| [Hallucination](#hallucination) vs [misconception](#misconception) | A hallucination is false or invented output from an AI model, and checks aim to catch it before learners see it. A misconception is a wrong belief a learner may hold, and the tutor is designed to recognise it. |
| [Protocol (tutor)](#protocol-tutor) vs [prompt](#prompt) | A protocol is a designed teaching pattern with a trigger and steps. A prompt is the text or file that instructs an AI. One is a design and the other is an instruction. |
| [Agent](#agent) vs [subagent](#subagent) vs [orchestrator](#orchestrator) | An agent is any AI that works toward a goal with tools. A subagent is a helper agent started for one part of a task. An orchestrator is an agent that assigns work to subagents and decides which results to accept. |
| [Dry run](#dry-run) vs the `mock` model provider | A dry run is a script mode that shows what a script would write, without writing it. The `mock` model provider lets a script that calls an AI model run offline. One is about writing files and the other is about calling an AI model. |
