---
title: "Authoring conventions"
parent: "Contributing"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-21"
---

# Authoring conventions

These are the rules for writing pages, prompts, and scripts. Every convention carries one of two labels.

- `[checked R##]` means the checker (`python3 -B scripts/site/check.py`) tests it. `R##` is the rule number. The [Release checklist](release-checklist.md) lists every rule.
- `[guidance]` means no tool tests it. A reviewer applies it.

## Terminology

- Call a major part of the pipeline a stage, and a numbered part of a stage a sub-stage. The site says stage, not phase. [guidance]
- Stage codes are `S1` to `S5`, `CA` (certification alignment), `DL` (delivery), and `OP` (operating practices that apply across stages). [checked R07]
- Sub-stage IDs look like `S1.4a`. [checked R07]

## Page template

A stage page has these sections, in this order: Outcome, Where it fits, Why this way, Steps, Artifacts and formats, Prompts, Scripts, Definition of done, Common failures, Adapting to your platform, and Where humans decide. A page with sections out of order gets a warning. [checked R21]

Copy this stub to start a page. Replace every value. [guidance]

```markdown
---
title: "S1.4a Title of this sub-stage"
parent: "Title of the parent page"
nav_order: 4
status: "draft"
last_reviewed: "2026-09-21"
stage: "S1"
sub_stage: "S1.4a"
prompts: []
scripts: []
---

# S1.4a Title of this sub-stage

## Outcome

Write one or two sentences that say what the reader will have at the end.

## Where it fits

Name the parts before and after this one. Say what this part takes in and hands on.

## Why this way

Give the reasons for this approach. Cite a source for every number.

## Steps

1. Start each step with a verb.
2. Give each step one action.

## Artifacts and formats

List each file the steps produce, with its format.

## Prompts

Link each prompt's generated page. If there are none, write "None."

## Scripts

Link each script's generated page. If there are none, write "None."

## Definition of done

List conditions that the reader can check.

## Common failures

Describe what goes wrong and how to spot it.

## Adapting to your platform

Describe each capability the steps need, and how to supply it on another platform.

## Where humans decide

List each point where a person must decide or approve.
```

## Front matter

- Open the front matter on line 1 with `---`. Close it at the next line that holds only `---`. Put nothing before it, not even a comment. [checked R01]
- Write every string in double quotes. Write booleans and integers bare, as in `title: "Tooling"`, `nav_order: 2`, and `nav_exclude: true`. Single quotes are not allowed. The site is set to fail its build on malformed front matter. [checked R01]
- Write lists inline, as in `prompts: ["P-S1-04", "P-S1-05"]`. An item is a double-quoted string, or a bare token that starts with a letter and holds only letters, digits, dots, underscores, and hyphens. A bare `true`, `false`, `yes`, `no`, `on`, `off`, or `null` is not allowed. `[]` is an empty list. [checked R01]
- Use one `key: value` pair per line. Do not add comments, nesting, multi-line values, or repeated keys. [checked R01]
- Give every `.md` file under `docs/` front matter, except files in folders whose names start with an underscore. Without it, the file is published as a bare page. [checked R01]

The keys:

- `title`: required. It must be unique across the site. [checked R02] Do not use `&`, `<`, or `>`. Write "and". [checked R01]
- `nav_order`: required on hand-written pages unless `nav_exclude` is `true`. [checked R01] Write a bare integer such as `4`. Do not quote it, and do not use a decimal. It must be unique among siblings, which are pages with the same `parent` and `grand_parent`. [checked R03]
- `parent`: required on a nested page. It must equal the title of an existing page. A wrong value makes the page vanish from the navigation. [checked R02]
- `grand_parent`: required on a three-level page. It must equal the parent's own parent. [checked R02]
- `has_children`: not needed with the pinned theme version. Never set it to `false`, which hides the children. [checked R02]
- `status`: required on hand-written pages, and it must be `"draft"`, `"reviewed"`, or `"stable"`. [checked R01] Use `"draft"` while the page is being written. Use `"reviewed"` after a second person or agent has checked it against sources. Use `"stable"` after it is reviewed and has been rendered and read on the live site. [guidance]
- `last_reviewed`: required on hand-written pages, as a real date written `"YYYY-MM-DD"`. [checked R01] Set it to the date of the last review. [guidance]
- `stage` and `sub_stage`: on stage pages, as in `"S1"` and `"S1.4a"`. The stage must agree with the stage of each prompt and script the page lists. `OP` items are the exception, because any stage may list them. [checked R07]
- `prompts` and `scripts`: optional lists of IDs. Each ID must exist. [checked R07] Link each generated page in the body. [checked R21]
- `generated`: set to `true` only by `sync.py`. Never add or edit it by hand. [checked R11]
- `layout`, `permalink`, `nav_exclude`, and `has_toc`: optional. They pass to the theme unchanged. [guidance]
- Other keys give a warning. [checked R01] Avoid keys that the theme uses for other things, such as `summary`, `description`, `date`, `last_modified_date`, `search_exclude`, and `ancestor`. [guidance]
- Do not leave unfinished-work markers, the all-caps words for to-do and fix-me notes, in a page whose status is not `"draft"`. [checked R15]

