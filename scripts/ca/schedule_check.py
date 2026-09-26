"""
ID: X-CA-01
Title: Schedule check
Stage: CA
Purpose: Check a study-schedule JSON file for the errors and warnings
    described below: that every chapter's reading and active-learning
    minutes sum to its own stated total, and that no lower
    importance-tier chapter is given strictly more total time than a
    higher-tier chapter.
Usage: python3 scripts/ca/schedule_check.py --help
    In a shell: python3 scripts/ca/schedule_check.py SCHEDULE.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A schedule JSON file: a list of chapter objects, each with
    chapter (a number), importance_tier ("high", "medium" or "low"),
    reading_minutes, active_minutes and total_minutes.
Outputs: One line per error or warning, then a summary line, all
    printed to standard output.

This script checks arithmetic and tier ordering only. It never judges
whether a chapter's own importance tier is the right one, or whether
its time allocation is realistic for a real learner.

Errors (exit 1): a chapter whose reading_minutes plus active_minutes
does not equal its own total_minutes.

Warnings (exit 0, never change the exit code): a chapter at a lower
importance tier with a strictly higher total_minutes than a chapter at
a higher tier. This is a warning, not an error, because a small,
invented schedule will not always order cleanly on its own.

A malformed schedule (not a JSON list; an entry that is not a JSON
object; a missing field; a chapter, reading_minutes, active_minutes or
total_minutes that is not a number; an importance_tier outside high,
medium and low) is a usage or input error (exit 2), not a finding,
since it means the file does not match the schema at all.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TypeGuard

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "schedule_check.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

TIER_ORDER = {"low": 0, "medium": 1, "high": 2}
REQUIRED_FIELDS = (
    "importance_tier",
    "reading_minutes",
    "active_minutes",
    "total_minutes",
)
MAX_BYTES = 5_000_000


def _is_number(value: Any) -> TypeGuard[float]:
    """True for an int or float, but not a bool (bool is a subclass of int)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def load_schedule(path: Path) -> Any:
    """Read and parse the schedule file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def check_schedule(data: Any) -> tuple[list[str], list[str], int]:
    """Return (errors, warnings, chapter_count) for a parsed schedule."""
    if not isinstance(data, list) or not data:
        raise ValueError("the schedule is not a non-empty JSON list")

    chapters: list[dict[str, Any]] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"entry #{position} is not a JSON object")
        if "chapter" not in entry or not _is_number(entry["chapter"]):
            raise ValueError(f"entry #{position} has no numeric 'chapter'")
        chapter = entry["chapter"]
        for field_name in REQUIRED_FIELDS:
            if field_name not in entry:
                raise ValueError(f"chapter {chapter} has no '{field_name}'")
        tier = entry["importance_tier"]
        if tier not in TIER_ORDER:
            raise ValueError(
                f"chapter {chapter} has importance_tier {tier!r}, "
                "not one of high, medium, low"
            )
        for field_name in ("reading_minutes", "active_minutes", "total_minutes"):
            if not _is_number(entry[field_name]):
                raise ValueError(f"chapter {chapter} has a non-numeric '{field_name}'")
        chapters.append(entry)

    errors: list[str] = []
    for entry in chapters:
        chapter = entry["chapter"]
        reading = entry["reading_minutes"]
        active = entry["active_minutes"]
        total = entry["total_minutes"]
        computed = reading + active
        if computed != total:
            errors.append(
                f"sum-mismatch: chapter {chapter} reading_minutes ({reading}) "
                f"+ active_minutes ({active}) = {computed}, not total_minutes "
                f"({total})"
            )

    warnings: list[str] = []
    for lower in chapters:
        lower_rank = TIER_ORDER[lower["importance_tier"]]
        for higher in chapters:
            if lower is higher:
                continue
            higher_rank = TIER_ORDER[higher["importance_tier"]]
            if lower_rank >= higher_rank:
                continue
            if lower["total_minutes"] > higher["total_minutes"]:
                warnings.append(
                    f"tier-order: chapter {lower['chapter']} "
                    f"({lower['importance_tier']}, total "
                    f"{lower['total_minutes']}) exceeds chapter "
                    f"{higher['chapter']} ({higher['importance_tier']}, "
                    f"total {higher['total_minutes']})"
                )

    return errors, warnings, len(chapters)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="schedule_check.py",
        description=(
            "Check a study-schedule JSON file's per-chapter time arithmetic "
            "and importance-tier ordering. Writes no files."
        ),
    )
    parser.add_argument(
        "schedule", metavar="SCHEDULE", help="path to the schedule JSON file"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = load_schedule(Path(args.schedule))
        errors, warnings, chapter_count = check_schedule(data)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"schedule_check.py: error: {exc}", file=sys.stderr)
        return 2
    for message in errors:
        print(f"error {message}")
    for message in warnings:
        print(f"warning {message}")
    print(f"chapters={chapter_count} errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
