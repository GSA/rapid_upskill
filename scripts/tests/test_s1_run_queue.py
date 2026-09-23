"""Unit tests for scripts/s1/run_queue.py.

Everything runs offline, on the virtual clock unless a test names
--real-time. See the module under test for the script this exercises.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import importlib.util
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
SCRIPT_PATH = REPO_ROOT / "scripts" / "s1" / "run_queue.py"
SEARCH_DIR = REPO_ROOT / "scripts" / "sample_data" / "git_basics_stage1" / "search"
SAMPLE_PLAN = SEARCH_DIR / "plan.json"
SAMPLE_INDEX = SEARCH_DIR / "mock_index.json"
REL_PLAN = "scripts/sample_data/git_basics_stage1/search/plan.json"
REL_INDEX = "scripts/sample_data/git_basics_stage1/search/mock_index.json"

# Lines this writer's page pastes verbatim from a real run.
PAGE_BASIC_LINES = [
    '{"query_id": "Q1", "start": 0.0, "finish": 0.0, "attempts": 1, "matches": 1, '
    '"new_candidates": 1, "stage": "listed", "state": "done", "anchors_expected": 2, '
    '"anchors_hit": 1}',
    '{"query_id": "Q4", "start": 9.0, "finish": 9.0, "attempts": 1, "matches": 0, '
    '"new_candidates": 0, "stage": "listed", "state": "empty", "anchors_expected": 2, '
    '"anchors_hit": 1}',
    "queries=4 done=3 empty=1 failed=0 candidates=1 anchors=1/2 recall=0.50",
]
PAGE_RETRY_LINE = (
    '{"query_id": "Q1", "start": 0.0, "finish": 15.0, "attempts": 3, "matches": 1, '
    '"new_candidates": 1, "stage": "listed", "state": "done", "anchors_expected": 2, '
    '"anchors_hit": 1}'
)
PAGE_BREAKER_LINES = [
    '{"query_id": "Q1", "start": 0.0, "finish": 15.0, "attempts": 3, "matches": 0, '
    '"new_candidates": 0, "stage": "listed", "state": "failed", "anchors_expected": 2, '
    '"anchors_hit": 0}',
    '{"query_id": "Q2", "start": 18.0, "finish": 33.0, "attempts": 3, "matches": 0, '
    '"new_candidates": 0, "stage": "listed", "state": "breaker_open", '
    '"anchors_expected": 2, "anchors_hit": 0}',
    "queries=2 done=0 empty=0 failed=1 candidates=0 anchors=0/2 recall=0.00",
]
PAGE_BREAK_LINE = (
    "run_queue.py: error: plan.extra-query.json: 5 queries exceed query_cap 4"
)

ABSOLUTE_PATH_RE = re.compile(r"(^|[\s'\"])(/[^\s'\"]+|[A-Za-z]:\\\S*)")


def load_module() -> ModuleType:
    """Import the script from its file.

    run_queue.py itself takes no sys.path.insert, because running it
    directly (python3 -B scripts/s1/run_queue.py) puts its own folder on
    sys.path automatically, which is what lets it import its sibling
    dedupe_candidates.py. Loading the file this way instead, so this test
    can call its functions in-process, does not get that for free, so this
    loader adds the same folder to sys.path itself, only for this test.
    """
    script_dir = str(SCRIPT_PATH.parent)
    added = script_dir not in sys.path
    if added:
        sys.path.insert(0, script_dir)
    try:
        spec = importlib.util.spec_from_file_location("run_queue", SCRIPT_PATH)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {SCRIPT_PATH}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if added:
            sys.path.remove(script_dir)


run_queue = load_module()


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


class HelpTests(unittest.TestCase):
    """--help works and documents the arguments."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PLAN.json", result.stdout)
        self.assertIn("--index", result.stdout)
        self.assertIn("--fail", result.stdout)
        self.assertIn("--real-time", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_missing_index_is_a_usage_error(self) -> None:
        result = run_cli(REL_PLAN)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--index", result.stderr)


class CleanRunTests(unittest.TestCase):
    """The sample plan and index run cleanly and match the page's pastes."""

    def test_basic_run_matches_the_page(self) -> None:
        result = run_cli(REL_PLAN, "--index", REL_INDEX)
        self.assertEqual(result.returncode, 0, result.stderr)
        for line in PAGE_BASIC_LINES:
            with self.subTest(line=line):
                self.assertIn(line, result.stdout)

    def test_retry_then_succeed_matches_the_page(self) -> None:
        result = run_cli(REL_PLAN, "--index", REL_INDEX, "--fail", "Q1:2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(PAGE_RETRY_LINE, result.stdout)
        self.assertIn(
            "queries=4 done=3 empty=1 failed=0 candidates=1 anchors=1/2 recall=0.50",
            result.stdout,
        )

    def test_breaker_opens_matches_the_page(self) -> None:
        result = run_cli(
            REL_PLAN, "--index", REL_INDEX, "--fail", "Q1:3", "--fail", "Q2:3"
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        for line in PAGE_BREAKER_LINES:
            with self.subTest(line=line):
                self.assertIn(line, result.stdout)
        lines = [ln for ln in result.stdout.splitlines() if ln.startswith("{")]
        self.assertEqual(
            len(lines), 2, "the breaker must stop the run before Q3 and Q4"
        )

    def test_empty_versus_done_state(self) -> None:
        result = run_cli(REL_PLAN, "--index", REL_INDEX)
        states = [
            json.loads(ln)["state"]
            for ln in result.stdout.splitlines()
            if ln.startswith("{")
        ]
        self.assertEqual(states, ["done", "done", "done", "empty"])


class PageOutputTests(unittest.TestCase):
    """Every line this writer's page pastes is real, reproducible output."""

    def test_pasted_lines_have_no_absolute_path(self) -> None:
        lines = (
            PAGE_BASIC_LINES
            + [PAGE_RETRY_LINE]
            + PAGE_BREAKER_LINES
            + [PAGE_BREAK_LINE]
        )
        for line in lines:
            with self.subTest(line=line):
                self.assertIsNone(ABSOLUTE_PATH_RE.search(line), line)

    def test_break_on_purpose_matches_the_real_output(self) -> None:
        """A copy of plan.json, with one query added but query_cap left as
        it was, is refused with exit code 2."""
        rel_copy = "plan.extra-query.json"
        copy_path = REPO_ROOT / rel_copy
        self.assertFalse(copy_path.exists(), "temporary fixture name is already taken")
        try:
            data = json.loads(SAMPLE_PLAN.read_text(encoding="utf-8"))
            data["clusters"][1]["queries"].append(
                {"query_id": "Q5", "text": "amend commit message"}
            )
            copy_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            result = run_cli(rel_copy, "--index", REL_INDEX)
        finally:
            if copy_path.exists():
                copy_path.unlink()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn(PAGE_BREAK_LINE, result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class ErrorPathTests(unittest.TestCase):
    """Every input problem is one clean line on stderr and exit code 2."""

    def test_missing_plan_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "missing.json"), "--index", REL_INDEX)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_missing_index_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(REL_PLAN, "--index", str(Path(tmp) / "missing.json"))
        self.assertEqual(result.returncode, 2)

    def test_query_cap_exceeded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(SAMPLE_PLAN.read_text(encoding="utf-8"))
            data["query_cap"] = 1
            path = Path(tmp) / "plan.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run_cli(str(path), "--index", REL_INDEX)
        self.assertEqual(result.returncode, 2)
        self.assertIn("exceed query_cap", result.stderr)

    def test_unknown_fail_query_id(self) -> None:
        result = run_cli(REL_PLAN, "--index", REL_INDEX, "--fail", "Q9:1")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown query id", result.stderr)

    def test_malformed_fail_value(self) -> None:
        result = run_cli(REL_PLAN, "--index", REL_INDEX, "--fail", "Q1")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--fail", result.stderr)

    def test_plan_missing_a_required_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(SAMPLE_PLAN.read_text(encoding="utf-8"))
            del data["anchors"]
            path = Path(tmp) / "plan.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run_cli(str(path), "--index", REL_INDEX)
        self.assertEqual(result.returncode, 2)
        self.assertIn("anchors", result.stderr)

    def test_duplicate_query_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(SAMPLE_PLAN.read_text(encoding="utf-8"))
            data["clusters"][0]["queries"].append(
                dict(data["clusters"][0]["queries"][0])
            )
            data["query_cap"] = 10
            path = Path(tmp) / "plan.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run_cli(str(path), "--index", REL_INDEX)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate query_id", result.stderr)


class WriteAndOverwriteTests(unittest.TestCase):
    """--manifest and --candidates-out write only with --write."""

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.jsonl"
            candidates = Path(tmp) / "candidates.json"
            result = run_cli(
                REL_PLAN,
                "--index",
                REL_INDEX,
                "--manifest",
                str(manifest),
                "--candidates-out",
                str(candidates),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("dry run", result.stdout)
            self.assertFalse(manifest.exists())
            self.assertFalse(candidates.exists())

    def test_write_creates_both_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.jsonl"
            candidates = Path(tmp) / "candidates.json"
            result = run_cli(
                REL_PLAN,
                "--index",
                REL_INDEX,
                "--manifest",
                str(manifest),
                "--candidates-out",
                str(candidates),
                "--write",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(manifest.read_text(encoding="utf-8").splitlines()), 4)
            self.assertEqual(len(json.loads(candidates.read_text(encoding="utf-8"))), 1)

    def test_refuses_to_overwrite_an_existing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.jsonl"
            manifest.write_text("", encoding="utf-8")
            result = run_cli(
                REL_PLAN, "--index", REL_INDEX, "--manifest", str(manifest), "--write"
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)


class VirtualClockTests(unittest.TestCase):
    """The virtual clock advances only on sleep(); nothing waits for real."""

    def test_virtual_clock_does_not_wait(self) -> None:
        clock = run_queue.VirtualClock()
        self.assertEqual(clock.now(), 0.0)
        clock.sleep(3)
        self.assertEqual(clock.now(), 3.0)
        clock.sleep(0)
        self.assertEqual(clock.now(), 3.0)

    def test_real_time_flag_uses_a_real_clock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.jsonl"
            result = run_cli(
                REL_PLAN,
                "--index",
                REL_INDEX,
                "--real-time",
                "--min-gap",
                "0.01",
                "--wait",
                "0.01",
                "--max-wait",
                "0.02",
                "--manifest",
                str(manifest),
                "--write",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        first_line = json.loads(result.stdout.splitlines()[0])
        self.assertGreaterEqual(first_line["finish"], 0.0)


class SourceHygieneTests(unittest.TestCase):
    """The script's own source stays ASCII-only, per this guide's rules."""

    def test_source_is_ascii_only(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertTrue(source.isascii(), "non-ASCII character in run_queue.py")


if __name__ == "__main__":
    unittest.main()
