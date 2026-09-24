"""Unit tests for scripts/s1/gap_check.py and docs/stage-1/coverage-and-gaps.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
running-example blueprint (read-only). The page-output tests re-run the
real script and compare its output with the text pasted on the page, so
the page can never drift from the script.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import ast
import importlib.util
import json
import re
import subprocess  # nosec B404
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "s1" / "gap_check.py"
SAMPLE = ROOT / "scripts" / "sample_data" / "git_basics" / "blueprint.json"
PAGE = ROOT / "docs" / "stage-1" / "coverage-and-gaps.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("gap_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gc = load_module()


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run the script as a separate process, exactly as the page shows."""
    return subprocess.run(  # nosec B603
        [sys.executable, "-B", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        timeout=60,
        check=False,
    )


def blueprint(objectives: list[dict[str, Any]]) -> dict[str, Any]:
    """A minimal, single-domain blueprint holding the given objectives."""
    return {
        "domains": [
            {"id": "D1", "name": "Domain D1", "weight": 100, "objectives": objectives}
        ]
    }


def objective(objective_id: str, supported_by: list[str] | None = None) -> dict[str, Any]:
    """A minimal objective; omit supported_by to test the 'absent' case."""
    data: dict[str, Any] = {"id": objective_id, "text": "Do the thing.", "bloom": "apply"}
    if supported_by is not None:
        data["supported_by"] = supported_by
    return data


class SafeIdTests(unittest.TestCase):
    """safe_id: plain ASCII passes through; non-ASCII is escaped."""

    def test_ascii_id_is_unchanged(self) -> None:
        self.assertEqual(gc.safe_id("D4.2"), "D4.2")

    def test_non_ascii_id_is_escaped(self) -> None:
        self.assertEqual(gc.safe_id("Dé"), "D\\xe9")


class FindObjectivesTests(unittest.TestCase):
    """find_objectives: counts, absent/empty lists, and malformed input."""

    def test_absent_supported_by_counts_as_zero(self) -> None:
        data = blueprint([objective("D1.1")])
        found = gc.find_objectives(data)
        self.assertEqual(found, [("D1.1", 0)])

    def test_empty_supported_by_counts_as_zero(self) -> None:
        data = blueprint([objective("D1.1", [])])
        found = gc.find_objectives(data)
        self.assertEqual(found, [("D1.1", 0)])

    def test_nonempty_supported_by_is_counted(self) -> None:
        data = blueprint([objective("D1.1", ["SRC-001", "SRC-002"])])
        found = gc.find_objectives(data)
        self.assertEqual(found, [("D1.1", 2)])

    def test_not_a_dict_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gc.find_objectives(["not", "a", "dict"])

    def test_missing_domains_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gc.find_objectives({})

    def test_bad_domain_is_skipped_not_reported(self) -> None:
        data = {"domains": ["not a domain", blueprint([objective("D1.1")])["domains"][0]]}
        found = gc.find_objectives(data)
        self.assertEqual(found, [("D1.1", 0)])

    def test_bad_objective_is_skipped_not_reported(self) -> None:
        data = blueprint(["not an objective", objective("D1.2")])
        found = gc.find_objectives(data)
        self.assertEqual(found, [("D1.2", 0)])

    def test_missing_id_falls_back_to_a_position_label(self) -> None:
        data = blueprint([{"text": "no id here", "bloom": "apply"}])
        found = gc.find_objectives(data)
        self.assertEqual(len(found), 1)
        self.assertIn("domain #1 objective #1", found[0][0])


class FindGapsTests(unittest.TestCase):
    """find_gaps: the exact line format, and the summary counts."""

    def test_gap_line_format(self) -> None:
        lines = gc.find_gaps([("D4.2", 0)], 1)
        self.assertEqual(lines, ["gap D4.2: 0 source(s), need at least 1"])

    def test_no_gap_when_count_meets_minimum(self) -> None:
        lines = gc.find_gaps([("D1.1", 1)], 1)
        self.assertEqual(lines, [])

    def test_raising_min_sources_finds_more_gaps(self) -> None:
        objectives = [("D1.1", 1), ("D1.2", 2)]
        self.assertEqual(gc.find_gaps(objectives, 1), [])
        self.assertEqual(
            gc.find_gaps(objectives, 2),
            ["gap D1.1: 1 source(s), need at least 2"],
        )


class LoadBlueprintTests(unittest.TestCase):
    """load_blueprint: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = gc.load_blueprint(SAMPLE)
        self.assertEqual(len(data["domains"]), 4)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                gc.load_blueprint(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * gc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                gc.load_blueprint(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 whether or not a gap is found, 2 for a usage or input error."""

    def write(self, tmp: Path, data: dict[str, Any]) -> Path:
        path = tmp / "blueprint.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_with_no_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = blueprint([objective("D1.1", ["SRC-001"])])
            path = self.write(Path(tmp), data)
            self.assertEqual(gc.main([str(path)]), 0)

    def test_exit_zero_with_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = blueprint([objective("D1.1", [])])
            path = self.write(Path(tmp), data)
            self.assertEqual(gc.main([str(path)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(gc.main([str(path)]), 2)

    def test_exit_two_on_usage_error(self) -> None:
        # argparse itself exits the process on a bad --min-sources value,
        # rather than returning from main(), so this checks SystemExit.
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), blueprint([objective("D1.1")]))
            with self.assertRaises(SystemExit) as cm:
                gc.main([str(path), "--min-sources", "not-a-number"])
            self.assertEqual(cm.exception.code, 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real sample."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BLUEPRINT", result.stdout)
        self.assertIn("--min-sources", result.stdout)

    def test_real_blueprint_has_twelve_objectives(self) -> None:
        data = gc.load_blueprint(SAMPLE)
        found = gc.find_objectives(data)
        self.assertEqual(len(found), 12)

    def test_default_flags_exactly_d4_2(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        lines = [line for line in result.stdout.splitlines() if line.startswith("gap ")]
        self.assertEqual(lines, ["gap D4.2: 0 source(s), need at least 1"])
        self.assertIn("objectives=12 gaps=1", result.stdout)

    def test_min_sources_two_flags_nine_of_twelve(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, "--min-sources", "2", cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = [line for line in result.stdout.splitlines() if line.startswith("gap ")]
        self.assertEqual(len(lines), 9)
        self.assertIn("objectives=12 gaps=9", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("gap_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            run_cli(str(SAMPLE), "--min-sources", "2", cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


KEY_LINE = re.compile(r"^([A-Za-z][A-Za-z ]*):[ \t]*(.*)$")
REQUIRED_KEYS = ("ID", "Purpose", "Usage", "Dependencies", "Writes files", "License")


class HeaderAndSourceTests(unittest.TestCase):
    """The module docstring is a valid script header; the source is safe."""

    source = SCRIPT.read_text(encoding="utf-8")
    docstring = ast.get_docstring(ast.parse(source)) or ""

    def parse_header(self) -> dict[str, str]:
        fields: dict[str, str] = {}
        current = ""
        for line in self.docstring.splitlines():
            if not line.strip():
                break
            if line[0] in " \t":
                fields[current] += " " + line.strip()
                continue
            match = KEY_LINE.match(line)
            if match is None:
                self.fail(f"header line is not 'Key: value': {line!r}")
            current = match.group(1)
            fields[current] = match.group(2).strip()
        return fields

    def test_required_fields(self) -> None:
        fields = self.parse_header()
        for key in REQUIRED_KEYS:
            self.assertTrue(fields.get(key), f"missing header field {key}")
        self.assertEqual(fields["ID"], "X-S1-10")
        self.assertEqual(fields["Stage"], "S1")
        self.assertEqual(fields["Dependencies"], "stdlib")
        self.assertEqual(fields["Writes files"], "no")
        self.assertEqual(fields["License"], "CC0-1.0")
        self.assertTrue(fields["Usage"].startswith("python3 "))

    def test_only_standard_library_imports(self) -> None:
        tree = ast.parse(self.source)
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names.add(node.module.split(".")[0])
        self.assertTrue(names)
        self.assertEqual(names - set(sys.stdlib_module_names), set())

    def test_source_is_ascii_only(self) -> None:
        self.assertTrue(self.source.isascii())

    def test_disables_bytecode_writing(self) -> None:
        self.assertIn("sys.dont_write_bytecode = True", self.source)

    def test_no_forbidden_calls(self) -> None:
        for token in ("subprocess", "eval(", "exec(", "random.", "md5", "sha1"):
            self.assertNotIn(token, self.source, token)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-1/coverage-and-gaps.md: every pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected the default run and the --min-sources 2 run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        default_run = run_cli(str(SAMPLE))
        min_two_run = run_cli(str(SAMPLE), "--min-sources", "2")
        real_outputs = [default_run.stdout, min_two_run.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_page_does_not_state_a_numeric_gap_threshold_as_the_sources_own_rule(
        self,
    ) -> None:
        # The gap-count number is this guide's own default, never the source
        # project's rule; guard against the most direct way to misstate it.
        self.assertNotIn("fewer than two sources", self.page_text.casefold())
        self.assertNotIn("at least two sources", self.page_text.casefold())


if __name__ == "__main__":
    unittest.main()
