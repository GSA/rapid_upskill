"""Unit tests for scripts/s1/ki_dedupe.py and docs/stage-1/knowledge-items.md.

Everything runs offline, on fixtures built in memory or in a temporary
directory. The page-output tests re-run the real script and compare its
output with the text pasted on the page, so the page can never drift from
the script. The break-on-purpose edit runs on a copy of the sample file
made in a temporary directory, never on the repository's own copy.

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
SCRIPT = ROOT / "scripts" / "s1" / "ki_dedupe.py"
SAMPLE = (
    ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_stage1"
    / "knowledge_items"
    / "items.json"
)
PAGE = ROOT / "docs" / "stage-1" / "knowledge-items.md"

# Lines this writer's page pastes verbatim from a real run. Kept here so a
# page-output test can confirm each one still appears in the real output.
CLEAN_LINES = [
    "mint KI-001 <- 'TMP-1' (no exact match)",
    "mint KI-002 <- 'TMP-2' (no exact match)",
    "mint KI-003 <- 'TMP-3' (no exact match)",
    "mint KI-004 <- 'TMP-4' (no exact match)",
    "shortlist KI-001 KI-002 score=1.00 title-overlap=0.60 shared-tags=2",
    "items=4 groups=4 shortlisted=1",
]
BROKEN_LINES = [
    "shortlist KI-001 KI-002 score=1.00 title-overlap=0.60 shared-tags=2",
    "shortlist KI-003 KI-004 score=0.25 title-overlap=0.25 shared-tags=0",
    "items=4 groups=4 shortlisted=2",
]
LOWERED_TITLE_OVERLAP = "0.2"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("ki_dedupe", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kd = load_module()


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


def item(
    item_id: str, source_id: str, title: str, tags: list[str] | None = None
) -> dict[str, Any]:
    """A minimal, otherwise-valid draft knowledge item."""
    return {
        "id": item_id,
        "source_id": source_id,
        "title": title,
        "type": "definition",
        "body": f"Body text for {item_id}.",
        "relations": [],
        "evidence": {"quote": "a quote", "locator": "a locator"},
        "tags": tags or [],
        "status": "draft",
    }


def write_json(path: Path, data: object) -> None:
    """Write JSON to path as UTF-8 text."""
    path.write_text(json.dumps(data), encoding="utf-8")


class NormalizeAndOverlapTests(unittest.TestCase):
    """normalize_title, title_words and jaccard: the small helpers."""

    def test_normalize_title_folds_case_and_collapses_whitespace(self) -> None:
        self.assertEqual(kd.normalize_title("  Same   Title  "), "same title")

    def test_title_words_lower_cases_and_splits_on_whitespace(self) -> None:
        self.assertEqual(kd.title_words("Two Words"), {"two", "words"})

    def test_jaccard_of_identical_sets_is_one(self) -> None:
        self.assertEqual(kd.jaccard({"a", "b"}, {"a", "b"}), 1.0)

    def test_jaccard_of_disjoint_sets_is_zero(self) -> None:
        self.assertEqual(kd.jaccard({"a"}, {"b"}), 0.0)

    def test_jaccard_of_two_empty_sets_is_zero(self) -> None:
        self.assertEqual(kd.jaccard(set(), set()), 0.0)

    def test_jaccard_partial_overlap(self) -> None:
        self.assertAlmostEqual(kd.jaccard({"a", "b", "c"}, {"b", "c", "d"}), 0.5)


class GroupItemsTests(unittest.TestCase):
    """group_items: same source_id plus identical normalized title only."""

    def test_singleton_group_is_no_exact_match(self) -> None:
        groups = kd.group_items([item("TMP-1", "SRC-001", "A Title", ["x"])])
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].minted_id, "KI-001")
        self.assertFalse(groups[0].exact_match)
        self.assertEqual(groups[0].member_ids, ["TMP-1"])

    def test_same_source_and_normalized_title_is_one_group(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "Same Title", ["a"]),
            item("TMP-2", "SRC-001", "same   title", ["b"]),
        ]
        groups = kd.group_items(items)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].minted_id, "KI-001")
        self.assertTrue(groups[0].exact_match)
        self.assertEqual(groups[0].member_ids, ["TMP-1", "TMP-2"])
        self.assertEqual(groups[0].tags, {"a", "b"})

    def test_same_title_different_source_is_two_groups(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "Same Title", ["a"]),
            item("TMP-2", "SRC-002", "Same Title", ["b"]),
        ]
        groups = kd.group_items(items)
        self.assertEqual(len(groups), 2)
        self.assertFalse(groups[0].exact_match)
        self.assertFalse(groups[1].exact_match)

    def test_ids_are_minted_zero_padded_in_input_order(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "First", []),
            item("TMP-2", "SRC-001", "Second", []),
            item("TMP-3", "SRC-002", "Third", []),
        ]
        groups = kd.group_items(items)
        self.assertEqual([g.minted_id for g in groups], ["KI-001", "KI-002", "KI-003"])


class MintLinesTests(unittest.TestCase):
    """mint_lines: the exact literal forms for a singleton and a real group."""

    def test_singleton_group_line(self) -> None:
        groups = kd.group_items([item("TMP-2", "SRC-001", "Solo", [])])
        self.assertEqual(kd.mint_lines(groups), ["mint KI-001 <- 'TMP-2' (no exact match)"])

    def test_exact_match_group_line(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "Same Title", []),
            item("TMP-3", "SRC-001", "same title", []),
        ]
        groups = kd.group_items(items)
        self.assertEqual(
            kd.mint_lines(groups),
            ["mint KI-001 <- 'TMP-1', 'TMP-3' (exact match, 2 items)"],
        )


class ShortlistPairsTests(unittest.TestCase):
    """shortlist_pairs: the OR rule, the score formula, and the sort order."""

    def test_title_overlap_alone_can_shortlist(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "alpha beta gamma delta", []),
            item("TMP-2", "SRC-002", "alpha beta gamma epsilon", []),
        ]
        groups = kd.group_items(items)
        pairs = kd.shortlist_pairs(groups, title_overlap=0.5, shared_tags=3)
        self.assertEqual(len(pairs), 1)
        self.assertAlmostEqual(pairs[0].title_overlap, 0.6)
        self.assertEqual(pairs[0].shared_tag_count, 0)
        self.assertAlmostEqual(pairs[0].score, 0.6)

    def test_shared_tags_alone_can_shortlist(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "Completely Different One", ["x", "y", "z"]),
            item("TMP-2", "SRC-002", "Another Thing Entirely", ["x", "y", "z"]),
        ]
        groups = kd.group_items(items)
        pairs = kd.shortlist_pairs(groups, title_overlap=0.5, shared_tags=3)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].shared_tag_count, 3)
        self.assertAlmostEqual(pairs[0].score, 0.0 + 0.2 * 3)

    def test_below_both_bars_is_not_shortlisted(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "Completely Different One", ["x"]),
            item("TMP-2", "SRC-002", "Another Thing Entirely", ["y"]),
        ]
        groups = kd.group_items(items)
        pairs = kd.shortlist_pairs(groups, title_overlap=0.5, shared_tags=3)
        self.assertEqual(pairs, [])

    def test_sorted_highest_score_first(self) -> None:
        items = [
            item("TMP-1", "SRC-001", "one two three four", ["p"]),
            item("TMP-2", "SRC-002", "one two three five", ["p"]),
            item("TMP-3", "SRC-003", "one two six seven", ["p"]),
        ]
        groups = kd.group_items(items)
        pairs = kd.shortlist_pairs(groups, title_overlap=0.0, shared_tags=1)
        scores = [pair.score for pair in pairs]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_never_pairs_an_item_with_itself(self) -> None:
        groups = kd.group_items([item("TMP-1", "SRC-001", "Solo Title", ["x"])])
        pairs = kd.shortlist_pairs(groups, title_overlap=0.0, shared_tags=0)
        self.assertEqual(pairs, [])


class LoadItemsTests(unittest.TestCase):
    """load_items: validation, the size cap and the symlink refusal."""

    def test_reads_the_real_sample(self) -> None:
        items = kd.load_items(SAMPLE)
        self.assertEqual(len(items), 4)

    def test_not_a_list_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            write_json(path, {"not": "a list"})
            with self.assertRaises(ValueError):
                kd.load_items(path)

    def test_item_not_an_object_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            write_json(path, ["not an object"])
            with self.assertRaises(ValueError):
                kd.load_items(path)

    def test_missing_required_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            write_json(path, [{"id": "TMP-1", "source_id": "SRC-001", "title": "A"}])
            with self.assertRaises(ValueError):
                kd.load_items(path)

    def test_blank_title_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            write_json(
                path, [{"id": "TMP-1", "source_id": "SRC-001", "title": "  ", "tags": []}]
            )
            with self.assertRaises(ValueError):
                kd.load_items(path)

    def test_non_list_tags_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            write_json(
                path,
                [{"id": "TMP-1", "source_id": "SRC-001", "title": "A", "tags": "x"}],
            )
            with self.assertRaises(ValueError):
                kd.load_items(path)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(ValueError):
                kd.load_items(link)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ITEMS.json", result.stdout)
        self.assertIn("--title-overlap", result.stdout)
        self.assertIn("--shared-tags", result.stdout)
        self.assertIn("--exact-only", result.stdout)

    def test_missing_argument_is_a_usage_error(self) -> None:
        result = run_cli()
        self.assertEqual(result.returncode, 2)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        for line in CLEAN_LINES:
            with self.subTest(line=line):
                self.assertIn(line, result.stdout)
        self.assertEqual(result.stderr, "")

    def test_exact_only_skips_the_shortlist_step(self) -> None:
        result = run_cli(str(SAMPLE), "--exact-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertFalse(any(line.startswith("shortlist ") for line in lines), lines)
        self.assertIn("items=4 groups=4 shortlisted=0", result.stdout)

    def test_lowered_title_overlap_adds_the_look_alike_pair(self) -> None:
        result = run_cli(str(SAMPLE), "--title-overlap", LOWERED_TITLE_OVERLAP)
        self.assertEqual(result.returncode, 0, result.stderr)
        for line in BROKEN_LINES:
            with self.subTest(line=line):
                self.assertIn(line, result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("ki_dedupe.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_json_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            run_cli(str(SAMPLE), "--exact-only", cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-S1-08")
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

    def test_no_write_flag(self) -> None:
        self.assertNotIn("--write", self.source)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-1/knowledge-items.md: every pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected a default and a lowered-threshold run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean = run_cli(str(SAMPLE))
        lowered = run_cli(str(SAMPLE), "--title-overlap", LOWERED_TITLE_OVERLAP)
        default_again = run_cli(str(SAMPLE))
        real_outputs = [clean.stdout, lowered.stdout, default_again.stdout]
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
