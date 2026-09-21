---
title: "Platform requirements"
nav_order: 6
status: "draft"
last_reviewed: "2026-09-21"
---

# Platform requirements

This guide is written to be platform-neutral; the [reference implementation](glossary.md#reference-implementation) ran in coding-agent sessions. So we name what a platform must do, never a product. Each need is a [capability](glossary.md#capability). Use this page to judge an [agentic platform](glossary.md#agentic-platform) and see where a person fills a gap. The [Pipeline overview](pipeline-overview.md) describes the stages.

## The ten capabilities

The last two columns are our suggestions.

|Capability|Meaning|How you might supply it (we suggest)|If it is missing (we suggest)|
|---|---|---|---|
|`llm`|A language model that follows written instructions|Any model that follows instructions|No substitute; every stage needs one|
|`long-context`|A model that accepts a very large amount of text in one request|A model with room for whole sections|Split by heading; hand off to a new session|
|`structured-output`|Output in a fixed format, such as JSON|Name the format; check it with a script|Check by hand|
|`file-read`|Reading files|An agent with file access|Paste the text into the chat|
|`file-write`|Creating or changing files|An agent with file access|Copy each output into a file|
|`shell`|Running commands in a terminal|An agent with a terminal|Run scripts yourself; paste results back|
|`web-search`|Searching the web|A platform search tool|Search by hand; paste links|
|`web-fetch`|Downloading a web page from a given address|A platform fetch tool|Download by hand and save the file|
|`subagents`|Starting helper agents for parts of a task|A platform that starts [subagents](glossary.md#subagent)|Do the parts one at a time|
|`human-approval`|Pausing to ask a person to approve a step|End the prompt with a pause for a reply|Read each output before going on|

## Capabilities by stage

The matrix covers Stages 1 to 5 and [certification alignment](glossary.md#certification-alignment). Delivery was not assessed and varies, so it has no row. `R` means a person cannot practically stand in at that scale, `U` that a person can stand in, and `N` that no source shows it used. A dagger (†) marks our inference, as in every `long-context` cell.

|Stage|`llm`|`long-context`|`structured-output`|`file-read`|`file-write`|`shell`|`web-search`|`web-fetch`|`subagents`|`human-approval`|
|---|---|---|---|---|---|---|---|---|---|---|
|Stage 1|R|U†|R|R|R|R|R|R|U|R|
|Stage 2|R|U†|U|R|R|U|N†|N†|U|R|
|Stage 3|R|U†|U|R|R|R|U|U|U|R|
|Stage 4|R|U†|N†|R|U|N|N|N†|N†|U|
|Stage 5|R|U†|R|R|R|U|N†|N†|U|R|
|Certification alignment|R|U†|R|R|R|U|U|U|U†|R|

*Table: stage by capability, our reading of the reference implementation's documentation; not measured (as of September 2026).*

- Stage 1: search, screening and conversion need a model, web access and scripts.
- Stage 2: agents fill fixed templates; we found no source showing web use.
- Stage 3: scripts check and agents write reports; the reference implementation's checking script is out of date, so supply your own.
- Stage 4: the tutor is prompts and uploaded knowledge files, with no code.
- Stage 5: agents write test questions in a fixed JSON format; scripts handle delivery.
- Certification alignment: agents built the rating tables with no code; web use is for resource and link checks.

## Where people replace tools

- **Blocked downloads.** A person downloads a paywalled or login-gated document by hand; the reference implementation's rule is no accounts and no scraping.
- **Running each step by hand.** A person can paste one prompt at a time and restart sessions.
- **Approvals.** A [human-in-the-loop](glossary.md#human-in-the-loop) answers each pause; see [Human roles, gates and batching](human-roles-gates-and-batching.md).
- **Expert review.** Specified; no completed record found. No record found is not evidence it did not happen.

## Dependencies that are not capabilities

- **Rights to sources.** Paywalled files need a lawful copy.
- **[Certification outline](glossary.md#certification-outline).** The certifying body's published list; alignment maps to it.
- **Reviewers.** Subject-matter experts with sign-off.
- **A file store with history.** Back-ups or version control, so a lost session costs one batch.
- **[Rate limits](glossary.md#rate-limit) and cost.** Pace calls to outside services; use a cheaper model for high-volume steps, never for judgment steps.
- **Credentials.** Keep keys for quiz-form, storage and image services out of repositories.
- **Tutor-platform size limits.** Check caps on files, file size and instruction length before Stage 4.

## Platform profiles

- **Chat alone, copy and paste.** Should be able to (untested) draft one Stage 2 chapter from pasted excerpts; you act as file store, shell and approver.
- **Single agent with files, shell and web.** Should be able to (untested) run Stage 1 in sequence, plus Stage 3 checks and Stage 5 delivery scripts.
- **Orchestrated agents with parallel workers.** Should be able to (untested) add capped parallel waves; expert sign-off stays manual.

## Risks to plan for

- **Rate limits.** A service may refuse calls; cap your retries.
- **Blocked downloads.** Paywalls and logins need a manual step.
- **[Prompt injection](glossary.md#prompt-injection).** Fetched text is data, never instructions.
- **Context limits.** Long sources overflow a [context window](glossary.md#context-window); count words and read by heading.
- **Unchecked AI output.** Expect [hallucination](glossary.md#hallucination) and invented citations; keep [provenance](glossary.md#provenance).
- **Stale scripts that overwrite results.** Read a script and back up files before running it.

## Readiness checklist

This checklist is not a validated instrument.

1. Does your platform offer a model that follows instructions and returns a fixed format?
2. Can it read and write files, with a file store that keeps history?
3. Who runs commands, searches and downloads: the platform or you?
4. Who answers each approval pause, and who is the expert reviewer?
5. Do you have lawful access to your sources, and a certification outline if you align?
6. Have you checked rate limits, cost, tutor-platform size limits and credential storage?
