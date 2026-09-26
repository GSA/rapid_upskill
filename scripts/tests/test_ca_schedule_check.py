"""Unit tests for scripts/ca/schedule_check.py and docs/certification-alignment.md.

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
SCRIPT = ROOT / "scripts" / "ca" / "schedule_check.py"
SAMPLE = (
    ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_batch8"
    / "schedule"
    / "schedule.json"
)
PAGE = ROOT / "docs" / "certification-alignment.md"
BROKEN_NEEDLE = '"total_minutes": 60'
BROKEN_REPLACEMENT = '"total_minutes": 130'


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("schedule_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load_module()


def chapter(
    number: int, tier: str, reading: int, active: int, total: int
) -> dict[str, Any]:
    """A minimal, otherwise-valid chapter entry."""
    return {
        "chapter": number,
        "importance_tier": tier,
        "reading_minutes": reading,
        "active_minutes": active,
        "total_minutes": total,
    }


def base_schedule() -> list[dict[str, Any]]:
    """A small, clean schedule: three chapters, ordered high, medium, low."""
    return [
        chapter(1, "high", 90, 30, 120),
        chapter(2, "medium", 60, 20, 80),
        chapter(3, "low", 45, 15, 60),
    ]


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


class CheckScheduleCleanTests(unittest.TestCase):
    """A clean schedule has no findings."""

    def test_clean_baseline_has_no_findings(self) -> None:
        errors, warnings, count = sc.check_schedule(base_schedule())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(count, 3)


class CheckScheduleErrorTests(unittest.TestCase):
    """The sum-mismatch error path."""

    def test_sum_mismatch_error(self) -> None:
        data = base_schedule()
        data[2]["total_minutes"] = 130
        errors, warnings, _ = sc.check_schedule(data)
        self.assertTrue(
            any("sum-mismatch" in e and "chapter 3" in e for e in errors), errors
        )
        self.assertIn(
            "sum-mismatch: chapter 3 reading_minutes (45) + active_minutes "
            "(15) = 60, not total_minutes (130)",
            errors,
        )

    def test_two_chapters_can_each_report_their_own_mismatch(self) -> None:
        data = base_schedule()
        data[0]["total_minutes"] = 999
        data[1]["total_minutes"] = 999
        errors, _, _ = sc.check_schedule(data)
        self.assertEqual(len(errors), 2)


class CheckScheduleWarningTests(unittest.TestCase):
    """The tier-order warning path; never changes error count."""

    def test_lower_tier_exceeding_higher_tier_warns(self) -> None:
        data = base_schedule()
        data[2]["total_minutes"] = 130
        data[2]["reading_minutes"] = 115
        errors, warnings, _ = sc.check_schedule(data)
        self.assertEqual(errors, [])
        self.assertEqual(
            warnings,
            [
                "tier-order: chapter 3 (low, total 130) exceeds "
                "chapter 1 (high, total 120)",
                "tier-order: chapter 3 (low, total 130) exceeds "
                "chapter 2 (medium, total 80)",
            ],
        )

    def test_equal_totals_across_tiers_do_not_warn(self) -> None:
        data = [
            chapter(1, "high", 60, 20, 80),
            chapter(2, "low", 60, 20, 80),
        ]
        errors, warnings, _ = sc.check_schedule(data)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_clean_order_has_no_warning(self) -> None:
        _, warnings, _ = sc.check_schedule(base_schedule())
        self.assertEqual(warnings, [])


class CheckScheduleInputErrorTests(unittest.TestCase):
    """A schedule that does not match the schema at all raises ValueError."""

    def test_not_a_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sc.check_schedule({"chapter": 1})

    def test_empty_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sc.check_schedule([])

    def test_entry_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sc.check_schedule(["not an object"])

    def test_missing_chapter_is_rejected(self) -> None:
        data = base_schedule()
        del data[0]["chapter"]
        with self.assertRaises(ValueError):
            sc.check_schedule(data)

    def test_missing_field_is_rejected(self) -> None:
        data = base_schedule()
        del data[0]["total_minutes"]
        with self.assertRaises(ValueError):
            sc.check_schedule(data)

    def test_bad_tier_is_rejected(self) -> None:
        data = base_schedule()
        data[0]["importance_tier"] = "urgent"
        with self.assertRaises(ValueError):
            sc.check_schedule(data)

    def test_non_numeric_minutes_is_rejected(self) -> None:
        data = base_schedule()
        data[0]["total_minutes"] = "one twenty"
        with self.assertRaises(ValueError):
            sc.check_schedule(data)


class LoadScheduleTests(unittest.TestCase):
    """load_schedule: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = sc.load_schedule(SAMPLE)
        self.assertEqual(len(data), 3)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                sc.load_schedule(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * sc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                sc.load_schedule(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input problem."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "schedule.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), base_schedule())
            self.assertEqual(sc.main([str(path)]), 0)

    def test_exit_one_on_sum_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_schedule()
            data[2]["total_minutes"] = 130
            path = self.write(Path(tmp), data)
            self.assertEqual(sc.main([str(path)]), 1)

    def test_exit_zero_with_only_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_schedule()
            data[2]["total_minutes"] = 130
            data[2]["reading_minutes"] = 115
            path = self.write(Path(tmp), data)
            self.assertEqual(sc.main([str(path)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(sc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(sc.main([str(path)]), 2)

    def test_exit_two_on_bad_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), {"not": "a list"})
            self.assertEqual(sc.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SCHEDULE", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "chapters=3 errors=0 warnings=0\n")
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("schedule_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a temporary copy."""

    def test_raising_chapter_threes_total_without_its_parts_breaks_both_checks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "schedule.json"
            original = SAMPLE.read_text(encoding="utf-8")
            self.assertEqual(original.count(BROKEN_NEEDLE), 1)
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1),
                encoding="utf-8",
            )
            result = run_cli(str(copy_path))
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "error sum-mismatch: chapter 3 reading_minutes (45) + "
            "active_minutes (15) = 60, not total_minutes (130)",
            result.stdout,
        )
        self.assertIn(
            "warning tier-order: chapter 3 (low, total 130) exceeds "
            "chapter 1 (high, total 120)",
            result.stdout,
        )
        self.assertIn(
            "warning tier-order: chapter 3 (low, total 130) exceeds "
            "chapter 2 (medium, total 80)",
            result.stdout,
        )
        self.assertIn("chapters=3 errors=1 warnings=2", result.stdout)


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
        self.assertEqual(fields["ID"], "X-CA-01")
        self.assertEqual(fields["Stage"], "CA")
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
    """docs/certification-alignment.md: every pasted output line is real."""

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
            copy_path = Path(tmp) / "schedule.json"
            original = SAMPLE.read_text(encoding="utf-8")
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1),
                encoding="utf-8",
            )
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
