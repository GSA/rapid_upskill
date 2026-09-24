"""
ID: X-S1-06
Title: Concept list lint
Stage: S1
Purpose: Check a per-source concept JSON file for name and definition
    lengths, relation types, relation targets and quotes, duplicate names,
    near-duplicate concepts, and an unusual average number of relations.
Usage: python3 scripts/s1/concept_lint.py --help
    In a shell: python3 scripts/s1/concept_lint.py CONCEPTS.json
    [--name-words A-B] [--def-words A-B] [--similar X]
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A concept JSON file: a list of objects, each with name,
    definition, an optional type, and an optional relations list. Each
    relation has type, target (a concept name) and quote.
Outputs: One line per error or warning, then a summary line, all printed
    to standard output.

This script checks that a quote is present on every relation; it never
checks whether a quote is true, or whether it supports the relation it is
attached to.

Errors (exit 1): a name or a definition outside the word-count range; a
relation with an empty quote; a relation whose target is not a concept
name in the file; a relation type outside the five this guide uses
(depends-on, part-of, implemented-by, contrasts-with, example-of); a
concept name used more than once; a concept or a relation entry that is
not a JSON object.

Warnings (exit 0, never change the exit code): two concepts whose names,
or whose definitions, have a word-set overlap (a stand-in for an
embeddings-based near-duplicate check, so it only finds near-identical
wording) at or above the similarity threshold; the average number of
relations per concept outside 1.5 to 2.5.

--name-words defaults to 2-5, --def-words to 15-50, --similar to 0.85.
Word counts split on whitespace; the overlap check lower-cases each word.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "concept_lint.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
RELATION_TYPES = (
    "depends-on",
    "part-of",
    "implemented-by",
    "contrasts-with",
    "example-of",
)
DEFAULT_NAME_WORDS = (2, 5)
DEFAULT_DEF_WORDS = (15, 50)
DEFAULT_SIMILAR = 0.85
AVG_RELATIONS_LOW = 1.5
AVG_RELATIONS_HIGH = 2.5


def load_concepts(path: Path) -> Any:
    """Read and parse the concept file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def parse_range(raw: str | None, default: tuple[int, int], flag: str) -> tuple[int, int]:
    """Parse "A-B" into (A, B); return default when raw is None."""
    if raw is None:
        return default
    parts = raw.split("-")
    if len(parts) != 2:
        raise ValueError(f"{flag} must be A-B, such as 2-5")
    try:
        low, high = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ValueError(f"{flag} must be A-B, such as 2-5") from exc
    if low < 0 or high < low:
        raise ValueError(f"{flag} must have 0 <= A <= B")
    return low, high


def parse_similar(raw: str | None, default: float) -> float:
    """Parse the --similar threshold; return default when raw is None."""
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError("--similar must be a number") from exc
    if not 0.0 <= value <= 1.0:
        raise ValueError("--similar must be between 0 and 1")
    return value


def _word_count(value: Any) -> int:
    """Whitespace-split word count; 0 for anything that is not a string."""
    if not isinstance(value, str):
        return 0
    return len(value.split())


def _jaccard(a: Any, b: Any) -> float:
    """Lower-cased word-set overlap of two strings; 0.0 if either is empty."""
    if not isinstance(a, str) or not isinstance(b, str):
        return 0.0
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def _display_name(concept: dict[str, Any], position: int) -> str:
    """The concept's own name if it has one, else a positional label."""
    name = concept.get("name")
    if isinstance(name, str) and name:
        return name
    return f"concept #{position}"


