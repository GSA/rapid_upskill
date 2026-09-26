"""
ID: X-S5-02
Title: Stem plan check
Stage: S5
Purpose: Check a chapter's stem plan JSON file against its own assessment
    concept items: whether each planned row's concept-item count matches
    its own difficulty's range, whether every concept item id a row names
    actually exists, and how far the plan's own overall difficulty mix
    sits from the reference implementation's 30/50/20 split.
Usage: python3 scripts/s5/stem_plan_check.py --help
    In a shell: python3 scripts/s5/stem_plan_check.py PLAN.json
    ITEMS.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: PLAN.json, a list of {"plan_row_id", "difficulty",
    "concept_item_ids", "distractor_misconceptions"} objects. ITEMS.json,
    a list of assessment concept item objects, each with at least a
    string "id" field.
Outputs: One line per finding, then a summary line, all printed to
    standard output.

This script checks three things only: whether each planned row's
concept_item_ids count falls inside its own difficulty's range (easy
exactly 1, medium 2 to 3, hard 3 to 5); whether every concept item id a
row names is actually present in ITEMS.json; and how far the plan's own
overall difficulty mix sits from the reference implementation's 30/50/20
split. It does not check ITEMS.json's own schema; a separate script
checks that a chapter's own assessment concept items are well formed. It
also does not check a row's own distractor_misconceptions field: naming
the misconception behind a planned distractor, and judging the plan's
other checklist items (cross-chapter opportunities, prerequisite
dependencies, duplicate concepts, stem-type coverage), are a person's own
read of the plan, not something this script can check by itself.

Errors (exit 1): a row that is not a JSON object; a row missing
plan_row_id, difficulty or concept_item_ids; a difficulty value other
than easy, medium or hard; a concept_item_ids count outside its own
difficulty's range; a concept_item_ids entry not present in ITEMS.json.

Warnings (exit 0, never change the exit code): the plan's own overall
difficulty mix, counted across every row with a recognized difficulty,
more than 10 percentage points off 30/50/20 on any one of the three
difficulties. A small sample plan will rarely hit the split exactly;
this is a warning a person reads, not a defect in the plan itself.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "stem_plan_check.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
DIFFICULTY_RANGES: dict[str, tuple[int, int]] = {
    "easy": (1, 1),
    "medium": (2, 3),
    "hard": (3, 5),
}
DIFFICULTY_TARGET: dict[str, int] = {"easy": 30, "medium": 50, "hard": 20}
MIX_TOLERANCE = 10


def load_json(path: Path) -> Any:
    """Read and parse one JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def load_item_ids(data: Any) -> set[str]:
    """Return the set of string ids found in an items list.

    A malformed entry (not a JSON object, or with no string id) is
    skipped rather than reported: checking an item's own shape is
    concept_item_check.py's job, not this script's.
    """
    if not isinstance(data, list):
        raise ValueError("ITEMS.json is not a JSON list")
    ids: set[str] = set()
    for entry in data:
        if not isinstance(entry, dict):
            continue
        item_id = entry.get("id")
        if isinstance(item_id, str) and item_id:
            ids.add(item_id)
    return ids


def _span(low: int, high: int) -> str:
    """Render a difficulty's own allowed count range for an error message."""
    return f"exactly {low}" if low == high else f"{low} to {high}"


def check_plan(
    data: Any, item_ids: set[str]
) -> tuple[list[str], list[str], int]:
    """Return (errors, warnings, row_count)."""
    if not isinstance(data, list):
        raise ValueError("PLAN.json is not a JSON list")

    errors: list[str] = []
    warnings: list[str] = []
    difficulty_counts: dict[str, int] = {level: 0 for level in DIFFICULTY_RANGES}
    categorized = 0

    for position, row in enumerate(data, start=1):
        label = f"row #{position}"
        if not isinstance(row, dict):
            errors.append(f"bad-row: {label} is not a JSON object")
            continue

        plan_row_id = row.get("plan_row_id")
        if isinstance(plan_row_id, str) and plan_row_id:
            label = f'row "{plan_row_id}"'
        else:
            errors.append(f"missing-field: {label} has no 'plan_row_id'")

        difficulty = row.get("difficulty")
        if not isinstance(difficulty, str) or not difficulty:
            errors.append(f"missing-field: {label} has no 'difficulty'")
            difficulty = None
        elif difficulty not in DIFFICULTY_RANGES:
            errors.append(
                f"bad-difficulty: {label} has difficulty {difficulty!r}, "
                "must be easy, medium or hard"
            )
            difficulty = None

        concept_item_ids = row.get("concept_item_ids")
        if not isinstance(concept_item_ids, list) or not all(
            isinstance(entry, str) for entry in concept_item_ids
        ):
            errors.append(f"missing-field: {label} has no 'concept_item_ids' list")
            concept_item_ids = []

        if difficulty is not None:
            low, high = DIFFICULTY_RANGES[difficulty]
            count = len(concept_item_ids)
            if not (low <= count <= high):
                errors.append(
                    f"count: {label} is {difficulty} with {count} "
                    f"concept_item_ids, needs {_span(low, high)}"
                )
            difficulty_counts[difficulty] += 1
            categorized += 1

        for concept_item_id in concept_item_ids:
            if concept_item_id not in item_ids:
                errors.append(
                    f"missing-item: {label} references concept item id "
                    f"{concept_item_id!r} not found in ITEMS.json"
                )

    if categorized:
        percentages = {
            level: difficulty_counts[level] * 100 / categorized
            for level in DIFFICULTY_RANGES
        }
        deviations = {
            level: abs(percentages[level] - DIFFICULTY_TARGET[level])
            for level in DIFFICULTY_RANGES
        }
        worst = max(deviations.values())
        if worst > MIX_TOLERANCE:
            shown = " ".join(
                f"{level}={round(percentages[level])}%"
                for level in ("easy", "medium", "hard")
            )
            warnings.append(
                f"mix: plan is {shown}, target is 30/50/20 "
                f"(off by up to {round(worst)} points)"
            )

    return errors, warnings, len(data)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="stem_plan_check.py",
        description=(
            "Check a chapter's stem plan against its own assessment concept "
            "items: concept-item counts by difficulty, referenced ids, and "
            "the plan's overall difficulty mix. Writes no files."
        ),
    )
    parser.add_argument("plan", metavar="PLAN.json", help="the stem plan JSON file")
    parser.add_argument(
        "items", metavar="ITEMS.json", help="the assessment concept items JSON file"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan_data = load_json(Path(args.plan))
        items_data = load_json(Path(args.items))
        item_ids = load_item_ids(items_data)
        errors, warnings, row_count = check_plan(plan_data, item_ids)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"stem_plan_check.py: error: {exc}", file=sys.stderr)
        return 2
    for message in errors:
        print(f"error {message}")
    for message in warnings:
        print(f"warning {message}")
    print(f"rows={row_count} errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
