"""
ID: X-OP-05
Title: Completion signal check
Stage: OP
Purpose: Check a batch of worker output files against a declared completion
    test (required fields present and non-empty), so a file's mere
    existence, or a file merely being non-empty, is never mistaken for
    proof that the work behind it is actually finished.
Usage: python3 scripts/op/completion_signal_check.py --help
    In a shell: python3 scripts/op/completion_signal_check.py OUTPUTS_DIR
    COMPLETION_TEST.json
Dependencies: stdlib
Writes files: no
License: CC0-1.0
Inputs: OUTPUTS_DIR, a folder holding one worker output file per dispatched
    item, each file expected to be a JSON object. COMPLETION_TEST.json, a
    JSON object with one field, required_fields: a list of field names
    every output file must carry, present and holding a non-empty value.
Outputs: One line per finding, then one summary line, all printed to
    standard output.

This script reads direct files inside OUTPUTS_DIR only; it does not
recurse into a subfolder. A subfolder found there is skipped, along with
any hidden entry (a name starting with "."). Every other entry is
treated as one dispatched item's own output file.

A file that cannot actually be read back as a JSON object, because it is
a symlink (refused, never followed), because it is over 5,000,000 bytes,
because it is not valid JSON, or because its top level is not a JSON
object at all, is reported as a "missing" finding. This is a deliberate
choice, not an oversight: the point of this check is that a file's mere
existence, even a non-empty one, is never the same as a real, readable
output, so a file this script cannot actually read counts the same as a
file that was never written.

Errors (exit 1): a "missing" finding, as described above; a "missing
field" finding, a field named in COMPLETION_TEST.json's own
required_fields that is absent from one output file's own JSON object; an
"empty field" finding, a required field that is present but holds an
empty value (an empty string, an empty list, an empty object, or a JSON
null). A number, including 0, and a boolean, including false, both count
as present and non-empty.

A COMPLETION_TEST.json that is not a JSON object, or whose
required_fields is missing, empty, or not a list of non-empty strings, is
a usage or input error (exit 2), not a finding, since there would be
nothing to check every output file against. The same is true of an
OUTPUTS_DIR that does not exist or is not a folder.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "completion_signal_check.py: this script needs Python 3.10 or "
        f"newer, but this is {sys.version_info.major}."
        f"{sys.version_info.minor}. Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

MAX_BYTES = 5_000_000


def load_completion_test(path: Path) -> list[str]:
    """Read COMPLETION_TEST.json and return its required_fields list."""
    if path.is_symlink():
        raise OSError(f"refusing to read a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is over {MAX_BYTES} bytes; skipping")
    text = path.read_text(encoding="utf-8", errors="replace")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    fields = data.get("required_fields")
    if not isinstance(fields, list) or not fields:
        raise ValueError(f"{path} has no non-empty 'required_fields' list")
    for field_name in fields:
        if not isinstance(field_name, str) or not field_name:
            raise ValueError(
                f"{path} 'required_fields' holds a non-string or empty entry"
            )
    return fields


def _is_empty(value: Any) -> bool:
    """True for None, or an empty string, list or dict; a number or bool is not."""
    if value is None:
        return True
    if isinstance(value, (str, list, dict)):
        return len(value) == 0
    return False


def _output_files(outputs_dir: Path) -> list[Path]:
    """Direct files inside outputs_dir, sorted by name; no recursion."""
    return sorted(
        (
            entry
            for entry in outputs_dir.iterdir()
            if not entry.name.startswith(".") and not entry.is_dir()
        ),
        key=lambda entry: entry.name,
    )


def check_outputs(
    outputs_dir: Path, required_fields: list[str]
) -> tuple[list[str], int]:
    """Return (findings, files_checked) for every output file in outputs_dir."""
    findings: list[str] = []
    files = _output_files(outputs_dir)
    for path in files:
        name = path.name
        if path.is_symlink():
            findings.append(f"missing: {name} is a symlink; refusing to read it")
            continue
        size = path.stat().st_size
        if size > MAX_BYTES:
            findings.append(f"missing: {name} is over {MAX_BYTES} bytes; skipping")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            findings.append(f"missing: {name} is not valid JSON")
            continue
        if not isinstance(data, dict):
            findings.append(f"missing: {name} is not a JSON object")
            continue
        for field_name in required_fields:
            if field_name not in data:
                findings.append(f"missing-field: {name} has no {field_name!r}")
            elif _is_empty(data[field_name]):
                findings.append(f"empty-field: {name} field {field_name!r} is empty")
    return findings, len(files)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="completion_signal_check.py",
        description=(
            "Check a batch of worker output files against a declared "
            "completion test. Writes no files."
        ),
    )
    parser.add_argument(
        "outputs_dir",
        metavar="OUTPUTS_DIR",
        help="folder holding one worker output file per dispatched item",
    )
    parser.add_argument(
        "completion_test",
        metavar="COMPLETION_TEST.json",
        help="path to the completion test JSON (a required_fields list)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; prints the report, returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    outputs_dir = Path(args.outputs_dir)
    try:
        if not outputs_dir.is_dir():
            raise OSError(f"{outputs_dir} is not a folder")
        required_fields = load_completion_test(Path(args.completion_test))
        findings, file_count = check_outputs(outputs_dir, required_fields)
    except (
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
    ) as exc:
        print(f"completion_signal_check.py: error: {exc}", file=sys.stderr)
        return 2
    for message in findings:
        print(message)
    print(f"outputs={file_count} errors={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
