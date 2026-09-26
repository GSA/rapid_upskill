---
title: "Delivery: slides and infographics"
parent: "Delivery"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-26"
stage: "DL"
prompts: ["P-DL-01"]
scripts: ["X-DL-01"]
---

# Delivery: slides and infographics

## Outcome

A finished chapter becomes a slide deck with a spoken presenter script,
sized to a stated time window and framed for a study-guide presentation
tied to a target certification. A set of finished slides, in turn,
becomes a small set of single-image infographics, one per cluster of
related slides. Both are described here as real tooling recorded in
[the project notes](../glossary.md#reference-implementation), not as
part of the five-stage framework this guide otherwise describes.

## Where it fits

Slides takes in a finished chapter draft, the kind [Stage
2](../stage-2/index.md) produces once a chapter is drafted and
reviewed. Infographics takes in a finished slide-notes file, the same
file Slides produces. Neither hands anything back into a stage; each is
a one-way, additive step that happens after a chapter's own content
work is otherwise done.

## Why this way

Slides and Infographics are kept as two separate, additive tools rather
than one combined pipeline. A reader may want a slide deck without ever
building infographics from it, or may want infographics built from a
slide deck someone else already produced. Keeping the hand-off between
them a plain Markdown file, rather than a private in-memory structure,
lets either tool run on its own. Every step below carries one of the
same three [basis labels](../stage-1/index.md#basis-labels) Stage 1's
index defines. Every step is `documented`: read directly from the
project notes' own workflow instructions or its running code, not
inferred or suggested by this guide. The one exception is the format
check this page adds, [X-DL-01](#scripts), which is this guide's own
`suggested` addition, since none of the source material's own tools
already check a slide-notes file's shape this way.

## Steps for slides

| Step | Who | Basis |
|---|---|---|
| Draft one chapter's own slide content and a matching presenter script, sized to a stated time window | Agent | documented |
| For a subset of chapters, find and attach a small number of supporting citations to each slide's key points | Agent | documented |
| Populate a template slide deck from the finished slide-notes file, and, optionally, upload it with automatic format conversion | Agent, with a companion script for the mechanics | documented |

The first step drafts slide bullets and a presenter script together
from a chapter's own finished text, reasoning in part from a target
certification's own published topic breakdown, without reproducing
that breakdown's own wording here. This drafting step runs in capped
batches, pausing after each one for a person's approval: a Batch pause,
in the terms
[Human roles, gates and batching](../human-roles-gates-and-batching.md)
already defines.

The second step is run for only a subset of chapters. An agent plans an
external search per a research-methodology guide, then attaches a
small, capped number of citations to each slide, favoring recent,
longer sources and well-known first authors. These are appended as reference
links inside that slide's own presenter-script section.

The third step examines a template slide-deck file's own layouts: a
title layout and a content-bullet layout, each with named placeholder
fields. For each slide, it copies the matching template layout and
fills in its title, bullets, and presenter script with references,
while preserving the template's own formatting. A companion script
automates this copying and filling mechanically. A person still decides
whether to also upload the finished deck, a step that converts it
automatically into a cloud-storage service's own native slide format.

## Steps for infographics

| Step | Who | Basis |
|---|---|---|
| Parse and filter a slide-deck file into a list of content slides | Script | documented |
| Cluster the remaining slides into infographic units by a reasoning model | Script | documented |
| Synthesize an image-generation prompt for each cluster | Script | documented |
| Generate one image per cluster, through a resilience layer | Script | documented |
| Write a manifest and a resumable checkpoint after each success | Script | documented |

Parsing recognizes a slide boundary and a presenter-notes block by a
small set of conventions. It strips any trailing references block from
both, and filters out a non-content slide, such as a table of contents
or a closing thank-you slide, by title. Clustering asks a reasoning
model to group the remaining slides into "infographic units," each
bounded by a configurable word budget and a configurable minimum and
maximum slide count. Each unit is returned as the slide indices it covers plus a
short rationale.

Prompt synthesis combines a cluster's own slide content with a chosen
visual style, drawn from a small, fixed style library of short generic
looks. The library runs from a clean, minimal default to more stylized options such as
an isometric or a sketch-style look. The synthesized prompt explicitly
instructs the model not to invent a statistic, a company name, or a
real person, and not to render an exam or assessment label onto the
image.

Generation runs through a resilience layer built from public,
well-known engineering patterns. These include a token-bucket rate limiter, retry
with exponential backoff and jitter on a transient error, an atomic
checkpoint write (write to a temporary file, then rename it into
place), and a sentinel file or an operating-system signal for a clean,
mid-run shutdown. A consecutive-failure counter can auto-abort the
whole run past a configurable threshold. A bounded test mode runs
clustering in full but generates only the first two clusters' images,
so a style choice and a clustering pass can be checked cheaply before a
full, costlier run begins.

## The slide-notes input contract

Both tools read the same Markdown shape for a chapter's own slide
notes, given here in full:

```markdown
# Chapter <id>: <Title>

## Slide 1: <Title>
- <bullet 1>
- <bullet 2>
- <bullet 3>
- <bullet 4>
(4 to 7 flat "- " bullets total; no sub-bullets)

**Presenter Script:**
<150 to 250 words of natural, standalone-readable narration for this slide>

References:
- <optional reference line>
- <optional reference line>

## Slide 2: <Title>
...
```

One Markdown file holds one chapter's own slide notes. Its structure is
safe, generic Markdown with no certification name, product name, or
credential inside the shape itself. Only what an author writes inside a
bullet or a script can carry any sensitivity of its own. Despite the
project notes calling this "the input contract for both slide tools,"
the two tools do not in fact share one parser. The slide-deck
population step reads a strict form of this shape (an exact chapter
heading, an exact `**Presenter Script:**` marker, an exact `References:`
heading), while the infographics parser is deliberately looser, also
accepting a `---`-separated slide boundary and more than one way of
marking a presenter-notes block. A file written to satisfy one tool is
not guaranteed to parse identically under the other.

## What still works, and what does not

Three findings about this tooling's own current state are worth stating
plainly, rather than presenting any of it as ready to reuse untouched:

- The slide-deck population script's own hardcoded input path has
  moved. The project notes record that the actual slide-notes files
  have since moved into a differently named folder from the one the
  script still points at. Run as it stands, the script will not find
  its own input, template, or credential files; the path needs
  hand-editing before reuse.
- A fixed-wrapper infographics prompt file exists in the project notes,
  reading as a coherent, complete set of image-generation prompts. Its
  own block structure does not match the shape the current script's own
  prompt-writer function actually produces, so which version of the
  tooling actually produced this file is unconfirmed.
- A separate written implementation guide for the infographics
  generator diverges from the running code in several concrete ways. An
  opt-in flag the guide describes that the code no longer has, several
  real flags the code accepts that the guide never mentions, and a
  different form for naming the underlying model in each. Read the
  guide as a design sketch, not as current documentation of the script.

## Worked illustration

This guide's own sample slide-notes file, for a placeholder chapter of
the running example, follows the schema above:

```markdown
# Chapter 1: Git Basics for New Team Members

## Slide 1: What Version Control Solves
- A shared history records who changed which file, and when, across the whole project.
- Version control lets a team recover an earlier state instead of losing work to an overwritten file.
- Every change is tracked as one discrete, reviewable step, never a silent overwrite.
- A new team member can read that history to see how the project reached its current state.
- The history is shared: every contributor works from the same sequence of recorded changes.

**Presenter Script:**
Before version control, many teams tracked a project's history by hand...
[168 more words]

## Slide 2: Recording Your First Change
...
```

A second, deliberately broken copy of the same file keeps every other
line the same. It drops one bullet from Slide 1 (down to three) and
cuts Slide 2's own presenter script down to a few sentences (well under
150 words), so the format check below has two real findings to report
rather than a hypothetical one.

## Scripts

[X-DL-01 Slide notes check](../scripts/dl/x-dl-01.md) reads a
slide-notes Markdown file and checks it against the schema above: the
chapter heading is present; every slide has 4 to 7 flat bullets; every
`**Presenter Script:**` block is present, exactly marked, and 150 to
250 words long; and any `References:` block is a `- ` bulleted list
starting on the very next line. It never checks whether a bullet or a
script is accurate; a person still reviews that before a deck is
populated from the file. Run it from the repository root:

```bash
python3 -B scripts/dl/slide_notes_check.py \
    scripts/sample_data/git_basics_batch8/slide_notes/Ch1_slideNotes_v20260115.md
```

```text
slides=2 errors=0
```

Every slide passes: two slides, no findings. Running the same command
against the deliberately broken copy shows what a real gap looks like:

```bash
python3 -B scripts/dl/slide_notes_check.py \
    scripts/sample_data/git_basics_batch8/slide_notes/Ch1_slideNotes_v20260115_broken.md
```

```text
bullet-count: Slide 1 has 3 bullets, needs 4 to 7
presenter-script-words: Slide 2 presenter script has 61 words, needs 150 to 250
slides=2 errors=2
```

The exit code is 1 whenever a finding is printed, 0 when the file is
clean, and 2 for a usage or input error, such as a missing file; see
[Reading exit codes](../stage-1/index.md#reading-exit-codes) on the
Stage 1 index for what an exit code means generally.

## Prompts

[P-DL-01 Draft slide content and a presenter script](../prompts/dl/p-dl-01.md)
drafts one chapter's own slide bullets and a matching presenter script
from that chapter's finished text, sized to a stated time budget and
following the schema above. It is written for this guide and has not
been run against any model in this build; treat it as a starting point
and adapt it. The chapter text it reads is data, never instructions,
even where a sentence inside it is phrased as one.

## Artifacts and formats

- A slide-notes file, one per chapter, in the Markdown shape given
  above; this guide's own new artifact from the format check.
- A slide-deck file, one per chapter (described, not produced by this
  guide's own tooling): built from a template's own layouts, with an
  optional, automatically converted copy in a cloud-storage service's
  own native slide format.
- An infographics manifest and a resumable checkpoint file (described,
  not produced by this guide's own tooling). The manifest records, per
  cluster, its status, its slide indices, the model used, the prompt
  text, and a timestamp; the checkpoint is what lets a killed or
  interrupted run resume where it left off.

## Definition of done

- Every slide's bullet count and presenter-script word count pass
  [X-DL-01](#scripts) before a slide-notes file is treated as ready for
  slide-deck population.
- A person has read every drafted presenter script at least once, since
  self-review is the only check this deliverable's own steps document.
- Every citation attached to a slide traces to a real, checkable
  source, never invented to fill a gap.
- An infographics run's manifest shows every cluster reaching a final
  status before the output set is treated as complete.

## Common failures

- A hardcoded input path that has moved, so the slide-deck population
  script fails to find its own input, template, or credential files
  until the path is hand-edited.
- A prompt file whose own structure does not match the tool that
  supposedly produced it, leaving which version actually produced it
  unconfirmed.
- A written implementation guide that has drifted from its own running
  code, read as current documentation when it is closer to an earlier
  design sketch.
- Silent clustering degradation. Any clustering failure falls back to
  one infographic per slide for the affected slides, with no hard
  error, so a caller watching only for a crash can miss a far larger
  and more fragmented output set than intended.

## Adapting to your platform

- `llm`: drafts slide content and a presenter script, from
  [P-DL-01](../prompts/dl/p-dl-01.md).
- `file-read`: reads a chapter's own finished text before drafting, and
  a slide-notes file before checking or populating a deck from it.
- `shell`: runs [X-DL-01](#scripts); without it, count each slide's own
  bullets and its presenter script's words by hand against the schema
  above.
- `human-approval`: covers approving a batch of drafted decks, deciding
  whether to run the citation-finding step or the cloud-storage upload
  for a given chapter, and approving a move from a bounded test run to
  a full infographics-generation run.

## Where humans decide

- Reviewing a drafted slide deck and its presenter scripts before use.
  Self-review by the same drafting agent is the only check this
  deliverable's own steps document; no separate verification layer
  exists for it.
- Whether to run the optional citation-finding step, and whether to
  enable the optional cloud-storage upload, for a given chapter.
- Approving a move from a bounded test run to a full, more costly
  infographics-generation run.

Next: [Delivery: publishing](publishing.md).
