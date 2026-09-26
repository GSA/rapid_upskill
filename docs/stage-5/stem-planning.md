---
title: "S5.2 Stem planning"
parent: "Stage 5 Assessment development"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-26"
stage: "S5"
sub_stage: "S5.2"
prompts: ["P-S5-02"]
scripts: ["X-S5-02"]
---

# S5.2 Stem planning

## Outcome

At the end of this sub-stage you have a chapter's own **stem plan**: before any [stem](../glossary.md#stem) is drafted, a chapter's own [assessment concept items](misconception-to-distractor-bridge.md) are mapped to a planned set of rows by difficulty, and each planned [distractor](../glossary.md#distractor) already names the [misconception](../glossary.md#misconception) behind it.

## Where it fits

This sub-stage takes in a chapter's own assessment concept items from [S5.1 Misconception-to-distractor bridge](misconception-to-distractor-bridge.md). It hands its own plan on to [S5.3 and S5.4 Distractors and format rules](distractors-and-format-rules.md), where each planned row actually gets drafted into a stem, on its way toward the chapter's own [item bank](../glossary.md#item-bank).

## Why this way

A plan fixes what a stem will draw on, and where each of its distractors will come from, before any stem text exists. Naming the assessment concept item ids and the misconception behind each planned distractor first means a later drafting pass fills in wording against an already-checked shape, rather than inventing a combination of items and a wrong-answer story at the same moment a stem's own text is written.

## Steps

| Step | Who | Basis |
|---|---|---|
| Map each planned row's difficulty to how many assessment concept items it draws on | Agent | documented |
| Name the misconception behind each of a chapter's own planned distractors, before any stem text exists | Agent | documented |
| Check the plan against the eight-point checklist below | Agent | documented |
| Approve the plan before any stem is drafted | Person | suggested |

[The project notes](../glossary.md#reference-implementation) describe the difficulty-to-item-count mapping and the eight-point checklist as templates a person fills in by hand; naming a distractor's own misconception before any stem text exists is the one point every source this guide drew on agrees on. Approving the plan before drafting begins is this guide's own suggestion, since the project notes name no approver for this step.

## The eight-point checklist

Documented, in full. A person reads the plan against every point below before approving it; this page's own script (below) checks only the parts marked script-checked, by counting and by comparing ids.

1. Every assessment concept item the chapter has appears in at least one planned row.
2. The planned difficulty mix is roughly 30/50/20 (script-checked, as a warning).
3. Every planned row has a named distractor strategy.
4. A hard row genuinely needs more than one item, not just several items restated (item count is script-checked; whether the items genuinely need synthesis is not).
5. Cross-chapter opportunities are noted.
6. Prerequisite dependencies are noted.
7. No two planned rows duplicate the same concept.
8. Every stem type the chapter needs is represented.

The script also confirms that every id a row names resolves to a real assessment concept item; it does not confirm the reverse, that every concept item the chapter has appears somewhere in the plan (point 1), so that half of point 1 stays a person's own read.

## The difficulty-to-item-count mapping

Documented: how many assessment concept items a planned row draws on is fixed by its own difficulty.

| Difficulty | Assessment concept items |
|---|---|
| Easy | Exactly 1 |
| Medium | 2 to 3, combined in one scenario |
| Hard | 3 to 5, synthesized |

A hard row is not three items restated side by side; it needs a scenario where the items genuinely interact, so a learner cannot answer from any one of them alone. The reference implementation's parameters also target a whole plan's own difficulty mix at roughly 30 percent easy, 50 percent medium and 20 percent hard. "The 30/50/20 split is one of the reference implementation's parameters, that project's choice and not a universal rule," as the [pipeline overview](../pipeline-overview.md) already states. A small, single-chapter plan like the worked illustration below will rarely hit that split exactly, which is why this page's own script treats a wide miss as a warning, not an error.

## The stem-plan schema

The project notes' own stem-plan template is a Markdown document a person fills in by hand, not machine-checkable data. This guide's own `plan.json` schema below is this guide's own conversion of that same information into a shape a script can check, not a format the project notes themselves use.

A stem plan is a JSON list of rows: `{"plan_row_id": "PLAN-1", "difficulty": "easy"|"medium"|"hard", "concept_item_ids": [...], "distractor_misconceptions": [...]}`. Each row's `plan_row_id` names a planned row, never a stem: at this point no stem exists yet, only a plan a later sub-stage still has to draft. `concept_item_ids` lists the assessment concept item ids the row draws on, and its count must match the row's own difficulty from the table above. `distractor_misconceptions` names, in advance, the misconception behind each distractor the eventual stem will need; the script below does not check this field's own contents, since judging whether a named misconception is the right one is a person's own read.

## The id-scheme disagreement

This is the point in Stage 5 where a finished stem is first named, so the disagreement over how to id one belongs here. Two project documents disagree. A newer document ties a stem's id to its own chapter and sequence number, in the shape `STEM-<chapter>.<section>-<NNN>`, and links that id back to the assessment concept items that fed it. An older scaffold document uses a different id shape of its own, and separately carries a target certification's own domain and skill code fields; it does not link to any assessment concept item at all. This guide's own sample data uses the newer, chapter-linked scheme, adapted to the running example's own plain chapter numbers and dropping the certification-specific fields the older scaffold carries, because it is the scheme that actually names an assessment concept item. [S5.3 and S5.4](distractors-and-format-rules.md) drafts the two stems this plan calls for under that scheme.

## Worked illustration

The running example's own Chapter 2 gives this plan two rows. `PLAN-1` is easy and draws on `ACI-1-001` alone: the Chapter 1 item that a commit records a snapshot of the whole repository, not just the changed lines. Reusing a Chapter 1 item inside a Chapter 2 plan is not a mistake here; it is this worked illustration's own deliberate example of checklist point 5, cross-chapter opportunities are noted. A stem later drafted from this row still carries Chapter 2's own id, `STEM-2.1-001`, because a stem's id identifies where it is delivered, not where every item behind it first originated.

`PLAN-2` is medium and combines two Chapter 2 items, `ACI-2-001` and `ACI-2-002`, in a single merge-conflict scenario: one item about what merging itself does, the other about resolving a conflict a merge stops on. [S5.1](misconception-to-distractor-bridge.md) names both items in full; this plan only needs their ids and one misconception named per planned distractor, drawn from what each item's own extraction already found.

This small sample stops at two rows on purpose. A hard row needs three to five assessment concept items synthesized in one scenario, and this chapter's own plan has only three items to draw from in total; adding two invented items just to show a hard row would add a fact this guide's running example does not otherwise use. The pattern the difficulty-to-item-count table gives is what matters here, not a complete easy-medium-hard triple.

## Artifacts and formats

This sub-stage produces one file per chapter, the stem plan described above: a JSON list of rows, each with a `plan_row_id`, a `difficulty`, the `concept_item_ids` it draws on, and a `distractor_misconceptions` list naming the misconception behind each planned distractor.

## Prompts

[P-S5-02 Draft a stem plan](../prompts/s5/p-s5-02.md) drafts a chapter's own plan from its assessment concept items, naming a plan row id, a difficulty, the items each row draws on, and a misconception per planned distractor. It is written for this guide and has not been run against any model in this build; treat it as a starting point and adapt it.

## Scripts

[X-S5-02 Stem plan check](../scripts/s5/x-s5-02.md) checks a chapter's stem plan against its own assessment concept items: whether each row's item count matches its difficulty, whether every referenced id exists, and how far the plan's overall mix sits from 30/50/20. Run it from the repository root, against this plan and the chapter's own assessment concept items:

```bash
python3 -B scripts/s5/stem_plan_check.py scripts/sample_data/git_basics_stage5/stem_plan/plan.json scripts/sample_data/git_basics_stage5/concept_items/items.json
```

```text
warning mix: plan is easy=50% medium=50% hard=0%, target is 30/50/20 (off by up to 20 points)
rows=2 errors=0 warnings=1
```

The script reports zero errors: both rows' own item counts match their difficulty, and every id either row names is present among the chapter's own assessment concept items. It still warns about the mix, because two rows split evenly between easy and medium cannot land anywhere near 30/50/20; that is expected on a sample this small, and the warning is exactly what checklist point 2 asks a person to read, not evidence the plan is wrong. The script does not check the other checklist points above, or the `distractor_misconceptions` field's own contents, so a clean run here is not the same as an approved plan.

## Definition of done

- Every row's own `concept_item_ids` count matches its difficulty from the table above.
- Every id a row names resolves to a real assessment concept item.
- Every point of the eight-point checklist above has been read against the plan, not only the parts the script checks.
- A person has approved the plan before any stem is drafted.

## Common failures

- A plan that never checks its own difficulty mix against 30/50/20, so a chapter drifts toward all-medium rows without anyone noticing.
- A hard row planned from too few items to actually need synthesis, so each of its own items could stand as a separate, easier row instead.
- A planned distractor with no named misconception behind it yet, which pushes the job of inventing a plausible-sounding wrong answer onto whoever drafts the stem later, with no check that it traces to anything real.

## Adapting to your platform

- `llm`: proposes the planned rows and names a misconception per distractor from the chapter's own assessment concept items.
- `file-read`: reads the chapter's own assessment concept items; without it, paste them into the prompt by hand.
- `shell`: runs the stem plan check; without it, count each row's own items by hand against the table above, and check each id against the chapter's own item list.
- `human-approval`: a person reads the plan against the full eight-point checklist and approves it before any stem is drafted.

## Where humans decide

- Approving a chapter's own stem plan before any stem is drafted.
- Judging the checklist points the script does not check: cross-chapter opportunities, prerequisite dependencies, duplicate concepts, stem-type coverage, a genuinely synthesized hard row, and a named distractor strategy for every row.

Next: [S5.3 and S5.4 Distractors and format rules](distractors-and-format-rules.md).
