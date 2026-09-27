# Sample data: Batch 8, Parallel and cross-cutting

This folder holds sample data for the parallel and cross-cutting pages of the guide: the certification-alignment workstream and the two Delivery pages
(Part A), and the five Operating practices pages (Part B).

Everything here is synthetic and CC0-1.0. Most files draw on the guide's own established running example, [Git Basics for New Team Members](../../../docs/running-example.md),
and its own already-published, explicitly fictional certification ("Team Git Practitioner (fictional)"); `volumes/manifest.json` and
`volumes/manifest_off_convention.json` are one exception, an invented, unrelated multi-part chapter set built only to demonstrate numeral-aware
sorting at a larger scale than the three-chapter running example has chapters for. The four Part B folders (`worker_briefs/`, `run_records/`,
`citations/`, `handoffs/`) are a second exception: each is a small, invented, standalone fixture built to exercise its own page's script, not tied to the
running example's own three chapters. Nothing here names a real certification, a real accrediting body, or a real vendor or product.

## Files

| File | Role |
|---|---|
| `schedule/schedule.json` | Three chapters' own weekly study-time allocations (reading and active-learning minutes, an importance tier), checked by `schedule_check.py` |
| `schedule/schedule_broken.json` | A copy with chapter 3's own `total_minutes` raised to 130 with no matching change to its parts, for the break-on-purpose demonstration |
| `slide_notes/Ch1_slideNotes_v20260115.md` | A clean, placeholder chapter's own slide-notes file, following the slide-notes schema in full |
| `slide_notes/Ch1_slideNotes_v20260115_broken.md` | A deliberately broken copy (a short bullet count, an under-length presenter script), for the break-on-purpose demonstration |
| `volumes/manifest.json` | A small, invented, multi-part chapter set demonstrating numeral-aware chapter ordering and per-chapter section-numbering resets |
| `volumes/manifest_off_convention.json` | A copy with one chapter renamed to an off-convention id, for the break-on-purpose demonstration |
| `worker_briefs/completion_test.json` | A completion test (`required_fields: [document_id, status, findings]`) for an invented "review a batch of generic documents" task, checked by `completion_signal_check.py` |
| `worker_briefs/outputs/*.json` | Four clean worker output files, each satisfying the completion test |
| `worker_briefs/outputs_broken/*.json` | The same four filenames, with one file missing `status` entirely and another's `findings` list left empty, for the break-on-purpose demonstration |
| `run_records/run.json` | An invented run record (`schema_version`, `run`, `steps[]`, `metrics[]`, `breakdowns[]`, `checks[]`, `budget`) for an invented workflow, "reference-catalog-refresh", checked by `run_record_check.py` |
| `run_records/events.jsonl` | The paired step log for the same run: one JSON object per line, an append-only ledger the run record above rolls up |
| `citations/TEXT.md` | A small body-text excerpt about a generic engineering topic, citing four keys, one of which does not resolve |
| `citations/REFERENCES.json` | The matching reference list, defining four keys, one of which is never cited, checked bidirectionally by `citation_key_check.py` |
| `handoffs/handoff.json` | A clean, structured hand-off document (`done`, `pending`, `artifact_locations`, `open_decisions`, `remaining_budget`) for a placeholder interrupted task, checked by `handoff_completeness_check.py` |
| `handoffs/handoff_narrative_only.json` | A contrasting `{"note": "..."}` shape with none of the five structured fields, for the break-on-purpose demonstration |

Related files outside this folder: `docs/certification-alignment.md`, `docs/delivery/index.md`, `docs/delivery/slides-and-infographics.md`,
`docs/delivery/publishing.md`, `docs/operating-practices/index.md`, `docs/operating-practices/agent-orchestration-patterns.md`,
`docs/operating-practices/run-logging-and-dashboards.md`, `docs/operating-practices/provenance-and-verification.md`, and
`docs/operating-practices/hand-off-documents-and-sessions.md` (the pages that describe each file above in full), and
`scripts/tests/test_batch8_sample_data.py` (checks everything described here). Run the test from the repository root with
`python3 -B scripts/tests/test_batch8_sample_data.py`.

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication.