## IDs, folders, and names

- Prompt IDs look like `P-<code>-<nn>`. Script IDs look like `X-<code>-<nn>`. The code is a stage code, and `nn` has two digits. Examples are `P-S1-04` and `X-OP-01`. An ID such as `P-OP-7` is an error. [checked R07]
- Every ID is unique. The folder, the ID code, and the `stage` value must agree. The folder is the stage code in lowercase, as in `prompts/s1/`. [checked R07]
- Name each file with a slug of lowercase letters, digits, hyphens, and underscores, as in `prompts/s1/search-plan.md` and `scripts/s1/search_plan.py`. A name such as `Bad_Name` is an error. [checked R07]
- Keep IDs in metadata only. Do not put them in file names. [guidance]
- Files in `scripts/common/` are published too. Their stage is `OP`. [guidance]
- Lists sort by stage in the order S1 to S5, CA, DL, OP, and then by number. So `S1.4` comes before `S1.4a`, which comes before `S1.10`. [guidance]
- Some ID forms are reserved for the running example: `SRC-001`, `KI-c.n-NNN`, `MC-c-NNN`, `STEM-c.n-NNN`, and `CB-d.n`. Do not reuse them for anything else. [guidance]
- Never edit `docs/prompts/`, `docs/scripts/`, or `docs/assets/images/` by hand. The sync tool owns them. [checked R11]

## Prompt file format

A prompt is one Markdown file at `prompts/<code>/<slug>.md`. [checked R07] The front matter follows the rules above.

- Required keys: `id`, `title`, `stage`, `purpose`, `placeholders`, and `capabilities`. [checked R08]
- Optional keys: `kind`, `sub_stage`, `inputs`, `outputs`, and `version`. [guidance]
- `kind` is `prompt` by default. If you set it, use `template`, `contract`, or `brief`. [checked R08]
- Do not store where a prompt is used. The sync tool derives "Used in" from pages that list the ID under `prompts:`. [guidance]
- The body has exactly one fence of four backticks tagged `text`. It starts in column 1, and only blank lines come before it. That fence is the prompt. Text after the fence is notes. [checked R08]
- Write a placeholder as an upper-snake-case name inside double curly braces, such as {% raw %}`{{OBJECTIVE_ID}}`{% endraw %}. In the front matter, list the names without braces. [checked R08]
- The declared placeholders must equal the placeholders the prompt uses. [checked R08]
- Every capability must come from the vocabulary below. [checked R08]
- Never put the closing tag of a raw block in a prompt. The generated page wraps the whole body in a raw block, and that tag would end it early. [checked R08]

An example file:

{% raw %}

~~~~~markdown
---
id: "P-S1-04"
title: "Search plan for one objective"
stage: "S1"
sub_stage: "S1.4a"
purpose: "Draft a search plan for one learning objective."
placeholders: ["OBJECTIVE_ID", "OBJECTIVE_TEXT"]
capabilities: ["llm", "web-search"]
---
````text
Plan a search for learning objective {{OBJECTIVE_ID}}.
The objective is: {{OBJECTIVE_TEXT}}
List the questions to answer and the kinds of sources to look for.
Mark each point where a person must decide.
````

Use this prompt after the objectives are agreed.
~~~~~

{% endraw %}

## Script header

A script starts with a header. In Python, the header is the module docstring. In a shell script, it is the leading `# Key: value` comment lines. Write each field as `Key: value`. An indented line continues the value above it. [checked R09]

