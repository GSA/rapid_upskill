# Sample data: Batch 8, Parallel and cross-cutting

This folder holds sample data for the parallel and cross-cutting pages of the guide: the certification-alignment workstream and the two Delivery pages
(Part A). A second set of sub-folders is added here once Part B (Operating practices) lands.

Everything here is synthetic, CC0-1.0, and drawn from the guide's own established running example, [Git Basics for New Team Members](../../../docs/running-example.md),
and its own already-published, explicitly fictional certification ("Team Git Practitioner (fictional)"). Nothing here names a real certification, a real
accrediting body, or a real vendor or product.

## Files

| File | Role |
|---|---|
| `schedule/schedule.json` | Three chapters' own weekly study-time allocations (reading and active-learning minutes, an importance tier), checked by `schedule_check.py` |
| `slide_notes/Ch1_slideNotes_v20260115.md` | A clean, placeholder chapter's own slide-notes file, following the slide-notes schema in full |
| `slide_notes/Ch1_slideNotes_v20260115_broken.md` | A deliberately broken copy (a short bullet count, an under-length presenter script), for the break-on-purpose demonstration |
| `volumes/manifest.json` | A small, invented, multi-part chapter set demonstrating numeral-aware chapter ordering and per-chapter section-numbering resets |
| `volumes/manifest_off_convention.json` | A copy with one chapter renamed to an off-convention id, for the break-on-purpose demonstration |

Related files outside this folder: `docs/certification-alignment.md`, `docs/delivery/index.md`, `docs/delivery/slides-and-infographics.md`, and
`docs/delivery/publishing.md` (the pages that describe each file above in full), and `scripts/tests/test_batch8_sample_data.py` (checks everything
described here). Run the test from the repository root with `python3 -B scripts/tests/test_batch8_sample_data.py`.

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication.
