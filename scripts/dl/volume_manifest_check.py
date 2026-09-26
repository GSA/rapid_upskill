"""
ID: X-DL-02
Title: Volume manifest check
Stage: DL
Purpose: Check a proposed chapter-to-volume manifest for an off-convention
    chapter id, a section id that does not reset at its own chapter's
    boundary, and a volume whose chapters are not in numeral-aware order.
Usage: python3 scripts/dl/volume_manifest_check.py --help
    In a shell: python3 scripts/dl/volume_manifest_check.py MANIFEST.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A volume-manifest JSON file: a top-level "volumes" list. Each
    volume is a JSON object with a "volume" number and a "chapters"
    list. Each chapter is a JSON object with an "id" string (the
    expected "<part>.<chapter>" pattern, such as "3.9") and a
    "sections" list holding its own section ids.
Outputs: One line per finding, then a summary line, all printed to
    standard output.

A manifest whose basic shape does not match this input contract (the
top-level "volumes" list missing, a volume with no "chapters" list, or
a chapter entry that is not a JSON object) is a usage error (exit 2),
not a finding; the two finding kinds below only run once a chapter's
own shape can actually be read.

Errors (exit 1): a chapter whose "id" does not match the expected
"<part>.<chapter>" pattern. An off-convention id is flagged here, never
silently skipped; this is the one behavior change this script makes
from a real, confirmed bug in comparable chapter-filename parsing,
which moved on to the next file instead of reporting the one it could
not parse, quietly losing a chapter from a volume. The other finding:
a section id that does not start with its own chapter's id, evidence
that section numbering did not reset at the chapter boundary. A
chapter whose own id fails the pattern check is skipped for the
remaining checks on that one chapter, the same way a bad entry is
skipped elsewhere in this guide's scripts, so it does not also crowd
out the ordering warning below with a value it has no numeral-aware
sort key for. A chapter's own "sections" entry that is missing or is
not a JSON list is treated as holding no sections, so it contributes
no section-reset finding of its own.

Warnings (exit 0, never change the exit code): within one volume, the
chapters whose ids passed the pattern check are not in numeral-aware
order (so a chapter id such as "3.10" must sort after "3.9", not
before "3.2", the way a plain text sort would place it).
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "volume_manifest_check.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
CHAPTER_ID_PATTERN = re.compile(r"^[0-9]+\.[0-9]+$")


def load_json(path: Path) -> Any:
    """Read and parse a JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def numeral_key(chapter_id: str) -> tuple[int, int]:
    """Return the (part, chapter) integer sort key for a matched chapter id.

    Only call this on an id that already passed CHAPTER_ID_PATTERN, so the
    split and the two int() conversions always succeed.
    """
    part, chapter = chapter_id.split(".")
    return int(part), int(chapter)


def check_manifest(data: Any) -> tuple[list[str], list[str], int, int]:
    """Return (errors, warnings, volume_count, chapter_count)."""
    if not isinstance(data, dict):
        raise ValueError("the manifest is not a JSON object")
    volumes = data.get("volumes")
    if not isinstance(volumes, list) or not volumes:
        raise ValueError("'volumes' is missing, empty, or is not a JSON list")

    errors: list[str] = []
    warnings: list[str] = []
    chapter_count = 0

    for vpos, volume in enumerate(volumes, start=1):
        if not isinstance(volume, dict):
            raise ValueError(f"volume #{vpos} is not a JSON object")
        chapters = volume.get("chapters")
        if not isinstance(chapters, list) or not chapters:
            raise ValueError(f"volume #{vpos} has no 'chapters' list")
        number = volume.get("volume")
        if isinstance(number, (int, float)) and not isinstance(number, bool):
            vlabel = f"volume {number!r}"
        else:
            vlabel = f"volume #{vpos}"

        ordered_ids: list[str] = []
        for cpos, chapter in enumerate(chapters, start=1):
            chapter_count += 1
            if not isinstance(chapter, dict):
                raise ValueError(f"{vlabel} chapter #{cpos} is not a JSON object")
            label = f"{vlabel} chapter #{cpos}"
            chapter_id = chapter.get("id")
            if isinstance(chapter_id, str) and chapter_id:
                label = f"{vlabel} chapter {chapter_id!r}"
            if not (
                isinstance(chapter_id, str) and CHAPTER_ID_PATTERN.match(chapter_id)
            ):
                errors.append(
                    f"off-convention: {label} has id {chapter_id!r}, expected "
                    "the pattern '<part>.<chapter>' such as '3.9'"
                )
                continue
            ordered_ids.append(chapter_id)

            sections = chapter.get("sections")
            if not isinstance(sections, list):
                continue
            for section_id in sections:
                if not (
                    isinstance(section_id, str) and section_id.startswith(chapter_id)
                ):
                    errors.append(
                        f"no-reset: {label} has section {section_id!r}, which "
                        f"does not start with chapter id {chapter_id!r}"
                    )

        if ordered_ids and ordered_ids != sorted(ordered_ids, key=numeral_key):
            got = ", ".join(ordered_ids)
            expected = ", ".join(sorted(ordered_ids, key=numeral_key))
            warnings.append(
                f"order: {vlabel} chapters are not in numeral-aware order: "
                f"got {got}; expected {expected}"
            )

    return errors, warnings, len(volumes), chapter_count


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="volume_manifest_check.py",
        description=(
            "Check a chapter-to-volume manifest's chapter ids, section-id "
            "resets and numeral-aware chapter order. Writes no files."
        ),
    )
    parser.add_argument(
        "manifest", metavar="MANIFEST", help="path to the volume-manifest JSON"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = load_json(Path(args.manifest))
        errors, warnings, volume_count, chapter_count = check_manifest(data)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"volume_manifest_check.py: error: {exc}", file=sys.stderr)
        return 2
    for message in errors:
        print(f"error {message}")
    for message in warnings:
        print(f"warning {message}")
    print(
        f"volumes={volume_count} chapters={chapter_count} "
        f"errors={len(errors)} warnings={len(warnings)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
