---
title: "S1.3 Draft the blueprint"
parent: "Stage 1 Knowledge acquisition"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-22"
stage: "S1"
sub_stage: "S1.3"
prompts: ["P-S1-03"]
scripts: ["X-S1-01"]
---

# S1.3 Draft the blueprint

## Outcome

At the end of this sub-stage you have a weighted **[blueprint](../glossary.md#blueprint)**: the program's own plan, grouping learning objectives into domains with a weight each. A person has approved it, and it passes the blueprint check script.

## Where it fits

This sub-stage takes in the boundary file and the task list from [S1.1 and S1.2 Frame the domain and list the tasks](frame-and-tasks.md). It hands on the blueprint to every later Stage 1 sub-stage: search planning reads its objectives, screening and extraction check sources against it, and the planned coverage sub-stage reads it again once sources are admitted.

## Why this way

The blueprint is the coverage instrument the rest of Stage 1 checks against. Later steps test whether a search result or a source fits one of its objectives, rather than re-reading the task list each time. A weight with no stated reason cannot be checked later against the task list it came from, so every weight here carries a one-line rationale a reader can audit. This page uses the [basis labels](index.md#basis-labels) defined on the Stage 1 index: most of the grouping and drafting is documented in [the project notes](../glossary.md#reference-implementation)' outline; the weight formula and the arithmetic check are this guide's own suggestion, because the project notes give no formula for turning ratings into weights.

## Steps

| Step | Who | Basis |
|---|---|---|
| Group tasks into domains | Agent | documented |
| Propose objectives with a cognitive level each | Agent | documented |
| Propose weights as frequency times criticality | Agent | suggested |
| Write a one-line rationale for each weight | Person | inferred |
| Edit weights so they sum to 100 | Person | suggested |
| Run the blueprint check | Script | suggested |
| Cross-tabulate domain by cognitive level and read the empty cells | Script | documented |
| Approve the blueprint | Person | suggested |

Grouping tasks into domains is documented in the project notes' outline; the JSON shape that holds the result, below, is this guide's suggestion. The weight rationale is inferred from an exam-development guide that requires a reason for every weight, applied here to this sub-stage. The formula, the rounding and the blueprint check itself have no described precedent, so they are marked suggested.

### Worked example

Five fictional tasks show the weighting method: multiply each task's frequency rating by its criticality rating, take each product's share of the total, then round to whole numbers that sum to 100.

| Task | Frequency (1-5) | Criticality (1-5) | Product | Share of the total | Weight (rounded) |
|---|---|---|---|---|---|
| T1 | 5 | 4 | 20 | 25.0 | 25 |
| T2 | 3 | 5 | 15 | 18.75 | 19 |
| T3 | 4 | 3 | 12 | 15.0 | 15 |
| T4 | 2 | 4 | 8 | 10.0 | 10 |
| T5 | 5 | 5 | 25 | 31.25 | 31 |
| Total | - | - | 80 | 100.0 | 100 |

Rounding rarely lands on 100 by itself. When it does not, edit the largest weight up or down by a point until the column sums to exactly 100, and say in the rationale that you did.

## Parameters

| Parameter | Value used in this guide | Basis |
|---|---|---|
| Cognitive scale | Six levels: remember, understand, apply, analyze, evaluate, create (configurable) | documented; the project notes describe three different scales (a three-level scale, a six-level scale, and a three-band split), and this guide's script defaults to the six-level one |
| Bank-size arithmetic | A domain's weight, times the bank size, divided by 100, should be a whole number | suggested |
| Objectives per chapter | 3 to 8 | documented; a parameter, not a rule |
| Lifecycle-stage axis | Not used | documented; the project notes name this axis once and never define it, so it is left out of this guide's blueprint |

## Artifacts and formats

This sub-stage produces one file, the blueprint: a JSON file with a top-level `program` name and a list of `domains`. Each domain holds an `id`, a `name`, a `weight` and a list of `objectives`, and may hold a one-line `rationale`. Each objective holds an `id`, a `text` statement and a `bloom` cognitive level.

Three more objective fields are filled in later and may be empty or missing at this point: `tier` (added at the planned concept-map sub-stage), `chapter`, and `supported_by` (added from S1.4 onward, once sources are admitted). An empty `supported_by` list is allowed here; the blueprint check never reads it. It becomes a coverage gap only once sources exist to check it against. The [running example](../running-example.md)'s finished blueprint file has every field, including `tier`, `chapter` and `supported_by`, because later sub-stages have already filled them in.

## Prompts

[P-S1-03 Blueprint domains, objectives and weights](../prompts/s1/p-s1-03.md) drafts the domains, objectives and weights from the task list and the boundary statement; a person edits the weights and writes the rationale. The prompt is written for this guide and not run against any model in this build.

## Scripts

[X-S1-01 Blueprint check](../scripts/s1/x-s1-01.md) checks a blueprint file's weights, ids and cognitive levels, and prints the domain by cognitive level cross-tab. It never reads `supported_by`. Run it from the repository root:

```bash
python3 -B scripts/s1/blueprint_check.py scripts/sample_data/git_basics/blueprint.json
```

On the running example's blueprint, which has no problems, it prints the cross-tab and a summary line:

```text
domain by cognitive level (dash means no objective at that level):
D1  remember=- understand=1 apply=1 analyze=1 evaluate=- create=-
D2  remember=- understand=1 apply=1 analyze=1 evaluate=- create=-
D3  remember=1 understand=- apply=1 analyze=1 evaluate=- create=-
D4  remember=- understand=- apply=1 analyze=- evaluate=1 create=1
domains=4 objectives=12 errors=0 warnings=0
```

Each row is one domain; each column is a cognitive level; a dash means no objective in that domain uses that level. The summary line counts domains, objectives, errors and warnings. See [Reading exit codes](index.md#reading-exit-codes) on the Stage 1 index for what the exit code means.

Break it on purpose: copy the file, then change the "Branching and merging" domain's weight from 30 to 31, so the weights no longer sum to 100, and run the check again on the copy:

```text
error weight-sum: domain weights sum to 101, not 100
warning bank-size: domain D2 weight 31 gives bank_size * weight / 100 = 6.2, not a whole number
domain by cognitive level (dash means no objective at that level):
D1  remember=- understand=1 apply=1 analyze=1 evaluate=- create=-
D2  remember=- understand=1 apply=1 analyze=1 evaluate=- create=-
D3  remember=1 understand=- apply=1 analyze=1 evaluate=- create=-
D4  remember=- understand=- apply=1 analyze=- evaluate=1 create=1
domains=4 objectives=12 errors=1 warnings=1
```

The one-point change trips two checks at once: the weights no longer sum to 100, and the changed weight no longer divides evenly into the bank size. With `--json`, the script prints the same information as one JSON object, for another script to read. `--levels` replaces the six-level scale with a comma-separated list of your own; a `bloom` value outside that list becomes an error. A clean run is not proof the weights are right, only that they are well-formed and add up; the rationale still needs a person's read.

## Definition of done

- Every domain has an `id`, a `name`, a `weight` and at least one objective.
- Every objective has an `id`, a `text` statement and a `bloom` value from the cognitive scale.
- The weights sum to exactly 100.
- Every weight has a one-line rationale that names the tasks behind it.
- The blueprint check reports no errors.
- A person has approved the blueprint.

## Common failures

- A weight with no rationale: a reader cannot check where the number came from.
- Two cognitive scales merged into one column, so "apply" and "medium difficulty" are treated as the same thing.
- Weights that sum to 100 by luck, but do not reflect the task list's frequency and criticality ratings.
- A domain with every objective below apply: the blueprint check warns, but a person still has to judge whether that is right for this domain.

## Adapting to your platform

- `llm`: drafts the domains, objectives and weights from the task list.
- `structured-output`: the blueprint is JSON; ask for that shape directly, or convert a plain-text reply by hand.
- `shell`: runs the blueprint check; without it, check the weight sum, the ids and the cognitive levels by hand, using the same rules.
- `human-approval`: a person edits the weights, writes the rationale, and approves the result before later sub-stages use it.

## Where humans decide

- The final weights, and the rationale behind each one.
- Approval of the blueprint before search planning begins.

Next: [S1.4a Search planning and execution](search-planning-and-execution.md).
