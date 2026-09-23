"""Unit tests for scripts/s1/dedupe_candidates.py.

Everything runs offline, on temporary copies of files. See the module under
test for the script this exercises.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import contextlib
import importlib.util
import io
import json
import re
import subprocess  # nosec B404
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "s1" / "dedupe_candidates.py"
SAMPLE_INDEX = (
    REPO_ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_stage1"
    / "search"
    / "mock_index.json"
)

# Lines this writer's page pastes verbatim from a real run. Kept here so a
# page-output test can confirm each one still appears in the real output, and
# so a regex check can confirm none holds an absolute path.
PAGE_DEDUPE_LINES = [
    "merge: kept 'Branches are just names' dropped 'branches are just names' "
    "rule=title-author-year",
    "flag: 'Quick cheat sheet: sending and getting changes' too_old "
    "(year=2019 < 2020)",
    "flag: 'Distributed version control before Git: a 1998 retrospective' "
    "too_old (year=1998 < 2020)",
    "dedupe_candidates: 9 in, 8 out, 1 merged",
]
PAGE_BREAK_LINE = (
    "dedupe_candidates.py: error: Expecting ',' delimiter: line 81 column 1 (char 3406)"
)

ABSOLUTE_PATH_RE = re.compile(r"(^|[\s'\"])(/[^\s'\"]+|[A-Za-z]:\\\S*)")


def load_module() -> ModuleType:
    """Import the script from its file, without needing it on sys.path."""
    spec = importlib.util.spec_from_file_location("dedupe_candidates", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dedupe_candidates = load_module()


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the script as a subprocess, from the repository root."""
    return subprocess.run(  # nosec B603
        [sys.executable, "-B", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
        timeout=60,
    )


def write_json(path: Path, data: object) -> None:
    """Write JSON to path as UTF-8 text."""
    path.write_text(json.dumps(data), encoding="utf-8")


class HelpTests(unittest.TestCase):
    """--help works and documents the arguments."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CANDIDATES.json", result.stdout)
        self.assertIn("--min-year", result.stdout)
        self.assertIn("--write", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_missing_argument_is_a_usage_error(self) -> None:
        result = run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("CANDIDATES.json", result.stderr)


class CleanSampleTests(unittest.TestCase):
    """The sample index runs cleanly and matches what the page pastes."""

    def test_clean_sample_passes(self) -> None:
        result = run_cli(str(SAMPLE_INDEX), "--min-year", "2020")
        self.assertEqual(result.returncode, 0, result.stderr)
        for line in PAGE_DEDUPE_LINES:
            with self.subTest(line=line):
                self.assertIn(line, result.stdout)

    def test_without_min_year_no_flags_are_printed(self) -> None:
        result = run_cli(str(SAMPLE_INDEX))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("too_old", result.stdout)
        self.assertIn("dedupe_candidates: 9 in, 8 out, 1 merged", result.stdout)


class PageOutputTests(unittest.TestCase):
    """Every line this writer's page pastes is real, reproducible output."""

    def test_pasted_lines_have_no_absolute_path(self) -> None:
        for line in PAGE_DEDUPE_LINES + [PAGE_BREAK_LINE]:
            with self.subTest(line=line):
                self.assertIsNone(ABSOLUTE_PATH_RE.search(line), line)

    def test_break_on_purpose_matches_the_real_output(self) -> None:
        """Deleting the sample file's last character breaks its JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "mock_index.broken.json"
            original = SAMPLE_INDEX.read_text(encoding="utf-8").rstrip()
            broken.write_text(original[:-1], encoding="utf-8")
            result = run_cli(str(broken))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn(
            "Expecting ',' delimiter: line 81 column 1 (char 3406)", result.stderr
        )
        self.assertNotIn("Traceback", result.stderr)


class ErrorPathTests(unittest.TestCase):
    """Every input problem is one clean line on stderr and exit code 2."""

    def test_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "does-not-exist.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_not_a_json_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            write_json(path, {"title": "not a list"})
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("expected a JSON list", result.stderr)

    def test_record_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            write_json(path, [{"title": "No URL or year"}])
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing", result.stderr)

    def test_record_with_blank_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            write_json(
                path, [{"title": "  ", "url": "https://example.com/a", "year": 2026}]
            )
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("title", result.stderr)

    def test_record_with_non_integer_year(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            write_json(
                path, [{"title": "A", "url": "https://example.com/a", "year": "2026"}]
            )
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("year", result.stderr)

    def test_symlink_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.json"
            write_json(
                target, [{"title": "A", "url": "https://example.com/a", "year": 2026}]
            )
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks are not available in this environment")
            result = run_cli(str(link))
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stderr)


class WriteAndOverwriteTests(unittest.TestCase):
    """--out writes only with --write, and never overwrites a file."""

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            result = run_cli(str(SAMPLE_INDEX), "--out", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dry run", result.stdout)
        self.assertFalse(out.exists())

    def test_write_creates_the_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            result = run_cli(str(SAMPLE_INDEX), "--out", str(out), "--write")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            written = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(len(written), 8)

    def test_refuses_to_overwrite_an_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            out.write_text("[]", encoding="utf-8")
            result = run_cli(str(SAMPLE_INDEX), "--out", str(out), "--write")
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)

    def test_refuses_to_overwrite_an_input_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidates = Path(tmp) / "candidates.json"
            write_json(
                candidates,
                [{"title": "A", "url": "https://example.com/a", "year": 2026}],
            )
            result = run_cli(str(candidates), "--out", str(candidates), "--write")
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)


class DedupeLogicTests(unittest.TestCase):
    """The grouping rules, in-process, on small constructed records."""

    def test_identifier_tier_wins_and_strips_version_suffix(self) -> None:
        a = {
            "title": "A",
            "url": "https://example.com/a",
            "year": 2026,
            "identifier": "GB-1",
        }
        b = {
            "title": "A, revised",
            "url": "https://example.com/b",
            "year": 2026,
            "identifier": "GB-1-v2",
            "authors": ["Author A"],
        }
        kept, events = dedupe_candidates.dedupe([a, b])
        self.assertEqual(len(kept), 1)
        self.assertEqual(events[0].rule, "identifier")
        self.assertEqual(kept[0]["identifier"], "GB-1-v2")  # more filled fields

    def test_url_tier_ignores_scheme_www_and_tracking_params(self) -> None:
        a = {
            "title": "A",
            "url": "http://www.example.com/page/?utm_source=x",
            "year": 2026,
        }
        b = {
            "title": "A copy",
            "url": "https://example.com/page",
            "year": 2026,
            "authors": ["Author A"],
        }
        kept, events = dedupe_candidates.dedupe([a, b])
        self.assertEqual(len(kept), 1)
        self.assertEqual(events[0].rule, "url")

    def test_title_author_year_tier_is_the_fallback(self) -> None:
        a = {
            "title": "Same Title",
            "url": "https://example.com/a",
            "year": 2026,
            "authors": ["X"],
        }
        b = {
            "title": "same   title",
            "url": "https://example.org/completely-different",
            "year": 2026,
            "authors": ["X"],
            "summary": "More complete record.",
        }
        kept, events = dedupe_candidates.dedupe([a, b])
        self.assertEqual(len(kept), 1)
        self.assertEqual(events[0].rule, "title-author-year")

    def test_distinct_records_are_not_merged(self) -> None:
        a = {"title": "A", "url": "https://example.com/a", "year": 2026}
        b = {"title": "B", "url": "https://example.com/b", "year": 2026}
        kept, events = dedupe_candidates.dedupe([a, b])
        self.assertEqual(len(kept), 2)
        self.assertEqual(events, [])

    def test_flag_too_old_never_drops_a_record(self) -> None:
        records = [{"title": "Old", "url": "https://example.com/a", "year": 2000}]
        dedupe_candidates.flag_too_old(records, 2020)
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["too_old"])

    def test_flag_too_old_with_no_min_year_changes_nothing(self) -> None:
        records = [{"title": "Old", "url": "https://example.com/a", "year": 2000}]
        dedupe_candidates.flag_too_old(records, None)
        self.assertNotIn("too_old", records[0])

    def test_read_capped_reports_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "big.json"
            path.write_text("0123456789", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                text = dedupe_candidates._read_capped(path, limit=5)
        self.assertEqual(text, "01234")
        self.assertIn("first 5 bytes", err.getvalue())


class SourceHygieneTests(unittest.TestCase):
    """The script's own source stays ASCII-only, per this guide's rules."""

    def test_source_is_ascii_only(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertTrue(source.isascii(), "non-ASCII character in dedupe_candidates.py")


if __name__ == "__main__":
    unittest.main()
