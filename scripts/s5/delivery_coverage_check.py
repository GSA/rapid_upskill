"""
ID: X-S5-06
Title: Delivery coverage check
Stage: S5
Purpose: Flag each stem a finished bank actually holds that is not
    assigned to any deliverable kind in a delivery manifest, and print
    a summary line.
Usage: python3 scripts/s5/delivery_coverage_check.py --help
    In a shell: python3 scripts/s5/delivery_coverage_check.py
    MANIFEST.json STEMS.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A delivery-manifest JSON file: a JSON object mapping a stem id
    to a list of deliverable-kind strings, such as "bank",
    "chapter_quiz", "mock_exam" or "practice_test". A stem id absent
    from the manifest and a stem id present with an empty list both
    count as zero deliverable kinds. A stem JSON file (see
    format_rules_check.py): a list of objects, each with a stem_id.
Outputs: One line per gap, then a summary line, all printed to
    standard output.

This script checks one criterion only: whether each stem the bank
actually holds is assigned to at least one deliverable kind. It does
not check a stem's own format, an answer key, or a bank's own
difficulty or domain composition; other scripts in this stage already
do that. It also does not check the other direction: a manifest entry
naming a stem id no longer in the bank is not reported here. A stem
entry that is not a JSON object, or has no stem_id, is skipped rather
than reported, and a manifest value that is not a JSON list is treated
as zero deliverable kinds rather than raising an error.

A gap is information a person reads, not a failure of this script, so
a gap never changes the exit code. The exit code is 0 unless an input
file cannot be read, or is not the JSON shape this script expects.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "delivery_coverage_check.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000


def load_json(path: Path) -> Any:
    """Read and parse a JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def find_stem_ids(data: Any) -> list[str]:
    """Return every stem id STEMS.json actually holds, in file order.

    This walks the same stem-list shape format_rules_check.py reads,
    but does not repeat its checks here: a stem entry that is not a
    JSON object, or has no stem_id, is skipped rather than reported.
    """
    if not isinstance(data, list):
        raise ValueError("the stem file is not a JSON list")
    found: list[str] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        stem_id = entry.get("stem_id")
        if isinstance(stem_id, str) and stem_id:
            found.append(stem_id)
    return found


def find_gaps(stem_ids: list[str], manifest: Any) -> list[str]:
    """Return one 'gap: ...' line for every stem id assigned zero kinds.

    A stem id absent from the manifest and a stem id present with an
    empty (or malformed) list both count as zero deliverable kinds.
    """
    if not isinstance(manifest, dict):
        raise ValueError("the manifest file is not a JSON object")
    lines: list[str] = []
    for stem_id in stem_ids:
        kinds = manifest.get(stem_id)
        count = len(kinds) if isinstance(kinds, list) else 0
        if count == 0:
            lines.append(
                f'gap: "{stem_id}" is in the bank but not assigned to any '
                "deliverable"
            )
    return lines


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="delivery_coverage_check.py",
        description=(
            "Flag each stem in a finished bank with no deliverable-kind "
            "assignment, and print a summary. Never fails on its own; "
            "writes no files."
        ),
    )
    parser.add_argument(
        "manifest", metavar="MANIFEST", help="path to the delivery-manifest JSON"
    )
    parser.add_argument("stems", metavar="STEMS", help="path to the stem JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest = load_json(Path(args.manifest))
        stems = load_json(Path(args.stems))
        stem_ids = find_stem_ids(stems)
        gaps = find_gaps(stem_ids, manifest)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"delivery_coverage_check.py: error: {exc}", file=sys.stderr)
        return 2
    for line in gaps:
        print(line)
    print(f"stems={len(stem_ids)} unassigned={len(gaps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
