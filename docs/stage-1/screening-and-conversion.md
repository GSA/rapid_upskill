---
title: "S1.4b Screening and conversion"
parent: "Stage 1 Knowledge acquisition"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-22"
stage: "S1"
sub_stage: "S1.4b"
prompts: ["P-S1-05"]
scripts: ["X-S1-04"]
---

# S1.4b Screening and conversion

## Outcome

At the end of this sub-stage, every admitted source is a Markdown file whose
conversion has been checked against a second copy of the original. Blocked
and failed documents are listed for the person who approves after
[S1.4c](injection-screening.md).

## Where it fits

This sub-stage takes in the deduplicated candidates (see
[S1.4a](search-planning-and-execution.md#outcome) for what a candidate is
and is not) from [S1.4a](search-planning-and-execution.md). It hands on
converted, checked sources, plus the blocked and failed lists, to S1.4c
for injection screening.

## Why this way

A source is worth reading only after it clears a content grade and its
conversion is checked against the original, so a conversion error is caught
before anyone reads the converted copy instead of the source itself. Most
steps below are documented in
[the project notes](../glossary.md#reference-implementation); the
conversion check's own thresholds are suggested by this guide, because the
project notes describe the checks without giving one script for them.

A **hard** check stops a source from moving on until it is fixed or the
source is marked failed. A **soft** check does not stop anything by
itself; it only asks a person to look before the source moves on.

Text you send to a model service leaves your machine. Read that service's
terms before you send it any candidate summary or source text.

## Steps

| Step | Who | Basis |
|---|---|---|
| Run a metadata check on each candidate: recency, a named venue or explicit **preprint** status (a paper posted before peer review), page count when it is already known, and source type (article, standard, vendor documentation, blog, other) | Script or agent | documented (thresholds are parameters you set; no script in this guide performs this check, so run it by eye or write your own, for example flagging anything more than 3 years old, under 4 pages, or with no named venue or preprint status) |
| Grade each candidate Green, Yellow or Red with a quoted metadata line as evidence, using the source-screening prompt | [Subagent](../glossary.md#subagent) | documented |
| Download each admitted source and record a fingerprint, a **hash** (a short, exact digest of the file's bytes; the same bytes always give the same hash) | Script or person | documented |
| Download a blocked document by hand when a script cannot reach it; never create an account and never copy paywalled material | Person | documented |
| Convert the document to Markdown with a converter of your choice | Script | documented |
| Get a plain-text copy of the same document by a second route: the visible text of an HTML page, or a PDF tool's own plain-text output | Script | suggested |
| Run the conversion check on the plain-text copy and the converted Markdown | Script | suggested |
| Re-convert once with different settings if a hard check fails; otherwise mark the source failed | Person or script | documented |
| Hand the admitted, converted sources, the blocked list and the failed list on to injection screening | Script or person | documented |

The grading rubric, restated in general terms: Green means the candidate is
on target, with a stated method and a number; Yellow means it is relevant
but at the wrong level, and should be rerouted; Red means it is off target
or out of date. Approval of the sources this sub-stage admits happens after
S1.4c, not here.

The metadata check drops any tiering of sources by country or by
organization; only recency, venue or preprint status, page count and source
type feed the grade. A page-count threshold can only be checked once the
document exists as a file, so when a candidate's metadata does not already
give a page count, this part of the check runs after conversion instead of
before it (an inference from how the checks are described).

### Conversion check parameters

| Check | Threshold | Kind |
|---|---|---|
| ratio | 0.85 to 1.15, converted words divided by original words; set with `--ratio-low` and `--ratio-high` | hard |
| garble | more than 1 replacement character in 100 characters | hard |
| character-mix | ASCII letters and digits under 0.45 of non-space characters; skipped with `--allow-non-latin` | hard |
| repeats | the same line of at least 4 words, 3 or more times | soft |
| words-per-page | fewer than 50 or more than 1,200 words per page; checked only when you pass `--pages` | soft |

The project notes give three different word-ratio bands in three places:
0.95 to 1.05, 0.85 to 1.35, and 0.85 to 1.15. This guide's script defaults
to the third of these and lets you widen or narrow it with `--ratio-low`
and `--ratio-high`. Calibrate the band on your own converter and material;
these are starting values chosen for this guide, not measured limits. The
words-per-page check is this guide's own addition: the project notes name a
check like it, but no script among them carries one out.

## Artifacts and formats

- An inventory row per candidate, simplified to: id, title, source type, how
  and when it was retrieved, its hash, where its files live, conversion
  status, screening status, and one overall status.
- A short log per candidate: what was checked, when, and the result.
- The grading output, one object per candidate: `title`, `grade` (`green`,
  `yellow` or `red`), `evidence` (a line quoted from the candidate record),
  `reason`.
- The **manifest** (the line-by-line record of every query the search step
  ran, from S1.4a) gains no new lines here; this sub-stage reads it, and
  adds to the inventory instead.
- Each admitted source as a Markdown file, plus its plain-text second copy,
  kept side by side so the conversion check can compare them again later.

## Prompts

[Source screening](../prompts/s1/p-s1-05.md) (P-S1-05) grades one batch of
candidates against one objective. It is written for this guide and has not
been run against any model in this build; treat it as a starting point and
adapt it.

## Scripts

[Conversion quality check](../scripts/s1/x-s1-04.md) (X-S1-04) compares a
converted Markdown file with a plain-text copy of the same document and
prints one line per check that applies. A passing run is a sign the
conversion did not lose, truncate or garble the text; it does not check that
the meaning of a passage survived the conversion, and a passing run does not
prove the conversion is complete.

Run it from the repository root on the sample pair, which is missing its
last section on purpose:

```bash
python3 -B scripts/s1/check_conversion.py \
    scripts/sample_data/git_basics_stage1/conversion/SRC-004.original.txt \
    scripts/sample_data/git_basics_stage1/conversion/SRC-004.converted.md
```

```text
pass empty the converted file has 325 words
hard ratio 0.70 (325 of 462 words), band 0.85-1.15
pass garble 0 replacement character(s) in 2001 characters (0.00%)
pass character-mix 0.94 of non-space characters are ASCII letters or digits
pass repeats no line of at least 4 words repeats 3+ times
```

The `ratio` line is `hard`, so the exit code is 1: the converted file has
far fewer words than the original, which is what a missing section looks
like. The other checks pass, because the text that did convert is intact.

Break it on purpose: copy the converted file, then pad it with a long run of
punctuation characters, so its word count catches up with the original
while the added text is not made of letters or digits.

```bash
cp scripts/sample_data/git_basics_stage1/conversion/SRC-004.converted.md SRC-004.broken.md
yes '#$%^&*()_+' | head -n 190 | tr '\n' ' ' >> SRC-004.broken.md
python3 -B scripts/s1/check_conversion.py \
    scripts/sample_data/git_basics_stage1/conversion/SRC-004.original.txt SRC-004.broken.md
rm SRC-004.broken.md
```

```text
pass empty the converted file has 515 words
pass ratio 1.11 (515 of 462 words), band 0.85-1.15
pass garble 0 replacement character(s) in 4091 characters (0.00%)
hard character-mix 0.44 of non-space characters are ASCII letters or digits
pass repeats no line of at least 4 words repeats 3+ times
```

Now `ratio` passes, because the word count lines up, but `character-mix` is
`hard`: most of the padding is punctuation, not ordinary text. This is the
common failure below in miniature: word count alone can look right while
the content is glyph noise, and the character-mix check is what catches it.
The exit code is still 1.

## Definition of done

- Every admitted candidate has a metadata check result and a grade with its
  quoted evidence line.
- Every admitted source exists as a converted Markdown file and a
  plain-text second copy of the same document.
- The conversion check has run on every converted source, and no source
  carries an unresolved hard failure: it was either fixed by a second
  conversion attempt, or it is marked failed.
- The blocked-document list and the failed-source list are ready for the
  person who approves after S1.4c.

## Common failures

- A half-written download saved as if it were the whole document. The
  `ratio` check catches a short result; a download that stopped partway
  through can still pass if the missing part was mostly boilerplate, so
  also check the file's size against what you expected.
- A landing page or a login page saved in place of the document. The
  `character-mix` and `repeats` checks often catch this, because such pages
  repeat navigation text and carry little of the source's own wording.
- Glyph substitution, where a converter swaps in look-alike or symbol
  characters instead of ordinary letters. The word count can still land
  inside the ratio band, as the break-it-on-purpose run above shows; the
  `character-mix` check is what catches it.
- An empty or near-empty page from a conversion that silently failed. The
  `empty` check catches a converted file with no words at all.

## Adapting to your platform

This sub-stage needs `llm` and `structured-output` for grading, `file-read`
and `file-write` for the converter and the checks, `shell` to run
`check_conversion.py`, `web-fetch` for scripted downloads, and
`human-approval` for blocked documents and failed sources. The project
notes also use subagents to grade candidates in waves; without that
capability, grade one candidate at a time in a single chat window. Without
`shell`, run the check on another machine that has Python 3.10 or newer and
paste its output back in. Without scripted `web-fetch`, download every
source by hand, which is required anyway for blocked documents.

## Where humans decide

- Whether a blocked document is worth downloading by hand, and whether it
  is available lawfully.
- Whether a source that fails a hard check should be re-converted, marked
  failed, or dropped.
- The approval after S1.4c, which covers the sources this sub-stage admits
  together with the sources S1.4c flags.

Next: [S1.4c Injection screening](injection-screening.md).
