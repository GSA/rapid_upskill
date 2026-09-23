---
id: "P-S1-02"
title: "Job-task analysis with guessed ratings"
stage: "S1"
sub_stage: "S1.2"
purpose: "Draft duties, tasks and knowledge, skills and abilities; ratings are guesses."
placeholders: ["BOUNDARY_TEXT", "AUDIENCE"]
capabilities: ["llm", "human-approval"]
inputs: "The boundary statement text and the audience description."
outputs: "A task list: duty, task, knowledge/skills/abilities, and a frequency and criticality guess for each task."
---
````text
You are drafting a job-task analysis for an upskilling program. A job-task
analysis lists the duties and tasks of a job, with the knowledge, skills and
abilities each task needs.

Boundary statement:
{{BOUNDARY_TEXT}}

Audience: {{AUDIENCE}}

Do this:
1. List the duties this audience performs inside the boundary above. A duty
   is a broad area of responsibility, such as "combining and sharing work".
2. For each duty, list its tasks: specific, observable actions, such as
   "resolve a merge conflict".
3. For each task, list the knowledge, skills and abilities (facts, methods
   and capacities) it needs.
4. Rate each task's frequency (how often the audience does it) and its
   criticality (how much a mistake would cost), each on a 1 to 5 scale.
5. Mark every rating "guess". You are not a subject-matter expert. Do not
   invent a rater's name or a date; a person adds those when they re-rate
   the task.

Report one row per task, in this order: duty; task; knowledge, skills and
abilities; frequency guess; criticality guess.
````
Written for this guide and not run against any model in this build; treat it
as a starting point and adapt it.

Filled example, using the running example's values (synthetic): `BOUNDARY_TEXT`
"covers everyday commands for commits, branches, remotes, conflict
resolution and safe recovery; excludes Git internals and server
administration" and `AUDIENCE` "a developer newly hired onto a small team
that already uses Git". A plausible reply includes the row: duty "Combining
and sharing work"; task "Resolve a merge conflict"; knowledge, skills and
abilities "reads conflict markers, edits the conflicting file, stages the
resolved file, completes the merge"; frequency guess 3 (guess); criticality
guess 4 (guess).

Check the output by confirming every task names a duty from the same list,
that every rating is explicitly marked "guess", and that no row invents a
rater's name or a date.