- Required fields: `ID`, `Purpose`, `Usage`, `Dependencies`, `Writes files`, and `License`. [checked R09]
- `Dependencies` is `stdlib` or a list. Every imported module that is not in the standard library must be listed. Modules in `scripts/common/` count as declared. [checked R09]
- `Writes files` is `yes` or `no`. `License` is `CC0-1.0`. [checked R09]
- Optional fields: `Title`, `Stage`, `Inputs`, and `Outputs`. [guidance] The stage already comes from the ID, so `Stage` is redundant. If you write it, it must equal the ID code. [checked R07]
- A script that writes or deletes anything makes a dry run unless `--write` is passed. [guidance]
- Keys and tokens come only from environment variables. Never write one in a file. [checked R09]
- A script that calls a language model should use the shared adapter in `scripts/common/llm_adapter.py`, not a vendor library. Its `mock` provider runs offline. [guidance]
- `scripts/common/` is not a Python package. To import a shared module from a stage script, add that folder to the import path first, as below. [guidance]

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
import llm_adapter  # noqa: E402
```

```python
"""
ID: X-S1-01
Title: Search plan
Purpose: Print a search plan for one learning objective.
Usage: python3 scripts/s1/search_plan.py --help
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A learning objective, as text, and an optional list of
    source names.
Outputs: A search plan, printed to the terminal.
"""
```

## Capability vocabulary

A prompt lists what it needs from a platform, using only these words. [checked R08]

| Capability | Meaning |
|---|---|
| `llm` | A language model that follows written instructions |
| `long-context` | A model that accepts a very large amount of text in one request |
| `structured-output` | Output in a fixed format, such as JSON |
| `file-read` | Reading files |
| `file-write` | Creating or changing files |
| `shell` | Running commands in a terminal |
| `web-search` | Searching the web |
| `web-fetch` | Downloading a web page from a given address |
| `subagents` | Starting helper agents for parts of a task |
| `human-approval` | Pausing to ask a person to approve a step |

## Style rules

### Writing

- Use plain language: short sentences and common words. A page in which more than 10 percent of sentences run over 35 words gets an advisory warning. [checked R14]
- Define each piece of jargon where it first appears. [guidance]
- Give each step one action, and start it with a verb. [guidance]
- Give a source for every number. Add an "as of" date to anything that can change, such as a version, price, limit, or policy. [guidance]
- Describe what a step needs as a capability, and name a product only as an example. Do not word a step so that it needs one vendor. [guidance]
- Use bold sparingly. [guidance]
- Keep a page under 2,500 words. Split longer pages. [checked R14]

### Headings and links

- Start each page with one H1, and do not skip heading levels. [checked R12] A page needs an H1 and at least 60 words of body text. [checked R19]
- Do not repeat a heading on the same page. [checked R20]
- Link to other pages with relative Markdown links to `.md` files, and match letter case exactly. [checked R04]
- Never start a link with a slash. It breaks when the site is served under a base path. [checked R04]
- Do not link by relative path to a file outside `docs/`. Link to the site page, or use an absolute URL. [checked R05]
- Link to a heading with `#anchor`. The checker computes anchors the way the site's Markdown engine does. It only warns for headings with code spans, entities, `--`, `...`, or non-ASCII characters, because the result is less certain there. [checked R04a]
- Write link text that says where the link goes. Never use "here" or "click here". [checked R13]
- In an HTML include, send a `src` or `href` that starts with a slash through the `relative_url` filter. [checked R22]

### Code, images, and files

- Give every code fence a language. Use `text` when none applies. [checked R13]
- Make sure every image exists and has alt text. [checked R06]
- Do not add decorative images. The checker cannot detect them, so a reviewer does. [guidance]
- Do not include local paths, keys, tokens, or email addresses. Only reserved example addresses are allowed. [checked R10]
- Save text files as UTF-8 with `\n` line endings and no byte order mark. [checked R17]
- Do not use symlinks, or names that differ only by letter case, under `docs/`. [checked R18]

### Showing Liquid text

Jekyll evaluates Liquid even inside code fences and inline code. Text that shows a placeholder or any Liquid delimiter must sit inside a raw block. A double curly brace or a curly brace with a percent sign outside a raw block is an error. [checked R16]

To show such text, put an opening raw tag before it and a closing raw tag after it. The tags are named `raw` and `endraw`. Each is written like any Liquid tag: a curly brace and a percent sign, the tag name, then a percent sign and a curly brace. Every place on this page that shows such text uses this pattern. To see it, open the Markdown source of [this page on GitHub](https://github.com/GSA/rapid_upskill/blob/master/docs/contributing/authoring-conventions.md). [checked R16]

Two forms may appear outside a raw block, because you mean Jekyll to evaluate them. These are the `relative_url` filter and the `link` tag. Here they are, shown inside a raw block. [checked R16]

{% raw %}

```text
{{ '/assets/js/copy-announce.js' | relative_url }}
{% link contributing/index.md %}
```

{% endraw %}
