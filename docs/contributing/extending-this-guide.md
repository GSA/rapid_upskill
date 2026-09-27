---
title: "Extending this guide"
parent: "Contributing"
nav_order: 5
status: "draft"
last_reviewed: "2026-09-26"
prompts: []
scripts: []
---

# Extending this guide

The source material behind this guide has no dedicated guide of its own for generalizing this method to a new subject or platform. No sixth stage, no alternative assessment format, and no alternative delivery channel is proposed anywhere in it as a deliberate move. Most of what follows is therefore this guide's own `suggested` synthesis, clearly labeled throughout. It is built on two real, sourced findings named below, and on what [Platform requirements](../platform-requirements.md) and [The running example](../running-example.md) already publish.

## Outcome

By the end of this page, a reader knows what changes, and what does not, when this guide's own method is retargeted at a different subject-matter domain, a different running example, or a different [agentic platform](../glossary.md#agentic-platform).

## Where it fits

This is the fifth page under [Contributing](index.md), extending, not duplicating, the other four. [Authoring conventions](authoring-conventions.md), [Tooling](tooling.md), [Your first prompt](first-prompt.md) and [Release checklist](release-checklist.md) cover the mechanics of contributing to this site's own text, prompts and scripts. None of the four covers the mechanics of retargeting the method's own content at a new domain or platform, which is this page's own subject. This page also cross-references [Platform requirements](../platform-requirements.md) for the capability vocabulary and the per-stage substitutability table, rather than restating either.

## Why this way

