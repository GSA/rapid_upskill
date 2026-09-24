"""Unit tests for scripts/s1/concept_lint.py and docs/stage-1/concept-extraction.md.

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
SCRIPT = ROOT / "scripts" / "s1" / "concept_lint.py"
SAMPLE = ROOT / "scripts" / "sample_data" / "git_basics_stage1" / "extraction" / (
    "SRC-002.concepts.json"
)
PAGE = ROOT / "docs" / "stage-1" / "concept-extraction.md"
BROKEN_NEEDLE = '"type": "part-of"'
BROKEN_REPLACEMENT = '"type": "contains"'


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("concept_lint", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cl = load_module()


def word_definition(count: int) -> str:
    """A definition of exactly count whitespace-separated words."""
    return " ".join(["word"] * count)


def concept(name: str = "Two words", def_words: int = 20, **extra: Any) -> dict[str, Any]:
    """A minimal, otherwise-valid concept."""
    data: dict[str, Any] = {
        "name": name,
        "definition": word_definition(def_words),
        "relations": [],
    }
    data.update(extra)
    return data


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


class ParseRangeTests(unittest.TestCase):
    """parse_range: default, a custom range, and every rejected form."""

    def test_default_when_none(self) -> None:
        self.assertEqual(cl.parse_range(None, (2, 5), "--name-words"), (2, 5))

    def test_custom_range(self) -> None:
        self.assertEqual(cl.parse_range("3-9", (2, 5), "--name-words"), (3, 9))

    def test_wrong_shape_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cl.parse_range("2-5-9", (2, 5), "--name-words")

    def test_non_integer_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cl.parse_range("a-b", (2, 5), "--name-words")

    def test_low_over_high_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cl.parse_range("5-2", (2, 5), "--name-words")


class ParseSimilarTests(unittest.TestCase):
    """parse_similar: default, a custom value, and every rejected form."""

    def test_default_when_none(self) -> None:
        self.assertEqual(cl.parse_similar(None, 0.85), 0.85)

    def test_custom_value(self) -> None:
        self.assertEqual(cl.parse_similar("0.5", 0.85), 0.5)

    def test_not_a_number_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cl.parse_similar("nope", 0.85)

    def test_out_of_range_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cl.parse_similar("2", 0.85)


class JaccardTests(unittest.TestCase):
    """_jaccard: word-set overlap, lower-cased, on the two strings."""

    def test_identical_strings_overlap_fully(self) -> None:
        self.assertEqual(cl._jaccard("Alpha Beta", "alpha beta"), 1.0)

    def test_disjoint_strings_do_not_overlap(self) -> None:
        self.assertEqual(cl._jaccard("Alpha", "Gamma"), 0.0)

    def test_partial_overlap(self) -> None:
        self.assertAlmostEqual(cl._jaccard("Alpha Beta", "Alpha Beta Gamma"), 2 / 3)

    def test_non_string_is_zero(self) -> None:
        self.assertEqual(cl._jaccard(None, "Alpha"), 0.0)


class CheckConceptsErrorTests(unittest.TestCase):
    """Every error path, exercised on small in-memory fixtures."""

    def check(self, data: Any) -> tuple[list[str], list[str]]:
        errors, warnings, _, _ = cl.check_concepts(data, (2, 5), (15, 50), 0.85)
        return errors, warnings

    def test_clean_pair_has_no_errors(self) -> None:
        data = [
            concept(
                "Alpha term",
                20,
                relations=[
                    {"type": "depends-on", "target": "Beta term", "quote": "a quote"}
                ],
            ),
            concept("Beta term", 20),
        ]
        errors, _ = self.check(data)
        self.assertEqual(errors, [])

    def test_name_too_short_error(self) -> None:
        data = [concept("Onlyone", 20)]
        errors, _ = self.check(data)
        self.assertTrue(any("name-length" in e for e in errors), errors)

    def test_name_too_long_error(self) -> None:
        data = [concept("One two three four five six", 20)]
        errors, _ = self.check(data)
        self.assertTrue(any("name-length" in e for e in errors), errors)

    def test_definition_too_short_error(self) -> None:
        data = [concept("Alpha term", 5)]
        errors, _ = self.check(data)
        self.assertTrue(any("def-length" in e and "5-word" in e for e in errors), errors)

    def test_definition_too_long_error(self) -> None:
        data = [concept("Alpha term", 60)]
        errors, _ = self.check(data)
        self.assertTrue(any("def-length" in e for e in errors), errors)

    def test_duplicate_name_error(self) -> None:
        data = [concept("Alpha term", 20), concept("Alpha term", 20)]
        errors, _ = self.check(data)
        self.assertTrue(any("duplicate-name" in e for e in errors), errors)

    def test_bad_relation_type_error(self) -> None:
        data = [
            concept(
                "Alpha term",
                20,
                relations=[{"type": "invented", "target": "Alpha term", "quote": "q"}],
            )
        ]
        errors, _ = self.check(data)
        self.assertTrue(any("bad-relation-type" in e for e in errors), errors)

    def test_bad_target_error(self) -> None:
        data = [
            concept(
                "Alpha term",
                20,
                relations=[
                    {"type": "depends-on", "target": "Missing term", "quote": "q"}
                ],
            )
        ]
        errors, _ = self.check(data)
        self.assertTrue(any("bad-target" in e for e in errors), errors)

    def test_empty_quote_error(self) -> None:
        data = [
            concept(
                "Alpha term",
                20,
                relations=[{"type": "depends-on", "target": "Alpha term", "quote": ""}],
            )
        ]
        errors, _ = self.check(data)
        self.assertTrue(any("empty-quote" in e for e in errors), errors)

    def test_bad_concept_not_an_object_error(self) -> None:
        data = [concept("Alpha term", 20), "not a concept"]
        errors, _ = self.check(data)
        self.assertTrue(any("bad-concept" in e for e in errors), errors)

    def test_bad_relation_not_a_list_error(self) -> None:
        data = [concept("Alpha term", 20, relations="not a list")]
        errors, _ = self.check(data)
        self.assertTrue(any("bad-relation" in e for e in errors), errors)

    def test_bad_relation_not_an_object_error(self) -> None:
        data = [concept("Alpha term", 20, relations=["not a relation"])]
        errors, _ = self.check(data)
        self.assertTrue(any("bad-relation" in e for e in errors), errors)

    def test_not_a_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            cl.check_concepts({}, (2, 5), (15, 50), 0.85)


class CheckConceptsWarningTests(unittest.TestCase):
    """Every warning path; none of these change the exit code by themselves."""

    def check(self, data: Any, similar: float = 0.85) -> tuple[list[str], list[str]]:
        errors, warnings, _, _ = cl.check_concepts(data, (2, 5), (15, 50), similar)
        return errors, warnings

    def test_near_duplicate_name_warning(self) -> None:
        data = [concept("Alpha beta", 20), concept("Alpha beta", 20)]
        # duplicate-name is also an error; use different definitions to
        # isolate the near-duplicate-name warning from near-duplicate-definition.
        data[0]["definition"] = word_definition(20)
        data[1]["definition"] = "different " * 19 + "content"
        data[1]["name"] = "Beta alpha"
        _, warnings = self.check(data)
        self.assertTrue(any("near-duplicate-name" in w for w in warnings), warnings)

    def test_near_duplicate_definition_warning(self) -> None:
        data = [concept("Alpha term", 20), concept("Beta term", 20)]
        _, warnings = self.check(data)
        self.assertTrue(any("near-duplicate-definition" in w for w in warnings), warnings)

    def test_no_near_duplicate_below_threshold(self) -> None:
        data = [
            concept("Alpha term", 20),
            {
                "name": "Gamma delta",
                "definition": " ".join(f"epsilon{i}" for i in range(20)),
                "relations": [],
            },
        ]
        _, warnings = self.check(data)
        self.assertFalse(any("near-duplicate" in w for w in warnings), warnings)

    def test_avg_relations_low_warning(self) -> None:
        data = [concept("Alpha term", 20), concept("Beta term", 20)]
        _, warnings = self.check(data)
        self.assertTrue(any("avg-relations" in w for w in warnings), warnings)

    def test_avg_relations_high_warning(self) -> None:
        relations = [
            {"type": "depends-on", "target": "Alpha term", "quote": f"q{i}"}
            for i in range(3)
        ]
        data = [concept("Alpha term", 20, relations=relations)]
        _, warnings = self.check(data)
        self.assertTrue(any("avg-relations" in w for w in warnings), warnings)

    def test_avg_relations_in_band_is_silent(self) -> None:
        rel_a = [
            {"type": "depends-on", "target": "Beta term", "quote": "q1"},
            {"type": "part-of", "target": "Beta term", "quote": "q2"},
        ]
        rel_b = [
            {"type": "contrasts-with", "target": "Alpha term", "quote": "q3"},
            {"type": "example-of", "target": "Alpha term", "quote": "q4"},
        ]
        data = [
            concept("Alpha term", 20, relations=rel_a),
            concept("Beta term", 20, relations=rel_b),
        ]
        _, warnings = self.check(data)
        self.assertFalse(any("avg-relations" in w for w in warnings), warnings)

    def test_no_concepts_skips_avg_relations(self) -> None:
        _, warnings = self.check([])
        self.assertEqual(warnings, [])


class LoadConceptsTests(unittest.TestCase):
    """load_concepts: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        data = cl.load_concepts(SAMPLE)
        self.assertEqual(len(data), 6)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                cl.load_concepts(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * cl.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                cl.load_concepts(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean or warning-only, 1 for any error, 2 for bad input."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "concepts.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_sample(self) -> None:
        self.assertEqual(cl.main([str(SAMPLE)]), 0)

    def test_exit_one_on_any_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = [concept("Onlyone", 20)]
            path = self.write(Path(tmp), data)
            self.assertEqual(cl.main([str(path)]), 1)

    def test_exit_zero_with_only_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = [concept("Alpha term", 20), concept("Beta term", 20)]
            path = self.write(Path(tmp), data)
            self.assertEqual(cl.main([str(path)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cl.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(cl.main([str(path)]), 2)

    def test_exit_two_on_bad_flag(self) -> None:
        self.assertEqual(cl.main([str(SAMPLE), "--name-words", "a-b"]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CONCEPTS", result.stdout)
        self.assertIn("--similar", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(), "concepts=6 relations=11 errors=0 warnings=0"
        )
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("concept_lint.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a temporary copy."""

    def test_invalid_relation_type_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "concepts.json"
            original = SAMPLE.read_text(encoding="utf-8")
            self.assertEqual(original.count(BROKEN_NEEDLE), 1)
            copy_path.write_text(
                original.replace(BROKEN_NEEDLE, BROKEN_REPLACEMENT, 1), encoding="utf-8"
            )
            result = run_cli(str(copy_path))
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "error bad-relation-type: concept 'Detached HEAD' relation #1 has "
            "type 'contains', not in depends-on, part-of, implemented-by, "
            "contrasts-with, example-of",
            result.stdout,
        )
        self.assertIn("concepts=6 relations=11 errors=1 warnings=0", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S1-06")
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
    """docs/stage-1/concept-extraction.md: every pasted output line is real."""

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
            copy_path = Path(tmp) / "concepts.json"
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
