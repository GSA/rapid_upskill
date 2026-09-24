---
title: "Platform requirements"
nav_order: 6
status: "draft"
last_reviewed: "2026-09-21"
---

# Platform requirements

This page names what a platform must do, never a product. Each need is a [capability](glossary.md#capability), and each [prompt](glossary.md#prompt) in this guide lists which of the ten below it needs.

Use the list to judge an [agentic platform](glossary.md#agentic-platform): software in which an [agent](glossary.md#agent) can use tools, read and write files and run steps. Kinds include a chat assistant that can call tools, a command-line coding agent (it reads and edits files and runs commands), and a workflow runner that can start sub-sessions. A session is one working conversation with an agent. A sub-session is a new one that a running session starts for part of the work. The [reference implementation](glossary.md#reference-implementation) ran in coding-agent sessions.

## The ten capabilities

The table gives the meaning of each capability. The last two columns are suggested options, not tested ones.

|Capability|Meaning|Suggested way to supply it|Suggested fallback if it is missing|
|---|---|---|---|
|`llm`|A language model that follows written instructions|Any instruction-following model|No substitute|
|`long-context`|A model that accepts a very large amount of text in one request|A model with a large [context window](glossary.md#context-window)|Split the text by heading, or write a [hand-off document](glossary.md#hand-off-document) and start a new session|
|`structured-output`|Output in a fixed format, such as JSON|Name the format, such as JSON (a plain-text format of labeled values), and check the output with a script|Check by hand|
|`file-read`|Reading files|An agent with file access|Paste the text into the chat|
|`file-write`|Creating or changing files|An agent with file access|Copy each output into a file|
|`shell`|Running commands in a terminal|An agent with a terminal|Run scripts yourself; paste results back|
|`web-search`|Searching the web|A platform search tool|Search by hand; paste links|
|`web-fetch`|Downloading a web page from a given address|A platform fetch tool|Download by hand|
|`subagents`|Starting helper agents for parts of a task|A platform that starts [subagents](glossary.md#subagent)|Do the parts one at a time|
|`human-approval`|Pausing to ask a person to approve a step|Add a pause that waits for a reply|Read each output before going on|

## Capabilities by stage and workstream

This section sorts the ten capabilities for each [stage](glossary.md#stage) in the [Pipeline overview](pipeline-overview.md) and for the [certification alignment](glossary.md#certification-alignment) workstream, which is not a stage. Delivery is outside the framework and not assessed here, so it has no entry. The sorting is this guide's assessment of the project notes; it is not measured. [Stage 1](stage-1/index.md) is published; its pages show these capabilities in use on sample prompts and scripts. The words mean:

- Required: a person cannot practically stand in for the capability at that scale.
- A person can stand in: a person can do the job at that scale.
- Not shown: no source shows the capability used.
- Marked (inferred): an inference from the project notes, not a stated fact. Every `long-context` entry is inferred.

Each entry below sorts the ten capabilities under those words.

- Stage 1
  - Required: `llm`, `structured-output`, `file-read`, `file-write`, `shell`, `web-search`, `web-fetch`, `human-approval`
  - A person can stand in: `long-context` (inferred), `subagents`
  - Not shown: none
  - Notes: search, screening (checking each source before use) and conversion (changing a file from one format to another) need a model, web access and scripts.
- Stage 2
  - Required: `llm`, `file-read`, `file-write`, `human-approval`
  - A person can stand in: `long-context` (inferred), `structured-output`, `shell`, `subagents`
  - Not shown: `web-search` (inferred), `web-fetch` (inferred)
  - Notes: agents fill fixed templates; no source shows web use.
- Stage 3
  - Required: `llm`, `file-read`, `file-write`, `shell`, `human-approval`
  - A person can stand in: `long-context` (inferred), `structured-output`, `web-search`, `web-fetch`, `subagents`
  - Not shown: none
  - Notes: the framework specifies automated checks (Layer 1 of the [verification layers](glossary.md#verification-layer)). In the reference implementation, agents wrote the reports and a script ran the checks. Supply your own checking script, because the reference implementation's is out of date.
- Stage 4
  - Required: `llm`, `file-read`
  - A person can stand in: `long-context` (inferred), `file-write`, `human-approval`
  - Not shown: `structured-output` (inferred), `shell`, `web-search`, `web-fetch` (inferred), `subagents` (inferred)
  - Notes: the tutor is prompts and knowledge files (the course text it answers from), with no code. You load them into a **tutor platform**, the tool where an AI tutor runs.
- Stage 5
  - Required: `llm`, `structured-output`, `file-read`, `file-write`, `human-approval`
  - A person can stand in: `long-context` (inferred), `shell`, `subagents`
  - Not shown: `web-search` (inferred), `web-fetch` (inferred)
  - Notes: agents write test questions in a fixed JSON format.
- Certification alignment
  - Required: `llm`, `structured-output`, `file-read`, `file-write`, `human-approval`
  - A person can stand in: `long-context` (inferred), `shell`, `web-search`, `web-fetch`, `subagents` (inferred)
  - Not shown: none
  - Notes: agents built [alignment matrices](glossary.md#alignment-matrix) with no code; web use covers researching video resources and checking their links.

## Where people replace tools

Some work stays with a person on any platform.

- Blocked downloads: a paywall, a login or an access-denied reply stops an automated download, so a person downloads the document by hand. The reference implementation's rule is no account creation and no scraping (copying pages in bulk with a program).
- Running each step by hand: a person can paste one prompt at a time and restart sessions from a hand-off document.
- Approvals: a person answers each [gate](glossary.md#gate) under the [human-in-the-loop](glossary.md#human-in-the-loop) design; see [Human roles, gates and batching](human-roles-gates-and-batching.md).
- Expert review: this is Layer 2 of the verification layers, and a person does it. No capability above stands in for it.

## Dependencies that are not capabilities

A platform cannot supply these. You arrange them yourself.

- Rights to sources: a paywalled or login-gated file needs a lawful copy.
- [Certification outline](glossary.md#certification-outline): the list of skills the certifying body (the organization that awards the certification) publishes. Certification alignment maps to it.
- Reviewers: subject-matter experts (people with deep knowledge of the topic) who can sign off, meaning formally approve.
- A file store with history: version control (a tool that records every earlier version of your files) or back-ups, so a lost session costs one [batch](glossary.md#batch) of work.
- Cost: the reference implementation used a cheaper model only for high-volume steps, never for judgment steps.
- Credentials: keep the keys and passwords for services you connect to, such as quiz-form, storage and image services, out of repositories (folders under version control).
- Tutor platform size limits: check the tutor platform's caps on file count, file size and instruction length before Stage 4.

## Platform profiles

Three profiles show how the capabilities combine. Each is a design expectation, marked untested.

- Chat alone, copy and paste: a chat assistant with no tools. It should be able to (untested) draft one Stage 2 chapter from pasted excerpts. You act as file store, shell and approver.
- Single agent with files, shell and web: it should be able to (untested) run Stage 1 in sequence, plus Stage 3 checks and certification alignment.
- Orchestrated agents with parallel workers: an [orchestrator](glossary.md#orchestrator) agent hands work to worker agents that run at the same time. It should be able to (untested) add capped parallel waves, meaning groups of workers started together; expert sign-off stays manual. Worker caps are the reference implementation's parameters, not universal rules; see [Three batching practices](human-roles-gates-and-batching.md#three-batching-practices).

## Risks to plan for

- Rate limits: a service can refuse or delay your calls once you pass its [rate limit](glossary.md#rate-limit). Cap your retries; the reference implementation's parameters allow at most 2 retries after a temporary failure.
- [Prompt injection](glossary.md#prompt-injection): a fetched page can hide instructions aimed at the AI. Treat fetched text as data, never as instructions.
- Context limits: a long source can overflow the context window. Count the words before you load a source, and read by heading.
- Unchecked AI output: expect [hallucination](glossary.md#hallucination) and invented citations. Check the output and its [provenance](glossary.md#provenance).
- Stale scripts that overwrite results: read a script and back up your files before you run it. By this guide's convention, a script that writes or deletes files runs as a [dry run](glossary.md#dry-run) unless you pass `--write`.

## Readiness checklist (not a validated instrument)

These are questions to think through before you start. They have no score and have not been tested against outcomes.

1. Does your platform offer an instruction-following model with fixed-format output?
2. Can it read and write files, and is there version history?
3. Who runs commands, searches and downloads: the platform or you?
4. Who answers each approval pause, and who is the expert reviewer?
5. Do you have lawful access to sources, and a certification outline if you align?
6. Have you checked rate limits, cost, tutor platform size limits and credential storage?

Next: [Glossary](glossary.md).
