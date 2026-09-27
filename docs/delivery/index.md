---
title: "Delivery"
nav_order: 65
status: "draft"
last_reviewed: "2026-09-26"
stage: "DL"
---

# Delivery

## Outcome

A reader understands that Delivery is real tooling the reference implementation used to turn finished chapters into distributable artifacts. It is
described here because it exists in [the project notes](../glossary.md#reference-implementation), not because this guide asks a reader to adopt it as
part of the framework it otherwise teaches. By the end of the two pages this page links to, a reader knows what a finished chapter can become once its
own content work is otherwise done. It can become a slide deck with a spoken presenter script, a small set of single-image infographics, a distributable
book volume, or a submission-formatted paper manuscript.

## Where it fits

Delivery sits outside the five-[stage](../glossary.md#stage) framework and outside the [certification-alignment](../certification-alignment.md)
workstream. It takes in already-drafted, already-reviewed chapter content the five stages produce; it hands nothing back into any stage. Where
certification alignment rates a chapter's own content against an outside skill list, Delivery does not judge a chapter's content at all. It only takes
what is already finished and reshapes it into a form meant for a reader, a listener, or a submission venue, outside the chapter-production pipeline this
guide otherwise describes in full.

## Why this way

Every earlier stage, and the certification-alignment workstream, produces something meant to stay inside this guide's own framework: a knowledge base, a
chapter, a tutoring package, an item bank, a rating. Delivery is different. Its own outputs are meant to leave the framework entirely, as files a person
downloads, uploads, or submits somewhere else. Describing Delivery on its own pages, separate from the five stages, keeps that boundary visible. Nothing
downstream of a stage page ever depends on Delivery having run, and nothing on a Delivery page ever feeds back into a stage.

## Two functions covered here

- [Delivery: slides and infographics](slides-and-infographics.md) — turning a finished chapter into a slide deck with a spoken presenter script, sized to
  a stated time window. It also turns a finished slide deck into a small set of single-image infographics, one per cluster of related slides.
- [Delivery: publishing](publishing.md) — compiling reviewed chapters into distributable book volumes with hand-edited front and back matter, and turning
  the project's own strategy and method documents into a submission-formatted paper manuscript with its own bibliography.

Both pages describe real tooling: real workflow instructions, real scripts, and, in more than one case, real tooling that has since gone stale. Each page
states plainly, by name of the finding rather than by the real script's own name or file location, which of its own pieces of tooling still works as
documented and which does not.

## Two further functions, out of scope here

Two more Delivery functions exist in the project notes and are out of this guide's own scope, named here so a reader knows they exist without expecting a
page for either.

- **Generic program-delivery administration**: participant records, scheduling, and similar logistics with nothing specific to this guide's own method.
  Nothing about it is particular to an upskilling program built this way, so it adds nothing this guide would teach differently from any other program's
  own administration.
- **Continuing-education accreditation paperwork**, built against a real accrediting body's own published standards. This guide never names that body,
  and describing the paperwork itself would risk naming it indirectly, so the function is acknowledged here and described no further on any page in this
  guide.

## Artifacts

- A slide-notes file, one per chapter, in the schema [Delivery: slides and infographics](slides-and-infographics.md) gives in full.
- A slide-deck file, and, separately, an infographics manifest and a resumable checkpoint file (both described on that same page, neither produced by
  this guide's own tooling).
- A volume manifest, a marketing-copy file, and a structurally-checked paper manuscript with its bibliography (all described on
  [Delivery: publishing](publishing.md)).

## What is documented versus suggested

Every step on both Delivery pages traces directly to the project notes' own workflow instructions or its running code — documented, not inferred or
suggested by this guide. The one exception on each page is a format-checking script this guide adds where the source material never checked a file's own
shape this way: `slide_notes_check.py` on the slides page, and `volume_manifest_check.py` on the publishing page. Both scripts' own default values and
behaviors are this guide's own suggested addition, stated as such on their own pages. Several pieces of real tooling described on these two pages are
stale, broken, or unconfirmed as still working. Both pages say so plainly, naming: a hardcoded path that has moved; a prompt file whose own structure does not
match the tool that supposedly produces it; a written implementation guide that has drifted from its own code; and a real, confirmed bug in comparable
tooling elsewhere in this stage's own family of scripts, fixed in this guide's own version rather than repeated.

## First actions for a new team

Suggested:

- Decide which of the two Delivery functions covered here your own team actually needs. Neither depends on the other, and a team building only a slide
  deck, or only a compiled volume, can read one page and skip the other.
- Before reusing any real script this guide describes, confirm its own current state against the tooling-currency findings named on its own page. Do not
  assume a script still runs as its own source material once claimed.
- If your own platform's delivery needs resemble the two out-of-scope functions above, budget for building that tooling yourself; this guide describes
  neither.

Next: [Delivery: slides and infographics](slides-and-infographics.md).
