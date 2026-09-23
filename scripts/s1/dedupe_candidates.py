"""
ID: X-S1-02
Title: Deduplicate search candidates
Purpose: Group candidate search records that likely describe the same
    document, keep the most complete record from each group, and flag
    records older than a minimum year for a person to review.
Usage: python3 scripts/s1/dedupe_candidates.py CANDIDATES.json
    [--min-year Y] [--out FILE --write]
Dependencies: stdlib
Writes files: yes
License: CC0-1.0
Inputs: A JSON file holding a list of candidate records. Each record has
    title, url and year, plus the optional fields identifier, authors,
    summary and source_type.
Outputs: One line per merge and, when --min-year is given, one line per
    flagged record, printed to standard output; the deduplicated list,
    written to --out only with --write.

Records are grouped by, in this order: identifier (lower-cased, with a
trailing version suffix such as "v2" removed); normalized URL (scheme and a
leading "www." dropped, host lower-cased, tracking parameters, fragment and
a trailing slash removed); normalized title plus first author plus year. The
URL and title rules are this guide's own choice, offered as starting values;
calibrate them on your own material. Tracking parameters are treated as any
name starting with "utm_" or matching "ref", "fbclid", "gclid", "mc_cid" or
"mc_eid"; the project notes name no fixed list. Within a group, the record
with the most filled fields is kept.

--min-year adds "too_old": true to a record; it never drops a record, so a
person still decides. Exit 0 always, unless the input cannot be read; exit 2
for a usage or input error, printed as one line with no traceback.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "dedupe_candidates.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
REQUIRED_FIELDS = ("title", "url", "year")
_VERSION_SUFFIX_RE = re.compile(r"[-_ ]?v\d+$", re.IGNORECASE)
_TRACKING_PREFIXES = ("utm_",)
_TRACKING_NAMES = {"ref", "fbclid", "gclid", "mc_cid", "mc_eid"}


@dataclass
class MergeEvent:
    """One decision made while grouping candidate records."""

    kept_title: str
    dropped_title: str
    rule: str


def normalize_identifier(identifier: str) -> str:
    """Lower-case an identifier and drop a trailing version suffix."""
    value = identifier.strip().lower()
    return _VERSION_SUFFIX_RE.sub("", value)


def normalize_title(title: str) -> str:
    """Case-fold a title and collapse whitespace runs to one space."""
    return " ".join(title.strip().lower().split())


def _is_tracking_param(name: str) -> bool:
    """Report whether a URL query parameter name looks like a tracking tag."""
    lowered = name.lower()
    return lowered in _TRACKING_NAMES or lowered.startswith(_TRACKING_PREFIXES)


def _normalize_url(url: str) -> str:
    """Normalize a URL for duplicate matching (see the module docstring)."""
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    pairs = [
        (name, value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
        if not _is_tracking_param(name)
    ]
    normalized = host + path
    if pairs:
        normalized += "?" + urlencode(pairs)
    return normalized.lower()


def _identifier_key(record: dict[str, Any]) -> str | None:
    """The record's normalized identifier, or None when it has none."""
    identifier = record.get("identifier")
    if not identifier or not str(identifier).strip():
        return None
    return normalize_identifier(str(identifier))


def _url_key(record: dict[str, Any]) -> str | None:
    """The record's normalized URL, or None when it has none."""
    url = record.get("url")
    if not url or not str(url).strip():
        return None
    return _normalize_url(str(url))


def _title_author_year_key(record: dict[str, Any]) -> tuple[str, str, Any]:
    """A key of (normalized title, normalized first author, year)."""
    title = normalize_title(str(record.get("title", "")))
    authors = record.get("authors") or []
    first_author = str(authors[0]).strip().lower() if authors else ""
    return (title, first_author, record.get("year"))


def _filled_field_count(record: dict[str, Any]) -> int:
    """Count fields with a non-empty value; too_old does not count."""
    count = 0
    for key, value in record.items():
        if key == "too_old":
            continue
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (list, dict)) and not value:
            continue
        count += 1
    return count


def _match_rule(existing: dict[str, Any], record: dict[str, Any]) -> str:
    """Name the tier at which two records were judged to be duplicates."""
    existing_id = _identifier_key(existing)
    if existing_id is not None and existing_id == _identifier_key(record):
        return "identifier"
    existing_url = _url_key(existing)
    if existing_url is not None and existing_url == _url_key(record):
        return "url"
    return "title-author-year"


def _find_match(kept: list[dict[str, Any]], record: dict[str, Any]) -> int | None:
    """Return the index in kept that record duplicates, or None."""
    record_id = _identifier_key(record)
    if record_id is not None:
        for index, existing in enumerate(kept):
            if _identifier_key(existing) == record_id:
                return index
    record_url = _url_key(record)
    if record_url is not None:
        for index, existing in enumerate(kept):
            if _url_key(existing) == record_url:
                return index
    record_key = _title_author_year_key(record)
    for index, existing in enumerate(kept):
        if _title_author_year_key(existing) == record_key:
            return index
    return None


