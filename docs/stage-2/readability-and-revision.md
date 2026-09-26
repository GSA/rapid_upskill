---
title: "S2.3 and S2.4 Readability polish and six-pass revision"
parent: "Stage 2 Content development"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-25"
stage: "S2"
sub_stage: "S2.3"
prompts: ["P-S2-03"]
scripts: ["X-S2-03"]
---

# S2.3 and S2.4 Readability polish and six-pass revision

## Outcome

At the end of this sub-stage a chapter reads well to a beginner: each section adds only one new idea at a time, worked examples come before independent practice, and jargon is defined in place. The wording changes; the technical content does not. Six fixed passes check the result, one concern at a time, ending with a non-expert reading the chapter aloud and confirming that nothing earlier is assumed rather than reviewed.

## Where it fits

This sub-stage takes in the condensed chapter from [S2.2 Condensation](condensation.md). It hands on the revised chapter to [S2.5 Closing templates and the prerequisite check](closing-templates.md), which adds a summary and a prerequisite-review block to the chapter this sub-stage leaves behind.

## Why this way

Condensing for length and revising for readability are different jobs. Doing them in this order means the shorter chapter is what gets polished, not a draft that later gets thrown away. Running the six passes separately, one concern at a time, also matters. A single holistic read tends to catch whichever problem is most obvious and miss the rest; a fixed order of narrow passes makes each concern someone's job in turn. This page's steps carry the same three [basis labels](../stage-1/index.md#basis-labels) used across this guide: documented, inferred and suggested.

## Steps

The readability polish sets up the material a chapter needs; the six-pass revision then checks that the material actually landed, one concern per pass.

### Readability polish

| Step | Who | Basis |
|---|---|---|
| Restructure each section to add exactly one new complexity dimension, called One New Element (defined below), while reviewing what came before | Agent | documented for the technique, suggested for who does it |
| Order each section's material concrete before abstract, with a worked example before independent practice | Agent | documented for the technique, suggested for who does it |
| Distribute cumulative-review questions every third section, mixed 70/20/10 (defined below) | Agent | documented for the split, suggested for who does it |
| Add one captioned diagram per dense concept | Agent | documented for the technique, suggested for who does it |

### Six-pass revision

Run these six passes in this fixed order.

| Pass | Step | Who | Basis |
|---|---|---|---|
| 1 Structure | Check the chapter's overall flow and its links back to earlier chapters | Agent | documented for the pass, suggested for who runs it |
| 2 Scaffolding | Check each section's scaffolding: a definition at the start, a worked example before practice, One New Element kept, review distributed | Agent | documented for the pass, suggested for who runs it |
| 3 Readability | Rewrite sentences over about 25 words, cut passive voice, replace vague quantifiers, and define jargon in place | Agent | documented for the pass, suggested for who runs it |
| 4 Visuals | Add a captioned diagram near every complex concept that still lacks one | Agent | documented for the pass, suggested for who runs it |
| 5 Terminology | Make each term consistent and defined once, at its first use, across the whole chapter | Agent | documented for the pass, suggested for who runs it |
| 6 Beginner validation | Read the whole chapter aloud as a non-expert, and confirm every prerequisite is reviewed, not assumed | Person | documented |

[The project notes](../glossary.md#reference-implementation) never say who runs passes 1 to 5. Only pass 6 is stated as explicitly human. Suggested: an agent drafts each pass's changes and a person judges fit, matching the pattern the rest of this guide uses.

## Parameters

**One New Element** means one new complexity or technique dimension added per section, such as a new sub-case or one more problem-and-solution pair. It does not mean literally one vocabulary term or one command. For a section on resolving a merge conflict, for instance, one section's new dimension might be what a conflict is. The next section's new dimension might be a tool that helps pick a version, and a later section's new dimension might be aborting or retrying the merge. Each section adds one dimension at a time, never several at once.

**70/20/10** is the mix of cumulative-review questions placed every third section: 70% from the current chapter, 20% from the immediately prior chapter, and 10% from the first chapter. It is never a time split or a word-count split. Reviewing the first chapter's material this often keeps a learner's earliest, most load-bearing ideas in view, even well into later chapters.

### Numbers that look alike

Three numbers in this sub-stage's project notes look similar. Keeping them apart matters for reading a chapter's own working notes correctly.

| Number | What it is | Defined |
|---|---|---|
| 70/20/10 | The cumulative-review question mix above | This page |
| 70/30, then 50/50, then 20/80 | A worked-example-to-independent-practice ratio that shifts across a chapter's own progression | This page |
| 60/30/10 | A chapter summary's own content mix | [S2.5](closing-templates.md#chapter-summary) |

The worked-example ratio moves from mostly worked examples early in a chapter toward mostly independent practice later, fading the scaffolding across a chapter the same way [S2.1](structural-drafting.md)'s I Do, We Do, You Do pattern fades it within one worked example.

### Readability targets

This page reuses the same Grade Level and Reading Ease meanings [S2.2](condensation.md) already defines, and does not redefine either scale here. S2.2's own delta bands describe a change from the original text. This page's targets are different in kind: an absolute band for the finished chapter, not a change from a starting point. The reference implementation's parameters set that band at Grade Level about 9 to 11, and the same Reading Ease band S2.2 already gives, about 60 to 70.

One project script checks a Grade-Level number against a Reading-Ease-shaped band and prints the result as one number, as if the two scales were the same thing. This is a real, confirmed defect in that script's own logic, not a difference of opinion. This guide's own script, `readability_report.py` below, keeps the two scales separate and labels each one, so a reader is never handed an ambiguous number.

### A defective draft, in kind

Without naming any real chapter, a defective draft can bundle three or four new ideas into one section, bury a definition mid-paragraph, and run at a high share of passive voice. It can also carry far fewer worked examples than the chapter needs, have only one diagram for the whole chapter, and never link back to an earlier chapter. The six passes above exist to catch failures of exactly this kind, one pass at a time. That variety is also why the passes stay separate, rather than folding into one general readability review.

## Artifacts and formats

- Revised chapter: the same Markdown skeleton [S2.1](structural-drafting.md) established, now polished for readability, reassembled from every section's pass-5 output into one file.
- Read-aloud note: a short, free-text note from the outside reader, recording who read the chapter, what was read, what it confirmed, and any prerequisite that needed a review link added.

## Prompts

[P-S2-03 Six-pass revision for one chapter section](../prompts/s2/p-s2-03.md) revises one section at a time, one call per pass, for passes 1 to 5; pass 6 has no prompt, since it is a person reading aloud. It takes the section text and the prior pass's output as input, fences both as data rather than instructions, and reports a revised section plus a one-line note on what that pass changed. The prompt is written for this guide and not run against any model in this build.

## Scripts

[X-S2-03 Readability report](../scripts/s2/x-s2-03.md) prints a file's Grade Level and Reading Ease scores against target bands. `in-band` and `out-of-band` never change its exit code, and this script never passes or fails anything by itself: it exits 0 whenever it can compute both scores, and 2 only for a usage or input error. Run it from the repository root:

```bash
python3 -B scripts/s2/readability_report.py scripts/sample_data/git_basics_stage2/readability/before.md
```

On a draft passage about resolving a merge conflict, written before this sub-stage's polish, both scores fall outside the targets:

```text
grade-level 21.50 (target 9-11) out-of-band
reading-ease 25.49 (target 60-70, higher is easier) out-of-band
```

Run it again on the same passage after the readability polish:

```bash
python3 -B scripts/s2/readability_report.py scripts/sample_data/git_basics_stage2/readability/after.md
```

```text
grade-level 9.35 (target 9-11) in-band
reading-ease 67.22 (target 60-70, higher is easier) in-band
```

The sentences got shorter, most passive constructions became active, and the "ours" and "theirs" markers got defined in place; both scores moved into their target bands. `--grade-low`, `--grade-high`, `--re-low` and `--re-high` change the target bands; their defaults already match the targets given above, so most runs need no flag at all. This page has no break-it-on-purpose step: with no pass or fail state to break, there is nothing a bad edit would change about the script's own behavior. That is also why the exit code stays 0 for both runs above, even though the first run is out of band on both scores. See [Reading exit codes](index.md#reading-exit-codes) on the Stage 2 index for what an exit code means in general; this script's own exit code never reflects `in-band` or `out-of-band`, for the reason just given.

The script writes no file. If you want a record of a run, copy its two printed lines into your own notes; the printed report is the whole of what the script produces.

## Definition of done

- Every section adds only One New Element, and shows a worked example before independent practice.
- Cumulative-review questions appear every third section, mixed 70/20/10.
- Sentences mostly run under about 25 words, most verbs are active, and jargon is defined where it first appears.
- Every complex concept has a nearby captioned diagram.
- Every term is used consistently, defined once, at its first use.
- An outside, non-expert reader has read the chapter aloud and confirmed every prerequisite is reviewed, not assumed.

## Common failures

- A chapter passes the readability report while one section still overloads the reader with new ideas. The script counts sentences and syllables; a person's judgment tests whether the section actually teaches.
- Mixing up the Grade Level and Reading Ease scales when reading a number back from a script or a note, the same mistake the defective project script above makes in its own logic.
- Skipping the beginner-validation pass because the first five passes already ran and the chapter reads fine to the person who wrote it.
- Confusing 70/20/10, the worked-example-to-practice ratio, and 60/30/10 when reading the project's own notes, since all three are written as three numbers that sum to 100.
- Running the six passes out of order, so a later pass's fix, such as adding a diagram in pass 4, gets undone by an earlier pass's edit repeated by mistake, such as re-splitting a sentence pass 3 already fixed.

## Adapting to your platform

- `llm`: drafts the readability-polish changes and each of the first five revision passes, one pass per call.
- `structured-output`: keeps a revised section and its pass note as two separate, clearly labelled parts of one reply, so the note never gets folded into the revised text by mistake.
- `shell`: runs the readability report; without it, count sentence length, passive constructions and defined terms by hand, using the same rules the script applies.
- `human-approval`: a person reads the chapter aloud for pass 6, and approves the revised chapter before it moves on to closing templates.

## Where humans decide

- The beginner-validation read-aloud itself: no script substitutes for a person reading the chapter as a newcomer would.
- Approval of the chapter after the sixth pass, before it moves on to [S2.5](closing-templates.md).

Next: [S2.5 Closing templates and the prerequisite check](closing-templates.md).
