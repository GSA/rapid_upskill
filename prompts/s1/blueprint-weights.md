---
id: "P-S1-03"
title: "Blueprint domains, objectives and weights"
stage: "S1"
sub_stage: "S1.3"
purpose: "Propose domains, objectives, weights with a one-line rationale each."
placeholders: ["TASK_LIST", "BOUNDARY_TEXT", "BANK_SIZE"]
capabilities: ["llm", "structured-output", "human-approval"]
inputs: "The task list, the boundary statement text, and the target bank size (a count of test questions)."
outputs: "A blueprint JSON fragment: domains with id, name, weight and rationale, each with objectives holding id, text and bloom."
---
````text
You are proposing a weighted blueprint for an upskilling program. A
blueprint groups learning objectives into weighted domains; the weights are
each domain's share of the program, out of 100.

Boundary statement:
{{BOUNDARY_TEXT}}

Task list (duty, task, knowledge/skills/abilities, frequency, criticality):
{{TASK_LIST}}

Target bank size: {{BANK_SIZE}} test questions.

Do this:
1. Group the tasks into a small number of domains. Give each domain a short
   name.
2. For each domain, propose one or more objectives: statements of what a
   learner should be able to do. Give each objective a cognitive level from
   this scale: remember, understand, apply, analyze, evaluate, create.
3. Propose a weight for each domain as its tasks' frequency multiplied by
   criticality, then scaled so the weights sum to 100.
4. Write a one-line rationale for each domain's weight that names the tasks
   behind the number.
5. Mark every weight and rationale as a proposal. A person edits the
   weights so they sum to exactly 100, and approves the result before it is
   used.

Report the blueprint as JSON: a list of domains, each with `id`, `name`,
`weight`, `rationale` and a list of `objectives`, each with `id`, `text` and
`bloom`.
````
Written for this guide and not run against any model in this build; treat it
as a starting point and adapt it.

Filled example, using the running example's values (synthetic): `BOUNDARY_TEXT`
"covers everyday commands for commits, branches, remotes, conflict
resolution and safe recovery" and `BANK_SIZE` 20, with a `TASK_LIST` whose
rows cover committing, branching, merging, fetching, pulling, pushing and
recovering a lost commit. A plausible reply proposes four domains close to
"Snapshots and history", "Branching and merging", "Working with remotes"
and "Recovering and collaborating safely", each with two or three
objectives, weights near 25, 30, 25 and 20, and a rationale such as "weighted
above the others because sharing work is where new team members make the
most costly mistakes".

Check the output by running the blueprint check script on the reply's JSON
and confirming the weights sum to 100, every `bloom` value is one of the
six cognitive levels, and every domain has at least one objective at apply
or above.
