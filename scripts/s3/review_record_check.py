"""
ID: X-S3-02
Title: Review record check
Stage: S3
Purpose: Check a set of Layer 2 review flags: that each status is one
    of the four allowed values, that every flag gives a reason, and
    that a flag whose status calls for a suggestion has one.
Usage: python3 scripts/s3/review_record_check.py --help
    In a shell: python3 scripts/s3/review_record_check.py FLAGS.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: A review-flags JSON file: a list of objects, each with
    claim_id, status, reason and, when the status calls for one,
    suggestion.
Outputs: One line per finding, then a summary line, all printed to
    standard output.

This script checks the shape and vocabulary of a set of review flags.
It does not judge whether a status, a reason or a suggestion is
actually right: that is a subject-matter expert's own call, recorded
in the flag itself, not something a script can verify.

The allowed status values are accurate, needs-review, reject and
unverifiable. A flag needs a suggestion only when its status is
needs-review or reject; an accurate or unverifiable flag may carry one
or leave it out.

Errors (exit 1), one line per finding: a status value outside the four
allowed ('bad-status: claim "C2" has status "wrong", not in the
allowed set'); a missing or empty reason ('missing-reason: claim
"C3"'); a missing or empty suggestion on a flag whose status is
needs-review or reject ('missing-suggestion: claim "C1" status
"reject" needs one'). A flags file that is not a JSON list, an entry
that is not a JSON object, or an entry with no usable claim_id, is a
usage or input error (exit 2), not a finding: no finding line can name
a claim without one.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "review_record_check.py: this script needs Python 3.10 or newer, "
        f"but this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000
ALLOWED_STATUSES = ("accurate", "needs-review", "reject", "unverifiable")
STATUSES_NEEDING_SUGGESTION = ("needs-review", "reject")


def load_json(path: Path) -> Any:
    """Read and parse one JSON file; never follows a symlink."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(text)


def load_flags(data: Any) -> list[dict[str, Any]]:
    """Return the flags list, after checking its basic shape.

    Each entry must be a JSON object with a non-empty claim_id string.
    Every finding line this script prints names a claim, so an entry
    with no usable id is a usage error, not a finding.
    """
    if not isinstance(data, list):
        raise ValueError("the flags file is not a JSON list")
    flags: list[dict[str, Any]] = []
    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"entry #{position} is not a JSON object")
        claim_id = entry.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"entry #{position} has no claim_id")
        flags.append(entry)
    return flags


def check_flags(flags: list[dict[str, Any]]) -> list[str]:
    """Return one finding line per problem, in claim order.

    Checks, per flag, in this order: the status is one of the four
    allowed values; the reason is a non-empty string; a flag whose
    status is needs-review or reject also has a non-empty suggestion.
    """
    findings: list[str] = []
    for entry in flags:
        claim_id = entry["claim_id"]
        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            findings.append(
                f'bad-status: claim "{claim_id}" has status '
                f"{json.dumps(status)}, not in the allowed set"
            )
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason:
            findings.append(f'missing-reason: claim "{claim_id}"')
        if status in STATUSES_NEEDING_SUGGESTION:
            suggestion = entry.get("suggestion")
            if not isinstance(suggestion, str) or not suggestion:
                findings.append(
                    f'missing-suggestion: claim "{claim_id}" status '
                    f'"{status}" needs one'
                )
    return findings


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="review_record_check.py",
        description=(
            "Check a set of Layer 2 review flags: the status vocabulary, "
            "a reason on every flag, and a suggestion where the status "
            "calls for one. Writes no files."
        ),
    )
    parser.add_argument("flags", metavar="FLAGS", help="path to the flags JSON file")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        flags = load_flags(load_json(Path(args.flags)))
        findings = check_flags(flags)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"review_record_check.py: error: {exc}", file=sys.stderr)
        return 2
    for line in findings:
        print(line)
    print(f"claims={len(flags)} errors={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
