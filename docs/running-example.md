---
title: "The running example"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-21"
---

# The running example

Every stage of this guide works on the same small, fictional program: **Git Basics for New Team Members**. Using one example throughout keeps the prompts, data and scripts consistent. You can follow a single thread from the first source search to the last quiz question.

This guide is not affiliated with or endorsed by the Git project.

## What the program is

The program teaches a new developer the everyday Git skills needed to work on a shared codebase. It has four domains, twelve objectives, three chapters and a blueprint for a bank of 20 quiz stems. A second file describes a fictional certification, so the alignment step has an outline to compare against. Seven short sources supply the knowledge. Some are good, and some are flawed on purpose.

Everything is synthetic. The authors, dates and links are invented, the URLs use reserved example domains, and all prose is original. The files are released under CC0-1.0.

## Why this example

- **Relevant to developers.** Version control is part of daily work on a software team, so the topic matters to the readers of this guide.
- **Checkable facts.** The behaviors described in the accurate sources were run on Git 2.54.0, and you can repeat them offline in a few minutes. Statements about older versions come from release notes and were not run.
- **Misconceptions with clear answers.** Some ideas about commits, branches and pulls are easy to get wrong, and a command shows which reading is right. That gives the misconception steps real material.
- **Version-dependent details.** A few behaviors change with the Git version or with settings. The sources say so, which lets the guide teach how to handle a claim that depends on context.
- **A small scope.** The whole example fits in one sitting, yet it is large enough to exercise the stages.

To see which version you have, run this command and compare it with the pinned version:

```bash
git --version
```

The pinned output is:

```text
git version 2.54.0
```

## The four domains

| ID | Domain | Weight |
|---|---|---|
| D1 | Snapshots and history | 25 |
| D2 | Branching and merging | 30 |
| D3 | Working with remotes | 25 |
| D4 | Recovering and collaborating safely | 20 |

The weights add up to 100. Each domain has three objectives. Applied to a bank of 20 stems, the weights give 5, 6, 5 and 4 stems, and the difficulty split of 30, 50 and 20 gives 6, 10 and 4.

Each objective records a Bloom level, a tier from 1 to 4, a chapter, and the sources that support it. This is one objective as it appears in the blueprint:

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

Exactly one objective, D4.2, has an empty `supported_by` list. It is a planted coverage gap that no source teaches.

## The seven sources

| ID | Title | Role |
|---|---|---|
| SRC-001 | What a commit really records | Accurate. Snapshots and staging, with misconception sentences |
| SRC-002 | Branches are just names | Accurate. Branches, HEAD and merging, with misconception sentences |
| SRC-003 | Conflicts and undo: a field guide | Accurate. Conflicts, restore, revert and reset, with misconception sentences |
| SRC-004 | Sharing work: fetch, pull and push | Accurate. Remotes, with version and setting caveats |
| SRC-005 | Quick cheat sheet: sending and getting changes | Older source that conflicts with SRC-004 on what a pull does |
| SRC-006 | A tidy commit routine | Ordinary tutorial with one harmless embedded instruction, for injection screening |
| SRC-007 | The best graphical Git clients, ranked | Promotional, low quality, with unsupported claims |

## Where later pages will use each part

These uses are planned. Page titles may change.

- **Blueprint.** The framing and blueprint pages show its shape. The coverage page finds the gap at D4.2. The concept-map page uses the tiers. The stem-planning and difficulty pages use the bank size, the split and the weights.
- **SRC-001 to SRC-003.** The extraction and knowledge-item pages use them as clean sources. Their "common mistake" sentences feed the misconception catalog and the distractor pages.
- **SRC-004 and SRC-005.** The conflict-handling steps compare them. The older date is one clue for deciding which claim to trust.
- **SRC-006.** The screening pages use it to practice spotting an instruction hidden inside otherwise normal text.
- **SRC-007.** The search and relevance steps use it as a source to reject.
- **Certification outline.** The alignment pages use it to find one skill that no chapter covers and one chapter that matches no skill.
- **Pinned version.** The provenance pages use it to show how facts were checked.

## Get the files

The full example lives in [the sample data folder](https://github.com/GSA/rapid_upskill/tree/master/scripts/sample_data/git_basics). Its README explains every file, the reserved ID formats and the stem arithmetic. The seven sources are in [the sources folder](https://github.com/GSA/rapid_upskill/tree/master/scripts/sample_data/git_basics/sources).
