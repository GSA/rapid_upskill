"""Unit tests for scripts/s5/stem_plan_check.py and
docs/stage-5/stem-planning.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, plus the real, already-published running example's
own `stem_plan/plan.json` (read-only, checked into this batch by the
same writer as this test). The sibling `concept_items/items.json` file
this script also reads is built by a different writer working in
parallel on this batch, so every test below stands in a temporary copy
holding only the three assessment concept item ids this plan actually
references (`ACI-1-001`, `ACI-2-001`, `ACI-2-002`): this script's own
output depends only on which ids are present in that file, never on any
of an item's other fields, so a temporary stand-in gives the same real
output the finished, shared file will. The page-output tests re-run the
real script and compare its output with the text pasted on the page, so
the page can never drift from the script.

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
SCRIPT = ROOT / "scripts" / "s5" / "stem_plan_check.py"
PLAN = (
    ROOT / "scripts" / "sample_data" / "git_basics_stage5" / "stem_plan" / "plan.json"
)
PAGE = ROOT / "docs" / "stage-5" / "stem-planning.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("stem_plan_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


spc = load_module()

FIXTURE_ITEM_IDS = ("ACI-1-001", "ACI-2-001", "ACI-2-002")


def base_items() -> list[dict[str, Any]]:
    """The three fixture assessment concept items, id only.

    A real items.json also carries chapter, description, misconceptions
    and so on; this script never reads any of that, so a test fixture
    holding only ids exercises exactly what stem_plan_check.py checks.
    """
    return [{"id": item_id} for item_id in FIXTURE_ITEM_IDS]


def base_plan() -> list[dict[str, Any]]:
    """Two clean rows: PLAN-1 easy on one item, PLAN-2 medium on two."""
    return [
        {
            "plan_row_id": "PLAN-1",
            "difficulty": "easy",
            "concept_item_ids": ["ACI-1-001"],
            "distractor_misconceptions": ["a"],
        },
        {
            "plan_row_id": "PLAN-2",
            "difficulty": "medium",
            "concept_item_ids": ["ACI-2-001", "ACI-2-002"],
            "distractor_misconceptions": ["b", "c"],
        },
    ]


def write_json(tmp: Path, name: str, data: Any) -> Path:
    """Write `data` as JSON to tmp/name and return its path."""
    path = tmp / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


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


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_plan_file(self) -> None:
        data = spc.load_json(PLAN)
        self.assertEqual(len(data), 2)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(PLAN)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                spc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * spc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                spc.load_json(big)


class LoadItemIdsTests(unittest.TestCase):
    """load_item_ids: which ids count, malformed entries are skipped."""

    def test_accepts_a_clean_list(self) -> None:
        self.assertEqual(spc.load_item_ids(base_items()), set(FIXTURE_ITEM_IDS))

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            spc.load_item_ids({"not": "a list"})

    def test_skips_a_non_object_entry(self) -> None:
        self.assertEqual(spc.load_item_ids(["not an object", 3, None]), set())

    def test_skips_an_entry_with_no_string_id(self) -> None:
        data = [{"id": 7}, {"title": "no id field"}, {"id": ""}]
        self.assertEqual(spc.load_item_ids(data), set())


class CheckPlanTests(unittest.TestCase):
    """check_plan: every error and warning path, on small fixtures."""

    def test_clean_plan_has_no_errors_but_warns_on_the_mix(self) -> None:
        errors, warnings, rows = spc.check_plan(base_plan(), set(FIXTURE_ITEM_IDS))
        self.assertEqual(errors, [])
        self.assertEqual(rows, 2)
        self.assertEqual(len(warnings), 1)
        self.assertIn("mix:", warnings[0])

    def test_bad_row_not_an_object(self) -> None:
        errors, _, _ = spc.check_plan(["not an object"], set(FIXTURE_ITEM_IDS))
        self.assertEqual(errors, ["bad-row: row #1 is not a JSON object"])

    def test_missing_plan_row_id(self) -> None:
        rows = base_plan()
        del rows[0]["plan_row_id"]
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn("missing-field: row #1 has no 'plan_row_id'", errors)

    def test_missing_difficulty(self) -> None:
        rows = base_plan()
        del rows[0]["difficulty"]
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn("missing-field: row \"PLAN-1\" has no 'difficulty'", errors)

    def test_bad_difficulty_value(self) -> None:
        rows = base_plan()
        rows[0]["difficulty"] = "expert"
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn(
            "bad-difficulty: row \"PLAN-1\" has difficulty 'expert', "
            "must be easy, medium or hard",
            errors,
        )

    def test_missing_concept_item_ids(self) -> None:
        rows = base_plan()
        del rows[0]["concept_item_ids"]
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn(
            "missing-field: row \"PLAN-1\" has no 'concept_item_ids' list", errors
        )

    def test_count_outside_range_easy(self) -> None:
        rows = base_plan()
        rows[0]["concept_item_ids"] = ["ACI-1-001", "ACI-2-001"]
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn(
            'count: row "PLAN-1" is easy with 2 concept_item_ids, needs exactly 1',
            errors,
        )

    def test_count_outside_range_medium(self) -> None:
        rows = base_plan()
        rows[1]["concept_item_ids"] = ["ACI-2-001"]
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn(
            'count: row "PLAN-2" is medium with 1 concept_item_ids, needs 2 to 3',
            errors,
        )

    def test_missing_item_reference(self) -> None:
        rows = base_plan()
        rows[1]["concept_item_ids"] = ["ACI-2-001", "ACI-9-999"]
        errors, _, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertIn(
            'missing-item: row "PLAN-2" references concept item id '
            "'ACI-9-999' not found in ITEMS.json",
            errors,
        )

    def test_mix_within_tolerance_gives_no_warning(self) -> None:
        rows = []
        for index in range(3):
            rows.append(
                {
                    "plan_row_id": f"E{index}",
                    "difficulty": "easy",
                    "concept_item_ids": ["ACI-1-001"],
                }
            )
        for index in range(5):
            rows.append(
                {
                    "plan_row_id": f"M{index}",
                    "difficulty": "medium",
                    "concept_item_ids": ["ACI-2-001", "ACI-2-002"],
                }
            )
        for index in range(2):
            rows.append(
                {
                    "plan_row_id": f"H{index}",
                    "difficulty": "hard",
                    "concept_item_ids": ["ACI-1-001", "ACI-2-001", "ACI-2-002"],
                }
            )
        _, warnings, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        self.assertEqual(warnings, [])

    def test_unrecognized_difficulty_excluded_from_mix(self) -> None:
        rows = base_plan()
        rows[0]["difficulty"] = "expert"
        _, warnings, _ = spc.check_plan(rows, set(FIXTURE_ITEM_IDS))
        # Only PLAN-2 (medium) is categorized; a single-category mix is
        # 100% off every other difficulty, so the warning still fires.
        self.assertEqual(len(warnings), 1)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input error."""

    def test_exit_zero_on_clean_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = write_json(root, "plan.json", base_plan())
            items = write_json(root, "items.json", base_items())
            self.assertEqual(spc.main([str(plan), str(items)]), 0)

    def test_exit_one_on_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = base_plan()
            rows[1]["concept_item_ids"] = ["ACI-9-999"]
            plan = write_json(root, "plan.json", rows)
            items = write_json(root, "items.json", base_items())
            self.assertEqual(spc.main([str(plan), str(items)]), 1)

    def test_exit_two_on_missing_plan_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = write_json(root, "items.json", base_items())
            self.assertEqual(spc.main([str(root / "nope.json"), str(items)]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.json"
            bad.write_text("not json", encoding="utf-8")
            items = write_json(root, "items.json", base_items())
            self.assertEqual(spc.main([str(bad), str(items)]), 2)

    def test_exit_two_on_bad_top_level_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = write_json(root, "plan.json", {"not": "a list"})
            items = write_json(root, "items.json", base_items())
            self.assertEqual(spc.main([str(plan), str(items)]), 2)

    def test_exit_two_on_bad_items_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = write_json(root, "plan.json", base_plan())
            items = write_json(root, "items.json", {"not": "a list"})
            self.assertEqual(spc.main([str(plan), str(items)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PLAN.json", result.stdout)
        self.assertIn("ITEMS.json", result.stdout)

    def test_real_plan_against_a_stand_in_items_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            items = write_json(Path(tmp), "items.json", base_items())
            result = run_cli(PLAN.relative_to(ROOT).as_posix(), str(items), cwd=ROOT)
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "warning mix: plan is easy=50% medium=50% hard=0%, "
            "target is 30/50/20 (off by up to 20 points)",
            result.stdout,
        )
        self.assertIn("rows=2 errors=0 warnings=1", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            items = write_json(Path(tmp), "items.json", base_items())
            before = set(Path(tmp).iterdir())
            run_cli(PLAN.relative_to(ROOT).as_posix(), str(items), cwd=ROOT)
            self.assertEqual(set(Path(tmp).iterdir()), before)


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
        self.assertEqual(fields["ID"], "X-S5-02")
        self.assertEqual(fields["Stage"], "S5")
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


class SampleDataTests(unittest.TestCase):
    """The checked-in stem_plan/plan.json uses the fixed fixture ids."""

    def test_plan_uses_the_shared_fixture_ids(self) -> None:
        data = json.loads(PLAN.read_text(encoding="utf-8"))
        self.assertEqual([row["plan_row_id"] for row in data], ["PLAN-1", "PLAN-2"])
        self.assertEqual(data[0]["concept_item_ids"], ["ACI-1-001"])
        self.assertEqual(data[1]["concept_item_ids"], ["ACI-2-001", "ACI-2-002"])
        self.assertEqual(data[0]["difficulty"], "easy")
        self.assertEqual(data[1]["difficulty"], "medium")

    def test_plan_is_ascii_only(self) -> None:
        self.assertTrue(PLAN.read_text(encoding="utf-8").isascii())


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-5/stem-planning.md: every pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_one_output_fence(self) -> None:
        self.assertEqual(len(self.fences), 1)

    def test_no_absolute_path_in_the_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_fence_matches_the_real_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            items = write_json(Path(tmp), "items.json", base_items())
            result = run_cli(PLAN.relative_to(ROOT).as_posix(), str(items), cwd=ROOT)
        lines = [line for line in self.fences[0].splitlines() if line.strip()]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn(line, result.stdout, f"pasted line not found: {line!r}")

    def test_page_names_both_real_sample_paths(self) -> None:
        self.assertIn(
            "scripts/sample_data/git_basics_stage5/stem_plan/plan.json", self.page_text
        )
        self.assertIn(
            "scripts/sample_data/git_basics_stage5/concept_items/items.json",
            self.page_text,
        )


if __name__ == "__main__":
    unittest.main()
