"""Unit tests for scripts/op/run_record_check.py and
docs/operating-practices/run-logging-and-dashboards.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample run record and step log (read-only). The page-output test
re-runs the real script and compares its output with the text pasted
on the page, so the page can never drift from the script.

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
SCRIPT = ROOT / "scripts" / "op" / "run_record_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_batch8" / "run_records"
SAMPLE_RUN = SAMPLE_DIR / "run.json"
SAMPLE_EVENTS = SAMPLE_DIR / "events.jsonl"
PAGE = ROOT / "docs" / "operating-practices" / "run-logging-and-dashboards.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("run_record_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rrc = load_module()


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


def record(**overrides: Any) -> dict[str, Any]:
    """A minimal, valid run record; keyword arguments override its fields."""
    base: dict[str, Any] = {
        "schema_version": "1.0.0",
        "run": {"id": "2026-01-01-1", "workflow": "sample", "status": "done"},
        "steps": [{"id": "one", "status": "done"}],
    }
    base.update(overrides)
    return base


class CheckRecordCoreTests(unittest.TestCase):
    """The required core: schema_version, run, steps."""

    def test_clean_minimal_record_has_no_findings(self) -> None:
        errors, warnings, count = rrc.check_record(record())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(count, 1)

    def test_missing_schema_version_is_an_error(self) -> None:
        data = record()
        del data["schema_version"]
        errors, _, _ = rrc.check_record(data)
        self.assertTrue(any("schema_version" in e for e in errors), errors)

    def test_missing_run_is_an_error(self) -> None:
        data = record()
        del data["run"]
        errors, _, _ = rrc.check_record(data)
        self.assertTrue(any("missing-core" in e and "'run'" in e for e in errors))

    def test_missing_steps_is_an_error(self) -> None:
        data = record()
        del data["steps"]
        errors, _, count = rrc.check_record(data)
        self.assertTrue(any("missing-core" in e and "'steps'" in e for e in errors))
        self.assertEqual(count, 0)

    def test_run_not_an_object_is_an_error(self) -> None:
        errors, _, _ = rrc.check_record(record(run="not an object"))
        self.assertTrue(any("bad-run" in e for e in errors), errors)

    def test_steps_not_a_list_is_an_error(self) -> None:
        errors, _, count = rrc.check_record(record(steps="not a list"))
        self.assertTrue(any("bad-steps" in e for e in errors), errors)
        self.assertEqual(count, 0)

    def test_step_count_matches_the_list_length(self) -> None:
        data = record(steps=[{"id": "a"}, {"id": "b"}, {"id": "c"}])
        _, _, count = rrc.check_record(data)
        self.assertEqual(count, 3)

    def test_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rrc.check_record(["not", "an", "object"])


class CheckRecordBreakdownScaleTests(unittest.TestCase):
    """Every breakdowns[] entry's scale must be nominal, ordinal or status."""

    def test_each_allowed_scale_has_no_finding(self) -> None:
        for scale in ("nominal", "ordinal", "status"):
            data = record(breakdowns=[{"id": "b", "scale": scale}])
            errors, _, _ = rrc.check_record(data)
            self.assertEqual(errors, [], scale)

    def test_missing_scale_is_an_error(self) -> None:
        data = record(breakdowns=[{"id": "b"}])
        errors, _, _ = rrc.check_record(data)
        self.assertTrue(any("bad-scale" in e and "'b'" in e for e in errors), errors)

    def test_unknown_scale_is_an_error(self) -> None:
        data = record(breakdowns=[{"id": "b", "scale": "continuous"}])
        errors, _, _ = rrc.check_record(data)
        self.assertTrue(any("bad-scale" in e for e in errors), errors)

    def test_breakdown_not_an_object_is_an_error(self) -> None:
        data = record(breakdowns=["not an object"])
        errors, _, _ = rrc.check_record(data)
        self.assertTrue(any("bad-breakdown" in e for e in errors), errors)

    def test_breakdowns_not_a_list_is_an_error(self) -> None:
        data = record(breakdowns={"not": "a list"})
        errors, _, _ = rrc.check_record(data)
        self.assertTrue(any("bad-breakdowns" in e for e in errors), errors)

    def test_breakdowns_absent_is_not_a_finding(self) -> None:
        errors, warnings, _ = rrc.check_record(record())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