def check_concepts(
    data: Any,
    name_words: tuple[int, int],
    def_words: tuple[int, int],
    similar: float,
) -> tuple[list[str], list[str], int, int]:
    """Return (errors, warnings, concept_count, relation_count)."""
    if not isinstance(data, list):
        raise ValueError("the concept list is not a JSON list")

    errors: list[str] = []
    warnings: list[str] = []
    names: dict[str, bool] = {}
    entries: list[dict[str, Any]] = []
    name_lo, name_hi = name_words
    def_lo, def_hi = def_words

    for position, concept in enumerate(data, start=1):
        if not isinstance(concept, dict):
            errors.append(f"bad-concept: concept #{position} is not a JSON object")
            continue
        label = f"concept {_display_name(concept, position)!r}"
        name_len = _word_count(concept.get("name"))
        if not name_lo <= name_len <= name_hi:
            errors.append(
                f"name-length: {label} has a {name_len}-word name, "
                f"must be {name_lo} to {name_hi} words"
            )
        def_len = _word_count(concept.get("definition"))
        if not def_lo <= def_len <= def_hi:
            errors.append(
                f"def-length: {label} has a {def_len}-word definition, "
                f"must be {def_lo} to {def_hi} words"
            )
        name = concept.get("name")
        if isinstance(name, str) and name:
            if name in names:
                errors.append(f"duplicate-name: concept name {name!r} is used twice")
            else:
                names[name] = True
        entries.append(concept)

    relation_count = 0
    for position, concept in enumerate(entries, start=1):
        label = f"concept {_display_name(concept, position)!r}"
        relations = concept.get("relations", [])
        if not isinstance(relations, list):
            errors.append(
                f"bad-relation: {label} has a 'relations' value that is not a "
                "JSON list"
            )
            continue
        for rel_position, relation in enumerate(relations, start=1):
            rel_label = f"{label} relation #{rel_position}"
            if not isinstance(relation, dict):
                errors.append(f"bad-relation: {rel_label} is not a JSON object")
                continue
            relation_count += 1
            rel_type = relation.get("type")
            if rel_type not in RELATION_TYPES:
                shown = ", ".join(RELATION_TYPES)
                errors.append(
                    f"bad-relation-type: {rel_label} has type {rel_type!r}, "
                    f"not in {shown}"
                )
            target = relation.get("target")
            if not (isinstance(target, str) and target and target in names):
                errors.append(
                    f"bad-target: {rel_label} has target {target!r}, not a "
                    "concept name in the file"
                )
            quote = relation.get("quote")
            if not (isinstance(quote, str) and quote.strip()):
                errors.append(f"empty-quote: {rel_label} has an empty quote")

    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            name_i, name_j = _display_name(entries[i], i + 1), _display_name(
                entries[j], j + 1
            )
            name_overlap = _jaccard(entries[i].get("name"), entries[j].get("name"))
            if name_overlap >= similar:
                warnings.append(
                    f"near-duplicate-name: {name_i!r} and {name_j!r} overlap "
                    f"{name_overlap:.2f} (threshold {similar:g})"
                )
            def_overlap = _jaccard(
                entries[i].get("definition"), entries[j].get("definition")
            )
            if def_overlap >= similar:
                warnings.append(
                    f"near-duplicate-definition: {name_i!r} and {name_j!r} "
                    f"overlap {def_overlap:.2f} (threshold {similar:g})"
                )

    if entries:
        average = relation_count / len(entries)
        if not AVG_RELATIONS_LOW <= average <= AVG_RELATIONS_HIGH:
            warnings.append(
                f"avg-relations: {relation_count} relation(s) over "
                f"{len(entries)} concept(s) average {average:.2f}, outside "
                f"{AVG_RELATIONS_LOW:g} to {AVG_RELATIONS_HIGH:g}"
            )

    return errors, warnings, len(entries), relation_count


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="concept_lint.py",
        description=(
            "Check a concept JSON file's name and definition lengths, "
            "relation types, relation targets and quotes, and warn on "
            "near-duplicate concepts and an unusual average relation count. "
            "Writes no files."
        ),
    )
    parser.add_argument("concepts", metavar="CONCEPTS", help="path to the concept JSON")
    parser.add_argument(
        "--name-words",
        metavar="A-B",
        help="allowed name length in words (default 2-5)",
    )
    parser.add_argument(
        "--def-words",
        metavar="A-B",
        help="allowed definition length in words (default 15-50)",
    )
    parser.add_argument(
        "--similar",
        metavar="X",
        help="word-overlap threshold for a near-duplicate warning (default 0.85)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        name_words = parse_range(args.name_words, DEFAULT_NAME_WORDS, "--name-words")
        def_words = parse_range(args.def_words, DEFAULT_DEF_WORDS, "--def-words")
        similar = parse_similar(args.similar, DEFAULT_SIMILAR)
        data = load_concepts(Path(args.concepts))
        errors, warnings, concept_count, relation_count = check_concepts(
            data, name_words, def_words, similar
        )
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"concept_lint.py: error: {exc}", file=sys.stderr)
        return 2
    for message in errors:
        print(f"error {message}")
    for message in warnings:
        print(f"warning {message}")
    print(
        f"concepts={concept_count} relations={relation_count} "
        f"errors={len(errors)} warnings={len(warnings)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
