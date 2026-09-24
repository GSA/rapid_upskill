"""
ID: X-S1-09
Title: Concept graph check
Stage: S1
Purpose: Check a concept-map catalog JSON file for cycles, dangling
    prerequisites, out-of-range tiers and duplicate node ids, then print
    a topological order and a tier-count summary.
Usage: python3 scripts/s1/check_concept_graph.py --help
    In a shell: python3 scripts/s1/check_concept_graph.py CATALOG.json
    [--min-tier N] [--max-tier N]
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A concept-map catalog JSON file: a list of nodes, each with an
    id, a name, a tier and a list of prerequisite ids.
Outputs: One line per finding (a cycle, a dangling prerequisite, an
    out-of-range tier or a duplicate node id), a topological-order line,
    a tier-count line, and a summary line, all printed to standard
    output.

This script checks the graph's shape only. It does not judge whether a
prerequisite relation is a good one, only whether the catalog is
well-formed: no cycle, no dangling reference, no duplicate id, and every
tier inside the given range.

Errors (exit 1), one line each: a cycle, found by walking the graph and
remembering which nodes are still open on the current path; a dangling
prerequisite, an id with no matching node after a case-insensitive,
whitespace-collapsed comparison; a tier outside --min-tier to --max-tier,
or missing, or not a number; a node id used by more than one node.

--min-tier and --max-tier default to 1 and 4.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, TypeGuard

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "check_concept_graph.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
DEFAULT_MIN_TIER, DEFAULT_MAX_TIER = 1, 4
WHITESPACE = re.compile(r"\s+")


def load_catalog(path: Path) -> Any:
    """Read and parse the catalog file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def validate_catalog(data: Any) -> list[dict[str, Any]]:
    """Check the top-level shape; raise ValueError on anything malformed.

    A missing or badly typed tier is not checked here: it is reported as
    a bad-tier finding instead, because every node still names one id.
    """
    if not isinstance(data, list):
        raise ValueError("the catalog is not a JSON list")
    nodes: list[dict[str, Any]] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"node #{position} is not a JSON object")
        node_id = entry.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError(f"node #{position} has no id")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"node {node_id!r} has no name")
        prerequisites = entry.get("prerequisites")
        if not isinstance(prerequisites, list) or not all(
            isinstance(item, str) for item in prerequisites
        ):
            raise ValueError(f"node {node_id!r} has a bad 'prerequisites' list")
        nodes.append(entry)
    return nodes


