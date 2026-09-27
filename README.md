# Rapid Upskilling Pipeline

A public, platform-neutral guide to building an AI-accelerated upskilling pipeline: a method for turning a set of source
documents into a full learning program (chapters, an AI tutor, and test questions) with people kept in the loop at every
judgment call. The guide is published from this repository's own `docs/` folder. Read it starting from
[How to use this guide](docs/how-to-use-this-guide.md).

## Repository contents

- `docs/` — the published site: every page, its Jekyll configuration, and the generated prompt and script listings. This
  is the only folder GitHub Pages actually serves.
- `images/` — source figures, copied into `docs/assets/images/` by the sync tool below.
- `scripts/` — every sample script the guide links to, organized by stage folder (`s1` through `s5`, `ca`, `dl`, `op`),
  plus `common/` (shared code), `sample_data/` (the running example's own files), `site/` (the sync and check tools), and
  `tests/`.
- `prompts/` — every sample prompt the guide links to, one file per prompt, organized the same way as `scripts/`.

`scripts/` and `prompts/` are the source of truth; `docs/prompts/` and `docs/scripts/` are generated from them by
`python3 scripts/site/sync.py --write` and must never be hand-edited. See
[Contributing: Tooling](docs/contributing/tooling.md) for the full command reference.

## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.