"""Unit tests for scripts/s5/bank_composition_check.py and
docs/stage-5/difficulty-and-blueprint-bank.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample composition and the running example's own blueprint (read-only).
The page-output tests re-run the real script and compare its output
with the text pasted on the page, so the page can never drift from the
script.

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
SCRIPT = ROOT / "scripts" / "s5" / "bank_composition_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_stage5" / "bank"
COMPOSITION = SAMPLE_DIR / "composition.json"
BLUEPRINT = ROOT / "scripts" / "sample_data" / "git_basics" / "blueprint.json"
PAGE = ROOT / "docs" / "stage-5" / "difficulty-and-blueprint-bank.md"
BROKEN_NEEDLE = '"D2": {"easy": 2, "medium": 3, "hard": 1}'
BROKEN_REPLACEMENT = '"D2": {"easy": 2, "medium": 3, "hard": 5}'


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("bank_composition_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bcc = load_module()


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


def blueprint_domains(*pairs: tuple[str, float]) -> dict[str, Any]:
    """A minimal, otherwise-valid blueprint with the given (id, weight) domains."""
    return {
        "domains": [{"id": domain_id, "weight": weight} for domain_id, weight in pairs]
    }


def composition(domains: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """A composition file; some tests deliberately pass a bad count."""
    return {"domains": domains}


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = bcc.load_json(COMPOSITION)
        self.assertIn("domains", data)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(COMPOSITION)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                bcc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * bcc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                bcc.load_json(big)


class ParseBlueprintDomainsTests(unittest.TestCase):
    """parse_blueprint_domains: the happy path and every malformed shape."""

    def test_parses_id_and_weight_pairs_in_order(self) -> None:
        data = blueprint_domains(("D1", 25), ("D2", 75))
        self.assertEqual(bcc.parse_blueprint_domains(data), [("D1", 25), ("D2", 75)])

    def test_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains(["not", "an", "object"])

    def test_missing_domains_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains({})

    def test_domains_not_a_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains({"domains": {"D1": {"weight": 100}}})

    def test_domain_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains({"domains": ["not an object"]})

    def test_missing_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains({"domains": [{"weight": 100}]})

    def test_missing_weight_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains({"domains": [{"id": "D1"}]})

    def test_non_numeric_weight_is_rejected(self) -> None:
        data = {"domains": [{"id": "D1", "weight": "25"}]}
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains(data)

    def test_duplicate_id_is_rejected(self) -> None:
        data = blueprint_domains(("D1", 50), ("D1", 50))
        with self.assertRaises(ValueError):
            bcc.parse_blueprint_domains(data)


class ParseCompositionDomainsTests(unittest.TestCase):
    """parse_composition_domains: the happy path and every malformed shape."""

    def test_parses_counts_and_fills_missing_keys_with_zero(self) -> None:
        data = composition({"D1": {"easy": 2}})
        self.assertEqual(
            bcc.parse_composition_domains(data),
            {"D1": {"easy": 2, "medium": 0, "hard": 0}},
        )

    def test_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains(["not", "an", "object"])

    def test_missing_domains_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains({})

    def test_domains_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains({"domains": [{"easy": 1}]})

    def test_domain_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains({"domains": {"D1": "not an object"}})

    def test_negative_count_is_rejected(self) -> None:
        data = composition({"D1": {"easy": -1}})
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains(data)

    def test_non_integer_count_is_rejected(self) -> None:
        data = composition({"D1": {"easy": 2.5}})
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains(data)

    def test_non_numeric_count_is_rejected(self) -> None:
        data = composition({"D1": {"easy": "two"}})
        with self.assertRaises(ValueError):
            bcc.parse_composition_domains(data)


class CheckCompositionTests(unittest.TestCase):
    """check_composition: the domain-count and difficulty-split warnings."""

    def test_clean_composition_has_no_warnings(self) -> None:
        blueprint = [("D1", 50.0), ("D2", 50.0)]
        data = {
            "D1": {"easy": 3, "medium": 5, "hard": 2},
            "D2": {"easy": 3, "medium": 5, "hard": 2},
        }
        warnings, rows, overall, bank_size = bcc.check_composition(data, blueprint)
        self.assertEqual(warnings, [])
        self.assertEqual(bank_size, 20)
        self.assertEqual(rows, [("D1", 50.0, 10.0, 10), ("D2", 50.0, 10.0, 10)])
        self.assertEqual(overall, {"easy": 6, "medium": 10, "hard": 4})

    def test_domain_count_warning_when_more_than_one_off(self) -> None:
        blueprint = [("D1", 50.0), ("D2", 50.0)]
        data = {
            "D1": {"easy": 3, "medium": 5, "hard": 4},
            "D2": {"easy": 3, "medium": 5, "hard": 0},
        }
        warnings, _, _, _ = bcc.check_composition(data, blueprint)
        self.assertTrue(
            any("domain-count" in w and "D1" in w for w in warnings), warnings
        )
        self.assertTrue(
            any("domain-count" in w and "D2" in w for w in warnings), warnings
        )
        self.assertFalse(any("difficulty-split" in w for w in warnings), warnings)

    def test_domain_count_within_tolerance_at_exactly_one_is_not_a_warning(
        self,
    ) -> None:
        blueprint = [("D1", 50.0), ("D2", 50.0)]
        data = {
            "D1": {"easy": 3, "medium": 5, "hard": 3},
            "D2": {"easy": 3, "medium": 5, "hard": 1},
        }
        warnings, _, _, _ = bcc.check_composition(data, blueprint)
        self.assertEqual(warnings, [])

    def test_difficulty_split_warning_when_more_than_ten_points_off(self) -> None:
        blueprint = [("D1", 50.0), ("D2", 50.0)]
        data = {
            "D1": {"easy": 0, "medium": 5, "hard": 5},
            "D2": {"easy": 0, "medium": 5, "hard": 5},
        }
        warnings, _, _, _ = bcc.check_composition(data, blueprint)
        self.assertFalse(any("domain-count" in w for w in warnings), warnings)
        self.assertTrue(any("difficulty-split" in w for w in warnings), warnings)

    def test_difficulty_split_within_tolerance_at_exactly_ten_points(self) -> None:
        blueprint = [("D1", 50.0), ("D2", 50.0)]
        data = {
            "D1": {"easy": 2, "medium": 5, "hard": 3},
            "D2": {"easy": 2, "medium": 5, "hard": 3},
        }
        warnings, _, _, _ = bcc.check_composition(data, blueprint)
        self.assertEqual(warnings, [])

    def test_missing_domain_in_composition_is_treated_as_zero(self) -> None:
        blueprint = [("D1", 50.0), ("D2", 50.0)]
        data = {"D1": {"easy": 3, "medium": 5, "hard": 2}}
        warnings, rows, _, bank_size = bcc.check_composition(data, blueprint)
        self.assertEqual(bank_size, 10)
        self.assertIn(("D2", 50.0, 5.0, 0), rows)
        self.assertTrue(
            any("domain-count" in w and "D2" in w for w in warnings), warnings
        )

    def test_zero_items_raises_value_error(self) -> None:
        blueprint = [("D1", 100.0)]
        data = {"D1": {"easy": 0, "medium": 0, "hard": 0}}
        with self.assertRaises(ValueError):
            bcc.check_composition(data, blueprint)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 whether or not it warns, 2 for a usage or input problem."""

    def write(self, tmp: Path, name: str, data: dict[str, Any]) -> Path:
        path = tmp / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_files(self) -> None:
        self.assertEqual(bcc.main([str(COMPOSITION), str(BLUEPRINT)]), 0)

    def test_exit_zero_with_only_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                Path(tmp),
                "composition.json",
                composition({"D1": {"easy": 100}}),
            )
            bp_path = self.write(
                Path(tmp), "blueprint.json", blueprint_domains(("D1", 50), ("D2", 50))
            )
            self.assertEqual(bcc.main([str(path), str(bp_path)]), 0)

    def test_exit_two_on_missing_composition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.json"
            self.assertEqual(bcc.main([str(missing), str(BLUEPRINT)]), 2)

    def test_exit_two_on_missing_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.json"
            self.assertEqual(bcc.main([str(COMPOSITION), str(missing)]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(bcc.main([str(path), str(BLUEPRINT)]), 2)

    def test_exit_two_on_malformed_composition_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "composition.json", {"domains": []})
            self.assertEqual(bcc.main([str(path), str(BLUEPRINT)]), 2)

    def test_exit_two_on_all_zero_composition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                Path(tmp),
                "composition.json",
                composition({"D1": {"easy": 0, "medium": 0, "hard": 0}}),
            )
            self.assertEqual(bcc.main([str(path), str(BLUEPRINT)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real samples."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("COMPOSITION", result.stdout)
        self.assertIn("BLUEPRINT", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        composition_rel = COMPOSITION.relative_to(ROOT).as_posix()
        blueprint_rel = BLUEPRINT.relative_to(ROOT).as_posix()
        result = run_cli(composition_rel, blueprint_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn(
            "domain by target and actual item count (bank_size=20):", result.stdout
        )
        self.assertIn("D1  weight=25 target=5.0 actual=5", result.stdout)
        self.assertIn("D2  weight=30 target=6.0 actual=6", result.stdout)
        self.assertIn("D3  weight=25 target=5.0 actual=5", result.stdout)
        self.assertIn("D4  weight=20 target=4.0 actual=4", result.stdout)
        self.assertIn(
            "difficulty split (bank_size=20): easy=6 (30.0%) medium=10 (50.0%) "
            "hard=4 (20.0%) target=30/50/20",
            result.stdout,
        )
        self.assertIn("domains=4 warnings=0", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"), str(BLUEPRINT))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("bank_composition_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(COMPOSITION), str(BLUEPRINT), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a temporary copy."""

    def test_bumping_one_domains_hard_count_trips_two_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "composition.json"
            original = COMPOSITION.read_text(encoding="utf-8")
            self.assertEqual(original.count(BROKEN_NEEDLE), 1)
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1),
                encoding="utf-8",
            )
            result = run_cli(str(copy_path), str(BLUEPRINT))
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "warning domain-count: domain D2 weight 30 gives "
            "bank_size * weight / 100 = 7.2 target, actual count is 10 "
            "(+2.8 away)",
            result.stdout,
        )
        self.assertIn(
            "warning difficulty-split: bank-wide split is easy=25.0% "
            "medium=41.7% hard=33.3%, more than 10 points off the reference "
            "implementation's 30/50/20",
            result.stdout,
        )
        self.assertIn("domains=4 warnings=2", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S5-04")
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

    def test_docstring_states_the_no_pass_fail_limit(self) -> None:
        lowered = " ".join(self.docstring.casefold().split())
        self.assertIn("never exits 1 on its own", lowered)
        self.assertIn("person's judgment call, not a hard failure", lowered)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-5/difficulty-and-blueprint-bank.md: every pasted line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected a clean run and a broken run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean = run_cli(str(COMPOSITION), str(BLUEPRINT))
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "composition.json"
            original = COMPOSITION.read_text(encoding="utf-8")
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1),
                encoding="utf-8",
            )
            broken = run_cli(str(copy_path), str(BLUEPRINT))
        real_outputs = [clean.stdout, broken.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_page_states_s5_5_and_s5_7_are_not_adjacent(self) -> None:
        self.assertIn("not adjacent", self.page_text)
        self.assertIn("S5.6", self.page_text)

    def test_page_never_states_the_real_certification_numbers(self) -> None:
        # The running example's own already-public numbers (4 domains, 12
        # objectives, weights 25/30/25/20) are allowed; the page must never
        # attribute a domain, skill or weight count to the target
        # certification itself.
        self.assertNotIn("certification's own domain count", self.page_text)

    def test_page_does_not_say_concept_counts_now_applied_to_items(self) -> None:
        self.assertNotIn("already used for concept counts", self.page_text)


if __name__ == "__main__":
    unittest.main()
