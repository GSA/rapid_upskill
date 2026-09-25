# Sample data: Stage 1 tools

This folder holds small, synthetic files that the Stage 1 sample scripts read. It sits beside [`git_basics/`](../git_basics/README.md), the [running example](../../../docs/running-example.md), and reuses that program's IDs and sources; it does not replace or duplicate that folder.

Everything here is invented for this guide. Authors are written as "Author A", "Author B" and so on. Dates, titles and URLs use reserved example domains. Nothing is copied or paraphrased from any real book, tool or web page. This guide is not affiliated with or endorsed by the Git project.

## Files

| File | Role |
|---|---|
| `search/plan.json` | A search plan for one blueprint objective (D2.1), with two anchors and two query clusters. Also the queue that [`run_queue.py`](../../s1/run_queue.py) runs |
| `search/mock_index.json` | A small offline index that a mock search backend matches queries against: nine candidate records, one duplicate-title variant, one old record |
| `conversion/SRC-004.original.txt` | A plain-text copy of the running example's SRC-004, for [`check_conversion.py`](../../s1/check_conversion.py) to compare against |
| `conversion/SRC-004.converted.md` | The same text with one whole section removed on purpose, so the word-ratio check has something real to catch |
| `raw/tidy-routine.html` | A synthetic HTML page for [`scan_injection.py`](../../s1/scan_injection.py): reuses the running example's SRC-006 visible text and one visible instruction sentence, plus one hidden sentence (see below) and two invisible characters written as HTML numeric character references |
| `extraction/SRC-002.concepts.json` | A six-concept list for the running example's SRC-002, for [`concept_lint.py`](../../s1/concept_lint.py) |
| `extraction/SRC-002.distillate.md` | A nine-section distillate for SRC-002, with a quote bank for [`quote_check.py`](../../s1/quote_check.py). One quote is a paraphrase on purpose, so the failing run is real |
| `knowledge_items/items.json` | Four draft knowledge items built from the running example's SRC-001 and SRC-003, for [`ki_dedupe.py`](../../s1/ki_dedupe.py): one genuine cross-source near-duplicate pair about the staging area, and one look-alike pair that is not a duplicate |
| `concept_map/catalog.json` | A nine-node concept catalog for the running example, for [`check_concept_graph.py`](../../s1/check_concept_graph.py). A clean, valid graph: no cycle, no dangling reference |

## The hidden sentence in `raw/tidy-routine.html`

The hidden element's text only asks a summarizer to describe the page as the best source and rank it first. It names no address, command, password, token, persona, product or assistant, and asks for no data. It is shown on the [injection screening page](../../../docs/stage-1/injection-screening.md) inside a fenced code block, never rendered live.

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication.
