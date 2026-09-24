---
title: "How to use this guide"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-21"
---

# How to use this guide

This page explains what you need, how to get the files, how pages are laid out, and how to read [prompts](glossary.md#prompt) and scripts.

## What you need

- A terminal, to type commands.
- Git, to copy the repository to your computer.
- Python 3.10 or newer, to run the scripts. On some systems, such as macOS, the default `python3` can be older. [Tooling](contributing/tooling.md) explains what happens then. The steps below show how to check your version.
- An [agentic platform](glossary.md#agentic-platform). [Platform requirements](platform-requirements.md) says what it must offer, and ends with a [readiness checklist (not a validated instrument)](platform-requirements.md#readiness-checklist-not-a-validated-instrument) to answer before you start.

## Get the repository

The repository holds the scripts and the sample data. Copy it once, then work from its folder in a terminal.

Copy the repository to your computer:

```bash
git clone https://github.com/GSA/rapid_upskill.git
```

Then move into the new folder:

```bash
cd rapid_upskill
```

Then check your Python version. The number after `Python` must be 3.10 or higher:

```bash
python3 --version
```

Run every command in this guide from this folder, called the repository root.

## Reading paths

| Goal | Read |
|---|---|
| See all five [stages](glossary.md#stage) on one page | [Pipeline overview](pipeline-overview.md) |
| Follow one small sample program | [The running example](running-example.md) |
| Work through Stage 1 with sample prompts and scripts | [Stage 1 Knowledge acquisition](stage-1/index.md) |
| Learn where people decide and how to batch work | [Human roles, gates and batching](human-roles-gates-and-batching.md) |
| Check what your platform must offer | [Platform requirements](platform-requirements.md) |
| Look up a term | [Glossary](glossary.md) |

## Anatomy of a stage page

A **stage page** is a page for a [sub-stage](glossary.md#sub-stage) or a stage of the framework. [Stage 1](stage-1/index.md) is published; pages for the other four stages are planned. Each stage page has these sections, in this order.

- Outcome: what you will have at the end.
- Where it fits: what comes before and after, and what this part takes in and hands on.
- Why this way: the reasons for the approach, with a source for every number.
- Steps: numbered actions, each starting with a verb.
- Artifacts and formats: the files the steps produce, and their formats.
- Prompts: links to the prompts the page uses.
- Scripts: links to the scripts the page uses.
- Definition of done: conditions you can check.
- Common failures: what goes wrong, and how to spot it.
- Adapting to your platform: what the steps need, and how to supply it elsewhere.
- Where humans decide: each point where a person must decide or approve.

The exact template is in the [authoring conventions](contributing/authoring-conventions.md).

## Prompts

A prompt is one file of instructions for your platform. A [placeholder](glossary.md#placeholder) is a name in double curly braces, such as {% raw %}`{{OBJECTIVE_ID}}`{% endraw %}. Replace each with your own value before you run the prompt. The `capabilities` line lists the [capabilities](glossary.md#capability) your platform must offer, for example `file-read` or `web-fetch`.

## Scripts

Before you let a script write files, run it as a [dry run](glossary.md#dry-run). By this guide's convention, a script that writes or deletes files does nothing until you pass `--write`. Without that flag, it reports what it would change.

A script that calls a language model uses the offline `mock` model provider by default. It needs no key. It stands in for a real model and is not a dry run. From the repository root, try it. The `-B` flag stops Python from writing cache folders.

```bash
python3 -B scripts/common/llm_adapter.py --prompt "Hello"
```

For the prompt `Hello`, the command prints this one line:

```text
MOCK:185f8db32271
```

The mock provider gives the same reply every time for the same prompt. A different prompt gives a different reply. On Python older than 3.10, the tool prints one line and stops with exit code 2.

The guided hands-on task is [Your first prompt](contributing/first-prompt.md). It takes about 15 minutes. You add a practice prompt, run the checker, and remove the practice files. Nothing is sent to an AI model.

## Status words and IDs

A page's status is `draft` (still being written), `reviewed` (a second person or [agent](glossary.md#agent) has checked it against sources), or `stable` (reviewed, and also read on the live site). Prompts, scripts, and sub-stages have IDs such as `P-S1-04`, `X-OP-01`, and `S1.4a`. The codes `CA` (certification alignment), `DL` (delivery), and `OP` (operating practices) do not label stages. Certification alignment is a parallel workstream, delivery is outside the framework, and operating practices apply across stages. The [authoring conventions](contributing/authoring-conventions.md) cover both.

## Scope of this guide

This guide is platform-neutral. It describes a design and how the [reference implementation](glossary.md#reference-implementation) was run, as of September 2026. It makes no claims about results.

## Terms

Pages explain each term where it is introduced. The [Glossary](glossary.md) gathers the key terms in one place.

Next: [The running example](running-example.md).