def dedupe(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[MergeEvent]]:
    """Group likely-duplicate records; keep the fullest one from each group.

    Records are compared against the groups formed so far, in the order
    given. The return value is (kept records, one MergeEvent per record
    dropped or replaced).
    """
    kept: list[dict[str, Any]] = []
    events: list[MergeEvent] = []
    for record in records:
        match_index = _find_match(kept, record)
        if match_index is None:
            kept.append(record)
            continue
        existing = kept[match_index]
        rule = _match_rule(existing, record)
        if _filled_field_count(record) > _filled_field_count(existing):
            events.append(
                MergeEvent(
                    str(record.get("title", "")), str(existing.get("title", "")), rule
                )
            )
            kept[match_index] = record
        else:
            events.append(
                MergeEvent(
                    str(existing.get("title", "")), str(record.get("title", "")), rule
                )
            )
    return kept, events


def flag_too_old(
    records: list[dict[str, Any]], min_year: int | None
) -> list[dict[str, Any]]:
    """Add too_old: true to records from before min_year; never drop one."""
    if min_year is None:
        return records
    for record in records:
        year = record.get("year")
        if isinstance(year, int) and year < min_year:
            record["too_old"] = True
    return records


def _check_not_symlink(path: Path) -> None:
    """Refuse to read through a symlink."""
    if path.is_symlink():
        raise ValueError(f"refusing to follow a symlink: {path}")


def _read_capped(path: Path, limit: int = MAX_BYTES) -> str:
    """Read a file as UTF-8 text, replacing bad bytes, capped at limit."""
    raw = path.read_bytes()
    if len(raw) > limit:
        print(
            f"dedupe_candidates.py: reading only the first {limit} bytes of {path}",
            file=sys.stderr,
        )
        raw = raw[:limit]
    return raw.decode("utf-8", errors="replace")


def load_records(path: Path) -> list[dict[str, Any]]:
    """Read and validate a JSON list of candidate records."""
    _check_not_symlink(path)
    parsed = json.loads(_read_capped(path))
    if not isinstance(parsed, list):
        raise ValueError(f"{path}: expected a JSON list of candidate records")
    records: list[dict[str, Any]] = []
    for index, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: record {index} is not a JSON object")
        for key in REQUIRED_FIELDS:
            if key not in item:
                raise ValueError(f"{path}: record {index} is missing '{key}'")
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError(f"{path}: record {index} has a blank or non-text title")
        if not isinstance(item.get("url"), str) or not item["url"].strip():
            raise ValueError(f"{path}: record {index} has a blank or non-text url")
        if not isinstance(item.get("year"), int):
            raise ValueError(f"{path}: record {index} has a non-integer year")
        records.append(item)
    return records


def _refuse_overwrite(target: Path, inputs: list[Path]) -> None:
    """Refuse to write to an existing file or to one of the input files."""
    if target.exists():
        raise ValueError(f"refusing to overwrite an existing file: {target}")
    for input_path in inputs:
        if str(target) == str(input_path):
            raise ValueError(f"refusing to overwrite an input file: {target}")


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints merges and flags; returns exit code."""
    parser = argparse.ArgumentParser(
        prog="dedupe_candidates.py",
        description=(
            "Group candidate search records that likely describe the same "
            "document, keep the fullest one, and flag old records for "
            "review. Writes nothing unless --write is given."
        ),
    )
    parser.add_argument(
        "candidates",
        metavar="CANDIDATES.json",
        help="candidate records, as a JSON list",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        metavar="Y",
        help="flag records from before this year as too_old (never dropped)",
    )
    parser.add_argument(
        "--out", metavar="FILE", help="where to write the deduplicated list"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write --out; refuses to overwrite an existing or input file",
    )
    args = parser.parse_args(argv)

    candidates_path = Path(args.candidates)
    try:
        records = load_records(candidates_path)
        kept, events = dedupe(records)
        flag_too_old(kept, args.min_year)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"dedupe_candidates.py: error: {exc}", file=sys.stderr)
        return 2

    for event in events:
        print(
            f"merge: kept {ascii(event.kept_title)} "
            f"dropped {ascii(event.dropped_title)} rule={event.rule}"
        )
    if args.min_year is not None:
        for record in kept:
            if record.get("too_old"):
                print(
                    f"flag: {ascii(str(record.get('title', '')))} too_old "
                    f"(year={record.get('year')} < {args.min_year})"
                )
    print(
        f"dedupe_candidates: {len(records)} in, {len(kept)} out, {len(events)} merged"
    )

    if args.out:
        if not args.write:
            print(
                f"dry run: would write {len(kept)} records to {args.out} "
                "(use --write to write)"
            )
        else:
            out_path = Path(args.out)
            try:
                _refuse_overwrite(out_path, [candidates_path])
                out_path.write_text(json.dumps(kept, indent=2) + "\n", encoding="utf-8")
            except (OSError, ValueError) as exc:
                print(f"dedupe_candidates.py: error: {exc}", file=sys.stderr)
                return 2
            print(f"wrote {len(kept)} records to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
