"""
ID: X-S1-04
Title: Conversion quality check
Stage: S1
Purpose: Check a converted Markdown file against a second, independently
    produced plain-text copy of the same document, to catch common
    conversion problems before anyone reads the converted copy.
Usage: python3 scripts/s1/check_conversion.py ORIGINAL CONVERTED
    [--pages N] [--ratio-low X] [--ratio-high Y] [--expect TEXT]
    [--allow-non-latin]
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: ORIGINAL, a plain-text copy of the document obtained by a route
    other than the converter under test (for example the visible text of
    an HTML page, or a PDF tool's own plain-text output). CONVERTED, the
    converter's Markdown output for the same document.
Outputs: One line per check that applies, printed to standard output, in
    the form "pass|soft|hard NAME detail". A failing hard check sets the
    exit code to 1; a soft check never changes it.

Words are whitespace-separated tokens, counted after removing Markdown
marks: a leading front-matter block, fenced code-block marker lines,
list markers, link and image brackets, and the characters # ` * _ >.
The word count feeds the ratio, words-per-page and repeated-line checks.

Checks, one line each that applies, in this order:

- empty (hard): the converted file has no words.
- ratio (hard): converted words divided by original words falls outside
  --ratio-low to --ratio-high (default 0.85 to 1.15).
- garble (hard): the Unicode replacement character (U+FFFD) makes up
  more than 1 in 100 characters of the converted file.
- character-mix (hard; the whole check is skipped with
  --allow-non-latin): ASCII letters and digits make up less than 0.45 of
  the non-space characters of the converted file.
- repeats (soft): a line of at least 4 words appears 3 or more times in
  the converted file.
- expected-text (soft; printed only when --expect is given at least
  once): reports how many of the given strings do not occur in the
  converted file.
- words-per-page (soft; printed only when --pages is given): the
  converted word count divided by the page count falls outside 50 to
  1,200 words per page.

A passing run is a sign that the conversion did not lose, truncate or
garble the text. It is not a check on the source's content, and it does
not show that the meaning of a passage survived the conversion.
"""

import argparse
import os
import re
import sys
from typing import NamedTuple

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "check_conversion.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
EXCERPT_CHARS = 60
DEFAULT_RATIO_LOW = 0.85
DEFAULT_RATIO_HIGH = 1.15
GARBLE_SHARE_LIMIT = 0.01
LATIN_SHARE_MIN = 0.45
REPEAT_MIN_WORDS = 4
REPEAT_MIN_COUNT = 3
PAGE_WORDS_LOW = 50
PAGE_WORDS_HIGH = 1200
REPLACEMENT_CHAR = "\ufffd"

_FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---[ \t]*\n?", re.S)
_FENCE_LINE_RE = re.compile(r"^[ \t]{0,3}(?:`{3,}|~{3,})[^\n]*$", re.M)
_IMAGE_RE = re.compile(r"!\[([^\]\n]*)\]\([^)\n]*\)")
_LINK_RE = re.compile(r"\[([^\]\n]*)\]\([^)\n]*\)")
_LIST_MARK_RE = re.compile(r"^[ \t]{0,3}(?:[-+*][ \t]+|[0-9]{1,9}[.)][ \t]+)", re.M)
_MD_CHAR_RE = re.compile(r"[#`*_>]")


class Check(NamedTuple):
    """One check result, as printed: "status name detail"."""

    status: str
    name: str
    detail: str


def strip_markdown(text: str) -> str:
    """Remove the Markdown marks this script knows about; keep the words."""
    text = _FRONT_MATTER_RE.sub("", text, count=1)
    text = _FENCE_LINE_RE.sub("", text)
    text = _IMAGE_RE.sub(lambda m: m.group(1), text)
    text = _LINK_RE.sub(lambda m: m.group(1), text)
    text = _LIST_MARK_RE.sub("", text)
    text = _MD_CHAR_RE.sub("", text)
    return text


def word_list(text: str) -> list[str]:
    """Whitespace-separated tokens of text, after removing Markdown marks."""
    return strip_markdown(text).split()


def excerpt(text: str) -> str:
    """The first EXCERPT_CHARS characters of text, ascii()-escaped."""
    return ascii(text[:EXCERPT_CHARS])


def read_capped(path: str) -> str:
    """Read path as UTF-8 text (errors replaced), capped at MAX_BYTES."""
    if os.path.islink(path):
        raise ValueError(f"{path}: refuses to follow a symlink")
    with open(path, "rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        print(
            f"check_conversion.py: {path}: skipping bytes past {MAX_BYTES}",
            file=sys.stderr,
        )
        raw = raw[:MAX_BYTES]
    return raw.decode("utf-8", errors="replace")


def check_empty(converted_words: list[str]) -> Check:
    """hard: the converted file has no words."""
    if not converted_words:
        return Check("hard", "empty", "the converted file has no words")
    return Check(
        "pass", "empty", f"the converted file has {len(converted_words)} words"
    )


def check_ratio(
    original_words: list[str], converted_words: list[str], low: float, high: float
) -> Check:
    """hard: converted words divided by original words falls outside low-high."""
    orig_n, conv_n = len(original_words), len(converted_words)
    if orig_n == 0:
        detail = "the original file has no words to compare against"
        return Check("hard", "ratio", detail)
    ratio = conv_n / orig_n
    detail = f"{ratio:.2f} ({conv_n} of {orig_n} words), band {low:g}-{high:g}"
    status = "pass" if low <= ratio <= high else "hard"
    return Check(status, "ratio", detail)


