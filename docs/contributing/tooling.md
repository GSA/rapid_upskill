---
title: "Tooling"
parent: "Contributing"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-21"
---

# Tooling

This page lists the tools that check and preview the site, and the commands that run them. Run every command from the repository root.

## Requirements

- Python 3.10 or newer. Check with `python3 --version`. On some systems, for example macOS, the default `python3` can be older. Then `sync.py`, `check.py`, and `run_all.py` stop with one line on standard error and exit with status 2, with no traceback. The line says the tool needs Python 3.10 or newer and to run it with a newer `python3`.
- Node.js, only for the JavaScript syntax test.
- Docker, only for the local preview described below.

## Commands

The `-B` flag stops Python from writing `__pycache__` folders.

| Command | What it does |
|---|---|
| `python3 -B scripts/site/check.py` | Runs every check offline. Prints one line per finding as `path:line RULE message`, then a summary line, `check: N errors, M warnings`. Exits with status 0 for no errors, 1 for at least one error, and 2 for a usage error or unreadable input. |
| `python3 -B scripts/site/sync.py` | Prints a plan of what the sync tool would change. Writes nothing. |
| `python3 -B scripts/site/sync.py --write` | Applies the plan. |
| `python3 -B scripts/site/sync.py --check` | Writes nothing. Exits with status 1 if a generated file has drifted from its source or a stale file exists, and 0 otherwise. |
| `python3 -B scripts/site/sync.py --prune` | Without `--write`, only prints the plan, including the files it would delete. |
| `python3 -B scripts/site/sync.py --write --prune` | Applies the plan and deletes stale images and stale generated pages. Any other stale file is only reported, never deleted, and the exit status is still 0. |
| `python3 -B scripts/tests/run_all.py` | Runs every test offline and prints one summary line. Exits with status 1 on any failure or error. |
| `node --check docs/assets/js/copy-announce.js` | Checks the JavaScript syntax without running the file. |

- `--check` cannot be combined with `--write` or `--prune`. That is a usage error. The sync tool exits with status 2 for a usage error or an input it cannot read.
- When a prompt or script cannot become a page, the sync tool writes nothing. It prints `sync: <path>: <message>` on standard error and exits with status 2. The checker then reports that file as `<path>:1 R11 cannot generate pages: <message>`, next to the rule error that caused it, such as R08 for a prompt.
- For `check.py`, a `--root` that is not a repository root holding a `docs` folder is a usage error. The message is `--root must be a repository root that holds a docs folder`.
- Both tools accept `--root DIR`. The default is the repository root. Run either tool with `--help` to see every option.
- When you give `check.py` no private list, every run prints `R10 private-term check skipped: no list supplied` on standard error. That is normal.

## What the sync tool owns

The sync tool turns the prompt, script, and image sources into pages and files. It owns three folders: `docs/prompts/`, `docs/scripts/`, and `docs/assets/images/`. Any file there that the tool does not produce counts as stale. Never edit these folders by hand. Change the source, then run `sync.py --write`.

## What the rules check

The [Release checklist](release-checklist.md) lists every rule. In short, the rules fall into these families.

- Front matter and navigation (R01 to R03): the front matter parses and has the required keys, titles and `nav_order` values are unique, and every parent exists.
- Links and anchors (R04, R04a, R05, R22): internal links and heading anchors resolve, no link starts with a slash, no relative link leaves `docs/`, and HTML includes use `relative_url`.
- Images (R06): images exist and have alt text.
- IDs, prompts, and scripts (R07 to R09): IDs and file names have the right shape and agree with their folders, prompt files follow their format, and script headers list their dependencies.
- Forbidden strings (R10): no local paths, keys, private-key blocks, unreserved email addresses, or maintainer-supplied private terms in `docs/`, `images/`, `prompts/`, or `scripts/`.
- Generated files (R11): what the sync tool produced matches the sources, and no stale files remain.
- Liquid safety (R16): no Liquid delimiter appears outside a raw block.
- File hygiene (R17, R18): no carriage returns or byte order marks, no symlinks, and no names that collide by letter case.
- Advisory warnings (R12 to R15, R19 to R21): heading levels, code fence languages, page length, unfinished-work markers, duplicate headings, and stage-page section order.

Errors make `check.py` exit with status 1. Warnings do not, but read them.

## Tests

`python3 -B scripts/tests/run_all.py` reports one skipped test on macOS. That is normal, because the test needs a case-sensitive file system. If Node.js is not installed, the JavaScript syntax tests are skipped too, and the summary counts them as skipped.

## A private list of forbidden terms

A maintainer can give the checker a private list of forbidden terms. Pass the path of a list file with `--extra-forbidden FILE`. Or set the `RAPID_UPSKILL_FORBIDDEN` environment variable to the path of a list file. The variable must hold a path, not the terms. If the file cannot be read, `check.py` exits with status 2 and says `cannot read the private term list`. The flag wins when both are set.

The list format is plain.

- Write one term per line. Blank lines and lines that start with `#` are ignored.
- A plain term matches without regard to letter case.
- A line that starts with `re:` holds a regular expression, which also ignores letter case. An invalid expression, or one that matches empty text, makes `check.py` exit with status 2.

A match is reported as `path:line R10 private-term #N`. The number N counts only the active lines of the list, and the output never prints the matched text. Keep the list outside the repository.

## Local preview

Status: UNTESTED. This command has not been run.

```bash
docker run --rm -v "$PWD/docs:/srv/jekyll" -p 127.0.0.1:4000:4000 jekyll/jekyll sh -c "bundle install && bundle exec jekyll serve --host 0.0.0.0"
```

The command publishes port 4000 only on your own machine. Jekyll listens on all interfaces inside the container, which is why the command has `--host 0.0.0.0`. The live-reload option is left out, because its port is not published. Jekyll normally rebuilds when a file changes, so reload the page in your browser by hand.

The build downloads gems and the theme, so it needs network access. Because the site sets a base URL, the preview is served at `http://localhost:4000/rapid_upskill/`, not at the root address.

Rendering has not yet been verified. The checker tests source files, not the rendered pages. Until someone has built the site and read the pages, treat the navigation, search, and copy-code announcement as unverified.
