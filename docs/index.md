---
title: "Home"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-21"
---

# Rapid Upskilling Pipeline

This guide teaches a method for building an [upskilling program](glossary.md#upskilling-program). It comes with sample prompts and scripts. The method is a framework of five [stages](glossary.md#stage).

Its premise is that AI does the volume work while people keep the judgment calls the framework assigns them, staying [in the loop](glossary.md#human-in-the-loop) wherever a decision matters. For example, an [agent](glossary.md#agent) reads many source documents and drafts a chapter. A person decides which sources to admit and whether the draft is right. [Human roles, gates and batching](human-roles-gates-and-batching.md) covers who decides what.

The **[reference implementation](glossary.md#reference-implementation)** is the original program and tooling this guide was written from. It was a certification-preparation program for a new technical topic, built with agent sessions and human review.

## What you end up with

The framework is designed to produce five things.

- A [knowledge base](glossary.md#knowledge-base) built from your sources.
- Chapters written from a fixed template.
- Review reports and an [audit trail](glossary.md#audit-trail): records of the checks made on the AI-drafted content.
- Coaching rules for an AI tutor, with a catalog of [misconceptions](glossary.md#misconception) (common wrong beliefs) for each chapter.
- A [bank of test questions](glossary.md#item-bank) tagged to the [blueprint](glossary.md#blueprint), the program's own plan.

The five stages are knowledge acquisition, content development, review and verification, AI-tutor coaching, and assessment development. The [Pipeline overview](pipeline-overview.md) shows how they connect.

## Where to start

Start with the [Pipeline overview](pipeline-overview.md). It shows all five stages on one page. Then read [How to use this guide](how-to-use-this-guide.md). It says what you need and how each page is laid out. Every stage will use one small, fictional program, the [running example](running-example.md). Stage 1 through Stage 3 and Stage 5 are published with sample prompts and scripts, and Stage 4 with sample prompts; all five stages are now published. The [certification-alignment](certification-alignment.md) workstream and the [Delivery](delivery/index.md) tooling are also now described.

## Should you try this?

Before you start, answer the six questions in the [Readiness checklist (not a validated instrument)](platform-requirements.md#readiness-checklist-not-a-validated-instrument). They help you judge whether your platform, your sources and your experts are ready.

## What this guide is

This guide is a method, not a product. It is written to be platform-neutral, so you can adapt it to your [agentic platform](glossary.md#agentic-platform). It describes a design and how the reference implementation was run, as of September 2026. It makes no claims about results.

The text, prompts, and scripts are released under CC0 1.0, a public domain dedication. To learn what that means, or to help, see [Contributing](contributing/index.md).

Next: [Pipeline overview](pipeline-overview.md).
