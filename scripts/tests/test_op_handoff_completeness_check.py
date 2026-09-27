"""Unit tests for scripts/op/handoff_completeness_check.py and
docs/operating-practices/hand-off-documents-and-sessions.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory. The page-output tests re-run the real script and
compare its output with the text pasted on the page, so the page can never
drift from the script.

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
SCRIPT = ROOT / "scripts" / "op" / "handoff_completeness_check.py"
HANDOFFS = ROOT / "scripts" / "sample_data" / "git_basics_batch8" / "handoffs"
CLEAN_SAMPLE = HANDOFFS / "handoff.json"
NARRATIVE_SAMPLE = HANDOFFS / "handoff_narrative_only.json"
PAGE = ROOT / "docs" / "operating-practices" / "hand-off-documents-and-sessions.md"

REQUIRED_FIELDS = (
    "done",
    "pending",
    "artifact_locations",
    "open_decisions",
    "remaining_budget",
)


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("handoff_completeness_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hc = load_module()


def base_handoff() -> dict[str, Any]:
    """A minimal, otherwise-valid, structured hand-off document."""
    return {
        "done": ["Reviewed write-ups 1 through 5"],
        "pending": ["Review write-ups 7 and 8"],
        "artifact_locations": {"comments": "work/comments/"},
        "open_decisions": ["Whether write-up 6 needs a second reviewer"],
        "remaining_budget": {"writeups_remaining": 3},
    }


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


class CheckHandoffCleanTests(unittest.TestCase):
    """A fully structured hand-off has no findings."""

    def test_clean_baseline_has_no_findings(self) -> None:
        self.assertEqual(hc.check_handoff(base_handoff()), [])


class CheckHandoffMissingFieldTests(unittest.TestCase):
    """The missing-field finding path: one finding per missing field."""

    def test_one_missing_field_is_one_finding(self) -> None:
        data = base_handoff()
        del data["pending"]
        findings = hc.check_handoff(data)
        self.assertEqual(
            findings, ["missing-field: the hand-off has no 'pending' field"]
        )

    def test_every_required_field_can_be_reported_missing_on_its_own(self) -> None:
        for field_name in REQUIRED_FIELDS:
            data = base_handoff()
            del data[field_name]
            findings = hc.check_handoff(data)
            self.assertEqual(
                findings,
                [f"missing-field: the hand-off has no '{field_name}' field"],
                field_name,
            )

    def test_two_missing_fields_are_two_findings(self) -> None:
        data = base_handoff()
        del data["pending"]
        del data["open_decisions"]
        findings = hc.check_handoff(data)
        self.assertEqual(len(findings), 2)
        self.assertTrue(any("pending" in f for f in findings))
        self.assertTrue(any("open_decisions" in f for f in findings))

    def test_extra_fields_alongside_the_required_ones_do_not_hide_a_gap(self) -> None:
        data = base_handoff()
        del data["remaining_budget"]
        data["extra_note"] = "not one of the five fields"
        findings = hc.check_handoff(data)
        self.assertEqual(
            findings,
            ["missing-field: the hand-off has no 'remaining_budget' field"],
        )


class CheckHandoffNarrativeOnlyTests(unittest.TestCase):
    """The narrative-only finding path: one finding, not five."""

    def test_note_only_shape_is_one_narrative_only_finding(self) -> None:
        findings = hc.check_handoff({"note": "Pick up where I left off."})
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].startswith("narrative-only:"))
        for field_name in REQUIRED_FIELDS:
            self.assertIn(field_name, findings[0])

    def test_empty_object_is_also_narrative_only(self) -> None:
        findings = hc.check_handoff({})
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].startswith("narrative-only:"))


class CheckHandoffInputErrorTests(unittest.TestCase):
    """A hand-off that is not a JSON object at all raises ValueError."""

    def test_a_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            hc.check_handoff(["done", "pending"])

    def test_a_string_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            hc.check_handoff("note text")


class LoadHandoffTests(unittest.TestCase):
    """load_handoff: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = hc.load_handoff(CLEAN_SAMPLE)
        self.assertIsInstance(data, dict)
        self.assertIn("done", data)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(CLEAN_SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                hc.load_handoff(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * hc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                hc.load_handoff(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any finding, 2 for a usage or input problem."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "handoff.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), base_handoff())
            self.assertEqual(hc.main([str(path)]), 0)

    def test_exit_one_on_missing_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_handoff()
            del data["done"]
            path = self.write(Path(tmp), data)
            self.assertEqual(hc.main([str(path)]), 1)

    def test_exit_one_on_narrative_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), {"note": "pick up where I left off"})
            self.assertEqual(hc.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(hc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(hc.main([str(path)]), 2)

    def test_exit_two_on_a_json_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), ["done", "pending"])
            self.assertEqual(hc.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HANDOFF", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = CLEAN_SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "handoff=1 errors=0\n")
        self.assertEqual(result.stderr, "")

    def test_narrative_only_sample_from_the_repository_root(self) -> None:
        rel = NARRATIVE_SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("narrative-only:", result.stdout)
        self.assertIn("handoff=1 errors=1", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("handoff_completeness_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(CLEAN_SAMPLE), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-OP-04")
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

    def test_test_source_is_ascii_only(self) -> None:
        self.assertTrue(Path(__file__).read_text(encoding="utf-8").isascii())


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/operating-practices/hand-off-documents-and-sessions.md: every
    pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected a clean and a broken run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean = run_cli(str(CLEAN_SAMPLE))
        narrative = run_cli(str(NARRATIVE_SAMPLE))
        real_outputs = [clean.stdout, narrative.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_json_worked_illustration_matches_the_checked_in_sample(self) -> None:
        matches = re.findall(r"```json\n(.*?)\n```", self.page_text, re.DOTALL)
        self.assertEqual(len(matches), 1, "expected exactly one JSON code fence")
        page_data = json.loads(matches[0])
        sample_data = json.loads(CLEAN_SAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(page_data, sample_data)


if __name__ == "__main__":
    unittest.main()
