---
title: "The running example"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-21"
---

# The running example

Every [stage](glossary.md#stage) of this guide will use the same small, fictional program: Git Basics for New Team Members. Using one example throughout keeps the prompts, data and scripts consistent. You can follow a single thread from the search for sources to the finished test questions.

This guide is not affiliated with or endorsed by the Git project.

## What the program is

The program teaches a new developer the everyday Git skills needed to work on a shared codebase. It has four domains (major topic areas), twelve objectives (things a learner should be able to do) and three chapters. Its [blueprint](glossary.md#blueprint) is the program's own plan. The blueprint sets a bank of 20 test questions, counted as [stems](glossary.md#stem), the question parts.

A second file describes a fictional certification. Its [certification outline](glossary.md#certification-outline) is a certifier's list of skills, so the [certification alignment](glossary.md#certification-alignment) workstream has a list to compare against. Each entry on that list is an [exam skill](glossary.md#exam-skill).

Seven short sources supply the knowledge. Some are good, and some are flawed on purpose.

Everything is synthetic, meaning invented for this guide. The authors, dates and links are invented, the URLs use reserved example domains, and all prose is original. The files are released under CC0-1.0.

## Why this example

- Relevant to developers: Version control is part of daily work on a software team, so the topic matters to the readers of this guide.
- Checkable facts: The behaviors described in the accurate sources were run on Git 2.54.0, and you can repeat them offline in a few minutes. Statements about older versions come from release notes and were not run.
- Clear answers to common mistakes: Some ideas about commits, branches and pulls are easy to get wrong. These wrong beliefs are called [misconceptions](glossary.md#misconception), and a command shows which reading is right. That gives the misconception steps real material.
- Version-dependent details: A few behaviors change with the Git version or with settings. The sources say so, which lets the guide teach how to handle a claim that depends on context.
- A small scope: The whole example fits in one sitting, yet it is large enough to use in every stage.

## What you need

Reading this page needs nothing extra. To repeat the Git behaviors yourself, you need these.

- A terminal, to type commands.
- Git, version 2.x. The behaviors were run on Git 2.54.0, and older versions may differ.
- The example files. [How to use this guide](how-to-use-this-guide.md#get-the-repository) shows how to copy the repository. The Get the files section below links to the folder.

To see which version you have, run this command:

```bash
git --version
```

The version this example was checked on prints as:

```text
git version 2.54.0
```

Some builds add a note after the number, such as the name of the company that packaged them. Compare the number, not the note.

## The four domains

| ID | Domain | Weight |
|---|---|---|
| D1 | Snapshots and history | 25 |
| D2 | Branching and merging | 30 |
| D3 | Working with remotes | 25 |
| D4 | Recovering and collaborating safely | 20 |

A weight is a domain's share of the program, out of 100. The four weights add up to 100. Each domain has three objectives. Applied to a bank of 20 stems, the weights give 5, 6, 5 and 4 stems. The blueprint also splits the 20 stems by difficulty, with shares of 30, 50 and 20 for easy, medium and hard. That gives 6, 10 and 4 stems.

Each objective records four things: a Bloom level, a tier, a chapter, and the sources that support it.

- A Bloom level is a label for the kind of thinking an objective asks for. The scale runs from remember, understand, apply, analyze and evaluate up to create.
- A tier is a number from 1 to 4 that gives the objective's place in the [prerequisite hierarchy](glossary.md#prerequisite-hierarchy). An objective at a higher tier builds on objectives at lower tiers.

The blueprint is stored as JSON, a plain-text data format in which each value has a name. This is one objective as it appears in the blueprint file:

```json
{
  "id": "D2.2",
  "text": "Tell a fast-forward merge from a merge commit and predict which one a given history will produce.",
  "bloom": "analyze",
  "tier": 3,
  "chapter": 2,
  "supported_by": ["SRC-002"]
}
```

In this file, `bloom` is the Bloom level, `tier` is the tier, `chapter` is the chapter, and `supported_by` lists the source IDs.

Exactly one objective, D4.2, has an empty `supported_by` list. No source teaches it. That makes it a coverage gap, meaning an objective that no source covers. The gap is planted: it is there on purpose, so that the coverage check has something to find.

## The seven sources

| ID | Title | Role |
|---|---|---|
| SRC-001 | What a commit really records | Accurate. Snapshots and staging, with sentences that name a common mistake |
| SRC-002 | Branches are just names | Accurate. Branches, HEAD and merging, with sentences that name a common mistake |
| SRC-003 | Conflicts and undo: a field guide | Accurate. Conflicts, restore, revert and reset, with sentences that name a common mistake |
| SRC-004 | Sharing work: fetch, pull and push | Accurate. Remotes, with version and setting caveats |
| SRC-005 | Quick cheat sheet: sending and getting changes | Older source that conflicts with SRC-004 on what a pull does |
| SRC-006 | A tidy commit routine | Ordinary tutorial with one harmless embedded instruction, for [prompt injection](glossary.md#prompt-injection) screening |
| SRC-007 | The best graphical Git clients, ranked | Promotional, low quality, with unsupported claims |

## Where later pages will use each part

Pages that show how each stage uses these files are planned and are not published yet, so this list does not link to them. Page titles may change.

- Blueprint: The framing and blueprint pages will show its shape. The coverage page will find the gap at D4.2. The page that maps how ideas depend on each other will use the tiers. The stem-planning and difficulty pages will use the bank size, the difficulty split and the weights.
- SRC-001 to SRC-003: The extraction and [knowledge item](glossary.md#knowledge-item) pages will use them as clean sources. Their "common mistake" sentences will feed the [misconception catalog](glossary.md#misconception-catalog) and the [distractor](glossary.md#distractor) pages.
- SRC-004 and SRC-005: The conflict-handling steps will compare them. The older date will be one clue for deciding which claim to trust.
- SRC-006: The screening pages will use it to practice spotting an instruction hidden inside otherwise normal text.
- SRC-007: The search and relevance steps will use it as a source to reject.
- Certification outline: The alignment pages will use it to find one exam skill that no chapter covers and one chapter that matches no exam skill.
- Tested Git version: The [provenance](glossary.md#provenance) pages will use it to show how the facts in the accurate sources were checked.

## Get the files

The full example lives in [the sample data folder](https://github.com/GSA/rapid_upskill/tree/master/scripts/sample_data/git_basics). Its README explains every file, the reserved ID formats and the stem arithmetic. The seven sources are in [the sources folder](https://github.com/GSA/rapid_upskill/tree/master/scripts/sample_data/git_basics/sources). In a clone of the repository, the same folder is `scripts/sample_data/git_basics`.

Next: [Human roles, gates and batching](human-roles-gates-and-batching.md).
