---
title: "S1.5b Distillate and quote bank"
parent: "Stage 1 Knowledge acquisition"
nav_order: 7
status: "draft"
last_reviewed: "2026-09-22"
stage: "S1"
sub_stage: "S1.5b"
prompts: ["P-S1-07"]
scripts: ["X-S1-07"]
---

# S1.5b Distillate and quote bank

## Outcome

At the end of this sub-stage, every source has a **distillate**: a
structured write-up in nine sections, ending with a quote bank that the
quote check script can check against the source. This sub-stage ends
when the quote check passes and a person approves the batch.

## Where it fits

This sub-stage takes in each source's concept list from
[S1.5a](concept-extraction.md). It hands on a distillate with a checked
quote bank to later, planned sub-stages.

## Why this way

A quote bank that a script can check against the source is what lets a
later stage trust a claim without re-reading the source itself every
time. A distillate that skips this step still reads well, but no one
downstream can tell which of its sentences are the source's own words
and which are the agent's summary of them. This page uses the
[basis labels](index.md#basis-labels) defined on the Stage 1 index.
Writing the nine sections and running the quote check are documented in
[the project notes](../glossary.md#reference-implementation), which also
document splitting a quote at a bracketed insertion and failing a
fragment under three words. The rest of this guide's version of the
check, and its exact normalization rules, are suggested, because the
project notes describe the check without giving one script that matches
this guide's simpler template. The Findings and Normative statements
fields below, and the quote bank's line format, are this guide's
simplification of a fuller set the project notes describe (which also
names the source's population for a finding, a status for a normative
statement, and a hash of the source file for each quote).

## Steps

| Step | Who | Basis |
|---|---|---|
| Build the brief, as in [S1.5a](concept-extraction.md#steps) | Script or person | documented |
| Write the nine sections, using the [distillate prompt](#prompts) | Agent | documented |
| Write each locator as a page number, or a heading path and a paragraph number; never estimate one | Agent | documented |
| Keep each quote at most 40 words | Agent | documented |
| Run the quote check | Script | documented |
| Spot-check two quotes per batch by hand; a fresh subagent, or a person if there is no coordinating session, rechecks a fifth of the quotes | Coordinating session, subagent or person | documented |
| Remove any quote that fails the recheck and mark it unchecked | Person | documented |
| Approve the batch | Person | documented |

Two quotes per batch by hand, and a fifth of the quotes by a fresh
recheck, are the reference implementation's parameters, not a rule every
project must reuse. Calibrate the share on your own batch size and on
how much a wrong quote would cost you downstream.

The nine sections, in order, are:

- Metadata.
- Problem and context.
- Scope.
- Findings: one bullet per finding, with a number, a unit, a
  denominator, a date, a short label and a quote.
- Normative statements: a rule the source states, and who it binds.
- Critical assessment: a conflict of interest, and whether the source is
  a primary account or repeats another source.
- Relation to **the seed** (a starting list of claims you already hold
  and want the sources to confirm, extend or contradict): say whether
  the source corroborates, extends, corrects or contradicts each seed
  claim it touches.
- Leads: one or two things worth checking later, logged here and not
  fetched now.
- Quote bank.

The 40-word limit on a quote is a choice made for this guide, not a
legal safe harbour for how much of a source you may copy; see
[Platform requirements](../platform-requirements.md#dependencies-that-are-not-capabilities)
for rights to sources.

## What the quote check does and does not do

The quote check shows only that a quote's words are present in the
source. It never checks that the quote is true, that it supports the
claim it is attached to, or that its locator is right. In this guide's
assessment, an invented or paraphrased quote is the failure most worth
watching for, because it is the one presence-checking alone is built to
catch.

Normalization forgives typography only. Curly quotes become straight
quotes, dash variants become a hyphen, a hyphen at a line end is joined
to the next word, and whitespace runs collapse to one space. The source
also has its front matter, backticks and Markdown emphasis marks
removed. The comparison is case-sensitive unless you pass
`--ignore-case`.

A quote is split into fragments at each bracketed insertion, such as
`[HEAD]`. An editorial note added this way is not itself checked
against the source, but every other fragment must still occur there.
A fragment under 3 words fails as too short, because a fragment that
short is too easy to find by accident.

Case sensitivity is the default, not an oversight. A source that always
writes a term in a specific way, paired with a quote that changes its
case, is one small sign the quote was retyped from memory rather than
copied. Reach for `--ignore-case` only when you already know the source
itself is inconsistent about case.

## Artifacts and formats

A distillate is a Markdown file with front matter (`source_id`, `date`)
and the nine `##` sections above, in that order. Its quote bank lines
each look like `- "quote text" | locator`. Every quote and its locator
sit on one line.

## Prompts

[Source distillate](../prompts/s1/p-s1-07.md) (P-S1-07) drafts all nine
sections and the quote bank from the source text, the objective it
supports and the seed. It is written for this guide and has not been run
against any model in this build; treat it as a starting point and adapt
it.

## Scripts

[Quote bank check](../scripts/s1/x-s1-07.md) (X-S1-07) reads the section
whose heading contains "Quote bank", checks each quote's length and
fragments against the source, and prints one line per quote.

Run it from the repository root on the sample distillate, which carries
one quote written as a paraphrase on purpose:

```bash
python3 -B scripts/s1/quote_check.py \
    scripts/sample_data/git_basics/sources/SRC-002.md \
    scripts/sample_data/git_basics_stage1/extraction/SRC-002.distillate.md
```

```text
pass quote-1 10 words, present in the source
pass quote-2 17 words, present in the source
pass quote-3 17 words, present in the source
pass quote-4 10 words, present in the source
pass quote-5 10 words, present in the source
fail quote-6 fragment "Git merges the two branches' changes together and writes one new commit that has two parent commits." not found in the source
quotes=6 pass=5 fail=1
```

Five quotes pass. The sixth fails because it restates the source's own
sentence about a merge commit's two parents in different words instead
of quoting it. The check does not know the underlying claim is right; it
only knows that this exact wording is not in the source. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 1 index
for what the exit code means.

Fix it by editing a copy of the distillate to quote the source's own
sentence instead of paraphrasing it, then run the check again:

```text
pass quote-1 10 words, present in the source
pass quote-2 17 words, present in the source
pass quote-3 17 words, present in the source
pass quote-4 10 words, present in the source
pass quote-5 10 words, present in the source
pass quote-6 15 words, present in the source
quotes=6 pass=6 fail=0
```

`--heading` points the check at a differently worded heading; `--ignore-case`
drops the default case-sensitive comparison. A passing run means every
quote's words are present in the source; it is not a check on whether
the distillate's own claims are correct.

## Definition of done

- Every source has a distillate with all nine sections filled in.
- Every locator is a page number, or a heading path and a paragraph
  number, never estimated.
- Every quote is at most 40 words.
- The quote check reports no failures.
- The coordinating session's or a person's spot-check, and the fresh
  subagent's or a person's recheck, have both run on the batch.
- A person has approved the batch.

## Common failures

- An invented page number for a source that carries no page numbers at
  all; use a heading path and a paragraph number instead, and never
  estimate a locator.
- A converted source's leftover glyph codes quoted as if they were text;
  quoting through a glyph code quotes nothing the check can find.
- A quote bank line that drifts from the `- "quote" | locator` format,
  so the check never sees it as a quote at all.
- An empty section, because a source has nothing to say on one of the
  nine headings; say so directly instead of leaving the heading blank.
- A long passage copied at length from a source instead of a short
  quote; keep quotes short even where the source allows more.

## Adapting to your platform

This sub-stage needs `llm` for drafting the nine sections, `file-read`
to load the source and the brief, and `file-write` to save the
distillate. `shell` runs the quote check; without it, check each quote
by searching for its words in the source file with a text editor.
`human-approval` covers the spot-check, the recheck and the batch
approval; without `subagents`, have a second person do the recheck
instead of a fresh subagent.

## Where humans decide

- Which quotes to trust after the spot-check and the recheck.
- The batch approval; see
  [Human roles, gates and batching](../human-roles-gates-and-batching.md)
  for batch size and worker caps.

Next: [Stage 1 Knowledge acquisition](index.md); the sub-stages S1.6 to
S1.8 are planned.
