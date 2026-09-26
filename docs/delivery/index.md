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
described here because it exists in the project notes, not because this guide asks a reader to adopt it as part of the framework it otherwise teaches.

## Where it fits

Delivery sits outside the five-[stage](../glossary.md#stage) framework and outside the [certification-alignment](../certification-alignment.md)
workstream. It takes in already-drafted, already-reviewed chapter content the five stages produce; it hands nothing back into any stage. Two of its
functions are covered here:

- [Delivery: slides and infographics](slides-and-infographics.md) — turning a finished chapter into a slide deck with a spoken presenter script, and
  turning a finished slide deck into a small set of single-image infographics.
- [Delivery: publishing](publishing.md) — compiling reviewed chapters into distributable book volumes, and turning the project's own strategy and method
  documents into a submission-formatted paper manuscript.

Two further Delivery functions exist in [the project notes](../glossary.md#reference-implementation) and are out of this guide's own scope. The first is
generic program-delivery administration: participant records, scheduling, and similar logistics with nothing specific to this guide's own method. The
second is continuing-education accreditation paperwork, built against a real accrediting body's own published standards this guide never names. Neither
is described further on any page in this guide.

## What is documented versus suggested

Every step on both Delivery pages traces directly to the project notes' own workflow instructions or its running code — documented, not inferred or
suggested by this guide. The one exception on each page is a format-checking script this guide adds where the source material never checked a file's own
shape this way: `slide_notes_check.py` on the slides page, and `volume_manifest_check.py` on the publishing page. Both scripts' own default values and
behaviors are this guide's own suggested addition, stated as such on their own pages. Several pieces of real tooling described on these two pages are
stale, broken, or unconfirmed as still working. Both pages say so plainly, by name of the finding, never by the real script's own name or file location.

Next: [Delivery: slides and infographics](slides-and-infographics.md).
