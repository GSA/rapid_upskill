---
title: "S1.7 Concept map and prerequisite hierarchy"
parent: "Stage 1 Knowledge acquisition"
nav_order: 9
status: "draft"
last_reviewed: "2026-09-24"
stage: "S1"
sub_stage: "S1.7"
prompts: ["P-S1-09"]
scripts: ["X-S1-09"]
---

# S1.7 Concept map and prerequisite hierarchy

## Outcome

At the end of this sub-stage, every admitted source's concepts sit in
one shared **concept map**. A concept map is one set of concepts and
typed relations, drawn together across every source instead of kept
apart one source at a time. Each concept also has a place in the
**[prerequisite hierarchy](../glossary.md#prerequisite-hierarchy)**, the
four-tier ordering the [Stage 1 index](index.md) already names. A
script has checked the map for a cycle and for a prerequisite that
points nowhere, a fresh reviewer has sampled it, and a person has
approved the result.

## Where it fits

This sub-stage takes in the canonical knowledge items and their typed
relations from [S1.6 Knowledge items](knowledge-items.md). It hands on
the map and the hierarchy to [S1.8 Coverage and gaps](coverage-and-gaps.md)
and, once published, to later sub-stages that present material in
dependency order.

## Why this way

A later stage can tell a reader "learn this before that" only once two
things are checked. First, that the map has no cycle: a chain of
concepts that each need the one before it, running back around to
where the chain started. In a cycle, nothing in the chain could ever
come first. Second, that every prerequisite id names a concept the map
actually has; an id that matches none is a dangling reference, pointing
nowhere. Checking both before any later stage builds on the map is
cheaper than finding either problem once several sub-stages already
depend on the order it gives. This page uses the
[basis labels](index.md#basis-labels) defined on the Stage 1 index.

## Steps

| Step | Who | Basis |
|---|---|---|
| Consolidate each source's typed relations into one shared concept map, merging concepts that name the same idea | Agent | documented |
| Assign each concept a tier from 1 to 4 | Agent | documented for the four names; suggested for the number each name gets |
| Order concepts that share a tier: dependency order first, then how often the sources use them, then concrete before abstract, then known before unknown | Agent | documented |
| A fresh reviewer samples about a tenth of the map against two checks: does each sampled edge's relation match what the source material actually supports, and does each sampled concept's tier make sense next to its prerequisites | Person | documented that a sample review with two checks happens; suggested for what the two checks are, since the project notes name a sample rate without naming the checks |
| Run the concept-graph check for cycles, dangling prerequisites and a topological order | Script | suggested |
| Read the manual-review list the check cannot resolve on its own | Person | documented |
| Approve the map and hierarchy | Person | suggested |

The four tier names come from the project notes: 1 foundational, 2
building blocks, 3 integrated, and 4 applied, each tier building on the
one below it. Pairing those four names with the numbers 1 to 4 is this
guide's own choice, marked suggested. The one worked example in the
project notes sorts its concepts into three complexity tiers, not four,
and nothing in the project notes says how the three-tier scheme lines
up with the four-name one. This guide uses four tiers and this pairing
throughout, and does not claim the project notes settled the question.

The `tier` field this step fills is the same field
[S1.3 Draft the blueprint](blueprint.md) already reserves on an
objective. It is the same 1-to-4 range that `blueprint_check.py`
already validates there; a concept's tier and an objective's tier are
one field under one name, not two similarly named fields. Filling it in
is what [the running example](../running-example.md) means when it
says the concept-map sub-stage adds an objective's tier.

## Parameters

| Parameter | Value used in this guide | Basis |
|---|---|---|
| Relations per concept | about 1.5 to 2.5 on average across the whole map; re-check once outside 1.0 to 3.0 | the reference implementation's parameters |
| Reviewer sample | about a tenth of the map | the reference implementation's parameters |
| Tier range | 1 to 4 (the script's default; `--min-tier` and `--max-tier` narrow or widen it) | documented; the same range `blueprint_check.py` already validates on an objective |

## Cycle and topological-order checks

The concept-graph check finds a cycle by walking the map one concept at
a time. It remembers which concepts are still open on the path it is
currently following, and reports a cycle the moment it revisits one of
them. In the terms a computer-science reader would use, this is a
depth-first search that keeps a recursion stack. It is one of three
ways the project notes detect a cycle, not the only one; the other two
tie-break differently or resolve some cycles automatically, which this
guide's script does not attempt.

Once a cycle is out of the way, a second pass builds the topological
order. It repeatedly places any concept whose prerequisites have all
already been placed, until every concept is placed or none of the
remaining ones qualify. A cycle among the remaining concepts is exactly
what stops that from finishing; the check reports how many concepts it
managed to place, out of how many the map has.

A dangling prerequisite is an id that names no concept in the map, even
after folding case and collapsing extra spaces; it is reported, never
silently dropped. This is the plainer of two related checks the project
notes describe: a fuller version also tries a short correction list and
a partial-match retry before giving up, which this guide's script does
not attempt.

Cycle detection and the topological order need only the standard
library, once the map is read as JSON instead of the format the
project notes use. A later, optional step that draws the map as a
picture needs an external program this guide does not require and does
not name; nothing on this page depends on it.

## Artifacts and formats

- Concept-map edges: a list of `source` (a concept id), `target` (a concept
  id), `relation` (one of `depends-on`, `part-of`, `implemented-by`,
  `contrasts-with`, `example-of`), and `item_ids` (the knowledge-item ids
  that support the edge).
- Hierarchy record, the format the check script reads: a list of nodes,
  each with an `id`, a `name`, a `tier` (1 to 4) and `prerequisites` (a
  list of ids). A node's id is a plain token; where its name has a space,
  such as "staging area", the id spells it with a hyphen instead, as in
  `staging-area`.
- Manual-review list: any relation or tier the check, the sample, or the
  reviewer could not settle on its own.

## Prompts

[P-S1-09 Concept map consolidation and tiering](../prompts/s1/p-s1-09.md)
merges several sources' concept lists into one set of edges and proposes
a tier for each concept that has none yet. It is written for this guide
and has not been run against any model in this build.

## Scripts

[X-S1-09 Concept graph check](../scripts/s1/x-s1-09.md) reads a catalog
file (id, name, tier, prerequisites per concept). It reports a cycle, a
dangling prerequisite, a tier outside range, or a duplicate id, then
prints a topological order and a count of concepts at each tier.

Run it from the repository root on the sample catalog, which starts
clean:

```bash
python3 -B scripts/s1/check_concept_graph.py \
    scripts/sample_data/git_basics_stage1/concept_map/catalog.json
```

```text
order: staging-area, commit, branch, head, remote, merge, conflict, fast-forward-merge, merge-commit
tiers: 1=2 2=2 3=3 4=2
nodes=9 edges=11 cycles=0 dangling=0
```

Nine concepts, no findings: every one of the nine placed in the
topological order, and the tier counts add up to nine. See
[Reading exit codes](index.md#reading-exit-codes) on the Stage 1 index
for what the exit code means.

Break it on purpose, the opposite way from every earlier Stage 1 page:
this sample starts clean, so breaking it means copying the file and
adding two problems instead of one. Add `"commit"` to `"staging-area"`'s
prerequisites. Staging area is already a prerequisite of commit, so
this makes each of the two require the other, a two-concept cycle
between `commit` and `staging-area`. Also add the typo `"haed"` (for
`head`) to `"remote"`'s prerequisites, then run the check again on the
copy:

```text
dangling: node "remote" lists unknown prerequisite "haed"
cycle: staging-area -> commit -> staging-area
order: incomplete, 0 of 9 nodes placed
tiers: 1=2 2=2 3=3 4=2
nodes=9 edges=13 cycles=1 dangling=1
```

Both problems are flagged, unaided. The topological order does not just
lose the two cycle members. Staging area and commit sit under every
other concept's chain of prerequisites, so the cycle blocks the whole
order, and zero of the nine concepts place. A real fix removes the
false prerequisite from staging area and corrects the typo in remote's
list, one change at a time, running the check again after each. With
`--min-tier` and `--max-tier`, narrowing the allowed range flags any
concept outside it as a bad tier, the same way `blueprint_check.py`
already flags an out-of-range tier on an objective. A clean run is not
proof that a prerequisite relation is the right one, only that the map
is well-formed and has a workable order.

## Definition of done

- Every source's concepts appear in the shared map, with no name kept
  as two separate concepts.
- Every concept has a tier from 1 to 4.
- The concept-graph check reports no cycle, no dangling prerequisite, no
  bad tier and no duplicate id.
- A fresh reviewer has sampled about a tenth of the map, checking that
  each sampled edge's relation matches the source material and each
  sampled concept's tier makes sense next to its prerequisites.
- The manual-review list, if any, has been read and closed by a person.
- A person has approved the map and hierarchy.

## Common failures

- A topological order shorter than the concept count: something in the
  map still has a cycle, even after the last fix.
- A relation density outside the 1.0-to-3.0 band: the map may be missing
  relations a person should add, or carrying more than the sources
  support.
- A nonzero dangling count: a prerequisite id was typed, copied or
  merged wrong, and now names nothing.
- A concept reachable from no tier-1 concept: nothing at the
  foundational tier leads to it, which the check does not test for by
  itself and a person has to notice.

## Adapting to your platform

- `llm`: proposes the merged edges and the tier for each new concept.
- `structured-output`: the concept map and the hierarchy record are
  both JSON; ask for that shape directly, or convert a plain-text reply
  by hand.
- `file-read`: reads each source's concept list before consolidating
  them.
- `shell`: runs the concept-graph check; without it, walk the map by
  hand for a cycle and check every prerequisite id against the concept
  list, using the same rules.
- `human-approval`: covers the sample review, the manual-review list,
  and final approval.

## Where humans decide

- What the tenth-sample check looks for, and which pairs it flags.
- Every item on the manual-review list the check cannot resolve on its
  own.
- Approval of the map and hierarchy before [S1.8](coverage-and-gaps.md)
  reads it.

Next: [S1.8 Coverage and gaps](coverage-and-gaps.md).
