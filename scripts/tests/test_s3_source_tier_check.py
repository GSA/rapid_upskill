"""Unit tests for scripts/s3/source_tier_check.py and
docs/stage-3/tiering-and-remediation.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample source-tiers file (read-only). The page-output test re-runs the
real script and compares its output with the text pasted on the page,
so the page can never drift from the script.

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

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "s3" / "source_tier_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_stage3" / "tiers"
SAMPLE = SAMPLE_DIR / "source_tiers.json"
PAGE = ROOT / "docs" / "stage-3" / "tiering-and-remediation.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("source_tier_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stc = load_module()


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


def write_json(tmp: Path, name: str, data: object) -> Path:
    path = tmp / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


VALID_DATA = [
    {"source_id": "SRC-001", "tier": 1, "rationale": "official docs"},
    {"source_id": "SRC-002", "tier": 2, "rationale": "expert writing"},
    {"source_id": "SRC-003", "tier": 3, "rationale": "individual writing"},
]


class LoadTiersTests(unittest.TestCase):
    """load_tiers: the fixture shape and every validation rule."""

    def test_loads_valid_entries_in_order(self) -> None:
        entries = stc.load_tiers(VALID_DATA)
        self.assertEqual(
            [entry.source_id for entry in entries], ["SRC-001", "SRC-002", "SRC-003"]
        )
        self.assertEqual([entry.tier for entry in entries], [1, 2, 3])

    def test_rejects_non_list(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers({"source_id": "SRC-001", "tier": 1, "rationale": "x"})

    def test_rejects_empty_list(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([])

    def test_rejects_non_object_entry(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers(["not-an-object"])

    def test_rejects_missing_source_id(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"tier": 1, "rationale": "x"}])

    def test_rejects_empty_source_id(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "", "tier": 1, "rationale": "x"}])

    def test_rejects_duplicate_source_id(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers(
                [
                    {"source_id": "SRC-001", "tier": 1, "rationale": "x"},
                    {"source_id": "SRC-001", "tier": 2, "rationale": "y"},
                ]
            )

    def test_rejects_non_int_tier(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "SRC-001", "tier": "1", "rationale": "x"}])

    def test_rejects_boolean_tier(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "SRC-001", "tier": True, "rationale": "x"}])

    def test_rejects_tier_below_range(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "SRC-001", "tier": 0, "rationale": "x"}])

    def test_rejects_tier_above_range(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "SRC-001", "tier": 5, "rationale": "x"}])

    def test_rejects_missing_rationale(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "SRC-001", "tier": 1}])

    def test_rejects_empty_rationale(self) -> None:
        with self.assertRaises(ValueError):
            stc.load_tiers([{"source_id": "SRC-001", "tier": 1, "rationale": ""}])


class LowTierFractionTests(unittest.TestCase):
    """low_tier_fraction: Tier 3 or below counts as low tier."""

    def test_counts_tier_3_and_4_as_low(self) -> None:
        entries = stc.load_tiers(
            [
                {"source_id": "SRC-001", "tier": 1, "rationale": "x"},
                {"source_id": "SRC-002", "tier": 2, "rationale": "x"},
                {"source_id": "SRC-003", "tier": 3, "rationale": "x"},
                {"source_id": "SRC-004", "tier": 4, "rationale": "x"},
            ]
        )
        low, fraction = stc.low_tier_fraction(entries)
        self.assertEqual(low, 2)
        self.assertAlmostEqual(fraction, 0.5)

    def test_zero_low_tier_sources(self) -> None:
        entries = stc.load_tiers(
            [
                {"source_id": "SRC-001", "tier": 1, "rationale": "x"},
                {"source_id": "SRC-002", "tier": 2, "rationale": "x"},
            ]
        )
        low, fraction = stc.low_tier_fraction(entries)
        self.assertEqual(low, 0)
        self.assertEqual(fraction, 0.0)


class MainExitCodeTests(unittest.TestCase):
    """main(): never 1; 0 whether or not the warning prints; 2 on bad input."""

    def test_exit_zero_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "tiers.json", VALID_DATA)
            self.assertEqual(stc.main([str(path)]), 0)

    def test_exit_zero_without_warning_when_limit_is_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "tiers.json", VALID_DATA)
            self.assertEqual(stc.main([str(path), "--max-low-tier-fraction", "0.9"]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(stc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_bad_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertEqual(stc.main([str(path)]), 2)

    def test_exit_two_on_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "tiers.json", [])
            self.assertEqual(stc.main([str(path)]), 2)

    def test_exit_two_on_fraction_above_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "tiers.json", VALID_DATA)
            self.assertEqual(stc.main([str(path), "--max-low-tier-fraction", "1.5"]), 2)

    def test_exit_two_on_negative_fraction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "tiers.json", VALID_DATA)
            self.assertEqual(
                stc.main([str(path), "--max-low-tier-fraction", "-0.1"]), 2
            )

    def test_exit_two_on_usage_error(self) -> None:
        # argparse itself exits the process on a bad option value, rather
        # than returning from main(), so this checks SystemExit.
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "tiers.json", VALID_DATA)
            with self.assertRaises(SystemExit) as cm:
                stc.main([str(path), "--max-low-tier-fraction", "not-a-number"])
            self.assertEqual(cm.exception.code, 2)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = write_json(Path(tmp), "real.json", VALID_DATA)
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            self.assertEqual(stc.main([str(link)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real sample."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TIERS", result.stdout)
        self.assertIn("--max-low-tier-fraction", result.stdout)

    def test_real_sample_warns_and_exits_zero(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("warning low-tier:", result.stdout)
        self.assertIn(
            "2 of 7 sources (0.29) are Tier 3 or below, over the 0.25 limit",
            result.stdout,
        )
        self.assertIn("sources=7 low_tier=2", result.stdout)

    def test_real_sample_has_no_warning_when_limit_is_raised(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, "--max-low-tier-fraction", "0.9", cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("warning", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("source_tier_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(rel, cwd=ROOT)
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
        self.assertEqual(fields["ID"], "X-S3-04")
        self.assertEqual(fields["Stage"], "S3")
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

    def test_docstring_states_the_never_exits_one_limit(self) -> None:
        lowered = " ".join(self.docstring.casefold().split())
        self.assertIn("never exits 1 on its own", lowered)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-3/tiering-and-remediation.md: every pasted line is real."""

    page_text: str
    flat_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        # Prose wraps across lines in the source file; a phrase search
        # needs single spaces where the source has a line break.
        cls.flat_text = " ".join(cls.page_text.split())
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_an_output_fence(self) -> None:
        self.assertGreaterEqual(len(self.fences), 1)

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        real_run = run_cli(rel, cwd=ROOT)
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertIn(line, real_run.stdout)

    def test_page_states_the_never_exits_one_limit_near_the_command(self) -> None:
        # The plan requires this right next to the script block, not only
        # in Common failures: check it appears before that heading.
        common_failures_pos = self.page_text.find("## Common failures")
        self.assertGreater(common_failures_pos, -1)
        before_common_failures = " ".join(self.page_text[:common_failures_pos].split())
        self.assertIn("never exits 1 on its own", before_common_failures)

    def test_page_does_not_use_an_hour_banded_backlog_figure(self) -> None:
        lowered = self.flat_text.casefold()
        for token in ("~9h", "~18h", "~120h", "9 hours", "18 hours", "120 hours"):
            self.assertNotIn(token, lowered)

    def test_page_names_both_checklists_distinctly(self) -> None:
        self.assertIn("five-point", self.flat_text)
        self.assertIn("citation-verification checklist", self.flat_text)

    def test_page_states_all_five_escalation_matrix_fields(self) -> None:
        for token in ("type", "severity", "owner role", "response-time target"):
            self.assertIn(token, self.flat_text.casefold())


if __name__ == "__main__":
    unittest.main()
