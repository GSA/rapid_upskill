# Sample data: Stage 3 tools

This folder holds small, synthetic files that the Stage 3 sample scripts read. It sits beside [`git_basics/`](../git_basics/README.md), [`git_basics_stage1/`](../git_basics_stage1/README.md) and [`git_basics_stage2/`](../git_basics_stage2/README.md), the [running example](../../../docs/running-example.md), and reuses that program's IDs and sources; it does not replace or duplicate any of them.

Everything here is invented for this guide. Authors are written as "Author A", "Author B" and so on. Dates, titles and URLs use reserved example domains. Nothing is copied or paraphrased from any real book, tool or web page. This guide is not affiliated with or endorsed by the Git project.

## Files

| File | Role |
|---|---|
| `claims/claims.json` | Four claims paraphrasing Chapter 1's own content, each citing a source id. Three cite a real, admitted source; one cites a source id that does not exist. For [`claim_source_check.py`](../../s3/claim_source_check.py) |
| `review/flags.json` | Four per-claim review flags, one of each allowed status, paraphrasing Chapter 1's own content. All clean. For [`review_record_check.py`](../../s3/review_record_check.py) |
| `citations/citations.json` | Five claim-and-quote entries checked against the running example's admitted sources. Four quote their source verbatim; one is a paraphrase that does not appear in its named source. For [`citation_fidelity_check.py`](../../s3/citation_fidelity_check.py) |
| `tiers/source_tiers.json` | This guide's own suggested credibility tier, 1 to 4, for each of the running example's seven admitted sources. For [`source_tier_check.py`](../../s3/source_tier_check.py) |

Two scripts in this stage also read a file outside this folder, read-only, never copied: `claim_source_check.py` and `citation_fidelity_check.py` both read the running example's own, already-published [`sources/`](../git_basics/README.md) folder, to confirm which sources are actually admitted and what their text actually says.

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication.
