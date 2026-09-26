"""Unit tests for scripts/s5/format_rules_check.py and
docs/stage-5/distractors-and-format-rules.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory. The page-output tests re-run the real script and
compare its output with the text pasted on the page, so the page can
never drift from the script.

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
SCRIPT = ROOT / "scripts" / "s5" / "format_rules_check.py"
SAMPLE = ROOT / "scripts" / "sample_data" / "git_basics_stage5" / "stems" / "stems.json"
PAGE = ROOT / "docs" / "stage-5" / "distractors-and-format-rules.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("format_rules_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


frc = load_module()


def distractor(
    option: str,
    text: str = "A plausible wrong answer of ordinary length.",
    misconception: str | None = "A named misconception behind this option.",
) -> dict[str, Any]:
    """A minimal, otherwise-valid distractor."""
    entry: dict[str, Any] = {"option": option, "text": text}
    if misconception is not None:
        entry["misconception"] = misconception
    return entry


def base_stem(stem_id: str = "STEM-9.9-001") -> dict[str, Any]:
    """A small, clean stem: three distractors, no rule violations."""
    return {
        "stem_id": stem_id,
        "difficulty": "easy",
        "cognitive_level": "knowledge",
        "bloom_level": "understand",
        "concept_item_ids": ["ACI-9-001"],
        "stem_content": "What does this sample stem ask about?",
        "correct_answer": "A",
        "correct_answer_text": "The correct option, of an ordinary, typical length.",
        "distractors": [distractor("B"), distractor("C"), distractor("D")],
        "explanation": "An explanation of the correct answer.",
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


class TokenAndPhraseHelperTests(unittest.TestCase):
    """The small text-matching helpers behind the format checks."""

    def test_tokens_splits_on_punctuation(self) -> None:
        self.assertEqual(
            frc._tokens("Is `notes.txt` really not staged?"),
            ["is", "notes", "txt", "really", "not", "staged"],
        )

    def test_negative_words_used_ignores_substrings(self) -> None:
        # "notes" contains "no" and "cannot" contains "not" as substrings;
        # neither should match, since matching is on whole tokens.
        self.assertEqual(frc._negative_words_used("Where are notes.txt now?"), [])
        self.assertEqual(frc._negative_words_used("You cannot skip this."), [])

    def test_negative_words_used_finds_real_words_in_list_order(self) -> None:
        self.assertEqual(
            frc._negative_words_used("Which is not true, except this one?"),
            ["not", "except"],
        )

    def test_multi_answer_phrase_found(self) -> None:
        self.assertEqual(
            frc._multi_answer_phrase("Select all that apply below."),
            "select all",
        )

    def test_multi_answer_phrase_absent(self) -> None:
        self.assertIsNone(frc._multi_answer_phrase("Pick the one best answer."))

    def test_is_all_or_none_both_forms(self) -> None:
        self.assertTrue(frc._is_all_or_none("All of the above."))
        self.assertTrue(frc._is_all_or_none("none of the above"))
        self.assertFalse(frc._is_all_or_none("Above all, stage the file first."))


class CheckOneStemTests(unittest.TestCase):
    """Every per-stem error path, exercised on a small in-memory fixture."""

    def test_clean_stem_has_no_findings(self) -> None:
        self.assertEqual(frc.check_one_stem(base_stem(), "stem X"), [])

    def test_missing_stem_content(self) -> None:
        stem = base_stem()
        del stem["stem_content"]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("missing-field" in e and "stem_content" in e for e in errors), errors
        )

    def test_missing_correct_answer(self) -> None:
        stem = base_stem()
        del stem["correct_answer"]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("missing-field" in e and "correct_answer'" in e for e in errors),
            errors,
        )

    def test_missing_correct_answer_text(self) -> None:
        stem = base_stem()
        del stem["correct_answer_text"]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("missing-field" in e and "correct_answer_text" in e for e in errors),
            errors,
        )

    def test_missing_distractors(self) -> None:
        stem = base_stem()
        del stem["distractors"]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("missing-field" in e and "distractors" in e for e in errors)
        )
        self.assertTrue(any("distractor-count" in e for e in errors), errors)

    def test_multi_answer_error(self) -> None:
        stem = base_stem()
        stem["stem_content"] = "Select all correct options below."
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("multi-answer" in e for e in errors), errors)

    def test_negative_stem_error(self) -> None:
        stem = base_stem()
        stem["stem_content"] = "Which of these is not a real Git command?"
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("negative-stem" in e and "not" in e for e in errors), errors
        )

    def test_all_or_none_on_distractor(self) -> None:
        stem = base_stem()
        stem["distractors"][0]["text"] = "All of the above."
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("all-or-none" in e for e in errors), errors)

    def test_all_or_none_on_correct_answer_text(self) -> None:
        stem = base_stem()
        stem["correct_answer_text"] = "None of the above."
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("all-or-none" in e and "correct_answer_text" in e for e in errors),
            errors,
        )

    def test_missing_misconception_error(self) -> None:
        stem = base_stem()
        stem["distractors"] = [
            distractor("B", misconception=None),
            distractor("C"),
            distractor("D"),
        ]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(
            any("missing-misconception" in e and "distractor B" in e for e in errors),
            errors,
        )

    def test_too_few_distractors_error(self) -> None:
        stem = base_stem()
        stem["distractors"] = [distractor("B"), distractor("C")]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("distractor-count" in e and "has 2" in e for e in errors))

    def test_too_many_distractors_error(self) -> None:
        stem = base_stem()
        stem["distractors"] = [
            distractor("B"),
            distractor("C"),
            distractor("D"),
            distractor("E"),
            distractor("F"),
        ]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("distractor-count" in e and "has 5" in e for e in errors))

    def test_parallel_length_too_short(self) -> None:
        stem = base_stem()
        stem["correct_answer_text"] = "A correct answer of ordinary length here."
        stem["distractors"][0]["text"] = "No."
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("parallel-length" in e for e in errors), errors)

    def test_parallel_length_too_long(self) -> None:
        stem = base_stem()
        stem["correct_answer_text"] = "Short answer."
        stem["distractors"][0]["text"] = "A" * 60
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("parallel-length" in e for e in errors), errors)

    def test_bad_distractor_not_an_object(self) -> None:
        stem = base_stem()
        stem["distractors"] = [distractor("B"), distractor("C"), "not an object"]
        errors = frc.check_one_stem(stem, "stem X")
        self.assertTrue(any("bad-distractor" in e for e in errors), errors)


class CheckStemsTests(unittest.TestCase):
    """check_stems: the whole-list walk, duplicates and the skip behavior."""

    def test_clean_two_stem_bank_has_no_errors(self) -> None:
        data = [base_stem("STEM-9.9-001"), base_stem("STEM-9.9-002")]
        notes, errors, checked = frc.check_stems(data, include_broken=False)
        self.assertEqual(errors, [])
        self.assertEqual(notes, [])
        self.assertEqual(checked, 2)

    def test_bad_stem_not_an_object(self) -> None:
        data = [base_stem(), "not a stem"]
        _, errors, _ = frc.check_stems(data, include_broken=False)
        self.assertTrue(any("bad-stem" in e for e in errors), errors)

    def test_duplicate_stem_id(self) -> None:
        data = [base_stem("STEM-9.9-001"), base_stem("STEM-9.9-001")]
        _, errors, _ = frc.check_stems(data, include_broken=False)
        self.assertTrue(any("duplicate-id" in e for e in errors), errors)

    def test_broken_on_purpose_skipped_by_default(self) -> None:
        broken = base_stem("STEM-9.9-BROKEN")
        broken["broken_on_purpose"] = True
        broken["stem_content"] = "Which is not correct, except this one?"
        data = [base_stem("STEM-9.9-001"), broken]
        notes, errors, checked = frc.check_stems(data, include_broken=False)
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)
        self.assertTrue(any("STEM-9.9-BROKEN" in n for n in notes), notes)

    def test_broken_on_purpose_checked_with_flag(self) -> None:
        broken = base_stem("STEM-9.9-BROKEN")
        broken["broken_on_purpose"] = True
        broken["stem_content"] = "Which is not correct, except this one?"
        data = [base_stem("STEM-9.9-001"), broken]
        notes, errors, checked = frc.check_stems(data, include_broken=True)
        self.assertEqual(notes, [])
        self.assertEqual(checked, 2)
        self.assertTrue(any("negative-stem" in e for e in errors), errors)

    def test_not_a_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            frc.check_stems({"not": "a list"}, include_broken=False)


class LoadStemsTests(unittest.TestCase):
    """load_stems: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_sample_file(self) -> None:
        data = frc.load_stems(SAMPLE)
        self.assertEqual(len(data), 3)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                frc.load_stems(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * frc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                frc.load_stems(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input problem."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "stems.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), [base_stem()])
            self.assertEqual(frc.main([str(path)]), 0)

    def test_exit_one_on_any_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stem = base_stem()
            stem["distractors"][0]["text"] = "All of the above."
            path = self.write(Path(tmp), [stem])
            self.assertEqual(frc.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(frc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(frc.main([str(path)]), 2)

    def test_exit_two_on_non_list_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), {"not": "a list"})
            self.assertEqual(frc.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("STEMS", result.stdout)
        self.assertIn("--include-broken-examples", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            'note: stem "STEM-2.1-BROKEN" is marked broken_on_purpose; skipped '
            "(rerun with --include-broken-examples to check it)",
            result.stdout,
        )
        self.assertIn("stems=2 errors=0", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_include_broken_examples_shows_the_miss(self) -> None:
        result = run_cli(str(SAMPLE), "--include-broken-examples")
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            'error negative-stem: stem "STEM-2.1-BROKEN" stem_content uses a '
            "banned word: not, except",
            result.stdout,
        )
        self.assertIn(
            'error all-or-none: stem "STEM-2.1-BROKEN" distractor B text is '
            "'All of the above.'",
            result.stdout,
        )
        self.assertIn(
            'error missing-misconception: stem "STEM-2.1-BROKEN" distractor C '
            "has no misconception",
            result.stdout,
        )
        self.assertIn("stems=3 errors=4", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("format_rules_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
            run_cli(str(SAMPLE), "--include-broken-examples", cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-S5-03")
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

    def test_no_write_flag(self) -> None:
        self.assertNotIn("--write", self.source)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-5/distractors-and-format-rules.md: every pasted line is real."""

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
        broken = run_cli(str(SAMPLE), "--include-broken-examples")
        real_outputs = [clean.stdout, broken.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_ascii_only(self) -> None:
        self.assertTrue(self.page_text.isascii())


if __name__ == "__main__":
    unittest.main()
