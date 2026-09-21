---
title: "Release checklist"
parent: "Contributing"
nav_order: 3
status: "draft"
last_reviewed: "2026-09-21"
---

# Release checklist

Use this list before a pull request is merged, and again before a page's status becomes "stable". The automated checks catch mistakes in the source files. They cannot judge whether a page is true, fair, or clear, so the manual checks matter as much.

## Automated checks

Run these three commands in order. First update the generated files, then check the site, then confirm that nothing has drifted. Fix every error.

```bash
python3 -B scripts/site/sync.py --write
python3 -B scripts/site/check.py
python3 -B scripts/site/sync.py --check
```

An error (E) makes `check.py` exit with status 1. A warning (W) does not, but read each one. Status 2 means a usage error or an input the tool could not read. The [Tooling](tooling.md) page explains the commands.

| Rule | Level | What it catches |
|---|---|---|
| R01 | E | Front matter that does not parse, missing required keys, repeated keys, a page with no front matter, a `status` that is not draft, reviewed, or stable, a `last_reviewed` that is not a `YYYY-MM-DD` date, and a title with `&`, `<`, or `>`. Unknown keys are warnings. |
| R02 | E | Duplicate titles, a `parent` or `grand_parent` that matches no title, and `has_children: false`. |
| R03 | E | A `nav_order` that is not an integer, or that repeats among siblings. Write it as a bare integer such as `4`. |
| R04 | E | Internal links that do not resolve, including links that start with a slash. |
| R04a | E or W | Heading anchors that do not exist. An error for plain headings. Only a warning for headings with code spans, entities, `--`, `...`, or non-ASCII characters. |
| R05 | E | A relative link to a file that is in the repository but outside `docs/`. |
| R06 | E | Missing image files and empty alt text. |
| R07 | E | Duplicate IDs, IDs that do not look like `P-S1-04` (prompts) or `X-S1-04` (scripts), file names that are not slugs, a folder, ID code, or `stage` that disagree, and `prompts:` or `scripts:` entries that do not exist. |
| R08 | E | Prompt file problems: declared and used placeholders that differ, capabilities outside the vocabulary, not exactly one prompt fence, and a closing raw tag in the body. |
| R09 | E | Script header problems: missing fields, non-standard-library imports not listed under `Dependencies`, and key patterns. |
| R10 | E | Forbidden strings: local paths, key and token patterns, private-key blocks, file URLs, and unreserved email addresses, plus any private terms a maintainer supplies. |
| R11 | E | Generated files that differ from what the sync tool would write, stale files in the folders it owns, and a prompt or script that cannot become a page. |
| R12 | W | Skipped heading levels, and more than one H1. |
| R13 | W | Code fences without a language, and link text such as "here" or "click here". |
| R14 | W | Pages over 2,500 words (generated pages excepted), and pages where over 10 percent of sentences run past 35 words. |
| R15 | W | Unfinished-work markers in a page whose status is not "draft". |
| R16 | E | A Liquid delimiter outside a raw block, in a fence or in inline code as well as in prose, and a raw block that is never closed. |
| R17 | E | Carriage returns or a byte order mark in a text file. |
| R18 | E | Symlinks, and names that differ only by letter case, under `docs/`. |
| R19 | W | A page with under 60 words of body text, or with no H1. |
| R20 | W | The same heading text twice on one page. |
| R21 | W | An ID listed under `prompts:` or `scripts:` with no link to its generated page, and stage-page sections out of template order. |
| R22 | E | In `docs/_includes`, a `src` or `href` that starts with a slash and does not use `relative_url`. |

For a decimal `nav_order` such as `2.5`, the R01 message tells you to double-quote the value. Do not. A quoted `nav_order` is an R03 error, because the key must be an integer.

## Manual checks

No tool does these. A reviewer must.

- Every number has a cited source, and anything that can change has an "as of" date.
- The wording never claims more than the evidence supports.
- No personal data appears: no names of private individuals, contact details, or paths from anyone's computer.
- No image is decorative. The checker cannot tell, because R06 only catches missing files and empty alt text. Each image must carry information that the text needs.
- The license of every text, image, and code snippet has been checked, and each can be dedicated to the public domain. See [Contributing](index.md).
- Every AI-assisted passage has been read and checked by a person against its sources.
- Every command and code sample was run and works as written.
- Every external link opens the page it is meant to open. The checker does not fetch external links.
- Each step is one action that starts with a verb, and each piece of jargon is defined at first use.
- The page was rendered and read on the live site or in a local preview before its status becomes "stable".

## Changing a page's status

1. Set `status` to `"reviewed"` after a second person or agent has checked the page against its sources.
2. Set `status` to `"stable"` only after the page has been rendered and read.
3. Update `last_reviewed` each time the status changes.