class CheckRecordZeroRowTests(unittest.TestCase):
    """A declared category missing its own row in counts is a warning."""

    def test_all_declared_categories_present_has_no_warning(self) -> None:
        data = record(
            breakdowns=[
                {
                    "id": "sources",
                    "scale": "nominal",
                    "categories": ["a", "b"],
                    "counts": {"a": 3, "b": 0},
                }
            ]
        )
        _, warnings, _ = rrc.check_record(data)
        self.assertEqual(warnings, [])

    def test_omitted_category_is_a_warning_not_an_error(self) -> None:
        data = record(
            breakdowns=[
                {
                    "id": "sources",
                    "scale": "nominal",
                    "categories": ["a", "b"],
                    "counts": {"a": 3},
                }
            ]
        )
        errors, warnings, _ = rrc.check_record(data)
        self.assertEqual(errors, [])
        self.assertTrue(
            any("omitted-zero" in w and "'b'" in w for w in warnings), warnings
        )

    def test_extra_count_not_in_categories_is_not_a_finding(self) -> None:
        data = record(
            breakdowns=[
                {
                    "id": "sources",
                    "scale": "nominal",
                    "categories": ["a"],
                    "counts": {"a": 1, "extra": 5},
                }
            ]
        )
        _, warnings, _ = rrc.check_record(data)
        self.assertEqual(warnings, [])

    def test_missing_categories_list_is_not_a_finding(self) -> None:
        data = record(
            breakdowns=[{"id": "sources", "scale": "nominal", "counts": {"a": 1}}]
        )
        _, warnings, _ = rrc.check_record(data)
        self.assertEqual(warnings, [])

    def test_missing_counts_object_is_not_a_finding(self) -> None:
        data = record(
            breakdowns=[{"id": "sources", "scale": "nominal", "categories": ["a"]}]
        )
        _, warnings, _ = rrc.check_record(data)
        self.assertEqual(warnings, [])

    def test_several_omitted_categories_each_get_their_own_warning(self) -> None:
        data = record(
            breakdowns=[
                {
                    "id": "sources",
                    "scale": "nominal",
                    "categories": ["a", "b", "c"],
                    "counts": {},
                }
            ]
        )
        _, warnings, _ = rrc.check_record(data)
        self.assertEqual(len(warnings), 3)


class LoadRecordTests(unittest.TestCase):
    """load_record: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_sample(self) -> None:
        data = rrc.load_record(SAMPLE_RUN)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["steps"]), 3)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE_RUN)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                rrc.load_record(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * rrc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                rrc.load_record(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input error."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "run.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), record())
            self.assertEqual(rrc.main([str(path)]), 0)

    def test_exit_one_on_missing_core_field(self) -> None:
        data = record()
        del data["run"]
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), data)
            self.assertEqual(rrc.main([str(path)]), 1)

    def test_exit_zero_with_only_a_warning(self) -> None:
        data = record(
            breakdowns=[
                {
                    "id": "b",
                    "scale": "status",
                    "categories": ["pass", "blocked"],
                    "counts": {"pass": 1},
                }
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), data)
            self.assertEqual(rrc.main([str(path)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rrc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(rrc.main([str(path)]), 2)

    def test_exit_two_on_bad_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), ["not", "an", "object"])
            self.assertEqual(rrc.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real sample."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("RUN", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE_RUN.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.strip(), "steps=3 errors=0 warnings=0")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("run_record_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE_RUN), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-OP-02")
        self.assertEqual(fields["Stage"], "OP")
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
    """docs/operating-practices/run-logging-and-dashboards.md: every pasted
    output line, and the sample data it shows, are real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_at_least_one_output_fence(self) -> None:
        self.assertGreaterEqual(len(self.fences), 1)

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean = run_cli(str(SAMPLE_RUN))
        real_outputs = [clean.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_sample_run_record_matches_the_schema_shown_on_the_page(self) -> None:
        data = json.loads(SAMPLE_RUN.read_text(encoding="utf-8"))
        for field_name in ("schema_version", "run", "steps"):
            self.assertIn(field_name, data)
        scales = {row["scale"] for row in data["breakdowns"]}
        self.assertEqual(scales, {"nominal", "ordinal", "status"})

    def test_sample_run_record_has_no_real_person_name_as_operator(self) -> None:
        data = json.loads(SAMPLE_RUN.read_text(encoding="utf-8"))
        self.assertEqual(data["run"]["operator"], "the operator")

    def test_sample_run_record_names_no_real_vendor_or_model(self) -> None:
        text = SAMPLE_RUN.read_text(encoding="utf-8")
        for token in ("openai", "anthropic", "google", "gpt-", "claude", "gemini"):
            self.assertNotIn(token, text.lower(), token)

    def test_sample_events_file_has_four_to_six_lines(self) -> None:
        lines = [
            line
            for line in SAMPLE_EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertGreaterEqual(len(lines), 4)
        self.assertLessEqual(len(lines), 6)

    def test_sample_events_file_is_one_json_object_per_line(self) -> None:
        for line in SAMPLE_EVENTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)

    def test_sample_events_file_has_exactly_one_handoff_event(self) -> None:
        types = [
            json.loads(line)["type"]
            for line in SAMPLE_EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(types.count("handoff"), 1)

    def test_sample_events_file_starts_and_ends_the_run(self) -> None:
        lines = [
            json.loads(line)
            for line in SAMPLE_EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(lines[0]["type"], "run_start")
        self.assertEqual(lines[-1]["type"], "run_end")


if __name__ == "__main__":
    unittest.main()
