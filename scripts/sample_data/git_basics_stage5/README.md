# Sample data: Stage 5 Assessment development

This folder holds Stage 5's own sample data for the running example, [Git Basics for New Team Members](../../../docs/running-example.md). It is built from the same three chapters, the same real blueprint (`scripts/sample_data/git_basics/blueprint.json`, read-only, not copied here), and the same real "common mistake" sentences from `SRC-001`, `SRC-002` and `SRC-003` that earlier stages already use.

Everything here is synthetic. Nothing is copied or paraphrased from any real certification, any real delivery product, or any credential-shaped material. This guide is not affiliated with or endorsed by the Git project.

## Three names, three artifacts

Stage 5's own pages give this in full; it is repeated here because every file below depends on it. [Stage 1](../../../docs/stage-1/knowledge-items.md)'s already-published `knowledge item` (`id`, `type`, `body`, `relations`, `evidence`, `tags`, `status`) is not the same artifact as this folder's `assessment concept item` (`concept_items/items.json`), which is not the same artifact as a `stem` (`stems/stems.json`), the finished, assembled question.

## Files

| File | Role |
|---|---|
| `concept_items/items.json` | Three assessment concept items: `ACI-1-001` (Chapter 1, a commit is a snapshot), `ACI-2-001` (Chapter 2, merging), `ACI-2-002` (Chapter 2, resolving a merge conflict). Checked by `concept_item_check.py` |
| `stem_plan/plan.json` | A two-row stem plan for Chapter 2: `PLAN-1` (easy, draws on `ACI-1-001`) and `PLAN-2` (medium, draws on `ACI-2-001` and `ACI-2-002`). Checked by `stem_plan_check.py` |
| `stems/stems.json` | Two finished, clean stems, `STEM-2.1-001` and `STEM-2.1-002`, drafted from the plan above, plus one separate, clearly-marked `STEM-2.1-BROKEN` fixture used only to demonstrate a failing check. Checked by `format_rules_check.py` |
| `bank/composition.json` | A small, invented per-domain, per-difficulty item-count composition, checked against the real running-example blueprint. Checked by `bank_composition_check.py` |
| `answer_key/key.json` | An answer key with one row each for `STEM-2.1-001` and `STEM-2.1-002`: a correct answer, a point value, and feedback text. Checked by `answer_key_check.py` |
| `delivery/manifest.json` | A delivery manifest assigning `STEM-2.1-001` to two deliverable kinds and deliberately leaving `STEM-2.1-002` assigned to none, so a real gap exists to find. Checked by `delivery_coverage_check.py` |

Related files outside this folder: `docs/stage-5/` (the six pages that describe each file above in full) and `scripts/tests/test_stage5_sample_data.py` (checks everything described here). Run the test from the repository root with `python3 -B scripts/tests/test_stage5_sample_data.py`.

## The `broken_on_purpose` convention

`stems/stems.json` keeps one deliberately broken stem, `STEM-2.1-BROKEN`, in the same file as the two clean ones, marked `"broken_on_purpose": true`. `format_rules_check.py` skips it by default and only checks it with `--include-broken-examples`. `delivery_coverage_check.py` also skips any entry marked this way, so the one real gap it reports (`STEM-2.1-002`, not assigned to any deliverable) is never confused with the broken fixture. `answer_key_check.py` has no such skip: it indexes every stem in the file unconditionally. This is harmless here, since `answer_key/key.json` never references `STEM-2.1-BROKEN`, but a reader extending this sample should not assume `answer_key_check.py` would skip a broken-on-purpose entry if one were ever added to the key.

## Reserved ID formats

| Format | Meaning | Used in this folder |
|---|---|---|
| `ACI-c-NNN` | An assessment concept item: chapter c, running number NNN | Yes |
| `PLAN-n` | A planned stem-plan row, not yet a stem | Yes |
| `STEM-c.s-NNN` | A finished stem: chapter c, section s, running number NNN. This guide's own choice between two disagreeing project id schemes, explained in full on [S5.2](../../../docs/stage-5/stem-planning.md) | Yes |

## License

All files in this folder are released under CC0 1.0 Universal (CC0-1.0), a public-domain dedication.
