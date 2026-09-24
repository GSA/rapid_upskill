"""Unit tests for scripts/s1/check_concept_graph.py and
docs/stage-1/concept-map-and-hierarchy.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory. The page-output tests re-run the real script and
compare its output with the text pasted on the page, so the page can
never drift from the script. The break-on-purpose edit is applied to a
copy in a temporary directory, never to the repository's own sample file.

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
SCRIPT = ROOT / "scripts" / "s1" / "check_concept_graph.py"
SAMPLE = (
    ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_stage1"
    / "concept_map"
    / "catalog.json"
)
PAGE = ROOT / "docs" / "stage-1" / "concept-map-and-hierarchy.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("check_concept_graph", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ccg = load_module()


def node(
    node_id: str, tier: Any = 1, prerequisites: list[str] | None = None
) -> dict[str, Any]:
    """A minimal, otherwise-valid catalog node."""
    return {
        "id": node_id,
        "name": node_id,
        "tier": tier,
        "prerequisites": [] if prerequisites is None else prerequisites,
    }


def base_catalog() -> list[dict[str, Any]]:
    """A small, clean catalog: three nodes, a straight-line dependency."""
    return [
        node("a", 1, []),
        node("b", 2, ["a"]),
        node("c", 3, ["b"]),
    ]


def load_sample() -> list[dict[str, Any]]:
    """A deep copy of the real sample catalog, safe to mutate in a test."""
    return copy.deepcopy(json.loads(SAMPLE.read_text(encoding="utf-8")))


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


def write_catalog(tmp: Path, data: list[dict[str, Any]]) -> Path:
    """Write a catalog list to tmp/catalog.json and return its path."""
    path = tmp / "catalog.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class ValidateCatalogTests(unittest.TestCase):
    """validate_catalog: the structural checks that raise ValueError."""

    def test_accepts_a_clean_list(self) -> None:
        nodes = ccg.validate_catalog(base_catalog())
        self.assertEqual(len(nodes), 3)

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            ccg.validate_catalog({"not": "a list"})

    def test_rejects_a_non_object_entry(self) -> None:
        with self.assertRaises(ValueError):
            ccg.validate_catalog(["not an object"])

    def test_rejects_a_missing_id(self) -> None:
        data = base_catalog()
        del data[0]["id"]
        with self.assertRaises(ValueError):
            ccg.validate_catalog(data)

    def test_rejects_a_missing_name(self) -> None:
        data = base_catalog()
        del data[0]["name"]
        with self.assertRaises(ValueError):
            ccg.validate_catalog(data)

    def test_rejects_a_bad_prerequisites_list(self) -> None:
        data = base_catalog()
        data[0]["prerequisites"] = "not a list"
        with self.assertRaises(ValueError):
            ccg.validate_catalog(data)

    def test_rejects_a_non_string_prerequisite(self) -> None:
        data = base_catalog()
        data[0]["prerequisites"] = [1]
        with self.assertRaises(ValueError):
            ccg.validate_catalog(data)


class CheckCatalogTests(unittest.TestCase):
    """check_catalog: every finding kind, exercised on small fixtures."""

    def check(
        self, data: list[dict[str, Any]], min_tier: int = 1, max_tier: int = 4
    ) -> tuple[list[str], list[str], bool, int, dict[int, int], int]:
        return ccg.check_catalog(ccg.validate_catalog(data), min_tier, max_tier)

    def test_clean_baseline_has_no_findings(self) -> None:
        errors, order, complete, placed, tiers, edges = self.check(base_catalog())
        self.assertEqual(errors, [])
        self.assertEqual(order, ["a", "b", "c"])
        self.assertTrue(complete)
        self.assertEqual(placed, 3)
        self.assertEqual(edges, 2)
        self.assertEqual(tiers, {1: 1, 2: 1, 3: 1, 4: 0})

    def test_two_node_cycle_is_named_in_order(self) -> None:
        data = base_catalog()
        data[0]["prerequisites"] = ["b"]
        errors, order, complete, placed, _, _ = self.check(data)
        self.assertIn("cycle: a -> b -> a", errors)
        self.assertFalse(complete)
        # "c" depends on "b", which never places, so nothing places at all.
        self.assertEqual(placed, 0)
        self.assertEqual(order, [])

    def test_self_loop_is_a_one_node_cycle(self) -> None:
        data = base_catalog()
        data[0]["prerequisites"] = ["a"]
        errors, _, _, _, _, _ = self.check(data)
        self.assertIn("cycle: a -> a", errors)

    def test_dangling_prerequisite_is_flagged_not_dropped(self) -> None:
        data = base_catalog()
        data[0]["prerequisites"] = ["nope"]
        errors, _, _, _, _, edges = self.check(data)
        self.assertIn('dangling: node "a" lists unknown prerequisite "nope"', errors)
        self.assertEqual(edges, 3)  # the dangling entry still counts as an edge

    def test_dangling_check_is_case_and_space_insensitive(self) -> None:
        data = base_catalog()
        data[0]["prerequisites"] = [" B "]
        errors, _, _, _, _, _ = self.check(data)
        self.assertNotIn('dangling: node "a" lists unknown prerequisite " B "', errors)

    def test_bad_tier_out_of_range(self) -> None:
        data = base_catalog()
        data[0]["tier"] = 5
        errors, _, _, _, _, _ = self.check(data)
        self.assertIn('bad-tier: node "a" has tier 5, must be 1 to 4', errors)

    def test_bad_tier_wrong_type(self) -> None:
        data = base_catalog()
        data[0]["tier"] = "one"
        errors, _, _, _, _, _ = self.check(data)
        self.assertIn("bad-tier: node \"a\" has tier 'one', must be 1 to 4", errors)

    def test_bad_tier_missing(self) -> None:
        data = base_catalog()
        del data[0]["tier"]
        errors, _, _, _, _, _ = self.check(data)
        self.assertIn('bad-tier: node "a" has tier None, must be 1 to 4', errors)

    def test_duplicate_id(self) -> None:
        data = base_catalog()
        data[1]["id"] = "a"
        errors, _, _, _, _, _ = self.check(data)
        self.assertIn('duplicate-id: "a" is used by more than one node', errors)

    def test_custom_tier_range(self) -> None:
        errors, _, _, _, tiers, _ = self.check(base_catalog(), min_tier=1, max_tier=2)
        self.assertIn('bad-tier: node "c" has tier 3, must be 1 to 2', errors)
        self.assertEqual(tiers, {1: 1, 2: 1})


class LoadCatalogTests(unittest.TestCase):
    """load_catalog: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_sample(self) -> None:
        data = ccg.load_catalog(SAMPLE)
        self.assertEqual(len(data), 9)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                ccg.load_catalog(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * ccg.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                ccg.load_catalog(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any finding, 2 for a usage or input error."""

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_catalog(Path(tmp), base_catalog())
            self.assertEqual(ccg.main([str(path)]), 0)

    def test_exit_one_on_a_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_catalog()
            data[0]["prerequisites"] = ["b"]
            path = write_catalog(Path(tmp), data)
            self.assertEqual(ccg.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(ccg.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(ccg.main([str(path)]), 2)

    def test_exit_two_on_bad_tier_range_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_catalog(Path(tmp), base_catalog())
            self.assertEqual(
                ccg.main([str(path), "--min-tier", "3", "--max-tier", "1"]), 2
            )

    def test_exit_two_on_bad_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
            self.assertEqual(ccg.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CATALOG", result.stdout)
        self.assertIn("--min-tier", result.stdout)
        self.assertIn("--max-tier", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "order: staging-area, commit, branch, head, remote, merge, "
            "conflict, fast-forward-merge, merge-commit",
            result.stdout,
        )
        self.assertIn("tiers: 1=2 2=2 3=3 4=2", result.stdout)
        self.assertIn("nodes=9 edges=11 cycles=0 dangling=0", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("check_concept_graph.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a copy in a temp dir.

    The sample catalog is already clean, so this is the opposite of the
    other Stage 1 pages' break-on-purpose step: it adds one prerequisite
    that creates a two-node cycle between "commit" and "staging-area",
    and one prerequisite id with a typo, "haed" (for "head"), that
    matches nothing.
    """

    def broken_copy(self, tmp: Path) -> Path:
        data = load_sample()
        for entry in data:
            if entry["id"] == "staging-area":
                entry["prerequisites"].append("commit")
            if entry["id"] == "remote":
                entry["prerequisites"].append("haed")
        return write_catalog(tmp, data)

    def test_break_on_purpose_flags_both_the_cycle_and_the_typo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.broken_copy(Path(tmp))
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            'dangling: node "remote" lists unknown prerequisite "haed"',
            result.stdout,
        )
        self.assertIn("cycle: staging-area -> commit -> staging-area", result.stdout)
        self.assertIn("order: incomplete, 0 of 9 nodes placed", result.stdout)
        self.assertIn("tiers: 1=2 2=2 3=3 4=2", result.stdout)
        self.assertIn("nodes=9 edges=13 cycles=1 dangling=1", result.stdout)

    def test_repository_sample_is_untouched(self) -> None:
        # The break-on-purpose edit above never writes to SAMPLE itself.
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        staging = next(n for n in data if n["id"] == "staging-area")
        remote = next(n for n in data if n["id"] == "remote")
        self.assertEqual(staging["prerequisites"], [])
        self.assertEqual(remote["prerequisites"], ["branch"])


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
        self.assertEqual(fields["ID"], "X-S1-09")
        self.assertEqual(fields["Stage"], "S1")
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
    """docs/stage-1/concept-map-and-hierarchy.md: every pasted line is real."""

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
            data = load_sample()
            for entry in data:
                if entry["id"] == "staging-area":
                    entry["prerequisites"].append("commit")
                if entry["id"] == "remote":
                    entry["prerequisites"].append("haed")
            path = write_catalog(Path(tmp), data)
            broken = run_cli(str(path))
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
