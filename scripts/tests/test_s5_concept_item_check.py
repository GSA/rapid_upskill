"""Unit tests for scripts/s5/concept_item_check.py and
docs/stage-5/misconception-to-distractor-bridge.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory. The page-output tests re-run the real script and
compare its output with the text pasted on the page, so the page can
never drift from the script.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import ast
import copy
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
SCRIPT = ROOT / "scripts" / "s5" / "concept_item_check.py"
SAMPLE = (
    ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_stage5"
    / "concept_items"
    / "items.json"
)
PAGE = ROOT / "docs" / "stage-5" / "misconception-to-distractor-bridge.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("concept_item_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cic = load_module()


def item(item_id: str, misconceptions: int = 2) -> dict[str, Any]:
    """A minimal, otherwise-valid assessment concept item."""
    return {
        "id": item_id,
        "chapter": 1,
        "section": "A test section",
        "description": "A test concept.",
        "cognitive_level": "knowledge",
        "bloom_level": "understand",
        "key_concepts": ["a", "b"],
        "misconceptions": [
            {"text": f"Wrong belief {n}.", "source_id": "SRC-001"}
            for n in range(misconceptions)
        ],
        "references": ['SRC-001, "A test section"'],
        "dependencies": [],
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


class CheckItemsTests(unittest.TestCase):
    """check_items: every finding path, on small in-memory fixtures."""

    def test_clean_items_have_no_findings(self) -> None:
        findings = cic.check_items([item("ACI-1-001"), item("ACI-2-001")])
        self.assertEqual(findings, [])

    def test_one_misconception_is_a_gap(self) -> None:
        findings = cic.check_items([item("ACI-1-001", misconceptions=1)])
        self.assertTrue(
            any(
                'gap: "ACI-1-001" has 1 misconception, needs at least 2' in f
                for f in findings
            ),
            findings,
        )

    def test_zero_misconceptions_is_a_gap(self) -> None:
        findings = cic.check_items([item("ACI-1-001", misconceptions=0)])
        self.assertTrue(
            any(
                'gap: "ACI-1-001" has 0 misconceptions, needs at least 2' in f
                for f in findings
            ),
            findings,
        )

    def test_missing_misconceptions_field_counts_as_zero(self) -> None:
        data = item("ACI-1-001")
        del data["misconceptions"]
        findings = cic.check_items([data])
        self.assertTrue(any("has 0 misconceptions" in f for f in findings), findings)

    def test_non_list_misconceptions_field_counts_as_zero(self) -> None:
        data = item("ACI-1-001")
        data["misconceptions"] = "not a list"
        findings = cic.check_items([data])
        self.assertTrue(any("has 0 misconceptions" in f for f in findings), findings)

    def test_malformed_id_is_flagged(self) -> None:
        findings = cic.check_items([item("KI-1-001")])
        self.assertTrue(
            any("malformed-id" in f and "KI-1-001" in f for f in findings), findings
        )

    def test_short_sequence_is_malformed(self) -> None:
        findings = cic.check_items([item("ACI-1-1")])
        self.assertTrue(any("malformed-id" in f for f in findings), findings)

    def test_non_numeric_chapter_is_malformed(self) -> None:
        findings = cic.check_items([item("ACI-one-001")])
        self.assertTrue(any("malformed-id" in f for f in findings), findings)

    def test_duplicate_id_is_flagged(self) -> None:
        findings = cic.check_items([item("ACI-1-001"), item("ACI-1-001")])
        self.assertTrue(any("duplicate-id" in f for f in findings), findings)

    def test_duplicate_id_reported_once_per_repeat(self) -> None:
        findings = cic.check_items(
            [item("ACI-1-001"), item("ACI-1-001"), item("ACI-1-001")]
        )
        self.assertEqual(sum(1 for f in findings if "duplicate-id" in f), 2)


class ValidateItemsTests(unittest.TestCase):
    """validate_items: the input-error boundary (exit 2, not a finding)."""

    def test_top_level_must_be_a_list(self) -> None:
        with self.assertRaises(ValueError):
            cic.validate_items({"not": "a list"})

    def test_entry_must_be_an_object(self) -> None:
        with self.assertRaises(ValueError):
            cic.validate_items(["not an object"])

    def test_entry_needs_an_id(self) -> None:
        data = item("ACI-1-001")
        del data["id"]
        with self.assertRaises(ValueError):
            cic.validate_items([data])

    def test_valid_list_passes_through(self) -> None:
        items = cic.validate_items([item("ACI-1-001")])
        self.assertEqual(len(items), 1)


class LoadItemsTests(unittest.TestCase):
    """load_items: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = cic.load_items(SAMPLE)
        self.assertEqual(len(data), 3)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                cic.load_items(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * cic.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                cic.load_items(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any finding, 2 for a usage or input problem."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "items.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), [item("ACI-1-001")])
            self.assertEqual(cic.main([str(path)]), 0)

    def test_exit_one_on_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), [item("ACI-1-001", misconceptions=1)])
            self.assertEqual(cic.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cic.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(cic.main([str(path)]), 2)

    def test_exit_two_on_non_list_top_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), {"not": "a list"})
            self.assertEqual(cic.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ITEMS", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("items=3 errors=0", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("concept_item_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


def _broken_copy() -> Any:
    """The sample data with one of ACI-1-001's two misconceptions removed."""
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    broken = copy.deepcopy(data)
    for entry in broken:
        if entry["id"] == "ACI-1-001":
            if len(entry["misconceptions"]) != 2:
                raise ValueError("ACI-1-001 no longer has exactly 2 misconceptions")
            entry["misconceptions"].pop()
    return broken


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a temporary copy."""

    def test_removing_one_misconception_from_aci_1_001_is_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "items.json"
            copy_path.write_text(json.dumps(_broken_copy()), encoding="utf-8")
            result = run_cli(str(copy_path))
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            'gap: "ACI-1-001" has 1 misconception, needs at least 2', result.stdout
        )
        self.assertIn("items=3 errors=1", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S5-01")
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


class SampleDataTests(unittest.TestCase):
    """scripts/sample_data/.../concept_items/items.json: the fixed fixture ids."""

    def test_fixture_ids_match_the_shared_contract(self) -> None:
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in data]
        self.assertEqual(ids, ["ACI-1-001", "ACI-2-001", "ACI-2-002"])

    def test_every_item_has_at_least_two_misconceptions(self) -> None:
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        for entry in data:
            self.assertGreaterEqual(len(entry["misconceptions"]), 2, entry["id"])

    def test_sample_file_is_ascii_only(self) -> None:
        self.assertTrue(SAMPLE.read_text(encoding="utf-8").isascii())

    def test_sample_file_has_no_percent_sign(self) -> None:
        self.assertNotIn("%", SAMPLE.read_text(encoding="utf-8"))


class PageOutputTests(unittest.TestCase):
    """docs/stage-5/misconception-to-distractor-bridge.md: pasted output is real."""

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
        clean = run_cli(str(SAMPLE))
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "items.json"
            copy_path.write_text(json.dumps(_broken_copy()), encoding="utf-8")
            broken = run_cli(str(copy_path))
        real_outputs = [clean.stdout, broken.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )


if __name__ == "__main__":
    unittest.main()
