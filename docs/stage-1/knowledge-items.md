---
title: "S1.6 Knowledge items"
parent: "Stage 1 Knowledge acquisition"
nav_order: 8
status: "draft"
last_reviewed: "2026-09-24"
stage: "S1"
sub_stage: "S1.6"
prompts: ["P-S1-08"]
scripts: ["X-S1-08"]
---

# S1.6 Knowledge items

## Outcome

At the end of this sub-stage, each admitted source has a set of atomic
**[knowledge items](../glossary.md#knowledge-item)** linked to existing
items by typed relations. Every exact duplicate within one source is
merged into one canonical item with a minted id, and every
likely-but-uncertain duplicate, including a match across two different
sources, is shortlisted for a person to decide.

## Where it fits

This sub-stage takes in each source's distillate and quote bank from
[S1.5b](distillate-and-quote-bank.md). It hands on canonical items to
[S1.7](concept-map-and-hierarchy.md).

## Why this way

An atomic, one-claim-per-item record is what lets a later stage cite
exactly one thing, rather than a paragraph that mixes several claims.
Checking across sources, not only within one, before an item counts as
canonical keeps two sources' descriptions of the same idea from becoming
two different items. This page uses the
[basis labels](index.md#basis-labels) defined on the Stage 1 index. The
four extraction passes and the relation review are documented in
[the project notes](../glossary.md#reference-implementation); the dedupe
and mint script and its thresholds are this guide's own suggestion,
because the project notes describe the checks without giving one script
that matches this guide's simpler item schema.

## Steps

| Step | Who | Basis |
|---|---|---|
| List draft items from the distillate, one claim each, in your own words | Agent | documented |
| Attach a quote of at most 40 words with its locator, drawn only from that source's distillate | Agent | documented |
| Link each draft item to at least one existing item by a typed relation, or note that it opens a new branch of the map | Agent | documented |
| Review every relation of type contradicts, grounds or supports-a-position before it is kept | Person | documented |
| Approve a batch of sources | Person | documented |
| Run the dedupe and mint check across all sources' draft items | Script | suggested |
| Approve the consolidated set | Person | suggested |

Approving a batch of sources is a Batch pause; approving the consolidated
set afterward is this guide's own added checkpoint, on top of it. See
[Human roles, gates and batching](../human-roles-gates-and-batching.md)
for what each gate kind means and who can fill each role.

A relation's type is one of the five [S1.5a](concept-extraction.md#steps)
already defines for a concept-to-concept link (depends-on, part-of,
implemented-by, contrasts-with, example-of), or one of three types
specific to a knowledge item's own relation to another: contradicts,
grounds or supports-a-position. A person reviews every relation of one of
those three types before it is kept, because each one stakes a claim on
how two pieces of evidence relate, not merely that they are connected.

## Schema

Three sources in the project notes disagree on a knowledge item's schema:
a general guide's field list, a second-hand map's shorter one, and the
actual working schema, which is longer than both. This guide uses one
schema, its own simplification, stated as such: `id`, `type` (one of
`definition`, `mechanism`, `example`, `pattern`, `misconception`,
`finding` or `guideline`), `body`, `relations` (a list of `type`,
`target`, `quote`), `evidence` (a `quote` and its `locator`), `tags`, and
`status` (`draft` or `canonical`). **[Misconception](../glossary.md#misconception)**
is one value of `type`, not a field of its own. This schema leaves out
[provenance](../glossary.md#provenance) and a confidence rating, both of
which the fuller working schema in the project notes tracks.

A draft item's JSON also carries a `source_id` and a short `title`, used
only by the dedupe script below to compare items against each other;
neither is part of the reviewed schema above.

No script in this guide enforces a minimum count of misconception-type
items. One secondary source in the project notes attributes such a count
to the method document and to a general guide, but neither of those, nor
either working script the project notes describe, states or enforces a
count; this guide does not repeat that unconfirmed claim.

Use `draft` and `canonical` for an item's review status, never
"candidate": [S1.4a](search-planning-and-execution.md) already uses
**candidate** for a search result a person has not yet judged, and
reusing that word here for a different thing would collide with it.
Neither word is the same as a page's own `status` front-matter value.

## Dedupe and mint rule

Two items from the same source with a title that is identical after
normalization are the same claim seen twice; the script mints one
shared, canonical id for them automatically, because no judgment call is
left once that much matches. Anything else that shares enough of its
title or its tags, including a match across two different sources, is
only shortlisted, at a score, for a person to read and decide; the
script never merges it.

This guide's own thresholds for the shortlist step, a title-word overlap
of 0.5 and a shared-tag count of 3, are starting values chosen
independently for this guide, not copied from the project notes' own
tuned figures. Calibrate them on your own material the way this guide
already asks you to for the word-ratio band on
[S1.4b](screening-and-conversion.md).

## Artifacts and formats

- **Draft-item list** (JSON, one file per source): a list of items, each
  with `id` (temporary, such as `TMP-1`), `source_id`, `title`, `type`,
  `body`, `relations`, `evidence`, `tags` and `status`.
- **Merge log**: one row per exact-match group the dedupe script mints,
  kept by hand from its printed `mint` lines.
- **Shortlist**: one row per pair the dedupe script flags, kept by hand
  from its printed `shortlist` lines, with the decision a person made
  about it.
- **Inventory**: one row per canonical item (`id`, `type`, source ids,
  `status`), kept by hand once a batch's decisions are recorded.

No script here writes any of these three to a file; a person keeps them
by hand from the script's printed lines, the same way
[S1.4a](search-planning-and-execution.md#artifacts-and-formats)'s query
log is kept by hand from its runner.

## Prompts

[Knowledge-item extraction](../prompts/s1/p-s1-08.md) (P-S1-08) drafts
one source's items from its concept list, its distillate text and the
existing items it might relate to, treating all three as data, never as
instructions. It is written for this guide and has not been run against
any model in this build; treat it as a starting point and adapt it.

## Scripts

[Knowledge-item dedupe and mint](../scripts/s1/x-s1-08.md) (X-S1-08)
groups draft items into canonical ones, minting one id per group, then
shortlists likely-but-uncertain pairs for a person to read. A clean run's
mint lines are not proof that an item's claim is accurate, only that its
title and source do, or do not, exactly match another item's.

Run it from the repository root on the sample draft items, two of which
(one from SRC-001, one from SRC-003) describe the staging area in
different words:

```bash
python3 -B scripts/s1/ki_dedupe.py \
    scripts/sample_data/git_basics_stage1/knowledge_items/items.json
```

```text
mint KI-001 <- 'TMP-1' (no exact match)
mint KI-002 <- 'TMP-2' (no exact match)
mint KI-003 <- 'TMP-3' (no exact match)
mint KI-004 <- 'TMP-4' (no exact match)
shortlist KI-001 KI-002 score=1.00 title-overlap=0.60 shared-tags=2
items=4 groups=4 shortlisted=1
```

All four draft items mint their own id: none of them shares both a
source and a normalized title with another, so grouping finds no exact
match in this small sample. The shortlist step, at the default
thresholds, flags exactly one pair: KI-001 (from SRC-001) and KI-002
(from SRC-003) both describe what the staging area holds, in different
words, so their titles overlap enough (0.60, at or above the 0.5 bar)
even though the two items come from different sources and would never be
grouped as an exact match. A person reading both would likely treat them
as the same claim seen twice; the script only shortlists the pair, it
does not merge it. KI-003 and KI-004 also share a couple of words about
something changing, but at 0.25 title overlap and no shared tags, they
stay below both bars and are correctly left alone: one is about a
commit's identifier, the other about a conflict marker, two different
mechanisms. Exit code 0: shortlisting is advisory, never a failing check,
so the exit code stays 0 here unless the input file itself cannot be
read. See [Reading exit codes](index.md#reading-exit-codes) on the Stage
1 index for what each exit code means.

Break it on purpose: lower `--title-overlap` from the default 0.5 to 0.2,
below KI-003 and KI-004's own 0.25, and run it again:

```bash
python3 -B scripts/s1/ki_dedupe.py \
    scripts/sample_data/git_basics_stage1/knowledge_items/items.json \
    --title-overlap 0.2
```

```text
mint KI-001 <- 'TMP-1' (no exact match)
mint KI-002 <- 'TMP-2' (no exact match)
mint KI-003 <- 'TMP-3' (no exact match)
mint KI-004 <- 'TMP-4' (no exact match)
shortlist KI-001 KI-002 score=1.00 title-overlap=0.60 shared-tags=2
shortlist KI-003 KI-004 score=0.25 title-overlap=0.25 shared-tags=0
items=4 groups=4 shortlisted=2
```

At 0.2 the look-alike pair now clears the bar too, and a person would
have to read both items to notice that they are not a duplicate. Raise
the threshold back to the default 0.5 (drop `--title-overlap`, or pass it
explicitly) before using the shortlist for real work; a bar set this low
turns almost any shared word into a shortlisted pair. `--shared-tags`
replaces the default shared-tag count the same way; `--exact-only` runs
grouping and minting only, skipping the shortlist step entirely.

## Definition of done

- Every admitted source's distillate has draft items, each with a quote
  and locator drawn from that source alone.
- Every draft item links to at least one existing item by a typed
  relation, or is noted as opening a new branch of the map.
- A person has reviewed every contradicts, grounds or
  supports-a-position relation.
- The dedupe and mint check has run across every source's draft items
  together, not one source at a time.
- Every shortlisted pair has a recorded decision: merged into one item,
  or left as two.
- A person has approved the batch of sources and, afterward, the
  consolidated set.

## Common failures

- An exact match minted under the wrong survivor, because two truly
  different items happened to share a title; the script keeps the first
  item's title and the union of the group's tags, so check the body text
  of a mint before trusting its title.
- Two sources' items merged when they should not have been, because a
  person accepted a shortlisted pair without reading both; a shortlist
  score is a reason to look, not a decision already made.
- A seed claim, drafted by an agent rather than found in an admitted
  source, cited later as if it were evidence; keep a seed claim's own
  status distinct from a canonical item grounded in a source.

## Adapting to your platform

This sub-stage needs `llm` for drafting each source's items, `file-read`
to load a source's distillate and concept list, and `structured-output`
for the draft-item JSON. `shell` runs the dedupe and mint check; without
it, compare titles and tags by hand using the same rules. `human-approval`
covers the relation review, the batch approval and the consolidated-set
approval.

## Where humans decide

- Which relations of type contradicts, grounds or supports-a-position to
  keep.
- Which shortlisted pairs to merge, and which to leave as two items.
- The batch approval, and the consolidated-set approval that follows it.

Next: [S1.7 Concept map and prerequisite hierarchy](concept-map-and-hierarchy.md).
