"""
ID: X-S1-05
Title: Injection screening scanner
Stage: S1
Purpose: Scan converted and original source files for prompt-injection
    patterns and print one line per finding. Looks for override phrases,
    sentences that address an assistant, model, reviewer or summarizer with
    a steering verb, invisible or bidirectional control characters
    (including ones written as HTML character references), hidden HTML
    carriers, data URIs and long encoded runs. Never decodes or acts on the
    matched text; it only reports where it is.
Usage: python3 scripts/s1/scan_injection.py PATH [PATH ...]
    [--adjudicated FILE.csv] [--log FILE] [--write]
Dependencies: stdlib
Writes files: yes
License: CC0-1.0
Inputs: One or more file or folder paths. A file given directly is scanned
    whatever its name; a folder is walked, without following symlinks, for
    files named *.md, *.txt, *.html, *.htm or *.json. An optional
    --adjudicated CSV marks findings a person has already judged to be
    false positives.
Outputs: One line per unsuppressed finding, printed to standard output as
    "file:line kind excerpt". With --log and --write, the same findings are
    also written to a CSV with columns file,line,kind,excerpt,fingerprint.

At most 5,000,000 bytes of any one file are read; the rest is skipped with
a notice on standard error. HTML character references are resolved with
html.unescape before any pattern is matched, so an invisible character
written as a reference, such as &#8203;, is still found. A finding's
fingerprint is the first 12 hex characters of the SHA-256 of the matched
text, so the same injected sentence keeps the same fingerprint even when
it moves to a different line.

A row with verdict false-positive in the --adjudicated CSV (columns
file,kind,fingerprint,verdict,reason) removes that one finding, matched by
its file, kind and fingerprint, from this run's printed output, from the
--log output and from the exit code. Adjudication never edits the
patterns: every other file, and every new finding in the same file, is
still scanned with the full pattern set on the next run.
"""

import argparse
import csv
import dataclasses
import hashlib
import html
import os
import re
import sys
from collections.abc import Iterator
from pathlib import Path

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "scan_injection.py: this script needs Python 3.10 or newer, but "
        f"this is {sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)

EXTENSIONS = (".md", ".txt", ".html", ".htm", ".json")
BYTE_CAP = 5_000_000
EXCERPT_WIDTH = 60
FINGERPRINT_CHARS = 12
ADJUDICATED_COLUMNS = ("file", "kind", "fingerprint", "verdict", "reason")
LOG_COLUMNS = ("file", "line", "kind", "excerpt", "fingerprint")

_OVERRIDE_PHRASES = (
    "ignore all earlier instructions",
    "disregard previous instructions",
    "new task",
    "respond only",
    "give a positive review",
    "system prompt",
)
_OVERRIDE_RE = re.compile(
    "|".join(re.escape(phrase) for phrase in _OVERRIDE_PHRASES), re.IGNORECASE
)

_ADDRESSEE_RE = re.compile(
    r"\b(?:assistants?|models?|ais?|reviewers?|summarizers?|agents?)\b",
    re.IGNORECASE,
)
_STEERING_VERB_RE = re.compile(
    r"\b(?:ignore|describe|rank|respond|output|reveal)\w*\b", re.IGNORECASE
)
_USER_AGENT_RE = re.compile(r"\buser[ -]agent\b", re.IGNORECASE)
# A sentence also ends at an HTML tag with no space after the punctuation,
# as in "...changed.</p>", so a converted paragraph never merges with the
# next one.
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])(?:\s+|(?=<))")
_LEADING_NOISE_RE = re.compile(r"^(?:\s+|<[^>]*>)+")

_INVISIBLE_CLASS = (
    "\u200b\u200c\u200d\ufeff\u00ad\u061c\u200e\u200f"
    "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
)
_INVISIBLE_RE = re.compile("[" + _INVISIBLE_CLASS + "\U000e0000-\U000e007f]")

_HIDDEN_HTML_PATTERNS = (
    re.compile(r"<[a-zA-Z][^>]*\bhidden\b[^>]*>"),
    re.compile(r'aria-hidden\s*=\s*"?true"?', re.IGNORECASE),
    re.compile(r"display\s*:\s*none", re.IGNORECASE),
    re.compile(r"visibility\s*:\s*hidden", re.IGNORECASE),
    re.compile(r"font-size\s*:\s*0(?:px|pt|em|%)?\b", re.IGNORECASE),
    re.compile(r"(?:left|text-indent)\s*:\s*-\d{3,}px", re.IGNORECASE),
    re.compile(r"<!--.*?-->", re.DOTALL),
    re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE),
)

