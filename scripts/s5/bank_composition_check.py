"""
ID: X-S5-04
Title: Bank composition check
Stage: S5
Purpose: Check a bank composition file's per-domain item counts
    against a blueprint's own weights, and its bank-wide difficulty
    split against the reference implementation's 30/50/20 split.
Usage: python3 scripts/s5/bank_composition_check.py --help
    In a shell: python3 scripts/s5/bank_composition_check.py
    COMPOSITION.json BLUEPRINT.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A bank composition JSON file: an object with one key,
    "domains", mapping each domain id to an object with an "easy", a
    "medium" and a "hard" item count. A blueprint JSON file (the shape
    S1.3 defines): an object with a "domains" list, each holding at
    least an "id" and a "weight".
Outputs: One line per warning, a domain-by-domain table of each
    domain's target and its real item count, one bank-wide
    difficulty-split line, and a summary line, all printed to standard
    output.

A gap between a composition and its blueprint is a person's judgment
call, not a hard failure: this script never exits 1 on its own. It
exits 0 whenever it can read both input files and finish the checks
below, and 2 only for a usage or input error, such as a missing file,
malformed JSON, a file that is not shaped as this script expects, or a
composition with no items at all to check.

Warnings (exit 0, never change the exit code): a domain's own real
item count (the sum of its easy, medium and hard counts) is not within
1 of `weight * bank_size / 100`, where `bank_size` is the sum of every
count in the composition file and `weight` is that domain's own weight
in the blueprint ("domain-count"); the whole bank's own easy, medium
and hard split is more than 10 percentage points off the reference
implementation's 30/50/20 split, on any one of the three tiers
("difficulty-split").
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TypeGuard

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "bank_composition_check.py: this script needs Python 3.10 or "
        f"newer, but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
DIFFICULTIES = ("easy", "medium", "hard")
REFERENCE_SPLIT = {"easy": 30.0, "medium": 50.0, "hard": 20.0}
DOMAIN_TOLERANCE = 1.0
SPLIT_TOLERANCE = 10.0
DomainRow = tuple[str, float, float, int]


def load_json(path: Path) -> Any:
    """Read and parse a JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def _is_number(value: Any) -> TypeGuard[float]:
    """True for an int or float, but not a bool (bool is a subclass of int)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_blueprint_domains(data: Any) -> list[tuple[str, float]]:
    """Return [(domain_id, weight), ...], in the blueprint's own order."""
    if not isinstance(data, dict):
        raise ValueError("the blueprint is not a JSON object")
    domains = data.get("domains")
    if not isinstance(domains, list) or not domains:
        raise ValueError("the blueprint's 'domains' is missing, empty or not a list")
    result: list[tuple[str, float]] = []
    seen: set[str] = set()
    for position, domain in enumerate(domains, start=1):
        if not isinstance(domain, dict):
            raise ValueError(f"blueprint domain #{position} is not a JSON object")
        domain_id = domain.get("id")
        if not isinstance(domain_id, str) or not domain_id:
            raise ValueError(f"blueprint domain #{position} has no string 'id'")
        if domain_id in seen:
            raise ValueError(f"blueprint domain id '{domain_id}' is used twice")
        seen.add(domain_id)
        weight = domain.get("weight")
        if not _is_number(weight):
            raise ValueError(f"blueprint domain '{domain_id}' has no numeric 'weight'")
        result.append((domain_id, weight))
    return result


def parse_composition_domains(data: Any) -> dict[str, dict[str, int]]:
    """Return {domain_id: {"easy": n, "medium": n, "hard": n}, ...}."""
    if not isinstance(data, dict):
        raise ValueError("the composition is not a JSON object")
    domains = data.get("domains")
    if not isinstance(domains, dict) or not domains:
        raise ValueError(
            "the composition's 'domains' is missing, empty or not a JSON object"
        )
    result: dict[str, dict[str, int]] = {}
    for domain_id, counts in domains.items():
        if not isinstance(counts, dict):
            raise ValueError(f"composition domain '{domain_id}' is not a JSON object")
        parsed: dict[str, int] = {}
        for difficulty in DIFFICULTIES:
            count = counts.get(difficulty, 0)
            valid = _is_number(count) and count >= 0 and float(count).is_integer()
            if not valid:
                raise ValueError(
                    f"composition domain '{domain_id}' has a bad '{difficulty}' "
                    f"count: {count!r}"
                )
            parsed[difficulty] = int(count)
        result[domain_id] = parsed
    return result


