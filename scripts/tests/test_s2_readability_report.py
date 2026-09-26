"""Unit tests for scripts/s2/readability_report.py and
docs/stage-2/readability-and-revision.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample passages (read-only). The page-output tests re-run the real
script and compare its output with the text pasted on the page, so the
page can never drift from the script.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import ast
import importlib.util
import re
import subprocess  # nosec B404
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "s2" / "readability_report.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_stage2" / "readability"
BEFORE = SAMPLE_DIR / "before.md"
AFTER = SAMPLE_DIR / "after.md"
PAGE = ROOT / "docs" / "stage-2" / "readability-and-revision.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("readability_report", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rr = load_module()


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


class SplitSentencesTests(unittest.TestCase):
    """split_sentences: delimiters, and text with no terminal punctuation."""

    def test_splits_on_period(self) -> None:
        self.assertEqual(
            rr.split_sentences("One sentence. Another one."),
            ["One sentence", "Another one"],
        )

    def test_splits_on_exclamation_and_question(self) -> None:
        self.assertEqual(
            rr.split_sentences("Stop! Really? Yes."), ["Stop", "Really", "Yes"]
        )

    def test_no_terminal_punctuation_is_one_sentence(self) -> None:
        self.assertEqual(rr.split_sentences("hello world"), ["hello world"])

    def test_punctuation_only_yields_no_sentence(self) -> None:
        self.assertEqual(rr.split_sentences("... !!! ???"), [])

    def test_empty_string_yields_no_sentence(self) -> None:
        self.assertEqual(rr.split_sentences(""), [])


class CountSyllablesTests(unittest.TestCase):
    """count_syllables: the vowel-group heuristic, and its silent-e rule."""

    def test_single_syllable_word(self) -> None:
        self.assertEqual(rr.count_syllables("cat"), 1)

    def test_two_syllable_word(self) -> None:
        self.assertEqual(rr.count_syllables("markers"), 2)

    def test_silent_e_is_dropped(self) -> None:
        self.assertEqual(rr.count_syllables("code"), 1)

    def test_le_ending_keeps_its_vowel_group(self) -> None:
        self.assertEqual(rr.count_syllables("able"), 2)

    def test_empty_or_non_letter_word_is_zero(self) -> None:
        self.assertEqual(rr.count_syllables("123"), 0)
        self.assertEqual(rr.count_syllables(""), 0)

    def test_never_returns_less_than_one_for_a_real_word(self) -> None:
        self.assertGreaterEqual(rr.count_syllables("a"), 1)


class ComputeScoresTests(unittest.TestCase):
    """compute_scores: the two formulas, and the two failure cases."""

    def test_raises_on_no_words(self) -> None:
        with self.assertRaises(ValueError):
            rr.compute_scores("... !!! ???")

    def test_raises_on_no_sentences(self) -> None:
        # split_sentences treats text with no delimiter as one sentence, so
        # this can only happen when there are also no words.
        with self.assertRaises(ValueError):
            rr.compute_scores("")

    def test_known_short_sentence(self) -> None:
        # Cross-check the two formulas against counts taken independently
        # from the same helper functions compute_scores itself calls.
        text = "Merging two branches is tricky."
        words = rr.WORD_RE.findall(text)
        sentences = rr.split_sentences(text)
        syllables = sum(rr.count_syllables(word) for word in words)
        wps = len(words) / len(sentences)
        spw = syllables / len(words)
        expected_grade = 0.39 * wps + 11.8 * spw - 15.59
        expected_ease = 206.835 - 1.015 * wps - 84.6 * spw
        grade, ease = rr.compute_scores(text)
        self.assertAlmostEqual(grade, expected_grade, places=6)
        self.assertAlmostEqual(ease, expected_ease, places=6)


class BandStatusTests(unittest.TestCase):
    """band_status and the two formatted lines."""

    def test_in_band_inclusive_of_both_ends(self) -> None:
        self.assertEqual(rr.band_status(9.0, 9.0, 11.0), "in-band")
        self.assertEqual(rr.band_status(11.0, 9.0, 11.0), "in-band")

    def test_out_of_band_below_and_above(self) -> None:
        self.assertEqual(rr.band_status(8.9, 9.0, 11.0), "out-of-band")
        self.assertEqual(rr.band_status(11.1, 9.0, 11.0), "out-of-band")

    def test_format_bound_drops_trailing_zero(self) -> None:
        self.assertEqual(rr.format_bound(9.0), "9")
        self.assertEqual(rr.format_bound(9.5), "9.5")

    def test_grade_line_format(self) -> None:
        line = rr.format_grade_line(12.1, 9.0, 11.0)
        self.assertEqual(line, "grade-level 12.10 (target 9-11) out-of-band")

    def test_reading_ease_line_format(self) -> None:
        line = rr.format_reading_ease_line(52.3, 60.0, 70.0)
        self.assertEqual(
            line,
            "reading-ease 52.30 (target 60-70, higher is easier) out-of-band",
        )


class LoadTextTests(unittest.TestCase):
    """load_text: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        text = rr.load_text(BEFORE)
        self.assertIn("conflict", text)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(BEFORE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                rr.load_text(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.md"
            big.write_text("a " * (rr.MAX_BYTES // 2 + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                rr.load_text(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 whether the score is in band or not, 2 for a bad input."""

    def write(self, tmp: Path, name: str, text: str) -> Path:
        path = tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_exit_zero_when_in_band(self) -> None:
        self.assertEqual(rr.main([str(AFTER)]), 0)

    def test_exit_zero_when_out_of_band(self) -> None:
        # in-band/out-of-band never changes the exit code.
        self.assertEqual(rr.main([str(BEFORE)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rr.main([str(Path(tmp) / "nope.md")]), 2)

    def test_exit_two_on_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "empty.md", "")
            self.assertEqual(rr.main([str(path)]), 2)

    def test_exit_two_when_grade_low_above_grade_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "text.md", "Merging two branches.")
            self.assertEqual(
                rr.main([str(path), "--grade-low", "20", "--grade-high", "10"]), 2
            )

    def test_exit_two_when_re_low_above_re_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "text.md", "Merging two branches.")
            self.assertEqual(
                rr.main([str(path), "--re-low", "80", "--re-high", "10"]), 2
            )

    def test_exit_two_on_usage_error(self) -> None:
        # argparse itself exits the process on a bad --grade-low value,
        # rather than returning from main(), so this checks SystemExit.
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "text.md", "Merging two branches.")
            with self.assertRaises(SystemExit) as cm:
                rr.main([str(path), "--grade-low", "not-a-number"])
            self.assertEqual(cm.exception.code, 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real samples."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TEXT", result.stdout)
        self.assertIn("--grade-low", result.stdout)

    def test_before_is_out_of_band_both_ways(self) -> None:
        rel = BEFORE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("out-of-band", result.stdout)
        lines = result.stdout.splitlines()
        self.assertTrue(lines[0].startswith("grade-level "))
        self.assertTrue(lines[1].startswith("reading-ease "))

    def test_after_is_in_band_both_ways(self) -> None:
        rel = AFTER.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("in-band", result.stdout)
        self.assertNotIn("out-of-band", result.stdout)

    def test_after_reads_noticeably_better_than_before(self) -> None:
        before_grade, before_ease = rr.compute_scores(rr.load_text(BEFORE))
        after_grade, after_ease = rr.compute_scores(rr.load_text(AFTER))
        self.assertLess(after_grade, before_grade)
        self.assertGreater(after_ease, before_ease)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.md"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("readability_report.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(BEFORE), cwd=Path(tmp))
            run_cli(str(AFTER), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-S2-03")
        self.assertEqual(fields["Stage"], "S2")
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
        self.assertIn("in-band and out-of-band never", lowered)
        self.assertIn("never passes or fails anything by itself", lowered)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-2/readability-and-revision.md: every pasted line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected the before.md run and the after.md run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        before_run = run_cli(str(BEFORE))
        after_run = run_cli(str(AFTER))
        real_outputs = [before_run.stdout, after_run.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_page_states_the_no_pass_fail_limit_near_the_command(self) -> None:
        # The plan requires this right next to the script block, not only
        # in Common failures: check it appears before that heading.
        common_failures_pos = self.page_text.find("## Common failures")
        self.assertGreater(common_failures_pos, -1)
        before_common_failures = self.page_text[:common_failures_pos]
        self.assertIn("in-band", before_common_failures)
        self.assertIn("out-of-band", before_common_failures)
        self.assertIn("never change its exit code", before_common_failures)
        self.assertIn(
            "never passes or fails anything by itself", before_common_failures
        )

    def test_page_does_not_use_unsourced_fk_figures(self) -> None:
        self.assertNotIn("55-65", self.page_text)
        self.assertNotIn("55 to 65", self.page_text)
        self.assertNotIn("college level", self.page_text.casefold())


if __name__ == "__main__":
    unittest.main()
