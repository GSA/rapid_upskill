---
title: "Glossary"
nav_order: 85
status: "draft"
last_reviewed: "2026-09-21"
---

# Glossary

Each term below has its own stable link that other pages can use. A definition describes how this guide uses the word, and "the framework" means the five-stage method this guide describes.

## Agent {#agent}

An AI system that works toward a goal by taking steps and using tools, such as reading files or running commands.

## Agentic platform {#agentic-platform}

Software in which an [agent](#agent) can use tools, read and write files and run steps.

## Alignment matrix {#alignment-matrix}

A grid that shows how well each chapter prepares learners for each [exam skill](#exam-skill), rated high, medium, low or none. The [certification alignment](#certification-alignment) workstream produces it.

## Audit trail {#audit-trail}

Layer 3 of the [verification layers](#verification-layer). The framework specifies it as a record of every check made on the content, every problem found and every correction. Expert review is a separate layer, Layer 2.

## Batch {#batch}

A small group of units of work, such as sources or plan files, that are processed together in one run. Work can pause after each batch at a [gate](#gate) for a person to say whether to continue.

## Blueprint {#blueprint}

The program's own plan, which groups learning objectives (what a learner should be able to do) into weighted content domains (major topic areas). A certifying body's published list is a [certification outline](#certification-outline), not a blueprint.

## Capability {#capability}

A feature that a platform must offer for a [prompt](#prompt) to work, such as reading files, running commands in a terminal or searching the web. Each prompt names what it needs from a fixed list of ten, given in the [authoring conventions](contributing/authoring-conventions.md#capability-vocabulary). [Platform requirements](platform-requirements.md) says how to supply each one.

## Certification alignment {#certification-alignment}

A parallel workstream, not a [stage](#stage), that rates each chapter against each [exam skill](#exam-skill) in a [certification outline](#certification-outline) and uses the ratings to pace study. The ratings form an [alignment matrix](#alignment-matrix).

## Certification outline {#certification-outline}

The list of skills that a certifying body (the organization that awards a certification) publishes for an exam. Each entry on it is an [exam skill](#exam-skill). The program's own plan is the [blueprint](#blueprint), not this list.

## Condensation {#condensation}

Shortening text by applying named techniques, instead of cutting it as you go. In the framework, AI makes condensation passes over drafted text.

## Context window {#context-window}

The amount of text an AI model can take in at one time. When a long task fills it, work can continue in a fresh session with a [hand-off document](#hand-off-document).

## Distractor {#distractor}

A plausible wrong answer option in a multiple-choice test question. In the framework, Stage 5 builds distractors from the [misconceptions](#misconception) recorded in Stage 1. The question part is the [stem](#stem).

## Dry run {#dry-run}

A script mode that shows what the script would write or delete, without doing it. By this guide's convention, a script that writes or deletes files runs as a dry run unless you pass `--write`. The `mock` model provider, which lets a script that calls an AI model run offline, is a different thing.

## Exam skill {#exam-skill}

One entry in a [certification outline](#certification-outline): one skill that the exam covers. Its ID has the form `CB-d.n`, as in `CB-3.1`.

## Gate {#gate}

A checkpoint where a person approves before work continues. The [project notes](#reference-implementation) also use "gate" for automated script checks; this guide means a person's approval unless it says otherwise.

## Grounding {#grounding}

Making an AI answer from text it is given, with citations, instead of from what the model learned in training. In the framework, the AI tutor is designed to answer from course material in this way.

## Hallucination {#hallucination}

Output from an AI model that sounds confident but is false or invented. It is an error in what the AI wrote, unlike a [misconception](#misconception), which is a wrong belief a person holds.

## Hand-off document {#hand-off-document}

A file that lets a fresh session, meaning a new working conversation with an [agent](#agent), continue a task. It records the goal, the current task and the next action. The framework specifies keeping it current (in the [reference implementation](#reference-implementation), after every [batch](#batch)) and starting a new session when the [context window](#context-window) runs low.

## Human in the loop {#human-in-the-loop}

A design in which a person makes some of the decisions and approves work at set points, called [gates](#gate) in this guide. The [Human roles, gates and batching](human-roles-gates-and-batching.md) page lists which decisions the framework assigns to people.

## Integrity guardrail {#integrity-guardrail}

In the framework, a tutor rule for graded work. Instructors decide whether AI help is allowed on graded work; when it is not, the tutor's integrity guardrail withholds full solutions and offers hints. The framework specifies that the tutor applies it before choosing a coaching [protocol](#protocol-tutor).

## Item bank {#item-bank}

A tagged pool of test questions organised against a [blueprint](#blueprint); sources also call it a question bank.

## Job-task analysis {#job-task-analysis}

A list of the duties and tasks of a job, with the knowledge, skills and abilities needed to do them.

## Knowledge base {#knowledge-base}

The whole collection of [knowledge items](#knowledge-item) extracted from a program's sources, arranged in a [prerequisite hierarchy](#prerequisite-hierarchy).

## Knowledge item {#knowledge-item}

An extracted content record: a small self-contained idea in your own words, with a type such as definition or mechanism, links to related items, the source passage it came from (see [provenance](#provenance)) and a review status. Together the items form the [knowledge base](#knowledge-base). Neither a test question nor an [exam skill](#exam-skill) is a knowledge item.

## Misconception {#misconception}

A specific wrong belief that many people hold about a topic. In the framework, misconceptions are recorded for each [knowledge item](#knowledge-item) in Stage 1, and Stage 5 builds [distractors](#distractor) from those records.

## Misconception catalog {#misconception-catalog}

In the framework, a numbered list of the [misconceptions](#misconception) for one chapter. The tutor uses it to diagnose learner errors. It is not used to write distractors, which are built from the Stage 1 misconception records.

## Orchestrator {#orchestrator}

An [agent](#agent) that coordinates helper agents, called [subagents](#subagent). It is given the accept and merge decisions in the contract that sets out the work. It is an AI session, not a person.

## Placeholder {#placeholder}

A named gap in a [prompt](#prompt), such as `OBJECTIVE_ID`, that you replace with a real value. It is written in capital letters with underscores, inside doubled curly braces.

## Prerequisite hierarchy {#prerequisite-hierarchy}

Content sorted into four levels, from foundational to applied, where each level builds on the levels below it.

## Prompt {#prompt}

A written instruction that you give to an AI model. In this guide each prompt is one file, and it may contain [placeholders](#placeholder) that you fill in.

## Prompt injection {#prompt-injection}

An instruction hidden in a document or web page and aimed at the AI that reads it. Treat text an AI fetches as data, never as instructions.

## Protocol (tutor) {#protocol-tutor}

In the framework, a coaching protocol: a named, reusable teaching pattern for the AI tutor, with a trigger that says when to use it and a script of steps. It is a design for teaching, not the [prompt](#prompt) text that tells the AI what to do.

## Provenance {#provenance}

A record of where a [knowledge item](#knowledge-item) came from: the source document, the section and, where possible, the page.

## Rate limit {#rate-limit}

A cap that a service puts on how many requests you may make in a period.

## Reference implementation {#reference-implementation}

The original program and tooling this guide was written from. Where the guide gives numbers from it, they are that project's parameters, not universal rules. Its own working documents are called the project notes in this guide.

## Stage {#stage}

A major part of the framework. The framework has five stages that run in order and together build an [upskilling program](#upskilling-program). They are described in the [Pipeline overview](pipeline-overview.md).

## Stem {#stem}

The question part of a multiple-choice test question, written to make sense without its answer options.

## Sub-stage {#sub-stage}

A numbered part of a [stage](#stage), with an ID such as `S1.4a`, where S1 is the stage.

## Subagent {#subagent}

A helper [agent](#agent) that another agent starts for one part of a task. Several can run at the same time.

## Upskilling program {#upskilling-program}

A structured course of instruction, practice and assessment that aims to bring working professionals to competency in a topic, measured against an external standard where one exists.

## Verification layer {#verification-layer}

In the framework, one of three layers of checking that the framework specifies for drafted content. Layer 1 is automated checks that look for errors such as [hallucinations](#hallucination). Layer 2 is expert review, in which a subject-matter expert checks the content. Layer 3 is the [audit trail](#audit-trail), a record of the checks.

## Easily confused pairs {#confused-pairs}

Each row compares terms that are easy to mix up.

| Pair | The difference |
|---|---|
| [Knowledge item](#knowledge-item) vs [knowledge base](#knowledge-base) | A knowledge item is one small idea. The knowledge base is the whole collection of them. |
| [Blueprint](#blueprint) vs [certification outline](#certification-outline) | A blueprint is the program's own plan. A certification outline is a certifying body's list of exam skills. |
| [Certification outline](#certification-outline) vs [exam skill](#exam-skill) | The outline is the whole published list. An exam skill is one entry on it. |
| [Misconception](#misconception) vs [distractor](#distractor) | A misconception is a wrong belief. A distractor is a wrong answer option built from one. |
| [Misconception catalog](#misconception-catalog) vs [distractor](#distractor) | The catalog is the tutor's per-chapter list for diagnosing learner errors. Distractors are built from the Stage 1 misconception records, not from the catalog. |
| [Hallucination](#hallucination) vs [misconception](#misconception) | A hallucination is false or invented output from an AI model. A misconception is a wrong belief a learner holds. |
| [Protocol (tutor)](#protocol-tutor) vs [prompt](#prompt) | A protocol is a teaching pattern. A prompt is the text that instructs the AI. |
| [Agent](#agent) vs [subagent](#subagent) vs [orchestrator](#orchestrator) | An agent is an AI that works toward a goal. A subagent is a helper agent for one part of a task. An orchestrator coordinates subagents and is given the accept and merge decisions in the contract. |
| [Expert review](#verification-layer) vs [audit trail](#audit-trail) | Expert review is Layer 2 of the [verification layers](#verification-layer): people check the content. The audit trail is Layer 3: the record of checks, problems and corrections. |
| [Gate](#gate) vs an automated script check | A gate is where a person approves before work continues. An automated script check is not a gate in this guide, although the project notes sometimes call it one. |
| [Dry run](#dry-run) vs the `mock` model provider | A dry run is about writing files: it shows what would be written. The `mock` model provider is about calling an AI model: it lets a script run offline. |