def check_composition(
    composition: dict[str, dict[str, int]], blueprint_domains: list[tuple[str, float]]
) -> tuple[list[str], list[DomainRow], dict[str, int], int]:
    """Return (warnings, domain_rows, overall_counts, bank_size).

    domain_rows holds (domain_id, weight, target, actual), one row per
    blueprint domain, in blueprint order. overall_counts holds the
    bank-wide easy, medium and hard totals, across every composition
    domain, whether or not it also appears in the blueprint.
    """
    bank_size = sum(
        count for counts in composition.values() for count in counts.values()
    )
    if bank_size <= 0:
        raise ValueError("the composition has no items to check")

    warnings: list[str] = []
    domain_rows: list[DomainRow] = []
    empty_counts = {difficulty: 0 for difficulty in DIFFICULTIES}
    for domain_id, weight in blueprint_domains:
        counts = composition.get(domain_id, empty_counts)
        actual = sum(counts.values())
        target = weight * bank_size / 100
        domain_rows.append((domain_id, weight, target, actual))
        if abs(actual - target) > DOMAIN_TOLERANCE + 1e-9:
            diff = actual - target
            warnings.append(
                f"domain-count: domain {domain_id} weight {weight!r} gives "
                f"bank_size * weight / 100 = {target!r} target, actual count "
                f"is {actual} ({diff:+.1f} away)"
            )

    overall_counts = {
        difficulty: sum(counts.get(difficulty, 0) for counts in composition.values())
        for difficulty in DIFFICULTIES
    }
    percentages = {
        difficulty: 100 * overall_counts[difficulty] / bank_size
        for difficulty in DIFFICULTIES
    }
    max_off = max(
        abs(percentages[difficulty] - REFERENCE_SPLIT[difficulty])
        for difficulty in DIFFICULTIES
    )
    if max_off > SPLIT_TOLERANCE + 1e-9:
        warnings.append(
            "difficulty-split: bank-wide split is "
            f"easy={percentages['easy']:.1f}% medium={percentages['medium']:.1f}% "
            f"hard={percentages['hard']:.1f}%, more than 10 points off the "
            "reference implementation's 30/50/20"
        )

    return warnings, domain_rows, overall_counts, bank_size


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="bank_composition_check.py",
        description=(
            "Check a bank composition's domain item counts against a "
            "blueprint's own weights, and its bank-wide difficulty split "
            "against the reference implementation's 30/50/20. Writes no "
            "files, and never fails on its own."
        ),
    )
    parser.add_argument(
        "composition", metavar="COMPOSITION", help="path to the composition JSON"
    )
    parser.add_argument(
        "blueprint", metavar="BLUEPRINT", help="path to the blueprint JSON"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        composition_data = load_json(Path(args.composition))
        blueprint_data = load_json(Path(args.blueprint))
        composition = parse_composition_domains(composition_data)
        blueprint_domains = parse_blueprint_domains(blueprint_data)
        warnings, domain_rows, overall_counts, bank_size = check_composition(
            composition, blueprint_domains
        )
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"bank_composition_check.py: error: {exc}", file=sys.stderr)
        return 2

    for message in warnings:
        print(f"warning {message}")
    print(f"domain by target and actual item count (bank_size={bank_size}):")
    for domain_id, weight, target, actual in domain_rows:
        print(f"{domain_id}  weight={weight!r} target={target:.1f} actual={actual}")
    percentages = {
        difficulty: 100 * overall_counts[difficulty] / bank_size
        for difficulty in DIFFICULTIES
    }
    print(
        f"difficulty split (bank_size={bank_size}): "
        f"easy={overall_counts['easy']} ({percentages['easy']:.1f}%) "
        f"medium={overall_counts['medium']} ({percentages['medium']:.1f}%) "
        f"hard={overall_counts['hard']} ({percentages['hard']:.1f}%) target=30/50/20"
    )
    print(f"domains={len(domain_rows)} warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