def _is_number(value: Any) -> TypeGuard[float]:
    """True for an int or float, but not a bool (bool is a subclass of int)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _normalize(value: str) -> str:
    """Case-fold and collapse whitespace, for a loose id comparison."""
    return WHITESPACE.sub(" ", value.strip()).casefold()


def _quoted(value: str) -> str:
    """Render an id as a safe, double-quoted excerpt (ascii() escapes it)."""
    return '"' + ascii(value).strip("'") + '"'


def _topological_order(
    order_ids: list[str], resolved_prereqs: dict[str, list[str]]
) -> tuple[list[str], bool]:
    """Repeatedly place a node whose prerequisites are all already placed."""
    remaining = list(order_ids)
    placed: list[str] = []
    placed_set: set[str] = set()
    progress = True
    while remaining and progress:
        progress = False
        for node_id in list(remaining):
            if all(target in placed_set for target in resolved_prereqs[node_id]):
                placed.append(node_id)
                placed_set.add(node_id)
                remaining.remove(node_id)
                progress = True
    return placed, not remaining


def _find_cycles(
    order_ids: list[str], resolved_prereqs: dict[str, list[str]]
) -> list[list[str]]:
    """Depth-first walk with a recursion-stack set; collects every cycle."""
    visited: set[str] = set()
    on_stack: set[str] = set()
    path: list[str] = []
    cycles: list[list[str]] = []

    def visit(current: str) -> None:
        if current in visited:
            return
        if current in on_stack:
            start = path.index(current)
            cycles.append(path[start:] + [current])
            return
        on_stack.add(current)
        path.append(current)
        for target in resolved_prereqs[current]:
            visit(target)
        path.pop()
        on_stack.discard(current)
        visited.add(current)

    for node_id in order_ids:
        visit(node_id)
    return cycles


def check_catalog(
    nodes: list[dict[str, Any]], min_tier: int, max_tier: int
) -> tuple[list[str], list[str], bool, int, dict[int, int], int]:
    """Return (errors, order, complete, placed_count, tier_counts, edges)."""
    errors: list[str] = []
    seen_ids: dict[str, bool] = {}
    known_ids: dict[str, str] = {}
    own_prereqs: dict[str, list[str]] = {}
    tier_counts: dict[int, int] = {tier: 0 for tier in range(min_tier, max_tier + 1)}
    edge_count = 0

    for node in nodes:
        node_id = node["id"]
        if node_id in seen_ids:
            errors.append(
                f"duplicate-id: {_quoted(node_id)} is used by more than one node"
            )
        else:
            seen_ids[node_id] = True
            known_ids.setdefault(_normalize(node_id), node_id)
        tier = node.get("tier")
        if _is_number(tier) and min_tier <= tier <= max_tier:
            tier_counts[int(tier)] += 1
        else:
            errors.append(
                f"bad-tier: node {_quoted(node_id)} has tier {tier!r}, "
                f"must be {min_tier} to {max_tier}"
            )
        prerequisites = [str(item) for item in node.get("prerequisites", [])]
        own_prereqs[node_id] = prerequisites
        edge_count += len(prerequisites)

    for node in nodes:
        node_id = node["id"]
        for prereq in own_prereqs[node_id]:
            if _normalize(prereq) not in known_ids:
                errors.append(
                    f"dangling: node {_quoted(node_id)} lists unknown "
                    f"prerequisite {_quoted(prereq)}"
                )

    order_ids = list(seen_ids.keys())
    resolved_prereqs: dict[str, list[str]] = {
        node_id: [
            target
            for target in (
                known_ids.get(_normalize(prereq)) for prereq in own_prereqs[node_id]
            )
            if target is not None
        ]
        for node_id in order_ids
    }

    for cycle in _find_cycles(order_ids, resolved_prereqs):
        errors.append("cycle: " + " -> ".join(cycle))

    order, complete = _topological_order(order_ids, resolved_prereqs)
    return errors, order, complete, len(order), tier_counts, edge_count


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="check_concept_graph.py",
        description=(
            "Check a concept-map catalog JSON file for cycles, dangling "
            "prerequisites, out-of-range tiers and duplicate ids, and print "
            "a topological order and a tier-count summary. Writes no files."
        ),
    )
    parser.add_argument("catalog", metavar="CATALOG", help="path to the catalog JSON")
    parser.add_argument(
        "--min-tier",
        type=int,
        default=DEFAULT_MIN_TIER,
        metavar="N",
        help=f"lowest allowed tier (default {DEFAULT_MIN_TIER})",
    )
    parser.add_argument(
        "--max-tier",
        type=int,
        default=DEFAULT_MAX_TIER,
        metavar="N",
        help=f"highest allowed tier (default {DEFAULT_MAX_TIER})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.min_tier > args.max_tier:
            raise ValueError("--min-tier must not be greater than --max-tier")
        data = load_catalog(Path(args.catalog))
        nodes = validate_catalog(data)
        errors, order, complete, placed_count, tier_counts, edge_count = check_catalog(
            nodes, args.min_tier, args.max_tier
        )
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"check_concept_graph.py: error: {exc}", file=sys.stderr)
        return 2
    for message in errors:
        print(message)
    if complete:
        print("order: " + ", ".join(order))
    else:
        print(f"order: incomplete, {placed_count} of {len(nodes)} nodes placed")
    tiers_text = " ".join(f"{tier}={tier_counts[tier]}" for tier in sorted(tier_counts))
    print(f"tiers: {tiers_text}")
    cycles = sum(1 for message in errors if message.startswith("cycle:"))
    dangling = sum(1 for message in errors if message.startswith("dangling:"))
    print(f"nodes={len(nodes)} edges={edge_count} cycles={cycles} dangling={dangling}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
