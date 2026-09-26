"""
ID: X-S3-04
Title: Source tier check
Stage: S3
Purpose: Print each admitted source's own credibility tier, then warn
    if too large a share of them sit at Tier 3 or below.
Usage: python3 scripts/s3/source_tier_check.py --help
    In a shell: python3 scripts/s3/source_tier_check.py TIERS.json
    [--max-low-tier-fraction F]
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A source-tiers JSON file: a list of source id, tier (1 to 4),
    and rationale entries, one per admitted source.
Outputs: One line per source, a warning line if the low-tier share is
    over the limit, then a summary line, all printed to standard
    output.

A source's tier is a judgment call for a person, not a hard pass or
fail, so this script never exits 1 on its own: a low-tier warning
never changes the exit code. It exits 0 whenever it can read its
input, and 2 only for a usage or input error, such as a missing file,
a tier outside 1 to 4, a duplicate source id, or a fraction limit
outside 0 to 1.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NamedTuple

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "source_tier_check.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
DEFAULT_MAX_LOW_TIER_FRACTION = 0.25
LOW_TIER_THRESHOLD = 3
MIN_TIER = 1
MAX_TIER = 4


class Entry(NamedTuple):
    """One admitted source's proposed tier and rationale."""

    source_id: str
    tier: int
    rationale: str


def load_json(path: Path) -> Any:
    """Read and parse one JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def load_tiers(data: Any) -> list[Entry]:
    """Return one Entry per source, in file order; validates the shape.

    Each entry needs a non-empty source_id, a tier from 1 to 4, and a
    non-empty rationale. A source_id repeated across two entries is a
    usage or input error, since the fixture is one entry per admitted
    source, not a log of repeated proposals.
    """
    if not isinstance(data, list):
        raise ValueError("TIERS.json is not a JSON list")
    if not data:
        raise ValueError("no sources found in TIERS.json")
    entries: list[Entry] = []
    seen: set[str] = set()
    for position, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"entry #{position} is not a JSON object")
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"entry #{position} has no source_id")
        if source_id in seen:
            raise ValueError(f'source_id "{source_id}" appears more than once')
        seen.add(source_id)
        tier = item.get("tier")
        if not isinstance(tier, int) or isinstance(tier, bool):
            raise ValueError(f'source "{source_id}" has a bad tier')
        if not MIN_TIER <= tier <= MAX_TIER:
            raise ValueError(
                f'source "{source_id}" has tier {tier}, '
                f"outside {MIN_TIER} to {MAX_TIER}"
            )
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale:
            raise ValueError(f'source "{source_id}" has no rationale')
        entries.append(Entry(source_id, tier, rationale))
    return entries


def low_tier_fraction(entries: list[Entry]) -> tuple[int, float]:
    """Return (count at Tier 3 or below, that count divided by the total)."""
    low_tier = sum(1 for entry in entries if entry.tier >= LOW_TIER_THRESHOLD)
    return low_tier, low_tier / len(entries)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="source_tier_check.py",
        description=(
            "Print each admitted source's own credibility tier, then warn "
            "if too large a share sit at Tier 3 or below. Writes no files, "
            "and never exits 1 on its own: the warning never changes the "
            "exit code."
        ),
    )
    parser.add_argument("tiers", metavar="TIERS", help="path to the source-tiers JSON")
    parser.add_argument(
        "--max-low-tier-fraction",
        type=float,
        default=DEFAULT_MAX_LOW_TIER_FRACTION,
        metavar="F",
        help=(
            "largest allowed share of sources at Tier 3 or below (default "
            f"{DEFAULT_MAX_LOW_TIER_FRACTION:g})"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if not 0.0 <= args.max_low_tier_fraction <= 1.0:
            raise ValueError("--max-low-tier-fraction must be between 0 and 1")
        entries = load_tiers(load_json(Path(args.tiers)))
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"source_tier_check.py: error: {exc}", file=sys.stderr)
        return 2
    for entry in entries:
        print(f"{entry.source_id} tier={entry.tier}")
    low_tier, fraction = low_tier_fraction(entries)
    if fraction > args.max_low_tier_fraction:
        print(
            f"warning low-tier: {low_tier} of {len(entries)} sources "
            f"({fraction:.2f}) are Tier 3 or below, over the "
            f"{args.max_low_tier_fraction:.2f} limit"
        )
    print(f"sources={len(entries)} low_tier={low_tier}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