_DATA_URI_RE = re.compile(r"\bdata:[A-Za-z0-9+.;\-/]{1,100}?,[^\s\"'<>]+")
_LONG_ENCODED_RE = re.compile(r"[A-Za-z0-9+/=]{200,}")


@dataclasses.dataclass(frozen=True)
class Finding:
    """One reported instance of a pattern, keyed by file, kind and fingerprint."""

    file: str
    line: int
    kind: str
    excerpt: str
    fingerprint: str


def sha_fingerprint(text: str) -> str:
    """First FINGERPRINT_CHARS hex characters of the SHA-256 of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:FINGERPRINT_CHARS]


def _line_of(text: str, pos: int) -> int:
    """1-based line number of an offset into text."""
    return text.count("\n", 0, pos) + 1


def _excerpt(text: str, pos: int, width: int = EXCERPT_WIDTH) -> str:
    """An ascii()-escaped excerpt of at most width characters near pos."""
    end = pos + width
    fragment = text[pos:end]
    if not fragment.strip():
        begin = max(0, pos - width)
        fragment = text[begin:pos]
    return ascii(fragment)


def _scan_override(rel: str, text: str) -> Iterator[Finding]:
    """override-phrase: a fixed list of override phrases, case-insensitive."""
    for match in _OVERRIDE_RE.finditer(text):
        yield Finding(
            file=rel,
            line=_line_of(text, match.start()),
            kind="override-phrase",
            excerpt=_excerpt(text, match.start()),
            fingerprint=sha_fingerprint(match.group(0)),
        )


def _sentences(text: str) -> Iterator[tuple[int, str]]:
    """(start offset, sentence text) pairs for the whole document."""
    start = 0
    for end in _SENTENCE_END_RE.finditer(text):
        stop = end.start()
        yield start, text[start:stop]
        start = end.end()
    yield start, text[start:]


def _scan_addressed(rel: str, text: str) -> Iterator[Finding]:
    """addressed-instruction: a sentence naming an addressee with a verb.

    "user agent" and "user-agent" do not count as naming an addressee, so an
    ordinary mention of an HTTP user agent string is not flagged.
    """
    for pos, sentence in _sentences(text):
        cleaned = _USER_AGENT_RE.sub(" ", sentence)
        if _ADDRESSEE_RE.search(cleaned) and _STEERING_VERB_RE.search(sentence):
            noise = _LEADING_NOISE_RE.match(sentence)
            start = pos + (noise.end() if noise else 0)
            yield Finding(
                file=rel,
                line=_line_of(text, start),
                kind="addressed-instruction",
                excerpt=_excerpt(text, start),
                fingerprint=sha_fingerprint(sentence.strip()),
            )


def _scan_invisible(rel: str, text: str) -> Iterator[Finding]:
    """invisible-char: one finding per zero-width, bidi, soft-hyphen or tag char."""
    for match in _INVISIBLE_RE.finditer(text):
        yield Finding(
            file=rel,
            line=_line_of(text, match.start()),
            kind="invisible-char",
            excerpt=_excerpt(text, match.start()),
            fingerprint=sha_fingerprint(match.group(0)),
        )


def _scan_hidden_html(rel: str, text: str) -> Iterator[Finding]:
    """hidden-html: a hidden attribute, hiding CSS, off-screen text or a carrier."""
    for pattern in _HIDDEN_HTML_PATTERNS:
        for match in pattern.finditer(text):
            yield Finding(
                file=rel,
                line=_line_of(text, match.start()),
                kind="hidden-html",
                excerpt=_excerpt(text, match.start()),
                fingerprint=sha_fingerprint(match.group(0)),
            )


def _scan_encoded(rel: str, text: str) -> Iterator[Finding]:
    """data-uri and long-encoded-run: never decoded; only length and hash shown."""
    for pattern, kind in (
        (_DATA_URI_RE, "data-uri"),
        (_LONG_ENCODED_RE, "long-encoded-run"),
    ):
        for match in pattern.finditer(text):
            span = match.group(0)
            digest = sha_fingerprint(span)
            yield Finding(
                file=rel,
                line=_line_of(text, match.start()),
                kind=kind,
                excerpt=f"length={len(span)} sha256={digest}",
                fingerprint=digest,
            )


def scan_text(rel: str, raw_text: str) -> list[Finding]:
    """All findings for one file's text, after resolving character references."""
    text = html.unescape(raw_text)
    findings: list[Finding] = []
    for scanner in (
        _scan_override,
        _scan_addressed,
        _scan_invisible,
        _scan_hidden_html,
        _scan_encoded,
    ):
        findings.extend(scanner(rel, text))
    return findings


