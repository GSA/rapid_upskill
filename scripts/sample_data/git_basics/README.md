# Sample data: Git Basics for New Team Members

This folder holds the running example used across the rapid_upskill guide: a small, fictional upskilling program called **Git Basics for New Team Members**. It gives every stage of the pipeline the same tiny, checkable subject to work on.

Everything here is synthetic. The authors, dates and links in the sources are invented, the URLs use reserved example domains, and the prose is original. Nothing is copied or paraphrased from any book, manual or certification outline.

This guide is not affiliated with or endorsed by the Git project.

## Pinned Git version

The behaviors described in the accurate sources (SRC-001 to SRC-004 and SRC-006) were run in throwaway repositories on Git 2.54.0. SRC-005 states one behavior wrongly on purpose, and SRC-007 makes no technical claims worth checking. The tool reported:

```text
git version 2.54.0
```

The tested build added a packaging suffix from its operating-system vendor, which is omitted here. New repositories were created with a branch named `main`, and settings from the test machine may have applied. Statements about older versions, such as the "Git 2.23 or later" and "Git 2.19 or later" notes, come from release notes and were not run. Where a behavior depends on the version or on a setting, the source says so instead of asserting one outcome. Check your own version with `git --version`.

## Files

| File | Role |
|---|---|
| `blueprint.json` | The program blueprint: four domains weighted 25, 30, 25 and 20, with three objectives each. Objective D4.2 (recovering a commit with the reflog) is supported by no source, so a coverage-gap check has something to find |
| `cert_blueprint.json` | A fictional certification outline with three domains and eight skills. Skill CB-3.1 is covered by no chapter, and chapter 3 matches no skill, so an alignment step has one gap of each kind to find |
| `sources/SRC-001.md` | Accurate. Commits as snapshots, staging and reading history. Has misconception sentences |
| `sources/SRC-002.md` | Accurate. Branches, HEAD, fast-forward and merge commits. Has misconception sentences |
| `sources/SRC-003.md` | Accurate. Merge conflicts, restore, revert and reset. Has misconception sentences |
| `sources/SRC-004.md` | Accurate. Remotes, fetch, pull and push. Says which behavior depends on version and settings |
| `sources/SRC-005.md` | Conflict test. An older source (2019) that disagrees with SRC-004 on one point: it says a pull only downloads changes and never touches your working files. That claim is deliberately wrong. Do not learn from it |
| `sources/SRC-006.md` | Injection test. An ordinary, accurate tutorial that contains one harmless instruction addressed to an AI assistant, for practicing prompt-injection screening |
| `sources/SRC-007.md` | Promotional, low quality. A list of graphical Git clients with unsupported claims and invented product names. Low quality on purpose |

Related files outside this folder: `docs/running-example.md` (the page that presents this example) and `scripts/tests/test_running_example.py` (checks everything described here). Run the test from the repository root with `python3 -B scripts/tests/test_running_example.py`.

## The blueprint

`blueprint.json` uses these fields:

- Top level: `schema_version`, `license`, `synthetic`, `program`, `difficulty_split`, `bank_size` and `domains`.
- Each domain has an `id` (D1 to D4), a `name`, a `weight` and three `objectives`. The four weights add up to 100.
- Each objective has an `id` such as D1.1, a `text`, a `bloom` level, a `tier` from 1 to 4, a `chapter` from 1 to 3, and `supported_by`.
- `tier` is a four-level prerequisite hierarchy. An objective at a higher tier builds on objectives at lower tiers.
- `supported_by` lists the source IDs that teach the objective. It is an extra field beyond the base schema. An empty list marks a coverage gap, and exactly one objective has one.

The three chapters are: 1, Snapshots, history and branches; 2, Combining and sharing work; 3, Recovery and team rules.

## The certification outline

`cert_blueprint.json` describes a fictional certification, "Team Git Practitioner (fictional)". Its three domains are arranged by activity, not by concept, so they differ from the program's four domains. Domain weights add up to 100. Skill weights are shares within their own domain and also add up to 100 per domain. The `chapters` list, an extra field, maps each program chapter to the skills it covers.

## Reserved ID formats

| Format | Meaning | Used in this folder |
|---|---|---|
| `SRC-001` | A source, numbered with three digits | Yes |
| `KI-c.n-NNN` | A knowledge item: chapter c, counter n inside that chapter, running number NNN | Reserved |
| `MC-c-NNN` | A misconception: chapter c, running number NNN | Reserved |
| `STEM-c.n-NNN` | A question stem: chapter c, counter n inside that chapter, running number NNN | Reserved |
| `CB-d.n` | A certification skill: domain number d, skill number n | Yes |

Domain and objective IDs (D1, D1.1) are local to `blueprint.json`.

## Stem arithmetic

The bank holds 20 stems (`bank_size`). Two independent splits describe the same 20 stems, and both must come out as whole numbers.

- By difficulty: `difficulty_split` is 30, 50, 20 for easy, medium and hard, as shares of 100. So 20 x 30 / 100 = 6, 20 x 50 / 100 = 10 and 20 x 20 / 100 = 4, which gives 6/10/4.
- By domain: the weights 25, 30, 25 and 20 give 20 x 25 / 100 = 5, 20 x 30 / 100 = 6, 5 and 20 x 20 / 100 = 4, which gives 5/6/5/4.

The four hard stems should draw across domains rather than sit in one. One illustration is one hard stem per domain, which leaves 4, 5, 4 and 3 stems for the easy and medium shares. It is an example, not a rule.

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication. Each source also carries `license: "CC0-1.0"` and `synthetic: true` in its header.
