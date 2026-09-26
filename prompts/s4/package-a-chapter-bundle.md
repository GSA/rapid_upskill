---
id: "P-S4-05"
title: "Package a chapter bundle"
stage: "S4"
sub_stage: "S4.7"
purpose: "Chunk a finished chapter's text into size-bounded bundle files, then draft the reference files a target platform's own package needs, from that platform's own current limits."
placeholders: ["CHAPTER_TEXT", "SIZE_LIMIT", "TARGET_PLATFORM_NOTES"]
capabilities: ["llm", "file-read"]
inputs: "A finished chapter's own text; a character limit for one bundle file; notes on a target platform's own current limits and what its package expects."
outputs: "A list of bundle files, each under the size limit; a short package manifest naming every file the package needs."
---
````text
You are packaging one finished chapter for delivery.

Chapter text:
{{CHAPTER_TEXT}}

Do this in two ordered steps.

Step 1. Produce size-bounded bundle files. Combine the chapter text
above into one or more bundle files. Each bundle file must stay under
this character limit: {{SIZE_LIMIT}}. If the chapter text is longer
than one file allows, split it into consecutively numbered files
(part1, part2, and so on) rather than truncating any of it. State each
bundle file's own character count.

Step 2. Prepare the content for the target platform described below.
Read the platform's own current limits and requirements first, then
build whatever short behavior text and reference-file list that
platform expects.

Target platform notes (read this before building anything for step 2;
this describes one platform's own current limits and requirements, not
a rule this guide sets):
{{TARGET_PLATFORM_NOTES}}

Report, for step 1, the bundle files produced and each one's character
count. Report, for step 2, a short behavior file and a package
manifest listing every file the package needs, each file's role, and
each file's size. Do not assume any character limit, file count, or
file-size limit beyond what the target platform notes above state; if
those notes do not answer a question the package needs answered, say
so instead of guessing a number.
````
Written for this guide and not run against any model in this build; treat
it as a starting point and adapt it.

Filled example, using the running example's values (synthetic; the
chapter text and platform notes below are shortened for this example):

```text
You are packaging one finished chapter for delivery.

Chapter text:
Chapter 2: Branching and merging. A branch is just a movable name
that points at one commit... [chapter text continues; the real prompt
carries the whole chapter, not this shortened stand-in]

Do this in two ordered steps.

Step 1. Produce size-bounded bundle files. Combine the chapter text
above into one or more bundle files. Each bundle file must stay under
this character limit: 2000. If the chapter text is longer than one
file allows, split it into consecutively numbered files (part1,
part2, and so on) rather than truncating any of it. State each bundle
file's own character count.

Step 2. Prepare the content for the target platform described below.
Read the platform's own current limits and requirements first, then
build whatever short behavior text and reference-file list that
platform expects.

Target platform notes (read this before building anything for step 2;
this describes one platform's own current limits and requirements,
not a rule this guide sets):
A hypothetical target platform for this illustration. Check its own
current documentation for its file-count, file-size, and
prompt-length limits before building against any number, including
any number given here.

Report, for step 1, the bundle files produced and each one's
character count. Report, for step 2, a short behavior file and a
package manifest listing every file the package needs, each file's
role, and each file's size. Do not assume any character limit, file
count, or file-size limit beyond what the target platform notes above
state; if those notes do not answer a question the package needs
answered, say so instead of guessing a number.
```

For this example, a model given this filled prompt would be expected
to split Chapter 2's text into `part1.md` and `part2.md`, each under
2,000 characters, and to report each file's own character count rather
than an estimate. For step 2 it would draft a short behavior file
telling the tutor to answer only from the chapter text supplied and to
apply the protocol library's named protocols, and a package manifest
listing `part1.md`, `part2.md`, the chapter's own misconception-catalog
file, a short excerpt of the protocol library, and the behavior file
itself, each with its role and its measured size. Since the target
platform notes here do not give an
actual file-count or file-size limit, the model should say so plainly
rather than inventing one. To check the output: confirm every bundle
file's stated character count is under the limit given, confirm the
manifest names no file the chapter package does not actually have, and
confirm every size in the manifest looks freshly measured rather than
carried over from an earlier run. Before using a package built this
way against a real target platform, read that platform's own current
documentation for its own limits; do not rely on the 2,000-character
figure in this example or on any other printed number, including the
500,000-character figure this guide's own S4.7 page names as one
project's own working parameter.