def check_garble(converted_text: str) -> Check:
    """hard: replacement characters above 1 in 100 characters."""
    total = len(converted_text)
    if total == 0:
        return Check("hard", "garble", "the converted file has no characters")
    bad = converted_text.count(REPLACEMENT_CHAR)
    share = bad / total
    detail = f"{bad} replacement character(s) in {total} characters ({share:.2%})"
    status = "pass" if share <= GARBLE_SHARE_LIMIT else "hard"
    return Check(status, "garble", detail)


def check_character_mix(converted_text: str, allow_non_latin: bool) -> Check | None:
    """hard, unless skipped: ASCII letters and digits under 0.45 of non-space."""
    if allow_non_latin:
        return None
    non_space = [c for c in converted_text if not c.isspace()]
    if not non_space:
        return Check("hard", "character-mix", "the converted file has no characters")
    latin = sum(1 for c in non_space if c.isascii() and c.isalnum())
    share = latin / len(non_space)
    detail = f"{share:.2f} of non-space characters are ASCII letters or digits"
    status = "pass" if share >= LATIN_SHARE_MIN else "hard"
    return Check(status, "character-mix", detail)


def check_repeats(converted_text: str) -> Check:
    """soft: a line of at least REPEAT_MIN_WORDS words repeated 3+ times."""
    counts: dict[str, int] = {}
    order: list[str] = []
    for raw_line in converted_text.split("\n"):
        line = " ".join(raw_line.split())
        if not line or len(word_list(line)) < REPEAT_MIN_WORDS:
            continue
        if line not in counts:
            order.append(line)
        counts[line] = counts.get(line, 0) + 1
    repeated = [
        (line, counts[line]) for line in order if counts[line] >= REPEAT_MIN_COUNT
    ]
    if not repeated:
        detail = f"no line of at least {REPEAT_MIN_WORDS} words repeats 3+ times"
        return Check("pass", "repeats", detail)
    line, count = repeated[0]
    detail = (
        f"{len(repeated)} line(s) repeat 3 or more times; "
        f"first, {count} times: {excerpt(line)}"
    )
    return Check("soft", "repeats", detail)


def check_expected_text(converted_text: str, expect: list[str]) -> Check | None:
    """soft, printed only when --expect is given: strings missing from converted."""
    if not expect:
        return None
    missing = [text for text in expect if text not in converted_text]
    if not missing:
        detail = f"all {len(expect)} given string(s) were found"
        return Check("pass", "expected-text", detail)
    shown = ", ".join(excerpt(text) for text in missing)
    detail = f"{len(missing)} of {len(expect)} given string(s) not found: {shown}"
    return Check("soft", "expected-text", detail)


def check_words_per_page(converted_words: list[str], pages: int | None) -> Check | None:
    """soft, printed only when --pages is given: words per page outside 50-1200."""
    if pages is None:
        return None
    if pages <= 0:
        raise ValueError("--pages must be a positive integer")
    per_page = len(converted_words) / pages
    detail = (
        f"{per_page:.1f} words per page "
        f"({len(converted_words)} words, {pages} pages)"
    )
    in_band = PAGE_WORDS_LOW <= per_page <= PAGE_WORDS_HIGH
    return Check("pass" if in_band else "soft", "words-per-page", detail)


def run_checks(
    original_text: str,
    converted_text: str,
    *,
    ratio_low: float = DEFAULT_RATIO_LOW,
    ratio_high: float = DEFAULT_RATIO_HIGH,
    pages: int | None = None,
    expect: list[str] | None = None,
    allow_non_latin: bool = False,
) -> list[Check]:
    """Run every check that applies and return the results, in order."""
    original_words = word_list(original_text)
    converted_words = word_list(converted_text)
    checks = [
        check_empty(converted_words),
        check_ratio(original_words, converted_words, ratio_low, ratio_high),
        check_garble(converted_text),
        check_character_mix(converted_text, allow_non_latin),
        check_repeats(converted_text),
        check_expected_text(converted_text, expect or []),
        check_words_per_page(converted_words, pages),
    ]
    return [check for check in checks if check is not None]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="check_conversion.py",
        description=(
            "Check a converted Markdown file against a plain-text copy of "
            "the original. Prints one line per check; writes no files."
        ),
    )
    parser.add_argument("original", metavar="ORIGINAL", help="plain-text original file")
    parser.add_argument(
        "converted", metavar="CONVERTED", help="converted Markdown file"
    )
    parser.add_argument(
        "--pages",
        type=int,
        metavar="N",
        help="page count, for the words-per-page check",
    )
    parser.add_argument(
        "--ratio-low",
        type=float,
        default=DEFAULT_RATIO_LOW,
        metavar="X",
        help=f"low end of the word-ratio band (default {DEFAULT_RATIO_LOW:g})",
    )
    parser.add_argument(
        "--ratio-high",
        type=float,
        default=DEFAULT_RATIO_HIGH,
        metavar="Y",
        help=f"high end of the word-ratio band (default {DEFAULT_RATIO_HIGH:g})",
    )
    parser.add_argument(
        "--expect",
        action="append",
        metavar="TEXT",
        default=[],
        help="a string that must occur in the converted file; may repeat",
    )
    parser.add_argument(
        "--allow-non-latin",
        action="store_true",
        help="skip the character-mix check",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point; prints the check lines, returns an exit code."""
    args = build_parser().parse_args(argv)
    try:
        original_text = read_capped(args.original)
        converted_text = read_capped(args.converted)
        checks = run_checks(
            original_text,
            converted_text,
            ratio_low=args.ratio_low,
            ratio_high=args.ratio_high,
            pages=args.pages,
            expect=args.expect,
            allow_non_latin=args.allow_non_latin,
        )
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(f"check_conversion.py: error: {exc}", file=sys.stderr)
        return 2
    for check in checks:
        print(f"{check.status} {check.name} {check.detail}")
    return 1 if any(check.status == "hard" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
