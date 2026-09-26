"""Unit tests for scripts/s2/prerequisite_check.py and
docs/stage-2/closing-templates.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, plus the real, already-published Stage 1 sample
catalog (read-only). The page-output test re-runs the real script and
compares its output with the text pasted on the page, so the page can
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
SCRIPT = ROOT / "scripts" / "s2" / "prerequisite_check.py"
CATALOG = (
    ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_stage1"
    / "concept_map"
    / "catalog.json"
)
PREREQ_DIR = ROOT / "scripts" / "sample_data" / "git_basics_stage2" / "prerequisites"
TAUGHT = PREREQ_DIR / "taught_so_far.json"
REQUIRES = PREREQ_DIR / "section_requires.json"
PAGE = ROOT / "docs" / "stage-2" / "closing-templates.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("prerequisite_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pc = load_module()


def catalog_node(concept_id: str, tier: Any = 1) -> dict[str, Any]:
    """A minimal, otherwise-valid catalog entry."""
    return {"id": concept_id, "name": concept_id, "tier": tier, "prerequisites": []}


def base_catalog() -> list[dict[str, Any]]:
    """A small, clean catalog: three concepts at three tiers."""
    return [catalog_node("a", 1), catalog_node("b", 2), catalog_node("c", 3)]


def base_taught() -> list[dict[str, Any]]:
    """Two sections, each teaching more than the one before."""
    return [
        {"section": "1.1", "concepts_taught": ["a"]},
        {"section": "1.2", "concepts_taught": ["a", "b"]},
    ]


def base_requires() -> list[dict[str, Any]]:
    """One section that should pass, checked against base_catalog/base_taught."""
    return [{"section": "1.2", "requires": [{"concept": "a", "min_tier": 1}]}]


def load_real_catalog() -> list[dict[str, Any]]:
    """A deep copy of the real, published Stage 1 sample catalog."""
    return copy.deepcopy(json.loads(CATALOG.read_text(encoding="utf-8")))


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


def write_json(tmp: Path, name: str, data: Any) -> Path:
    """Write `data` as JSON to tmp/name and return its path."""
    path = tmp / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class SectionKeyTests(unittest.TestCase):
    """section_key: dotted-number ordering, not plain-text ordering."""

    def test_parses_two_part_section(self) -> None:
        self.assertEqual(pc.section_key("1.2"), (1, 2))

    def test_orders_by_number_not_text(self) -> None:
        self.assertLess(pc.section_key("1.2"), pc.section_key("1.10"))
        self.assertGreater("1.2", "1.10")  # the plain-text order is the opposite

    def test_rejects_a_non_numeric_part(self) -> None:
        with self.assertRaises(ValueError):
            pc.section_key("1.a")


class LoadCatalogTiersTests(unittest.TestCase):
    """load_catalog_tiers: the structural checks that raise ValueError."""

    def test_accepts_a_clean_list(self) -> None:
        tiers = pc.load_catalog_tiers(base_catalog())
        self.assertEqual(tiers, {"a": 1, "b": 2, "c": 3})

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            pc.load_catalog_tiers({"not": "a list"})

    def test_rejects_a_non_object_entry(self) -> None:
        with self.assertRaises(ValueError):
            pc.load_catalog_tiers(["not an object"])

    def test_rejects_a_missing_id(self) -> None:
        data = base_catalog()
        del data[0]["id"]
        with self.assertRaises(ValueError):
            pc.load_catalog_tiers(data)

    def test_rejects_a_bad_tier(self) -> None:
        data = base_catalog()
        data[0]["tier"] = "one"
        with self.assertRaises(ValueError):
            pc.load_catalog_tiers(data)

    def test_rejects_a_bool_tier(self) -> None:
        data = base_catalog()
        data[0]["tier"] = True
        with self.assertRaises(ValueError):
            pc.load_catalog_tiers(data)


class LoadTaughtTests(unittest.TestCase):
    """load_taught: the structural checks that raise ValueError."""

    def test_accepts_a_clean_list(self) -> None:
        result = pc.load_taught(base_taught())
        self.assertEqual(result, [("1.1", ["a"]), ("1.2", ["a", "b"])])

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            pc.load_taught({"not": "a list"})

    def test_rejects_a_missing_section(self) -> None:
        data = base_taught()
        del data[0]["section"]
        with self.assertRaises(ValueError):
            pc.load_taught(data)

    def test_rejects_a_bad_concepts_taught_list(self) -> None:
        data = base_taught()
        data[0]["concepts_taught"] = "not a list"
        with self.assertRaises(ValueError):
            pc.load_taught(data)

    def test_rejects_a_non_string_concept(self) -> None:
        data = base_taught()
        data[0]["concepts_taught"] = [1]
        with self.assertRaises(ValueError):
            pc.load_taught(data)


class LoadRequiresTests(unittest.TestCase):
    """load_requires: the structural checks that raise ValueError."""

    def test_accepts_a_clean_list(self) -> None:
        result = pc.load_requires(base_requires())
        self.assertEqual(result, [("1.2", [("a", 1)])])

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            pc.load_requires({"not": "a list"})

    def test_rejects_a_missing_section(self) -> None:
        data = base_requires()
        del data[0]["section"]
        with self.assertRaises(ValueError):
            pc.load_requires(data)

    def test_rejects_a_bad_requires_list(self) -> None:
        data = base_requires()
        data[0]["requires"] = "not a list"
        with self.assertRaises(ValueError):
            pc.load_requires(data)

    def test_rejects_a_missing_concept(self) -> None:
        data = base_requires()
        del data[0]["requires"][0]["concept"]
        with self.assertRaises(ValueError):
            pc.load_requires(data)

    def test_rejects_a_bad_min_tier(self) -> None:
        data = base_requires()
        data[0]["requires"][0]["min_tier"] = "one"
        with self.assertRaises(ValueError):
            pc.load_requires(data)


class TaughtBeforeTests(unittest.TestCase):
    """taught_before: only sections strictly before the target count."""

    def test_unions_every_earlier_section(self) -> None:
        taught = pc.load_taught(base_taught())
        self.assertEqual(pc.taught_before(taught, "1.2"), {"a"})
        self.assertEqual(pc.taught_before(taught, "1.3"), {"a", "b"})

    def test_nothing_before_the_first_section(self) -> None:
        taught = pc.load_taught(base_taught())
        self.assertEqual(pc.taught_before(taught, "1.1"), set())

    def test_orders_by_number_not_text(self) -> None:
        taught = pc.load_taught([{"section": "1.9", "concepts_taught": ["a"]}])
        self.assertEqual(pc.taught_before(taught, "1.10"), {"a"})


class CheckPrerequisitesTests(unittest.TestCase):
    """check_prerequisites: every finding kind, on small fixtures."""

    def test_pass_when_taught_and_tier_satisfied(self) -> None:
        tiers = pc.load_catalog_tiers(base_catalog())
        taught = pc.load_taught(base_taught())
        requires = pc.load_requires(base_requires())
        lines = pc.check_prerequisites(tiers, taught, requires)
        self.assertEqual(lines, ['pass: section "1.2" requires "a", satisfied'])

    def test_gap_when_not_yet_taught(self) -> None:
        tiers = pc.load_catalog_tiers(base_catalog())
        taught = pc.load_taught(base_taught())
        requires = pc.load_requires(
            [{"section": "1.1", "requires": [{"concept": "b", "min_tier": 1}]}]
        )
        lines = pc.check_prerequisites(tiers, taught, requires)
        self.assertEqual(
            lines,
            ['gap: section "1.1" requires "b", not taught by that point'],
        )

    def test_gap_when_catalog_tier_higher_than_stated(self) -> None:
        tiers = pc.load_catalog_tiers(base_catalog())
        taught = pc.load_taught(base_taught())
        requires = pc.load_requires(
            [{"section": "1.3", "requires": [{"concept": "b", "min_tier": 1}]}]
        )
        lines = pc.check_prerequisites(tiers, taught, requires)
        self.assertEqual(
            lines,
            ['gap: section "1.3" requires "b" at tier 1, ' "catalog has it at tier 2"],
        )

    def test_unknown_concept_raises(self) -> None:
        tiers = pc.load_catalog_tiers(base_catalog())
        taught = pc.load_taught(base_taught())
        requires = pc.load_requires(
            [{"section": "1.2", "requires": [{"concept": "nope", "min_tier": 1}]}]
        )
        with self.assertRaises(ValueError):
            pc.check_prerequisites(tiers, taught, requires)

    def test_real_sample_has_one_pass_and_one_gap(self) -> None:
        tiers = pc.load_catalog_tiers(load_real_catalog())
        taught = pc.load_taught(json.loads(TAUGHT.read_text(encoding="utf-8")))
        requires = pc.load_requires(json.loads(REQUIRES.read_text(encoding="utf-8")))
        lines = pc.check_prerequisites(tiers, taught, requires)
        self.assertEqual(
            lines,
            [
                'pass: section "1.2" requires "commit", satisfied',
                'gap: section "1.3" requires "branch" at tier 1, '
                "catalog has it at tier 2",
            ],
        )


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_catalog(self) -> None:
        data = pc.load_json(CATALOG)
        self.assertEqual(len(data), 9)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(CATALOG)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                pc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * pc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                pc.load_json(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any gap, 2 for a usage or input error."""

    def test_exit_zero_on_clean_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = write_json(root, "catalog.json", base_catalog())
            taught = write_json(root, "taught.json", base_taught())
            requires = write_json(root, "requires.json", base_requires())
            self.assertEqual(pc.main([str(catalog), str(taught), str(requires)]), 0)

    def test_exit_one_on_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = write_json(root, "catalog.json", base_catalog())
            taught = write_json(root, "taught.json", base_taught())
            requires = write_json(
                root,
                "requires.json",
                [{"section": "1.1", "requires": [{"concept": "b", "min_tier": 1}]}],
            )
            self.assertEqual(pc.main([str(catalog), str(taught), str(requires)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            taught = write_json(root, "taught.json", base_taught())
            requires = write_json(root, "requires.json", base_requires())
            self.assertEqual(
                pc.main([str(root / "nope.json"), str(taught), str(requires)]), 2
            )

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.json"
            bad.write_text("not json", encoding="utf-8")
            taught = write_json(root, "taught.json", base_taught())
            requires = write_json(root, "requires.json", base_requires())
            self.assertEqual(pc.main([str(bad), str(taught), str(requires)]), 2)

    def test_exit_two_on_bad_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = write_json(root, "catalog.json", {"not": "a list"})
            taught = write_json(root, "taught.json", base_taught())
            requires = write_json(root, "requires.json", base_requires())
            self.assertEqual(pc.main([str(catalog), str(taught), str(requires)]), 2)

    def test_exit_two_on_unknown_concept(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = write_json(root, "catalog.json", base_catalog())
            taught = write_json(root, "taught.json", base_taught())
            requires = write_json(
                root,
                "requires.json",
                [{"section": "1.2", "requires": [{"concept": "nope", "min_tier": 1}]}],
            )
            self.assertEqual(pc.main([str(catalog), str(taught), str(requires)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CATALOG", result.stdout)
        self.assertIn("TAUGHT", result.stdout)
        self.assertIn("REQUIRES", result.stdout)

    def test_real_fixtures_from_the_repository_root(self) -> None:
        catalog_rel = CATALOG.relative_to(ROOT).as_posix()
        taught_rel = TAUGHT.relative_to(ROOT).as_posix()
        requires_rel = REQUIRES.relative_to(ROOT).as_posix()
        result = run_cli(catalog_rel, taught_rel, requires_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 1)
        self.assertIn('pass: section "1.2" requires "commit", satisfied', result.stdout)
        self.assertIn(
            'gap: section "1.3" requires "branch" at tier 1, '
            "catalog has it at tier 2",
            result.stdout,
        )
        self.assertIn("sections=2 gaps=1", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"), str(TAUGHT), str(REQUIRES))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("prerequisite_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(CATALOG), str(TAUGHT), str(REQUIRES), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-S2-04")
        self.assertEqual(fields["Stage"], "S2")
        self.assertEqual(fields["Dependencies"], "stdlib")
        self.assertEqual(fields["Writes files"], "no")
        self.assertEqual(fields["License"], "CC0-1.0")
        self.assertTrue(fields["Usage"].startswith("python3 "))

    def test_only_standard_library_imports(self) -> None:
        tree = ast.parse(self.source)
        names: set[str] = set()
        for tree_node in ast.walk(tree):
            if isinstance(tree_node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in tree_node.names)
            elif (
                isinstance(tree_node, ast.ImportFrom)
                and tree_node.module
                and not tree_node.level
            ):
                names.add(tree_node.module.split(".")[0])
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
    """docs/stage-2/closing-templates.md: every pasted line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_an_output_fence(self) -> None:
        self.assertGreaterEqual(len(self.fences), 1)

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        result = run_cli(
            CATALOG.relative_to(ROOT).as_posix(),
            TAUGHT.relative_to(ROOT).as_posix(),
            REQUIRES.relative_to(ROOT).as_posix(),
            cwd=ROOT,
        )
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertIn(line, result.stdout, f"pasted line not found: {line!r}")


if __name__ == "__main__":
    unittest.main()
