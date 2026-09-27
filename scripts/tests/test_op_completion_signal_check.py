"""Unit tests for scripts/op/completion_signal_check.py and
docs/operating-practices/agent-orchestration-patterns.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample outputs (read-only). The page-output tests re-run the real script
and compare its output with the text pasted on the page, so the page can
never drift from the script.

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
SCRIPT = ROOT / "scripts" / "op" / "completion_signal_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_batch8" / "worker_briefs"
SAMPLE_TEST = SAMPLE_DIR / "completion_test.json"
SAMPLE_OUTPUTS = SAMPLE_DIR / "outputs"
SAMPLE_OUTPUTS_BROKEN = SAMPLE_DIR / "outputs_broken"
PAGE = ROOT / "docs" / "operating-practices" / "agent-orchestration-patterns.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("completion_signal_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


csc = load_module()


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


def write_json(directory: Path, name: str, data: Any) -> Path:
    """Write one JSON file named `name` inside `directory`; returns its path."""
    path = directory / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class IsEmptyTests(unittest.TestCase):
    """_is_empty: None and an empty string, list or dict are empty; nothing else."""

    def test_none_is_empty(self) -> None:
        self.assertTrue(csc._is_empty(None))

    def test_empty_string_list_and_dict_are_empty(self) -> None:
        self.assertTrue(csc._is_empty(""))
        self.assertTrue(csc._is_empty([]))
        self.assertTrue(csc._is_empty({}))

    def test_non_empty_string_list_and_dict_are_not_empty(self) -> None:
        self.assertFalse(csc._is_empty("a"))
        self.assertFalse(csc._is_empty([0]))
        self.assertFalse(csc._is_empty({"k": "v"}))

    def test_zero_and_false_are_not_empty(self) -> None:
        self.assertFalse(csc._is_empty(0))
        self.assertFalse(csc._is_empty(False))
        self.assertFalse(csc._is_empty(0.0))


class LoadCompletionTestTests(unittest.TestCase):
    """load_completion_test: reading, the size cap, and the symlink refusal."""

    def test_reads_the_real_sample(self) -> None:
        fields = csc.load_completion_test(SAMPLE_TEST)
        self.assertEqual(fields, ["document_id", "status", "findings"])

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE_TEST)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                csc.load_completion_test(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * csc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                csc.load_completion_test(big)

    def test_not_an_object_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "test.json", ["a", "b"])
            with self.assertRaises(ValueError):
                csc.load_completion_test(path)

    def test_missing_required_fields_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "test.json", {})
            with self.assertRaises(ValueError):
                csc.load_completion_test(path)

    def test_empty_required_fields_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "test.json", {"required_fields": []})
            with self.assertRaises(ValueError):
                csc.load_completion_test(path)

    def test_required_fields_not_a_list_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "test.json", {"required_fields": "status"})
            with self.assertRaises(ValueError):
                csc.load_completion_test(path)

    def test_required_fields_with_empty_entry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = {"required_fields": ["status", ""]}
            path = write_json(Path(tmp), "test.json", data)
            with self.assertRaises(ValueError):
                csc.load_completion_test(path)

    def test_required_fields_with_non_string_entry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = {"required_fields": ["status", 3]}
            path = write_json(Path(tmp), "test.json", data)
            with self.assertRaises(ValueError):
                csc.load_completion_test(path)


class CheckOutputsTests(unittest.TestCase):
    """check_outputs: every finding path, on small in-memory fixtures."""

    def test_clean_directory_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", {"status": "done"})
            findings, count = csc.check_outputs(Path(tmp), ["status"])
            self.assertEqual(findings, [])
            self.assertEqual(count, 1)

    def test_missing_field_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", {"other": "value"})
            findings, _ = csc.check_outputs(Path(tmp), ["status"])
            self.assertTrue(
                any("missing-field" in f and "a.json" in f for f in findings), findings
            )

    def test_empty_field_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", {"status": ""})
            findings, _ = csc.check_outputs(Path(tmp), ["status"])
            self.assertTrue(
                any("empty-field" in f and "a.json" in f for f in findings), findings
            )

    def test_null_field_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", {"status": None})
            findings, _ = csc.check_outputs(Path(tmp), ["status"])
            self.assertTrue(any("empty-field" in f for f in findings), findings)

    def test_zero_and_false_fields_are_not_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", {"count": 0, "flag": False})
            findings, _ = csc.check_outputs(Path(tmp), ["count", "flag"])
            self.assertEqual(findings, [])

    def test_invalid_json_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.json").write_text("not json", encoding="utf-8")
            findings, count = csc.check_outputs(Path(tmp), ["status"])
            self.assertEqual(count, 1)
            self.assertTrue(
                any("missing" in f and "not valid JSON" in f for f in findings),
                findings,
            )

    def test_json_that_is_not_an_object_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", ["not", "an", "object"])
            findings, _ = csc.check_outputs(Path(tmp), ["status"])
            self.assertTrue(
                any("missing" in f and "not a JSON object" in f for f in findings),
                findings,
            )

    def test_oversized_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "a.json"
            big.write_text("[" + "1," * csc.MAX_BYTES + "1]", encoding="utf-8")
            findings, count = csc.check_outputs(Path(tmp), ["status"])
            self.assertEqual(count, 1)
            self.assertTrue(
                any("missing" in f and "bytes" in f for f in findings), findings
            )

    def test_symlinked_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            real = write_json(Path(tmp), "real.json", {"status": "done"})
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            findings, count = csc.check_outputs(Path(tmp), ["status"])
            self.assertEqual(count, 2)
            self.assertTrue(
                any("link.json" in f and "symlink" in f for f in findings), findings
            )

    def test_hidden_file_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".hidden.json").write_text("not json", encoding="utf-8")
            findings, count = csc.check_outputs(Path(tmp), ["status"])
            self.assertEqual((findings, count), ([], 0))

    def test_subfolder_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "nested").mkdir()
            findings, count = csc.check_outputs(Path(tmp), ["status"])
            self.assertEqual((findings, count), ([], 0))

    def test_files_are_checked_in_sorted_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "b.json", {})
            write_json(Path(tmp), "a.json", {})
            findings, _ = csc.check_outputs(Path(tmp), ["status"])
            self.assertTrue(findings[0].startswith("missing-field: a.json"))
            self.assertTrue(findings[1].startswith("missing-field: b.json"))

    def test_one_finding_per_missing_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp), "a.json", {})
            findings, _ = csc.check_outputs(Path(tmp), ["status", "findings"])
            self.assertEqual(len(findings), 2)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any finding, 2 for a usage or input error."""

    def test_exit_zero_on_clean_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outputs = Path(tmp) / "outputs"
            outputs.mkdir()
            write_json(outputs, "a.json", {"status": "done"})
            test_path = write_json(
                Path(tmp), "test.json", {"required_fields": ["status"]}
            )
            self.assertEqual(csc.main([str(outputs), str(test_path)]), 0)

    def test_exit_one_on_missing_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outputs = Path(tmp) / "outputs"
            outputs.mkdir()
            write_json(outputs, "a.json", {})
            test_path = write_json(
                Path(tmp), "test.json", {"required_fields": ["status"]}
            )
            self.assertEqual(csc.main([str(outputs), str(test_path)]), 1)

    def test_exit_two_on_missing_outputs_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            test_path = write_json(
                Path(tmp), "test.json", {"required_fields": ["status"]}
            )
            missing = Path(tmp) / "nope"
            self.assertEqual(csc.main([str(missing), str(test_path)]), 2)

    def test_exit_two_when_outputs_dir_is_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            not_a_dir = Path(tmp) / "outputs"
            not_a_dir.write_text("nope", encoding="utf-8")
            test_path = write_json(
                Path(tmp), "test.json", {"required_fields": ["status"]}
            )
            self.assertEqual(csc.main([str(not_a_dir), str(test_path)]), 2)

    def test_exit_two_on_missing_completion_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outputs = Path(tmp) / "outputs"
            outputs.mkdir()
            missing = Path(tmp) / "nope.json"
            self.assertEqual(csc.main([str(outputs), str(missing)]), 2)

    def test_exit_two_on_malformed_completion_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outputs = Path(tmp) / "outputs"
            outputs.mkdir()
            test_path = write_json(Path(tmp), "test.json", {"required_fields": []})
            self.assertEqual(csc.main([str(outputs), str(test_path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real samples."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OUTPUTS_DIR", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        outputs_rel = SAMPLE_OUTPUTS.relative_to(ROOT).as_posix()
        test_rel = SAMPLE_TEST.relative_to(ROOT).as_posix()
        result = run_cli(outputs_rel, test_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.strip(), "outputs=4 errors=0")

    def test_broken_sample_flags_exactly_two_findings(self) -> None:
        outputs_rel = SAMPLE_OUTPUTS_BROKEN.relative_to(ROOT).as_posix()
        test_rel = SAMPLE_TEST.relative_to(ROOT).as_posix()
        result = run_cli(outputs_rel, test_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("missing-field: doc-02.json has no 'status'", result.stdout)
        self.assertIn(
            "empty-field: doc-03.json field 'findings' is empty", result.stdout
        )
        self.assertIn("outputs=4 errors=2", result.stdout)

    def test_missing_outputs_dir_is_a_clean_input_error(self) -> None:
        test_rel = SAMPLE_TEST.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope"), test_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("completion_signal_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        outputs_rel = SAMPLE_OUTPUTS.relative_to(ROOT).as_posix()
        test_rel = SAMPLE_TEST.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(ROOT / outputs_rel), str(ROOT / test_rel), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-OP-05")
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
    """docs/operating-practices/agent-orchestration-patterns.md: every pasted
    output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_a_clean_and_a_broken_fence(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected a clean and a break-on-purpose run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean = run_cli(
            str(SAMPLE_OUTPUTS.relative_to(ROOT)),
            str(SAMPLE_TEST.relative_to(ROOT)),
            cwd=ROOT,
        )
        broken = run_cli(
            str(SAMPLE_OUTPUTS_BROKEN.relative_to(ROOT)),
            str(SAMPLE_TEST.relative_to(ROOT)),
            cwd=ROOT,
        )
        real_outputs = [clean.stdout, broken.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_sample_outputs_match_the_completion_test(self) -> None:
        fields = json.loads(SAMPLE_TEST.read_text(encoding="utf-8"))["required_fields"]
        self.assertEqual(fields, ["document_id", "status", "findings"])

    def test_broken_sample_differs_from_clean_in_two_files_only(self) -> None:
        clean_names = sorted(p.name for p in SAMPLE_OUTPUTS.iterdir())
        broken_names = sorted(p.name for p in SAMPLE_OUTPUTS_BROKEN.iterdir())
        self.assertEqual(clean_names, broken_names)
        differing = [
            name
            for name in clean_names
            if (SAMPLE_OUTPUTS / name).read_text(encoding="utf-8")
            != (SAMPLE_OUTPUTS_BROKEN / name).read_text(encoding="utf-8")
        ]
        self.assertEqual(sorted(differing), ["doc-02.json", "doc-03.json"])


if __name__ == "__main__":
    unittest.main()
