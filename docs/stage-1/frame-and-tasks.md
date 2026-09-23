---
title: "S1.1 and S1.2 Frame the domain and list the tasks"
parent: "Stage 1 Knowledge acquisition"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-22"
stage: "S1"
sub_stage: "S1.1"
prompts: ["P-S1-01", "P-S1-02"]
scripts: []
---

# S1.1 and S1.2 Frame the domain and list the tasks

## Outcome

At the end of this sub-stage you have a dated boundary file, and an expert-checked **[job-task analysis](../glossary.md#job-task-analysis)**: a task list with a duty, and knowledge, skills and abilities, for each task. The date and version on the boundary file let a later reader tell which draft an approval, or a blueprint built from it, actually matches.

## Where it fits

This [sub-stage](../glossary.md#sub-stage) takes in a program goal and an audience description. Someone has to state both before any drafting starts, because every later choice, from the boundary rules to the blueprint's weights, reads back to them. It hands the boundary file and the task list on to [S1.3 Draft the blueprint](blueprint.md), which groups the tasks into weighted domains and objectives.

## Why this way

The blueprint built on these two files is the coverage instrument for the rest of Stage 1. A gap shows up later by checking a candidate source, or a search plan, against the blueprint's objectives, not by looking at the domain a second time and guessing what is missing. That only works if the boundary and the task list are complete enough to build a blueprint that actually covers the job.

[The project notes](../glossary.md#reference-implementation) give a step-by-step method for S1.1: state the goal, gather reference material, draft layers, audit them against real tasks, and redraft if too many misfit. For S1.2 they only describe the activity, listing duties, tasks and ratings, without saying how an agent should draft them or how a small team should handle re-rating. Most of S1.2 below is this guide's own suggestion for filling that gap, not a documented method, and its step table is marked accordingly. Skipping the expert re-rate is the one shortcut this guide advises against. An agent's frequency and criticality guesses have nothing to check them against, and S1.3 turns them directly into the weights that later sub-stages treat as settled.

## Steps

### S1.1 Frame the domain

A **layer** here is a broad grouping inside the domain, such as "branching and merging"; a **component** is a narrower topic inside a layer. A task or topic "misfits" when it does not sit under any drafted layer, which is a sign the layers are drawn in the wrong place, not that the task is unimportant.

| Step | Who | Basis |
|---|---|---|
| State the program goal and the audience | Person | documented |
| Collect two or three published decompositions of the field | Person or agent | documented |
| Draft layers and components from the decompositions | Agent | documented |
| Audit the layers against ten named real tasks or topics, and count misfits | Agent | documented; the project notes use 10 to 15 |
| Redraft the layers when more than two or three misfit | Agent | documented |
| Write boundary rules: inclusion and exclusion statements | Person | documented |
| Add a version and a date | Person | documented |

A published decomposition is any existing breakdown of the field: a course outline, a reference manual's table of contents, or a vendor's own topic list. Reading two or three keeps the draft from copying just one source's shape. The audit step exists so the boundary is tested against real work, rather than accepted on the strength of the decompositions alone. Redrafting is cheap this early, and expensive once the blueprint and the task list are built on top of a boundary that turns out to be wrong.

### S1.2 List the tasks

A **duty** is a broad area of responsibility, such as "combining and sharing work". A **task** is one specific, observable action inside a duty, such as "resolve a merge conflict". The **knowledge, skills and abilities** for a task are the facts, methods and capacities it needs. Frequency and criticality exist here because [S1.3](blueprint.md) turns them into a domain's weight, so a careless guess at this stage becomes a careless weight later.

| Step | Who | Basis |
|---|---|---|
| List duties and tasks, with an agent's help | Agent, checked by a person | inferred |
| Attach knowledge, skills and abilities to each task | Agent, checked by a person | inferred |
| Rate frequency and criticality as guesses, and mark them so | Agent | suggested |
| Have an expert re-rate each task; a small program uses a panel of two or three | Person | suggested |
| Record each rating and who gave it | Person | suggested |

A small program has no access to the large survey of raters that the project notes describe for this step. A panel of two or three subject-matter experts stands in for it here. Each rater re-rates every task; when raters disagree, one of them writes a one-line rationale for the rating the panel settles on. Recording who rated a task, and when, matters for the same reason the boundary file carries a version: a later reader needs to tell a checked rating from a guess that was never revisited.

## Artifacts and formats

The **boundary file** is a short Markdown file with five headings, each holding one or two lines: Inclusions, Exclusions, Adjacent domains (with the one rule that excludes each domain), Version, and Date. An adjacent domain is a related field the program is not about. Naming the rule that excludes it keeps a later search (S1.4a) from wandering into that field just because it shares vocabulary with this one. A fictional example, in the running example's style, shown here as five lines, one per heading:

```text
Inclusions: everyday commands for commits, branches, remotes, conflict resolution and safe recovery.
Exclusions: Git's internal object-storage format; server administration.
Adjacent domains: general command-line skills (excluded: assumes an existing terminal); continuous-integration configuration (excluded: a separate, later program).
Version: 0.1
Date: 2026-01-15
```

The **task list** is a CSV file with one row per task and this header: `task_id,duty,task,knowledge_skills_abilities,frequency,criticality,rating_status,rater,rated_on`. `frequency` and `criticality` are 1 to 5; `rating_status` is `guess` or `expert`, so a reader never has to infer which ratings still need a re-rate. A fictional example with four rows:

```text
task_id,duty,task,knowledge_skills_abilities,frequency,criticality,rating_status,rater,rated_on
T1,Combining and sharing work,Resolve a merge conflict,"reads conflict markers; stages the resolved file; completes the merge",3,4,expert,Author A,2026-01-20
T2,Combining and sharing work,Push local commits to a remote,"names the remote and branch; checks for a rejected push",4,3,expert,Author A,2026-01-20
T3,Snapshots and history,Write a clear commit message,"separates a short summary from body detail",5,2,expert,Author A,2026-01-20
T4,Recovering safely,Recover a commit no branch points to,"reads the reflog; creates a new branch at the found commit",1,5,expert,Author A,2026-01-20
```

## Prompts

This sub-stage uses two [prompts](../glossary.md#prompt). [P-S1-01 Domain framing for a boundary statement](../prompts/s1/p-s1-01.md) drafts the layers, tests them against a list of sample tasks, and drafts the boundary rules. A person still states the goal and audience and writes the final rules. [P-S1-02 Job-task analysis with guessed ratings](../prompts/s1/p-s1-02.md) drafts duties, tasks, and knowledge, skills and abilities, with frequency and criticality marked as guesses for an expert to re-rate. Both prompts are written for this guide and not run against any model in this build; treat each as a starting point and adapt it to your own program.

## Scripts

None.

## Definition of done

- The boundary file has inclusions, exclusions, adjacent-domain rules, a version and a date.
- Every task has a duty, and knowledge, skills and abilities.
- Every rating carries a rater and a date, and no row's `rating_status` is still `guess`.

## Common failures

- Coverage follows what is easy to find online, rather than what the goal needs; a layer with no source behind it looks fine until S1.4 turns up nothing to put in it.
- An unstated boundary lets two people cover the same ground, or leaves ground neither expected to own.
- A missing adjacent-domain rule lets a later search pull in results from a related but out-of-scope field.
- A rating an agent guessed gets treated as an expert rating because no one checked the `rating_status` column.
- The boundary file changes after the blueprint is drafted from it, but the version is never bumped, so a later reader cannot tell the two are out of step.

## Adapting to your platform

- `llm`: drafts decompositions, layers, tasks, and knowledge, skills and abilities.
- `human-approval`: a person states the goal and audience, writes the boundary rules, and re-rates every guessed rating.

No other [capability](../glossary.md#capability) is needed for this sub-stage; a chat window is enough. Later Stage 1 sub-stages add `web-search`, `shell` and `structured-output` once there is a blueprint to search against.

## Where humans decide

- The program goal and the audience: everything else in this sub-stage is drafted against them.
- Every boundary rule: what is included, excluded, and adjacent, because these rules bound what S1.4 is allowed to search for.
- Every frequency and criticality rating, once an expert or a panel re-rates it, because these ratings become the blueprint's weights in S1.3.

Next: [S1.3 Draft the blueprint](blueprint.md).
