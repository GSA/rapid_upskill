"""
ID: X-S5-03
Title: Format rules check
Stage: S5
Purpose: Check a stems JSON file against this guide's own format rules for
    a finished, assembled test question: single-best-answer only, no
    negative stem, no "all of the above" or "none of the above" option, a
    distractor named to exactly one misconception, three to four
    distractors, and option lengths that do not give the answer away.
Usage: python3 scripts/s5/format_rules_check.py --help
    In a shell: python3 scripts/s5/format_rules_check.py STEMS.json
    [--include-broken-examples]
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A stems JSON file: a list of stem objects, each with stem_id,
    difficulty, cognitive_level, bloom_level, concept_item_ids,
    stem_content, correct_answer, correct_answer_text, distractors (a
    list of option, text and misconception) and explanation. A stem may
    also carry "broken_on_purpose": true, this guide's own marker for a
    fixture kept only to demonstrate a failing check; it is never part
    of a real bank.
Outputs: One line per finding, then a summary line, all printed to
    standard output.

This script checks format and wording only. It never judges whether a
distractor's misconception is the right one for the concept, or whether
the correct answer is actually correct; a person still reviews that.

Errors (exit 1): a stem entry that is not a JSON object; a stem missing
`stem_content`, `correct_answer`, `correct_answer_text` or
`distractors`; a duplicate `stem_id`; a distractor entry that is not a
JSON object; `stem_content` reading as more than one correct answer (a
fixed list of phrases, such as "select all" or "choose two": a
single-best-answer violation); `stem_content` using a banned
negative-stem word from a fixed list, matching the stricter source
guide's own list exactly: "no", "not", "least", "except", "worst"; an
"all of the above" or "none of the above" option text, on a distractor
or on the correct answer; a distractor missing its own `misconception`
field; fewer than 3 or more than 4 distractors; an option whose text
length is less than half or more than double the correct answer's own
length (the parallel-length check). Prints one line per finding, then a
summary (`stems=N errors=E`).

By default, a stem marked `broken_on_purpose` is skipped and noted, not
checked, and does not count toward N or E; `--include-broken-examples`
checks it too, the same as any other stem. This is this guide's own
suggested convention, not one the project notes describe. It lets this
guide's own sample bank keep its one deliberately broken fixture in the
same file as the two real stems, alongside them as the shared fixture
requires, without a plain, everyday run of this script over that real
file ever failing because of it.
"""

import argparse
import json
import string
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "format_rules_check.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

NEGATIVE_WORDS = ("no", "not", "least", "except", "worst")
MULTI_ANSWER_PHRASES = (
    "select all",
    "choose all",
    "all that apply",
    "select two",
    "choose two",
    "more than one correct answer",
    "mark all correct",
)
ALL_OR_NONE_PHRASES = ("all of the above", "none of the above")
MIN_DISTRACTORS, MAX_DISTRACTORS = 3, 4
MAX_BYTES = 5_000_000
_PUNCT_TO_SPACE = str.maketrans(string.punctuation, " " * len(string.punctuation))


def load_stems(path: Path) -> Any:
    """Read and parse the stems file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def _tokens(text: str) -> list[str]:
    """Lowercase word tokens, splitting on punctuation and whitespace."""
    return text.translate(_PUNCT_TO_SPACE).lower().split()


def _negative_words_used(stem_content: str) -> list[str]:
    """Banned negative-stem words actually present, in NEGATIVE_WORDS order."""
    found = set(_tokens(stem_content))
    return [word for word in NEGATIVE_WORDS if word in found]


def _multi_answer_phrase(stem_content: str) -> str | None:
    """The first multi-answer phrase found in stem_content, or None."""
    lowered = stem_content.lower()
    for phrase in MULTI_ANSWER_PHRASES:
        if phrase in lowered:
            return phrase
    return None


def _is_all_or_none(text: str) -> bool:
    """True if text reads as an "all/none of the above" option."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in ALL_OR_NONE_PHRASES)


