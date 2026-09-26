"""
ID: X-S3-03
Title: Citation fidelity check
Stage: S3
Purpose: Check that every claim's quoted phrase is an exact substring of
    its named source file, across a whole folder of admitted sources.
Usage: python3 scripts/s3/citation_fidelity_check.py --help
    In a shell: python3 scripts/s3/citation_fidelity_check.py CITATIONS.json
    SOURCES_DIR
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: CITATIONS.json, a list of objects with a claim id, a source id
    and a quoted phrase. SOURCES_DIR, a folder of admitted "SRC-*.md"
    source files, read-only.
Outputs: One line per citation ("pass ..." or "fail ..."), then a
    summary line, all printed to standard output.

This is a plainer version of scripts/s1/quote_check.py's idea, applied
at a chapter's larger scale: many claims checked against a shared
folder of several admitted sources, instead of one distillate's quote
bank checked against one source. It is a bare exact-substring check
only. It carries none of that script's typography normalization, its
case-insensitive option, or its bracket-delimited fragment matching: a
quote either sits in the source file's text unchanged, or it does not.

This script shows only that a quote's text is present in the named
source. It never checks whether the quote is true, whether it supports
the claim it is attached to, or whether the right source was named.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NamedTuple

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "citation_fidelity_check.py: this script needs Python 3.10 or "
        f"newer, but this is {sys.version_info.major}."
        f"{sys.version_info.minor}. Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000


class Citation(NamedTuple):
    """One claim id, source id and quoted phrase, from CITATIONS.json."""

    claim_id: str
    source_id: str
    quote: str


def load_json(path: Path) -> Any:
    """Read and parse one JSON file as UTF-8 text; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def load_citations(data: Any) -> list[Citation]:
    """Return a list of Citation entries, in file order."""
    if not isinstance(data, list):
        raise ValueError("CITATIONS.json is not a JSON list")
    citations: list[Citation] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"citation entry #{position} is not a JSON object")
        claim_id = entry.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"citation entry #{position} has no claim_id")
        source_id = entry.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f'citation entry "{claim_id}" has no source_id')
        quote = entry.get("quote")
        if not isinstance(quote, str) or not quote:
            raise ValueError(f'citation entry "{claim_id}" has no quote')
        citations.append(Citation(claim_id, source_id, quote))
    return citations


def find_source_files(sources_dir: Path) -> dict[str, Path]:
    """Map each admitted source id (its file stem) to its file path.

    Raises if the folder holds zero "SRC-*.md" files, so a stale path or
    an empty folder fails loudly instead of reporting every citation as
    a mismatch.
    """
    if not sources_dir.is_dir():
        raise ValueError(f"{sources_dir} is not a directory")
    files = sorted(sources_dir.glob("SRC-*.md"))
    if not files:
        raise ValueError("no admitted sources found in SOURCES_DIR")
    return {path.stem: path for path in files}


def read_source_text(path: Path) -> str:
    """Read one source file as UTF-8 text (errors replaced), capped."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    with open(path, "rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        print(
            f"citation_fidelity_check.py: {path}: skipping bytes past " f"{MAX_BYTES}",
            file=sys.stderr,
        )
        raw = raw[:MAX_BYTES]
    return raw.decode("utf-8", errors="replace")


def check_citations(citations: list[Citation], sources: dict[str, Path]) -> list[str]:
    """Return one "pass ..." or "fail ..." line per citation, in order."""
    lines: list[str] = []
    cache: dict[str, str] = {}
    for citation in citations:
        path = sources.get(citation.source_id)
        if path is None:
            lines.append(
                f'fail quote-{citation.claim_id}: source "{citation.source_id}" '
                "not present in SOURCES_DIR"
            )
            continue
        if citation.source_id not in cache:
            cache[citation.source_id] = read_source_text(path)
        text = cache[citation.source_id]
        if citation.quote in text:
            lines.append(f"pass quote-{citation.claim_id}: found in {path.name}")
        else:
            lines.append(
                f"fail quote-{citation.claim_id}: not found verbatim in {path.name}"
            )
    return lines


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="citation_fidelity_check.py",
        description=(
            "Check that every claim's quoted phrase is an exact substring "
            "of its named source file, across a shared folder of admitted "
            "sources. A bare substring check, with no typography "
            "normalization. Writes no files."
        ),
    )
    parser.add_argument(
        "citations", metavar="CITATIONS", help="path to the citations JSON file"
    )
    parser.add_argument(
        "sources_dir",
        metavar="SOURCES_DIR",
        help="folder of admitted SRC-*.md source files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints one line per citation, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        citations = load_citations(load_json(Path(args.citations)))
        sources = find_source_files(Path(args.sources_dir))
        lines = check_citations(citations, sources)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"citation_fidelity_check.py: error: {exc}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    failed = sum(1 for line in lines if line.startswith("fail "))
    print(f"quotes={len(lines)} pass={len(lines) - failed} fail={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
