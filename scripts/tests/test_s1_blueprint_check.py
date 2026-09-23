"""Unit tests for scripts/s1/blueprint_check.py and docs/stage-1/blueprint.md.

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
SCRIPT = ROOT / "scripts" / "s1" / "blueprint_check.py"
SAMPLE = ROOT / "scripts" / "sample_data" / "git_basics" / "blueprint.json"
PAGE = ROOT / "docs" / "stage-1" / "blueprint.md"
BROKEN_NEEDLE = '"weight": 30,'
BROKEN_REPLACEMENT = '"weight": 31,'


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("blueprint_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bc = load_module()


def domain(
    domain_id: str, weight: int, objectives: list[dict[str, Any]]
) -> dict[str, Any]:
    """A minimal, otherwise-valid domain."""
    return {
        "id": domain_id,
        "name": f"Domain {domain_id}",
        "weight": weight,
        "objectives": objectives,
    }


def objective(objective_id: str, bloom: str, tier: int = 2) -> dict[str, Any]:
    """A minimal, otherwise-valid objective."""
    return {
        "id": objective_id,
        "text": f"Do the thing for {objective_id}.",
        "bloom": bloom,
        "tier": tier,
    }


def base_blueprint() -> dict[str, Any]:
    """A small, clean blueprint: two domains, weights summing to 100."""
    return {
        "schema_version": "1.0.0",
        "program": "Test Program",
        "bank_size": 10,
        "domains": [
            domain(
                "D1",
                50,
                [objective("D1.1", "understand", 1), objective("D1.2", "apply", 2)],
            ),
            domain(
                "D2",
                50,
                [objective("D2.1", "analyze", 2), objective("D2.2", "create", 3)],
            ),
        ],
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


class ParseLevelsTests(unittest.TestCase):
    """parse_levels: default, custom list, and rejected input."""

    def test_default_is_the_six_level_scale(self) -> None:
        self.assertEqual(
            bc.parse_levels(None),
            ("remember", "understand", "apply", "analyze", "evaluate", "create"),
        )

    def test_custom_list_is_split_and_trimmed(self) -> None:
        self.assertEqual(bc.parse_levels(" a , b ,c"), ("a", "b", "c"))

    def test_empty_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bc.parse_levels("a,,c")

    def test_repeated_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bc.parse_levels("a,b,a")


class CrossTabLinesTests(unittest.TestCase):
    """cross_tab_lines: one row per domain, a dash for a zero cell."""

    def test_format_and_dash(self) -> None:
        cross_tab = {"D1": {"a": 1, "b": 0, "c": 2}}
        self.assertEqual(
            bc.cross_tab_lines(cross_tab, ("a", "b", "c")), ["D1  a=1 b=- c=2"]
        )

    def test_one_row_per_domain_in_order(self) -> None:
        cross_tab = {"D2": {"a": 0}, "D1": {"a": 3}}
        self.assertEqual(bc.cross_tab_lines(cross_tab, ("a",)), ["D2  a=-", "D1  a=3"])


class CheckBlueprintErrorTests(unittest.TestCase):
    """Every error path, exercised on a small in-memory fixture."""

    def check(self, data: dict[str, Any]) -> tuple[list[str], list[str]]:
        errors, warnings, _, _, _ = bc.check_blueprint(data, bc.DEFAULT_LEVELS)
        return errors, warnings

    def test_clean_baseline_has_no_findings(self) -> None:
        errors, warnings = self.check(base_blueprint())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_weight_sum_error(self) -> None:
        data = base_blueprint()
        data["domains"][1]["weight"] = 51
        errors, _ = self.check(data)
        self.assertTrue(any("weight-sum" in e and "101" in e for e in errors), errors)

    def test_missing_domain_field_error(self) -> None:
        data = base_blueprint()
        del data["domains"][0]["name"]
        errors, _ = self.check(data)
        self.assertTrue(
            any("missing-field" in e and "'name'" in e for e in errors), errors
        )

    def test_missing_objective_field_error(self) -> None:
        data = base_blueprint()
        del data["domains"][0]["objectives"][0]["text"]
        errors, _ = self.check(data)
        self.assertTrue(
            any("missing-field" in e and "'text'" in e for e in errors), errors
        )

    def test_bad_bloom_error(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"][0]["bloom"] = "invent"
        errors, _ = self.check(data)
        self.assertTrue(any("bad-bloom" in e and "invent" in e for e in errors), errors)

    def test_bad_tier_out_of_range_error(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"][0]["tier"] = 5
        errors, _ = self.check(data)
        self.assertTrue(any("bad-tier" in e for e in errors), errors)

    def test_bad_tier_wrong_type_error(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"][0]["tier"] = "two"
        errors, _ = self.check(data)
        self.assertTrue(any("bad-tier" in e for e in errors), errors)

    def test_empty_domain_error_missing_key(self) -> None:
        data = base_blueprint()
        del data["domains"][0]["objectives"]
        errors, _ = self.check(data)
        self.assertTrue(any("empty-domain" in e for e in errors), errors)

    def test_empty_domain_error_empty_list(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"] = []
        errors, _ = self.check(data)
        self.assertTrue(any("empty-domain" in e for e in errors), errors)

    def test_duplicate_domain_id_error(self) -> None:
        data = base_blueprint()
        data["domains"][1]["id"] = "D1"
        errors, _ = self.check(data)
        self.assertTrue(
            any("duplicate-id" in e and "domain" in e for e in errors), errors
        )

    def test_duplicate_objective_id_error(self) -> None:
        data = base_blueprint()
        data["domains"][1]["objectives"][0]["id"] = "D1.1"
        errors, _ = self.check(data)
        self.assertTrue(
            any("duplicate-id" in e and "objective" in e for e in errors), errors
        )

    def test_domain_not_an_object_error(self) -> None:
        data = base_blueprint()
        data["domains"].append("not a domain")
        errors, _ = self.check(data)
        self.assertTrue(any("bad-domain" in e for e in errors), errors)

    def test_objective_not_an_object_error(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"].append("not an objective")
        errors, _ = self.check(data)
        self.assertTrue(any("bad-objective" in e for e in errors), errors)


class CheckBlueprintWarningTests(unittest.TestCase):
    """Every warning path; none of these change the exit code by themselves."""

    def check(self, data: dict[str, Any]) -> tuple[list[str], list[str]]:
        errors, warnings, _, _, _ = bc.check_blueprint(data, bc.DEFAULT_LEVELS)
        return errors, warnings

    def test_missing_tier_warning(self) -> None:
        data = base_blueprint()
        del data["domains"][0]["objectives"][0]["tier"]
        errors, warnings = self.check(data)
        self.assertEqual(errors, [])
        self.assertTrue(any("missing-tier" in w for w in warnings), warnings)
        self.assertTrue(any("S1.7" in w for w in warnings), warnings)

    def test_bank_size_not_whole_number_warning(self) -> None:
        data = base_blueprint()
        data["domains"][0]["weight"] = 51
        data["domains"][1]["weight"] = 49
        errors, warnings = self.check(data)
        self.assertEqual(errors, [])
        self.assertTrue(any("bank-size" in w for w in warnings), warnings)

    def test_no_apply_or_above_warning(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"] = [objective("D1.1", "remember", 1)]
        errors, warnings = self.check(data)
        self.assertEqual(errors, [])
        self.assertTrue(
            any("no-apply-plus" in w and "D1" in w for w in warnings), warnings
        )

    def test_no_apply_plus_warning_is_skipped_without_apply_in_levels(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"] = [objective("D1.1", "remember", 1)]
        errors, warnings, _, _, _ = bc.check_blueprint(
            data, ("remember", "understand", "analyze", "evaluate", "create")
        )
        self.assertEqual(errors, [])
        self.assertFalse(any("no-apply-plus" in w for w in warnings), warnings)

    def test_supported_by_empty_list_is_ignored(self) -> None:
        data = base_blueprint()
        data["domains"][0]["objectives"][0]["supported_by"] = []
        errors, warnings = self.check(data)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


class LoadBlueprintTests(unittest.TestCase):
    """load_blueprint: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = bc.load_blueprint(SAMPLE)
        self.assertEqual(len(data["domains"]), 4)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                bc.load_blueprint(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * bc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                bc.load_blueprint(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input problem."""

    def write(self, tmp: Path, data: dict[str, Any]) -> Path:
        path = tmp / "blueprint.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), base_blueprint())
            self.assertEqual(bc.main([str(path)]), 0)

    def test_exit_one_on_any_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_blueprint()
            data["domains"][1]["weight"] = 51
            path = self.write(Path(tmp), data)
            self.assertEqual(bc.main([str(path)]), 1)

    def test_exit_zero_with_only_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_blueprint()
            del data["domains"][0]["objectives"][0]["tier"]
            path = self.write(Path(tmp), data)
            self.assertEqual(bc.main([str(path)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(bc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(bc.main([str(path)]), 2)

    def test_exit_two_on_bad_levels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), base_blueprint())
            self.assertEqual(bc.main([str(path), "--levels", "a,a"]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BLUEPRINT", result.stdout)
        self.assertIn("--levels", result.stdout)
        self.assertIn("--json", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("domains=4 objectives=12 errors=0 warnings=0", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_json_output_on_clean_sample(self) -> None:
        result = run_cli(str(SAMPLE), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["warnings"], [])
        self.assertEqual(payload["domains"], 4)
        self.assertEqual(payload["objectives"], 12)
        self.assertEqual(sorted(payload["cross_tab"]), ["D1", "D2", "D3", "D4"])

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("blueprint_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_custom_levels_flags_a_now_unknown_bloom(self) -> None:
        result = run_cli(str(SAMPLE), "--levels", "understand,apply")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("bad-bloom", result.stdout)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            run_cli("--json", str(SAMPLE), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a temporary copy."""

    def test_changing_one_weight_breaks_the_sum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "blueprint.json"
            original = SAMPLE.read_text(encoding="utf-8")
            self.assertEqual(original.count(BROKEN_NEEDLE), 1)
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1), encoding="utf-8"
            )
            result = run_cli(str(copy_path))
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "error weight-sum: domain weights sum to 101, not 100", result.stdout
        )
        self.assertIn(
            "warning bank-size: domain D2 weight 31 gives "
            "bank_size * weight / 100 = 6.2, not a whole number",
            result.stdout,
        )
        self.assertIn("domains=4 objectives=12 errors=1 warnings=1", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S1-01")
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
    """docs/stage-1/blueprint.md: every pasted output line is real."""

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
            copy_path = Path(tmp) / "blueprint.json"
            original = SAMPLE.read_text(encoding="utf-8")
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1), encoding="utf-8"
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
