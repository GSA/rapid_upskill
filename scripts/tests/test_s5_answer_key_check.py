"""Unit tests for scripts/s5/answer_key_check.py and
docs/stage-5/quiz-and-exam-assembly.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory. The checked-in answer key
(scripts/sample_data/git_basics_stage5/answer_key/key.json) is this
guide's own sample data, so it is read directly; the stems it checks
against are this test file's own fixture, matching the two stem ids
the shared plan for this batch fixes (STEM-2.1-001, STEM-2.1-002), so
this file runs on its own without waiting on any other file. The
page-output tests re-run the real script and compare its output with
the text pasted on the page, so the page can never drift from the
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
SCRIPT = ROOT / "scripts" / "s5" / "answer_key_check.py"
KEY_SAMPLE = (
    ROOT / "scripts" / "sample_data" / "git_basics_stage5" / "answer_key" / "key.json"
)
PAGE = ROOT / "docs" / "stage-5" / "quiz-and-exam-assembly.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("answer_key_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


akc = load_module()


def distractor(option: str) -> dict[str, str]:
    """A minimal, otherwise-valid distractor."""
    return {
        "option": option,
        "text": f"Distractor {option}.",
        "misconception": f"Misconception behind {option}.",
    }


def stem(stem_id: str, correct_answer: str, distractor_options: str) -> dict[str, Any]:
    """A minimal, otherwise-valid stem: correct answer plus its distractors."""
    return {
        "stem_id": stem_id,
        "difficulty": "easy",
        "correct_answer": correct_answer,
        "distractors": [distractor(option) for option in distractor_options],
    }


FALLBACK_STEMS: list[dict[str, Any]] = [
    stem("STEM-2.1-001", "A", "BCD"),
    stem("STEM-2.1-002", "A", "BCD"),
]


def stems_fixture_path(tmp: Path) -> Path:
    """Write this test file's own two-stem fixture and return its path.

    This mirrors the two stem ids the shared plan for this batch fixes,
    each with a correct answer of A and three distractors (B, C, D), the
    same shape the checked-in answer key expects.
    """
    path = tmp / "stems.json"
    path.write_text(json.dumps(FALLBACK_STEMS), encoding="utf-8")
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


class BuildStemIndexTests(unittest.TestCase):
    """build_stem_index: valid letters, skipped malformed entries."""

    def test_valid_letters_include_correct_answer_and_distractors(self) -> None:
        index = akc.build_stem_index([stem("STEM-2.1-001", "A", "BCD")])
        self.assertEqual(index["STEM-2.1-001"]["valid_letters"], {"A", "B", "C", "D"})
        self.assertEqual(index["STEM-2.1-001"]["correct_answer"], "A")

    def test_stem_missing_stem_id_is_skipped(self) -> None:
        index = akc.build_stem_index([{"correct_answer": "A", "distractors": []}])
        self.assertEqual(index, {})

    def test_stem_not_an_object_is_skipped(self) -> None:
        index = akc.build_stem_index(["not a stem"])
        self.assertEqual(index, {})

    def test_distractor_not_an_object_is_skipped(self) -> None:
        index = akc.build_stem_index(
            [{"stem_id": "S1", "correct_answer": "A", "distractors": ["bad"]}]
        )
        self.assertEqual(index["S1"]["valid_letters"], {"A"})

    def test_not_a_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            akc.build_stem_index({"not": "a list"})


class OptionRangeTests(unittest.TestCase):
    """option_range: a compact first-to-last range string."""

    def test_range_of_four_letters(self) -> None:
        self.assertEqual(akc.option_range({"A", "B", "C", "D"}), "(A-D)")

    def test_empty_set(self) -> None:
        self.assertEqual(akc.option_range(set()), "(none)")


class CheckAnswerKeyTests(unittest.TestCase):
    """check_answer_key: every error path, on a small in-memory fixture."""

    def setUp(self) -> None:
        self.index = akc.build_stem_index(FALLBACK_STEMS)

    def test_clean_key_has_no_errors(self) -> None:
        entries = [
            {
                "stem_id": "STEM-2.1-001",
                "correct_answer": "A",
                "points": 5,
                "feedback_correct": "Correct.",
                "feedback_by_distractor": {"B": "b", "C": "c", "D": "d"},
            }
        ]
        errors, count = akc.check_answer_key(entries, self.index)
        self.assertEqual(errors, [])
        self.assertEqual(count, 1)

    def test_entry_not_an_object_error(self) -> None:
        errors, _ = akc.check_answer_key(["not an object"], self.index)
        self.assertTrue(any("is not a JSON object" in e for e in errors), errors)

    def test_missing_stem_error(self) -> None:
        entries = [{"stem_id": "STEM-2.1-999", "correct_answer": "A"}]
        errors, _ = akc.check_answer_key(entries, self.index)
        self.assertTrue(
            any('stem "STEM-2.1-999" is not in the stems file' in e for e in errors),
            errors,
        )

    def test_mismatch_error(self) -> None:
        entries = [{"stem_id": "STEM-2.1-001", "correct_answer": "B"}]
        errors, _ = akc.check_answer_key(entries, self.index)
        self.assertTrue(
            any(
                'has correct_answer "B", but its own stem records '
                'correct_answer "A"' in e
                for e in errors
            ),
            errors,
        )

    def test_out_of_range_correct_answer_error(self) -> None:
        entries = [{"stem_id": "STEM-2.1-001", "correct_answer": "F"}]
        errors, _ = akc.check_answer_key(entries, self.index)
        self.assertTrue(
            any(
                'answer "F" is outside its own option range (A-D)' in e for e in errors
            ),
            errors,
        )

    def test_out_of_range_feedback_key_error(self) -> None:
        entries = [
            {
                "stem_id": "STEM-2.1-001",
                "correct_answer": "A",
                "feedback_by_distractor": {"E": "not a real option here"},
            }
        ]
        errors, _ = akc.check_answer_key(entries, self.index)
        self.assertTrue(
            any(
                'answer "E" is outside its own option range (A-D)' in e for e in errors
            ),
            errors,
        )

    def test_not_a_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            akc.check_answer_key({"not": "a list"}, self.index)


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"
            path.write_text("[1, 2, 3]", encoding="utf-8")
            self.assertEqual(akc.load_json(path), [1, 2, 3])

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.json"
            target.write_text("[]", encoding="utf-8")
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                akc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * akc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                akc.load_json(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input problem."""

    def write_key(self, tmp: Path, entries: list[dict[str, Any]]) -> Path:
        path = tmp / "key.json"
        path.write_text(json.dumps(entries), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            key_path = self.write_key(
                tmp_path, [{"stem_id": "STEM-2.1-001", "correct_answer": "A"}]
            )
            self.assertEqual(akc.main([str(key_path), str(stems_path)]), 0)

    def test_exit_one_on_any_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            key_path = self.write_key(
                tmp_path, [{"stem_id": "STEM-2.1-001", "correct_answer": "F"}]
            )
            self.assertEqual(akc.main([str(key_path), str(stems_path)]), 1)

    def test_exit_two_on_missing_key_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            missing = tmp_path / "nope.json"
            self.assertEqual(akc.main([str(missing), str(stems_path)]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            bad = tmp_path / "bad.json"
            bad.write_text("not json", encoding="utf-8")
            self.assertEqual(akc.main([str(bad), str(stems_path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("KEY", result.stdout)
        self.assertIn("STEMS", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = KEY_SAMPLE.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            stems_path = stems_fixture_path(Path(tmp))
            result = run_cli(rel, str(stems_path), cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("entries=2 errors=0", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stems_path = stems_fixture_path(Path(tmp))
            result = run_cli(str(Path(tmp) / "nope.json"), str(stems_path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("answer_key_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            before = set(tmp_path.iterdir())
            run_cli(str(KEY_SAMPLE), str(stems_path), cwd=tmp_path)
            after = set(tmp_path.iterdir())
            self.assertEqual(before, after)


class BreakOnPurposeTests(unittest.TestCase):
    """The page's break-on-purpose edit, applied to a temporary copy."""

    def test_out_of_range_letter_is_a_loud_error(self) -> None:
        original = json.loads(KEY_SAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(original[0]["stem_id"], "STEM-2.1-001")
        original[0]["correct_answer"] = "F"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            key_path = tmp_path / "key-broken.json"
            key_path.write_text(json.dumps(original), encoding="utf-8")
            result = run_cli(str(key_path), str(stems_path))
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            'error: stem "STEM-2.1-001" answer "F" is outside its own option '
            "range (A-D)",
            result.stdout,
        )
        self.assertIn("entries=2 errors=1", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S5-05")
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


class PageOutputTests(unittest.TestCase):
    """docs/stage-5/quiz-and-exam-assembly.md: every pasted output line is real."""

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
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stems_path = stems_fixture_path(tmp_path)
            clean = run_cli(str(KEY_SAMPLE), str(stems_path))

            broken_entries = json.loads(KEY_SAMPLE.read_text(encoding="utf-8"))
            broken_entries[0]["correct_answer"] = "F"
            broken_key_path = tmp_path / "key-broken.json"
            broken_key_path.write_text(json.dumps(broken_entries), encoding="utf-8")
            broken = run_cli(str(broken_key_path), str(stems_path))

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
