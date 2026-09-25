"""
ID: X-S2-04
Title: Prerequisite check
Stage: S2
Purpose: Check, section by section, whether every concept a section
    requires was already taught by that point, and at a tier no higher
    than the concept map's own tier for it.
Usage: python3 scripts/s2/prerequisite_check.py --help
    In a shell: python3 scripts/s2/prerequisite_check.py CATALOG.json
    TAUGHT.json REQUIRES.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A concept-map catalog JSON file (id, name, tier, prerequisites
    per concept, the same shape scripts/s1/check_concept_graph.py
    reads); a taught-so-far JSON file (a section id and a list of
    concept ids taught by that section, per entry); a
    section-requires JSON file (a section id and a list of required
    concepts, each with a min_tier, per entry).
Outputs: One line per section and required concept ("pass: ..." or
    "gap: ..."), then a summary line, all printed to standard output.

This script checks one thing only: whether a concept a section states
it requires was already taught in an earlier section, and whether the
catalog's own tier for that concept is no higher than the section's
stated minimum tier for it. It does not judge whether a section's own
requires list is the right one, and it does not read the chapter's
own text.

A concept counts as taught by a section if it appears in a
taught_so_far.json entry for a section that comes strictly before it.
Sections are ordered by comparing their dotted numbers ("1.2" comes
before "1.10"), never as plain text. Errors (exit 1), one line per
finding: a required concept not yet taught by that point ("gap:
section "1.2" requires "branch", not taught by that point"), or
taught, but at a tier the catalog places higher than the section's
own stated minimum ("gap: section "1.2" requires "branch" at tier 1,
catalog has it at tier 2"). A satisfied requirement prints a "pass:"
line instead. A required concept the catalog does not name at all is
a usage or input error (exit 2), not a gap: the fixtures are expected
to name only concepts the catalog already has.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "prerequisite_check.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000

Need = tuple[str, int]
Requirement = tuple[str, list[Need]]
Taught = tuple[str, list[str]]


def load_json(path: Path) -> Any:
    """Read and parse one JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def section_key(section: str) -> tuple[int, ...]:
    """Parse a dotted section id such as "1.2" into a tuple for ordering.

    Comparing these tuples orders "1.2" before "1.10", unlike comparing
    the section ids as plain text.
    """
    parts = section.split(".")
    try:
        return tuple(int(part) for part in parts)
    except ValueError as exc:
        raise ValueError(
            f'section id "{section}" is not dotted numbers, such as "1.2"'
        ) from exc


def load_catalog_tiers(data: Any) -> dict[str, int]:
    """Return a concept id to tier map from a concept-map catalog list."""
    if not isinstance(data, list):
        raise ValueError("the catalog is not a JSON list")
    tiers: dict[str, int] = {}
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"catalog entry #{position} is not a JSON object")
        concept_id = entry.get("id")
        if not isinstance(concept_id, str) or not concept_id:
            raise ValueError(f"catalog entry #{position} has no id")
        tier = entry.get("tier")
        if not isinstance(tier, int) or isinstance(tier, bool):
            raise ValueError(f'catalog entry "{concept_id}" has a bad tier')
        tiers[concept_id] = tier
    return tiers


def load_taught(data: Any) -> list[Taught]:
    """Return a list of (section, concepts_taught) pairs, in file order."""
    if not isinstance(data, list):
        raise ValueError("taught_so_far.json is not a JSON list")
    result: list[Taught] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"taught_so_far entry #{position} is not a JSON object")
        section = entry.get("section")
        if not isinstance(section, str) or not section:
            raise ValueError(f"taught_so_far entry #{position} has no section")
        concepts = entry.get("concepts_taught")
        if not isinstance(concepts, list) or not all(
            isinstance(item, str) for item in concepts
        ):
            raise ValueError(
                f'taught_so_far entry "{section}" has a bad concepts_taught list'
            )
        result.append((section, concepts))
    return result


def load_requires(data: Any) -> list[Requirement]:
    """Return a list of (section, [(concept, min_tier), ...]), in order."""
    if not isinstance(data, list):
        raise ValueError("section_requires.json is not a JSON list")
    result: list[Requirement] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"section_requires entry #{position} is not a JSON object")
        section = entry.get("section")
        if not isinstance(section, str) or not section:
            raise ValueError(f"section_requires entry #{position} has no section")
        requires = entry.get("requires")
        if not isinstance(requires, list):
            raise ValueError(f'section "{section}" has a bad requires list')
        needs: list[Need] = []
        for need in requires:
            if not isinstance(need, dict):
                raise ValueError(f'section "{section}" has a bad requires entry')
            concept = need.get("concept")
            min_tier = need.get("min_tier")
            if not isinstance(concept, str) or not concept:
                raise ValueError(
                    f'section "{section}" has a requires entry with no concept'
                )
            if not isinstance(min_tier, int) or isinstance(min_tier, bool):
                raise ValueError(
                    f'section "{section}" concept "{concept}" has a bad min_tier'
                )
            needs.append((concept, min_tier))
        result.append((section, needs))
    return result


def taught_before(taught: list[Taught], before: str) -> set[str]:
    """Union of concepts_taught for every section strictly before `before`."""
    target = section_key(before)
    covered: set[str] = set()
    for section, concepts in taught:
        if section_key(section) < target:
            covered.update(concepts)
    return covered


def check_prerequisites(
    tiers: dict[str, int], taught: list[Taught], requires: list[Requirement]
) -> list[str]:
    """Return one "pass: ..." or "gap: ..." line per section and concept."""
    lines: list[str] = []
    for section, needs in requires:
        already_taught = taught_before(taught, section)
        for concept, min_tier in needs:
            if concept not in tiers:
                raise ValueError(
                    f'section "{section}" requires "{concept}", '
                    "which the catalog does not name"
                )
            if concept not in already_taught:
                lines.append(
                    f'gap: section "{section}" requires "{concept}", '
                    "not taught by that point"
                )
                continue
            catalog_tier = tiers[concept]
            if catalog_tier > min_tier:
                lines.append(
                    f'gap: section "{section}" requires "{concept}" at tier '
                    f"{min_tier}, catalog has it at tier {catalog_tier}"
                )
                continue
            lines.append(f'pass: section "{section}" requires "{concept}", satisfied')
    return lines


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="prerequisite_check.py",
        description=(
            "Check, section by section, whether every required concept was "
            "already taught by that point, and at a tier no higher than the "
            "catalog's own tier for it. Writes no files."
        ),
    )
    parser.add_argument(
        "catalog", metavar="CATALOG", help="path to the concept-map catalog JSON"
    )
    parser.add_argument(
        "taught", metavar="TAUGHT", help="path to the taught-so-far JSON"
    )
    parser.add_argument(
        "requires", metavar="REQUIRES", help="path to the section-requires JSON"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        tiers = load_catalog_tiers(load_json(Path(args.catalog)))
        taught = load_taught(load_json(Path(args.taught)))
        requires = load_requires(load_json(Path(args.requires)))
        findings = check_prerequisites(tiers, taught, requires)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"prerequisite_check.py: error: {exc}", file=sys.stderr)
        return 2
    for line in findings:
        print(line)
    gaps = sum(1 for line in findings if line.startswith("gap:"))
    print(f"sections={len(requires)} gaps={gaps}")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