def read_capped(path: str, cap: int = BYTE_CAP) -> str:
    """Read at most cap bytes of path as UTF-8, replacing bad bytes."""
    with open(path, "rb") as handle:
        raw = handle.read(cap + 1)
    if len(raw) > cap:
        print(
            f"scan_injection.py: {path}: read only the first {cap} bytes; "
            "skipping the rest",
            file=sys.stderr,
        )
        raw = raw[:cap]
    return raw.decode("utf-8", errors="replace")


def _walk_dir(given: str, root: Path) -> Iterator[str]:
    """Files under root named with an allowed extension; symlinks skipped."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) / d).is_symlink()]
        rel_dir = os.path.relpath(dirpath, root)
        for name in sorted(filenames):
            full = Path(dirpath) / name
            if full.is_symlink() or full.suffix.lower() not in EXTENSIONS:
                continue
            prefix = given.rstrip("/")
            if rel_dir == ".":
                yield f"{prefix}/{name}"
            else:
                yield f"{prefix}/{rel_dir}/{name}"


def iter_targets(paths: list[str]) -> Iterator[str]:
    """Every file to scan, with its path printed exactly as given."""
    for raw in paths:
        candidate = Path(raw)
        if candidate.is_symlink():
            print(f"scan_injection.py: skipping symlink: {raw}", file=sys.stderr)
        elif candidate.is_dir():
            yield from _walk_dir(raw, candidate)
        elif candidate.is_file():
            yield raw
        else:
            raise ValueError(f"path not found: {raw}")


def load_adjudicated(path: Path) -> set[tuple[str, str, str]]:
    """(file, kind, fingerprint) triples whose verdict is false-positive."""
    suppressed: set[tuple[str, str, str]] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if not set(ADJUDICATED_COLUMNS).issubset(fields):
            raise ValueError(
                "--adjudicated CSV needs columns " + ",".join(ADJUDICATED_COLUMNS)
            )
        for row in reader:
            if (row.get("verdict") or "").strip() == "false-positive":
                suppressed.add((row["file"], row["kind"], row["fingerprint"]))
    return suppressed


def write_log(path: Path, findings: list[Finding]) -> None:
    """Write the findings CSV with the fixed LOG_COLUMNS header."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(LOG_COLUMNS)
        for finding in findings:
            writer.writerow(
                [
                    finding.file,
                    finding.line,
                    finding.kind,
                    finding.excerpt,
                    finding.fingerprint,
                ]
            )


def main(argv: list[str] | None = None) -> int:
    """Scan every path, print unsuppressed findings, return the exit code."""
    parser = argparse.ArgumentParser(
        prog="scan_injection.py",
        description=(
            "Scan files for prompt-injection patterns: override phrases, "
            "instructions addressed to an assistant, invisible or "
            "bidirectional control characters, hidden HTML carriers, and "
            "data URIs or long encoded runs. Never decodes or acts on the "
            "matched text."
        ),
    )
    parser.add_argument("paths", nargs="+", metavar="PATH", help="a file or folder")
    parser.add_argument(
        "--adjudicated",
        metavar="FILE.csv",
        help="a CSV that marks known false positives",
    )
    parser.add_argument(
        "--log", metavar="FILE", help="write the findings CSV here (needs --write)"
    )
    parser.add_argument(
        "--write", action="store_true", help="allow writing the --log file"
    )
    args = parser.parse_args(argv)

    active: list[Finding] = []
    try:
        targets = sorted(set(iter_targets(args.paths)))
        suppressed: set[tuple[str, str, str]] = set()
        if args.adjudicated:
            suppressed = load_adjudicated(Path(args.adjudicated))
        findings: list[Finding] = []
        for target in targets:
            findings.extend(scan_text(target, read_capped(target)))
        findings.sort(key=lambda f: (f.file, f.line, f.kind, f.fingerprint))
        active = [
            f for f in findings if (f.file, f.kind, f.fingerprint) not in suppressed
        ]
        for finding in active:
            print(f"{finding.file}:{finding.line} {finding.kind} {finding.excerpt}")
        if args.log and args.write:
            log_path = Path(args.log)
            if any(Path(t).resolve() == log_path.resolve() for t in targets):
                raise ValueError(f"--log must not equal an input path: {args.log}")
            if log_path.exists():
                raise ValueError(f"refusing to overwrite existing file: {args.log}")
            write_log(log_path, active)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(f"scan_injection.py: error: {exc}", file=sys.stderr)
        return 2
    return 1 if active else 0


if __name__ == "__main__":
    sys.exit(main())
