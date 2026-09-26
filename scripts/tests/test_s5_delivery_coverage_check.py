"""Unit tests for scripts/s5/delivery_coverage_check.py and
docs/stage-5/delivery-formats.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample delivery manifest and stem file (read-only). The page-output
tests re-run the real script and compare its output with the text
pasted on the page, so the page can never drift from the script.

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
SCRIPT = ROOT / "scripts" / "s5" / "delivery_coverage_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_stage5"
SAMPLE_MANIFEST = SAMPLE_DIR / "delivery" / "manifest.json"
SAMPLE_STEMS = SAMPLE_DIR / "stems" / "stems.json"
PAGE = ROOT / "docs" / "stage-5" / "delivery-formats.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("delivery_coverage_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dcc = load_module()


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


def stem(stem_id: str, broken: bool = False) -> dict[str, Any]:
    """A minimal stem entry; broken=True marks it broken_on_purpose."""
    data: dict[str, Any] = {"stem_id": stem_id}
    if broken:
        data["broken_on_purpose"] = True
    return data


class FindStemIdsTests(unittest.TestCase):
    """find_stem_ids: order, malformed entries, and the broken-copy skip."""

    def test_returns_ids_in_file_order(self) -> None:
        data = [stem("STEM-1.1-001"), stem("STEM-1.1-002")]
        self.assertEqual(dcc.find_stem_ids(data), ["STEM-1.1-001", "STEM-1.1-002"])

    def test_skips_entry_with_no_stem_id(self) -> None:
        data = [{"difficulty": "easy"}, stem("STEM-1.1-002")]
        self.assertEqual(dcc.find_stem_ids(data), ["STEM-1.1-002"])

    def test_skips_entry_that_is_not_an_object(self) -> None:
        data = ["not a stem", stem("STEM-1.1-002")]
        self.assertEqual(dcc.find_stem_ids(data), ["STEM-1.1-002"])

    def test_skips_entry_with_empty_stem_id(self) -> None:
        data = [{"stem_id": ""}, stem("STEM-1.1-002")]
        self.assertEqual(dcc.find_stem_ids(data), ["STEM-1.1-002"])

    def test_skips_broken_on_purpose_entry(self) -> None:
        data = [stem("STEM-1.1-001"), stem("STEM-1.1-BROKEN", broken=True)]
        self.assertEqual(dcc.find_stem_ids(data), ["STEM-1.1-001"])

    def test_not_a_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dcc.find_stem_ids({"stem_id": "STEM-1.1-001"})


class FindGapsTests(unittest.TestCase):
    """find_gaps: the exact line format, zero-kinds cases, and the summary."""

    def test_gap_line_format(self) -> None:
        lines = dcc.find_gaps(["STEM-2.1-002"], {})
        self.assertEqual(
            lines,
            ['gap: "STEM-2.1-002" is in the bank but not assigned to any deliverable'],
        )

    def test_no_gap_when_assigned_a_kind(self) -> None:
        lines = dcc.find_gaps(["STEM-2.1-001"], {"STEM-2.1-001": ["bank"]})
        self.assertEqual(lines, [])

    def test_missing_manifest_entry_is_a_gap(self) -> None:
        lines = dcc.find_gaps(["STEM-2.1-002"], {"STEM-2.1-001": ["bank"]})
        self.assertEqual(len(lines), 1)

    def test_empty_list_entry_is_a_gap(self) -> None:
        lines = dcc.find_gaps(["STEM-2.1-002"], {"STEM-2.1-002": []})
        self.assertEqual(len(lines), 1)

    def test_non_list_value_counts_as_zero_kinds(self) -> None:
        lines = dcc.find_gaps(["STEM-2.1-002"], {"STEM-2.1-002": "bank"})
        self.assertEqual(len(lines), 1)

    def test_manifest_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dcc.find_gaps(["STEM-2.1-001"], ["not", "an", "object"])

    def test_two_kinds_is_not_a_gap(self) -> None:
        manifest = {"STEM-2.1-001": ["bank", "chapter_quiz"]}
        self.assertEqual(dcc.find_gaps(["STEM-2.1-001"], manifest), [])


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_manifest(self) -> None:
        data = dcc.load_json(SAMPLE_MANIFEST)
        self.assertIsInstance(data, dict)

    def test_reads_a_real_stem_file(self) -> None:
        data = dcc.load_json(SAMPLE_STEMS)
        self.assertIsInstance(data, list)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE_MANIFEST)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                dcc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * dcc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                dcc.load_json(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 whether or not a gap is found, 2 for a usage or input error."""

    def write(self, tmp: Path, name: str, data: Any) -> Path:
        path = tmp / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_with_no_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = self.write(tmp_path, "m.json", {"STEM-1.1-001": ["bank"]})
            stems = self.write(tmp_path, "s.json", [stem("STEM-1.1-001")])
            self.assertEqual(dcc.main([str(manifest), str(stems)]), 0)

    def test_exit_zero_with_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = self.write(tmp_path, "m.json", {})
            stems = self.write(tmp_path, "s.json", [stem("STEM-1.1-001")])
            self.assertEqual(dcc.main([str(manifest), str(stems)]), 0)

    def test_exit_two_on_missing_manifest_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems = self.write(tmp_path, "s.json", [stem("STEM-1.1-001")])
            missing = tmp_path / "nope.json"
            self.assertEqual(dcc.main([str(missing), str(stems)]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bad = tmp_path / "bad.json"
            bad.write_text("not json", encoding="utf-8")
            stems = self.write(tmp_path, "s.json", [stem("STEM-1.1-001")])
            self.assertEqual(dcc.main([str(bad), str(stems)]), 2)

    def test_exit_two_on_stems_not_a_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = self.write(tmp_path, "m.json", {})
            stems = self.write(tmp_path, "s.json", {"stem_id": "STEM-1.1-001"})
            self.assertEqual(dcc.main([str(manifest), str(stems)]), 2)

    def test_exit_two_on_manifest_not_an_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = self.write(tmp_path, "m.json", ["not", "an", "object"])
            stems = self.write(tmp_path, "s.json", [stem("STEM-1.1-001")])
            self.assertEqual(dcc.main([str(manifest), str(stems)]), 2)

    def test_exit_two_on_usage_error(self) -> None:
        # argparse itself exits the process on a missing positional argument,
        # rather than returning from main(), so this checks SystemExit.
        with self.assertRaises(SystemExit) as cm:
            dcc.main(["only-one-argument.json"])
        self.assertEqual(cm.exception.code, 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real sample."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MANIFEST", result.stdout)
        self.assertIn("STEMS", result.stdout)

    def test_real_sample_flags_exactly_one_gap(self) -> None:
        manifest_rel = SAMPLE_MANIFEST.relative_to(ROOT).as_posix()
        stems_rel = SAMPLE_STEMS.relative_to(ROOT).as_posix()
        result = run_cli(manifest_rel, stems_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        lines = [line for line in result.stdout.splitlines() if line.startswith("gap")]
        self.assertEqual(
            lines,
            ['gap: "STEM-2.1-002" is in the bank but not assigned to any deliverable'],
        )
        self.assertIn("stems=2 unassigned=1", result.stdout)

    def test_broken_on_purpose_entry_is_not_counted(self) -> None:
        data = dcc.load_json(SAMPLE_STEMS)
        self.assertTrue(any(e.get("broken_on_purpose") for e in data))
        stem_ids = dcc.find_stem_ids(data)
        self.assertNotIn("STEM-2.1-BROKEN", stem_ids)
        self.assertEqual(len(stem_ids), 2)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"), str(SAMPLE_STEMS))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("delivery_coverage_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE_MANIFEST), str(SAMPLE_STEMS), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-S5-06")
        self.assertEqual(fields["Stage"], "S5")
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
    """docs/stage-5/delivery-formats.md: every pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_an_output_fence(self) -> None:
        self.assertGreaterEqual(len(self.fences), 1, "expected the sample run")

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        result = run_cli(str(SAMPLE_MANIFEST), str(SAMPLE_STEMS))
        real_outputs = [result.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_page_does_not_state_a_real_produced_count(self) -> None:
        # No real bank size, mock-exam count, chapter-quiz count, or
        # practice-test count is ever stated as a design rule (section 2).
        lowered = self.page_text.casefold()
        for phrase in ("mock exams,", "chapter quizzes,", "practice tests,"):
            self.assertNotRegex(lowered, r"\b\d+ " + re.escape(phrase))

    def test_manifest_json_matches_the_checked_in_sample(self) -> None:
        manifest_text = SAMPLE_MANIFEST.read_text(encoding="utf-8")
        manifest_data = json.loads(manifest_text)
        self.assertEqual(
            manifest_data,
            {"STEM-2.1-001": ["bank", "chapter_quiz"], "STEM-2.1-002": []},
        )


if __name__ == "__main__":
    unittest.main()
