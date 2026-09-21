---
title: "Tooling"
parent: "Contributing"
nav_order: 2
status: "draft"
last_reviewed: "2026-09-19"
---

# Tooling

This page lists the tools that check and preview the site, and the commands that run them. Run every command from the repository root.

## Requirements

- Python 3.10 or newer. The checker uses `sys.stdlib_module_names`, which arrived in Python 3.10.
- Node.js, only for the JavaScript syntax test. Without it, that test is skipped.
- Docker, only for the local preview described below.

## Commands

| Command | What it does |
|---|---|
| `python3 scripts/site/check.py` | Runs every check offline. Prints one line per finding as `path:line RULE message`. Exits with status 1 if there is any error. |
| `python3 scripts/site/sync.py` | Prints a plan of what the sync tool would change. Writes nothing. |
| `python3 scripts/site/sync.py --write` | Applies the plan. |
| `python3 scripts/site/sync.py --check` | Exits with status 1 if a generated file has drifted from its source, or if a stale file exists. Writes nothing. |
| `python3 scripts/site/sync.py --write --prune` | Applies the plan. Also deletes stale images and stale files marked `generated: true`. Other `.md` files are reported, never deleted. |
| `python3 scripts/tests/run_all.py` | Runs every test offline. |
| `node --check docs/assets/js/copy-announce.js` | Checks the JavaScript syntax without running the file. |

- `--check` cannot be combined with `--write` or `--prune`. That is a usage error. The sync tool exits with status 2 for a usage error or unreadable input.
- Both `check.py` and `sync.py` accept `--root DIR`. The default is the repository root.
- Run `python3 scripts/site/check.py --help` and `python3 scripts/site/sync.py --help` to see every option.

## What the sync tool owns

The sync tool turns the prompt, script, and image sources into pages and files. It owns three folders: `docs/prompts/`, `docs/scripts/`, and `docs/assets/images/`. Any file there that the tool does not produce counts as stale. Never edit these folders by hand. Change the source, then run `sync.py --write`.

## What the rules check

The [Release checklist](release-checklist.md) lists every rule. In short, the rules fall into these families.

- Front matter and navigation (R01 to R03): the front matter parses and has the required keys, titles and `nav_order` values are unique, and every parent exists.
- Links and anchors (R04, R04a, R05, R22): internal links and heading anchors resolve, no link starts with a slash, no relative link leaves `docs/`, and HTML includes use `relative_url`.
- Images (R06): images exist and have alt text.
- IDs, prompts, and scripts (R07 to R09): IDs are unique and consistent with folders, prompt files follow their format, and script headers list their dependencies.
- Forbidden strings (R10): no local paths, keys, private-key blocks, unreserved email addresses, or maintainer-supplied private terms.
- Generated files (R11): what the sync tool produced matches the sources, and no stale files remain.
- Liquid safety (R16): no Liquid delimiter appears outside a raw block.
- File hygiene (R17, R18): no carriage returns or byte order marks, no symlinks, and no names that collide by letter case.
- Advisory warnings (R12 to R15, R19 to R21): heading levels, code fence languages, page length, unfinished-work markers, duplicate headings, and stage-page section order.

Errors make `check.py` exit with status 1. Warnings do not, but read them.

## A private list of forbidden terms

A maintainer can pass an extra, private list of forbidden terms to the checker. Use `--extra-forbidden FILE`, or set the `RAPID_UPSKILL_FORBIDDEN` environment variable. Matches are reported by line number and list position, and the output never prints the matched text. Keep the list outside the repository.

## Local preview

Status: UNTESTED. No one has yet run this command against the site.

```bash
docker run --rm -v "$PWD/docs:/srv/jekyll" -p 4000:4000 jekyll/jekyll sh -c "bundle install && bundle exec jekyll serve --host 0.0.0.0 --livereload"
```

The build downloads gems and the theme, so it needs network access. Because the site sets a base URL, the preview is served at `http://localhost:4000/rapid_upskill/`, not at the root address.

By default, Docker publishes port 4000 on every network interface of your machine. To limit the preview to your own machine, change `-p 4000:4000` to `-p 127.0.0.1:4000:4000`.

Rendering has not yet been verified. The checker tests source files, not the rendered pages. Until someone has built the site and read the pages, treat the navigation, search, and copy-code announcement as unverified.
