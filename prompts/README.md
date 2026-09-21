# Prompts

Source files for the prompts published on the site. Each file holds one prompt. `python3 -B scripts/site/sync.py --write` turns them into pages under `docs/prompts/`. Never edit those pages by hand. The tools need Python 3.10 or newer.

This file is a short summary. The rules are in the [authoring conventions](../docs/contributing/authoring-conventions.md), where each rule is labeled as checked by a tool or as guidance. For a guided first try, see [Your first prompt](../docs/contributing/first-prompt.md).

## Folder layout

A prompt lives at `prompts/<code>/<slug>.md`. The folder is the stage code in lowercase, and the file name is a slug of lowercase letters, digits, hyphens, and underscores. The tools ignore `README.md` files and names that start with an underscore.

```text
prompts/
  s1/
    search-plan.md
```

| Folder | Stage code | Covers |
|---|---|---|
| `s1` to `s5` | `S1` to `S5` | The five stages |
| `ca` | `CA` | Certification alignment |
| `dl` | `DL` | Delivery |
| `op` | `OP` | Operating practices that apply across stages |

## File format in short

- The front matter needs `id`, `title`, `stage`, `purpose`, `placeholders`, and `capabilities`. It may also have `kind`, `sub_stage`, `inputs`, `outputs`, and `version`.
- Write every string in double quotes and every list inline. Do not add comments to the front matter.
- The ID is `P`, the stage code, and a two-digit number, as in `P-S1-04`. An ID such as `P-OP-7` is an error. The ID code, the `stage` value, and the folder must agree.
- The body has exactly one fence of four backticks tagged `text`. It starts in column 1, and only blank lines come before it. That fence is the prompt. Text after it is notes.
- A placeholder is an upper-snake-case name inside double curly braces. The front matter lists the names without braces. The declared names must equal the names the prompt uses.
- Each capability must be one of `llm`, `long-context`, `structured-output`, `file-read`, `file-write`, `shell`, `web-search`, `web-fetch`, `subagents`, or `human-approval`.
- Never put the closing tag of a Liquid raw block in a prompt. The generated page wraps the body in a raw block.

A minimal file with no placeholders:

~~~~markdown
---
id: "P-S1-04"
title: "Search plan for one objective"
stage: "S1"
purpose: "Draft a search plan for one learning objective."
placeholders: []
capabilities: ["llm"]
---
````text
The prompt text goes here.
````

Notes go here.
~~~~

## Before you open a pull request

1. Run `python3 -B scripts/site/sync.py --write` to update the generated pages. If a prompt has an error, the tool writes nothing. It prints `sync: <path>: <message>` and exits with status 2.
2. Run `python3 -B scripts/site/check.py` and fix every error. It reports a prompt with an error under R08, which names the line, and under R11.
