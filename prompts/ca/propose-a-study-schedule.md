---
id: "P-CA-01"
title: "Propose a study schedule"
stage: "CA"
purpose: "Propose one chapter's own weekly reading and active-learning time split, from its word count and its assessed importance tier."
placeholders: ["CHAPTER_ID", "CHAPTER_WORD_COUNT", "READING_PACE_WPM", "IMPORTANCE_TIER"]
capabilities: ["llm", "file-read"]
inputs: "One chapter's id and word count, a reading pace in words per minute (a starting value, calibrated on the reader's own pace), and the chapter's importance tier (high, medium or low) from the certification-alignment roll-up."
outputs: "A proposed reading_minutes, active_minutes and total_minutes for the chapter, in the shape schedule_check.py reads, plus a one-line rationale."
---
````text
You are proposing one chapter's own weekly study schedule: how many
minutes of passive reading, and how many minutes of active-learning
work, are worth budgeting before a learner starts the chapter.

Chapter id: {{CHAPTER_ID}}
Chapter word count: {{CHAPTER_WORD_COUNT}}
Reading pace: {{READING_PACE_WPM}} words per minute (a starting value;
calibrate it on your own reading speed and material, not a fixed rule)
Importance tier, from the certification-alignment roll-up: {{IMPORTANCE_TIER}}
(high, medium or low)

Do this:
1. Estimate a base reading time in minutes: the word count divided by
   the reading pace, rounded up to a whole number.
2. Propose a total weekly time allocation built from that base reading
   time, adjusted upward for a chapter that carries more weekly work
   because it needs active recall and a spaced review pass on top of
   the reading itself, not only the reading pass alone. Scale the
   total by the chapter's importance tier so that a higher-tier
   chapter is never given a strictly lower total than a lower-tier
   chapter. State, in one line, how you scaled it.
3. Split the total into reading_minutes and active_learning minutes at
   roughly 75 percent reading and 25 percent active-learning work as a
   starting point (this guide's own suggestion, not a fixed rule);
   active-learning work can be a short self-testing pass, an
   explain-it-to-a-novice pass, or a spaced review touch, depending on
   how much time is available. Round each part to a whole number of
   minutes, so that reading_minutes plus active_minutes equals the
   proposed total exactly.
4. Report the result and a one-line rationale naming the tier
   adjustment you applied.

Report the result as one JSON object with these keys: "chapter",
"importance_tier", "reading_minutes", "active_minutes",
"total_minutes", and "rationale".
````
Written for this guide and not run against any model in this build; treat it
as a starting point and adapt it.

Filled example, using the running example's own values (synthetic):
`CHAPTER_ID` is 1, `CHAPTER_WORD_COUNT` is 3000, `READING_PACE_WPM` is 150,
and `IMPORTANCE_TIER` is "high" (from a fictional certification's own
roll-up, where chapter 1 carries a high-relevance rating). A plausible
reply computes a base reading time of 20 minutes (3000 divided by 150,
rounded up), scales the total to 120 minutes given the chapter's high tier
and the extra active-recall and review passes that tier calls for, and
splits that total into 90 reading minutes and 30 active-learning minutes
(75 percent and 25 percent of 120), reporting a rationale such as "high
tier: scaled well above the base reading time to leave room for a spaced
review pass."

To check the output: confirm reading_minutes plus active_minutes equals
total_minutes exactly, then add the result to a schedule file alongside the
other chapters and run the schedule check script on the whole file,
confirming no chapter at a lower importance tier ends up with a strictly
higher total than this one.
