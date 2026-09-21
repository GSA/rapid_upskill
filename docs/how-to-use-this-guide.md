---
title: "How to use this guide"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-21"
---

# How to use this guide

This page explains what you need, how pages are laid out, and how to read prompts and scripts.

## What you need

- A terminal, where you type commands.
- Python 3.10 or newer, to run the scripts. Check with `python3 --version`. On some systems, for example macOS, the default `python3` can be older. [Tooling](contributing/tooling.md) explains what happens then.
- An [agentic platform](glossary.md#agentic-platform). [Platform requirements](platform-requirements.md) says what it must offer.

## Reading paths

| Goal | Read |
|---|---|
| See all five stages on one page | [Pipeline overview](pipeline-overview.md) |
| Follow one small sample program | [The running example](running-example.md) |
| Learn where people decide and how to batch work | [Human roles, gates and batching](human-roles-gates-and-batching.md) |
| Check what your platform must offer | [Platform requirements](platform-requirements.md) |
| Look up a term | [Glossary](glossary.md) |

## Anatomy of a stage page

A **stage page** is a page for a [sub-stage](glossary.md#sub-stage) or a [stage](glossary.md#stage) of the framework. Each one has these sections, in this order.

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

A [prompt](glossary.md#prompt) is one file of instructions for your platform. A [placeholder](glossary.md#placeholder) is a name in double curly braces, such as {% raw %}`{{OBJECTIVE_ID}}`{% endraw %}. Replace each one with your own value before you run the prompt. The `capabilities` line lists the [capabilities](glossary.md#capability) your platform must offer, for example `file-read` or `web-fetch`.

## Scripts

Run every script as a [dry run](glossary.md#dry-run) before you let it write. By this guide's convention, a script that writes or deletes files does nothing until you pass `--write`. Without that flag, it reports what it would change.

A script that calls a language model uses the offline `mock` model provider by default. It needs no key and stands in for a real model, so it is not a dry run. From the repository root, try it:

```bash
python3 -B scripts/common/llm_adapter.py --prompt "Hello"
```

## Status words and IDs

A page's status is `draft` (still being written), `reviewed` (a second person or agent has checked it against sources), or `stable` (reviewed, and also read on the live site). Prompts, scripts, and sub-stages have IDs such as `P-S1-04`, `X-OP-01`, and `S1.4a`. The codes `CA`, `DL`, and `OP` label side workstreams and cross-cutting pages, not stages of the framework. The [authoring conventions](contributing/authoring-conventions.md) cover both.

## Terms

Each term is explained where it is introduced. The [Glossary](glossary.md) lists them all.
