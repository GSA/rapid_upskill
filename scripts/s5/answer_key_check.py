"""
ID: X-S5-05
Title: Answer key check
Stage: S5
Purpose: Check an answer key JSON file against a stems JSON file: every
    stem id in the key resolves to a real stem, and every answer letter
    the key uses (a correct answer or a feedback key) is a real option
    for that stem, matching that stem's own real correct answer.
Usage: python3 scripts/s5/answer_key_check.py --help
    In a shell: python3 scripts/s5/answer_key_check.py KEY.json STEMS.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: An answer-key JSON file: a list of objects, each with stem_id,
    correct_answer, points, feedback_correct, and feedback_by_distractor
    (a map from an option letter to feedback text). A stems JSON file: a
    list of objects, each with stem_id, correct_answer, and distractors
    (a list of objects, each with an option letter).
Outputs: One line per error, then a summary line, all printed to
    standard output.

This script checks the answer key against the stems file only; it does
not re-check the stems file's own shape (a separate script does that).
A stem entry that is not a JSON object, or that has no usable stem_id,
is simply skipped when this script builds its own index of real
answers and real options, so any answer-key entry that names it is
reported as a missing stem, not a second, separate finding.

Errors (exit 1): an answer-key entry that is not a JSON object; a
stem_id in the answer key that is not present in the stems file (or
that the answer key never gives at all); a correct_answer letter that
is a real option for its own stem but does not match that stem's own
real correct answer; a correct_answer letter, or a
feedback_by_distractor key, that is not one of the letters that
stem's own correct answer and distractors actually use.

That last check is the point of this script. A real project's own
answer-parsing step once matched only part of a stem's valid option
range with a fixed pattern, so a letter outside that matched range
was silently treated as the first option instead of raising an error.
This script does the opposite: any letter outside a stem's own real
option range is a loud, reported error, never a silent default.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "answer_key_check.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
StemInfo = dict[str, Any]


def load_json(path: Path) -> Any:
    """Read and parse a JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def build_stem_index(stems: Any) -> dict[str, StemInfo]:
    """Return {stem_id: {"correct_answer": ..., "valid_letters": {...}}}.

    A stem entry that is not a JSON object, or has no usable stem_id, is
    skipped rather than reported; this script only checks the answer key
    against whatever real stems it can find.
    """
    if not isinstance(stems, list):
        raise ValueError("the stems file is not a JSON list")
    index: dict[str, StemInfo] = {}
    for stem in stems:
        if not isinstance(stem, dict):
            continue
        stem_id = stem.get("stem_id")
        if not isinstance(stem_id, str) or not stem_id:
            continue
        letters: set[str] = set()
        correct_answer = stem.get("correct_answer")
        if isinstance(correct_answer, str) and correct_answer:
            letters.add(correct_answer)
        distractors = stem.get("distractors")
        if isinstance(distractors, list):
            for distractor in distractors:
                if not isinstance(distractor, dict):
                    continue
                option = distractor.get("option")
                if isinstance(option, str) and option:
                    letters.add(option)
        index[stem_id] = {
            "correct_answer": correct_answer,
            "valid_letters": letters,
        }
    return index


def option_range(letters: set[str]) -> str:
    """Return a range string such as '(A-D)' for a set of option letters."""
    if not letters:
        return "(none)"
    ordered = sorted(letters)
    return f"({ordered[0]}-{ordered[-1]})"


def check_answer_key(
    entries: Any, stem_index: dict[str, StemInfo]
) -> tuple[list[str], int]:
    """Return (errors, entry_count) for the answer key against the index."""
    if not isinstance(entries, list):
        raise ValueError("the answer key is not a JSON list")

    errors: list[str] = []
    for position, entry in enumerate(entries, start=1):
        label = f"entry #{position}"
        if not isinstance(entry, dict):
            errors.append(f"error: {label} is not a JSON object")
            continue

        stem_id = entry.get("stem_id")
        if isinstance(stem_id, str) and stem_id:
            label = f'stem "{stem_id}"'
        stem = stem_index.get(stem_id) if isinstance(stem_id, str) else None
        if stem is None:
            errors.append(f"error: {label} is not in the stems file")
            continue

        valid_letters = stem["valid_letters"]
        real_answer = stem["correct_answer"]
        answer = entry.get("correct_answer")
        if isinstance(answer, str) and answer:
            if answer not in valid_letters:
                rng = option_range(valid_letters)
                errors.append(
                    f'error: {label} answer "{answer}" is outside its own '
                    f"option range {rng}"
                )
            elif answer != real_answer:
                errors.append(
                    f'error: {label} has correct_answer "{answer}", but '
                    f'its own stem records correct_answer "{real_answer}"'
                )

        feedback = entry.get("feedback_by_distractor")
        if isinstance(feedback, dict):
            for letter in feedback:
                if isinstance(letter, str) and letter in valid_letters:
                    continue
                shown = letter if isinstance(letter, str) else repr(letter)
                rng = option_range(valid_letters)
                errors.append(
                    f'error: {label} answer "{shown}" is outside its own '
                    f"option range {rng}"
                )

    count = len(entries)
    return errors, count


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="answer_key_check.py",
        description=(
            "Check an answer-key JSON file against a stems JSON file: every "
            "stem id resolves and every answer letter is a real, matching "
            "option. Writes no files."
        ),
    )
    parser.add_argument("key", metavar="KEY", help="path to the answer-key JSON")
    parser.add_argument("stems", metavar="STEMS", help="path to the stems JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        key_data = load_json(Path(args.key))
        stems_data = load_json(Path(args.stems))
        stem_index = build_stem_index(stems_data)
        errors, count = check_answer_key(key_data, stem_index)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"answer_key_check.py: error: {exc}", file=sys.stderr)
        return 2

    for message in errors:
        print(message)
    print(f"entries={count} errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