def check_one_stem(stem: dict[str, Any], label: str) -> list[str]:
    """Return the finding lines for one already-confirmed stem object."""
    errors: list[str] = []

    stem_content = stem.get("stem_content")
    if not isinstance(stem_content, str) or not stem_content:
        errors.append(f"missing-field: {label} has no 'stem_content'")
        stem_content = None

    if stem_content is not None:
        phrase = _multi_answer_phrase(stem_content)
        if phrase is not None:
            errors.append(
                f"multi-answer: {label} stem_content reads as more than one "
                f"correct answer (phrase: '{phrase}')"
            )
        negative_words = _negative_words_used(stem_content)
        if negative_words:
            shown = ", ".join(negative_words)
            errors.append(
                f"negative-stem: {label} stem_content uses a banned word: {shown}"
            )

    correct_answer = stem.get("correct_answer")
    if not isinstance(correct_answer, str) or not correct_answer:
        errors.append(f"missing-field: {label} has no 'correct_answer'")

    correct_text = stem.get("correct_answer_text")
    if not isinstance(correct_text, str) or not correct_text:
        errors.append(f"missing-field: {label} has no 'correct_answer_text'")
        correct_text = None
    elif _is_all_or_none(correct_text):
        errors.append(f"all-or-none: {label} correct_answer_text is '{correct_text}'")

    distractors = stem.get("distractors")
    if not isinstance(distractors, list):
        errors.append(f"missing-field: {label} has no 'distractors'")
        distractors = []

    good_distractors: list[dict[str, Any]] = []
    for position, distractor in enumerate(distractors, start=1):
        dlabel = f"{label} distractor #{position}"
        if not isinstance(distractor, dict):
            errors.append(f"bad-distractor: {dlabel} is not a JSON object")
            continue
        option = distractor.get("option")
        if isinstance(option, str) and option:
            dlabel = f"{label} distractor {option}"
        text = distractor.get("text")
        if not isinstance(text, str) or not text:
            errors.append(f"missing-field: {dlabel} has no 'text'")
            text = None
        misconception = distractor.get("misconception")
        if not isinstance(misconception, str) or not misconception:
            errors.append(f"missing-misconception: {dlabel} has no misconception")
        if text is not None:
            if _is_all_or_none(text):
                errors.append(f"all-or-none: {dlabel} text is '{text}'")
            good_distractors.append({"label": dlabel, "text": text})

    if not (MIN_DISTRACTORS <= len(distractors) <= MAX_DISTRACTORS):
        errors.append(
            f"distractor-count: {label} has {len(distractors)} distractors, "
            f"needs {MIN_DISTRACTORS} to {MAX_DISTRACTORS}"
        )

    if correct_text is not None:
        clen = len(correct_text)
        for entry in good_distractors:
            dlen = len(entry["text"])
            if dlen < clen / 2 or dlen > clen * 2:
                errors.append(
                    f"parallel-length: {entry['label']} text length {dlen} is not "
                    f"within half to double of the correct answer's length {clen}"
                )

    return errors


def check_stems(
    data: Any, include_broken: bool
) -> tuple[list[str], list[str], int]:
    """Return (notes, errors, stems_checked) for the whole stems list."""
    if not isinstance(data, list):
        raise ValueError("the stems file is not a JSON list")

    notes: list[str] = []
    errors: list[str] = []
    seen_ids: dict[str, bool] = {}
    checked = 0

    for position, stem in enumerate(data, start=1):
        label = f"stem #{position}"
        if not isinstance(stem, dict):
            errors.append(f"bad-stem: {label} is not a JSON object")
            continue

        stem_id = stem.get("stem_id")
        if isinstance(stem_id, str) and stem_id:
            label = f'stem "{stem_id}"'
            if stem_id in seen_ids:
                errors.append(f"duplicate-id: stem id '{stem_id}' is used twice")
            else:
                seen_ids[stem_id] = True

        if bool(stem.get("broken_on_purpose", False)) and not include_broken:
            notes.append(
                f"note: {label} is marked broken_on_purpose; skipped "
                "(rerun with --include-broken-examples to check it)"
            )
            continue

        checked += 1
        errors.extend(check_one_stem(stem, label))

    return notes, errors, checked


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="format_rules_check.py",
        description=(
            "Check a stems JSON file against this guide's own format rules: "
            "single-best-answer only, no negative stem, no all/none of the "
            "above, a named misconception per distractor, three to four "
            "distractors, and parallel option length. Writes no files."
        ),
    )
    parser.add_argument("stems", metavar="STEMS", help="path to the stems JSON")
    parser.add_argument(
        "--include-broken-examples",
        action="store_true",
        help=(
            "also check a stem marked broken_on_purpose (skipped by default); "
            "use this to see this guide's own sample break-on-purpose fixture "
            "fail the checks"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = load_stems(Path(args.stems))
        notes, errors, checked = check_stems(data, args.include_broken_examples)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"format_rules_check.py: error: {exc}", file=sys.stderr)
        return 2
    for message in notes:
        print(message)
    for message in errors:
        print(f"error {message}")
    print(f"stems={checked} errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