Every earlier page in this guide states the method the way the [reference implementation](../glossary.md#reference-implementation) actually ran it. That means one platform, for one domain: the running example set out in [The running example](../running-example.md). A team working on a different platform, or teaching a different subject, needs one place that names which of those specifics are the method itself. It also needs to know which specifics are only what happened to be available this one time. Reading the whole site stage by stage leaves that separation to the reader's own judgment; this page states it directly, once.

## Steps

Every step below carries one of the basis labels this guide's [Stage 1 index](../stage-1/index.md#basis-labels) defines. Unless a step names a further, documented source, it is this guide's own `suggested` synthesis, since the project notes propose no deliberate generalization move of their own.

| Step | Who | Basis |
|---|---|---|
| Swap the running example's own content shape (seven sources, four domains, twelve objectives, three chapters) for a new domain's own equivalent, keeping every schema this guide already defines (the [blueprint](../glossary.md#blueprint), the [knowledge item](../glossary.md#knowledge-item), the [misconception](../glossary.md#misconception), and similar) unchanged, and changing only the content that fills it | Person | suggested |
| Re-declare each prompt's own [capability](../glossary.md#capability) list against the new platform's real capability set, using the vocabulary [Platform requirements](../platform-requirements.md) already publishes, rather than assuming every capability the reference implementation happened to have | Person | suggested |
| Decide, explicitly and per stage, which automated step a smaller team substitutes with a person's own work, using the same substitutability table [Platform requirements](../platform-requirements.md#capabilities-by-stage-and-workstream) already publishes | Person | suggested |
| When starting a genuinely new instance of the method, base a new prompt set on this guide's own already-published, more heavily instrumented pattern, rather than on an earlier, less structured way of working | Person | suggested |

Three further points are safe to state more plainly, because each traces to a real, sourced finding rather than to this page's own reasoning alone.

The reference implementation's own Stage 1 tooling was run a second time, per the project notes, against an unrelated subject-matter book, never named. That run produced 1,380 concept nodes, 5,181 edges, 50 cycles resolved, and 699 dangling references left unresolved. This is `documented` evidence that the method has been exercised on more than one domain, not merely proposed as portable. It happened inside the reference implementation, though, and this guide has not independently reproduced it; read it as one recorded instance, not a general finding about how the method behaves on unfamiliar material.

A second, related finding in the same project notes describes a large literature-review knowledge base, built as a further different-domain example. Whenever this guide mentions it, the same caveat applies: it never passed [Stage 3](../stage-3/index.md) verification. Read it as an example of scale a domain switch can reach, never as a finished, checked result.

The fourth step in the table above mirrors a third finding. One real line of `documented` process guidance from the project notes states that the reference implementation itself, when it started a genuinely new instance of its own tooling, based the new prompt set on its own more mature, hardened prompt-and-contract structure. It did not base that new prompt set on the earlier, less-instrumented workflow logs that structure had grown out of. Applying that same logic here is this guide's own `suggested` extension. A team starting a new instance of this method has this guide's own already-published [batch](../glossary.md#batch), [gate](../glossary.md#gate) and [hand-off document](../glossary.md#hand-off-document) pattern to build a new prompt set from, rather than reconstructing one from a single stage page read on its own. See [Agent orchestration patterns](../operating-practices/agent-orchestration-patterns.md) and [Hand-off documents and sessions](../operating-practices/hand-off-documents-and-sessions.md) for that pattern in full.

## Worked illustration

The sketch below is invented for this page. It is not a second real run of this method, and it is a different thing from the documented second-domain evidence cited above. It exists only to show what changes, and what does not, when the running example's own shape is retargeted at a different subject.

Suppose a team adapts this guide's method to teach basic spreadsheet literacy to new office staff, instead of Git basics to new developers. The blueprint's own shape stays exactly as [The running example](../running-example.md) sets it out: four weighted domains, three objectives each, and three chapters. Only the content inside that shape changes.

| ID | Domain (invented) | Weight |
|---|---|---|
| D1 | Reading and entering data | 25 |
| D2 | Formulas and functions | 30 |
| D3 | Formatting and sharing a workbook | 25 |
| D4 | Finding and fixing errors | 20 |

One objective in this invented blueprint might read:

```json
{
  "id": "D2.2",
  "text": "Write a formula that references another sheet, and predict what happens to it when the referenced cell moves.",
  "bloom": "analyze",
  "tier": 3,
  "chapter": 2,
  "supported_by": ["SRC-002"]
}
```

Every field is the same one [S1.3 Draft the blueprint](../stage-1/blueprint.md) already defines; only the words filling `text` changed. A team doing this would still gather a comparable set of sources, and screen them the way [Stage 1](../stage-1/index.md) already describes. It could still plant a deliberate coverage gap the way the running example's own D4.2 does, so its own coverage check has something to find. Nothing about the blueprint's own JSON shape, a knowledge item's own fields, or a misconception record's own shape changes; only the words filling each one do. The sketch stops at the blueprint, since every later stage already states, on its own page, that it works from whatever blueprint and knowledge base Stage 1 hands it, regardless of subject.

## Scripts

None. Extending this guide's method to a new domain or platform is a set of decisions a team makes, not a check a script can run against a fixed answer key. No script in this guide is written to test whether a retargeted instance stays correct.

## Prompts

None. Every prompt already published elsewhere in this guide is written to be reused against new content, across Stage 1 through Stage 5, certification alignment, and operating practices. Reuse only needs its own `capabilities` list re-declared for the new platform, per the Steps above. This page introduces no prompt of its own.

## Artifacts and formats

None new. Every artifact this page names (the blueprint, the knowledge item, the misconception, the misconception catalog, and similar) is defined once, on its own owning page, linked above and in the Worked illustration above. Adapting to a new domain fills each one with different content, never a different shape.

## Definition of done

- A team can name, for its own platform, which stage's steps stay automated and which become a person's own work.
- A team can point to the one schema (the blueprint, the knowledge item, the misconception, or similar) it must keep unchanged when it swaps the running example's own content for a new domain.
- Every capability a new platform lacks has a named person filling the gap, not an unstated assumption that the reference implementation's own tooling is available.

## Common failures

- Assuming every capability the reference implementation had is available on a new platform, without checking it against [Platform requirements](../platform-requirements.md).
- Treating the one real second-domain evidence point above as proof the method generalizes broadly, when it is one documented instance, not a general finding.
- Treating the literature-review knowledge base above as a finished result, once the caveat that it never passed Stage 3 verification is forgotten.
- Inventing a sixth stage, a new assessment format, or a new delivery channel, and presenting it as something the source material itself proposes, rather than as this guide's own suggested synthesis.

## Adapting to your platform

Every other page's "Adapting to your platform" section names which capability its own steps need. This page's own subject is adapting itself, so it instead names the concrete first decisions a team starting a new instance of this method makes, each cross-linked to where it is already covered in depth.

- The running example's own content: which domain, sources, and chapters the new instance actually teaches. See [The running example](../running-example.md) for the shape a new domain's own equivalent replaces, and the Worked illustration above for an invented sketch of doing so.
- The platform's own real capability set: which of the ten capabilities the chosen platform actually supplies, and which a person on the new team supplies instead. See [Platform requirements](../platform-requirements.md) for the full vocabulary.
- The stage-by-stage automation split: which stage's steps stay run by an agent, and which a person does by hand, at the new team's own scale. See [Platform requirements: capabilities by stage and workstream](../platform-requirements.md#capabilities-by-stage-and-workstream) and [Human roles, gates and batching](../human-roles-gates-and-batching.md) for what each gate kind means and who can fill each role.
- How to bootstrap a new prompt set: whether to start from this guide's own already-published, more heavily instrumented batch, gate, hand-off document and contract pattern, rather than an earlier, less structured way of working. See [Operating practices](../operating-practices/index.md) and [Agent orchestration patterns](../operating-practices/agent-orchestration-patterns.md).

## Where humans decide

- Which domain and sources replace the running example's own content, and how closely a new blueprint's shape should match it.
- Which person supplies a capability that the new platform does not.
- Which stage's automated step becomes a person's own work, at the new team's own scale.
- Whether to bootstrap a new prompt set from this guide's own already-published, instrumented pattern, or from an earlier, less structured one.

Next: [Contributing](index.md).
