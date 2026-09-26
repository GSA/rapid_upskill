# Sample data: Stage 2 tools

This folder holds small, synthetic files that the Stage 2 sample scripts read. It sits beside [`git_basics/`](../git_basics/README.md) and [`git_basics_stage1/`](../git_basics_stage1/README.md), the [running example](../../../docs/running-example.md), and reuses that program's IDs, objectives and concept catalog; it does not replace or duplicate either folder.

Everything here is invented for this guide. Authors are written as "Author A", "Author B" and so on. Dates, titles and URLs use reserved example domains. Nothing is copied or paraphrased from any real book, tool or web page. This guide is not affiliated with or endorsed by the Git project.

## Files

| File | Role |
|---|---|
| `chapter-1/draft.md` | A short, synthetic first draft of Chapter 1, on the fixed skeleton, covering the running example's four Chapter 1 objectives (D1.1, D1.2, D1.3, D2.1). For [`chapter_structure_check.py`](../../s2/chapter_structure_check.py) |
| `condensation/original.md` | A short passage about what a Git commit records, before condensation. For [`condensation_check.py`](../../s2/condensation_check.py) |
| `condensation/condensed.md` | The same passage condensed by the five named techniques, about a fifth shorter |
| `readability/before.md` | A short passage about resolving a merge conflict, written before the readability polish. For [`readability_report.py`](../../s2/readability_report.py) |
| `readability/after.md` | The same passage after the polish: shorter sentences, less passive voice, jargon defined in place |
| `prerequisites/taught_so_far.json` | Which concepts Chapter 1 has taught by each of its first two sections. For [`prerequisite_check.py`](../../s2/prerequisite_check.py) |
| `prerequisites/section_requires.json` | What two later sections state they require: one passes, one is flagged because the concept catalog places its concept at a higher tier than the section's own stated minimum |

`prerequisite_check.py` also reads a file outside this folder: the running example's own, already-published [`concept_map/catalog.json`](../git_basics_stage1/README.md), read-only. This is the only script in Stage 2 that reads across two different sample-data folders.

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication.
