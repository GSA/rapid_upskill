"""Unit tests for scripts/s2/condensation_check.py and
docs/stage-2/condensation.md.

Everything runs offline, on synthetic text built in this file or in a
temporary directory, except the tests that read the real, published
sample pair (read-only). The page-output tests re-run the real script
and compare its output with the text pasted on the page, so the page
can never drift from the script.

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
SCRIPT = ROOT / "scripts" / "s2" / "condensation_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_stage2" / "condensation"
ORIGINAL_SAMPLE = SAMPLE_DIR / "original.md"
CONDENSED_SAMPLE = SAMPLE_DIR / "condensed.md"
PAGE = ROOT / "docs" / "stage-2" / "condensation.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("condensation_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cck = load_module()


def sentences(word: str, words_per_sentence: int, sentence_count: int) -> str:
    """sentence_count sentences, each holding words_per_sentence copies of word."""
    one = " ".join([word] * words_per_sentence) + "."
    return " ".join([one] * sentence_count)


def run_cli(*args: str) -> "subprocess.CompletedProcess[str]":
    """Run the script as a separate process, exactly as the page shows."""
    return subprocess.run(  # nosec B603
        [sys.executable, "-B", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def write(folder: Path, name: str, text: str) -> Path:
    """Write text to folder/name as UTF-8 and return the path."""
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


class WordListTests(unittest.TestCase):
    """word_list(): letters only; Markdown marks drop out on their own."""

    def test_counts_plain_words(self) -> None:
        self.assertEqual(cck.word_list("one two three"), ["one", "two", "three"])

    def test_keeps_an_internal_apostrophe(self) -> None:
        self.assertEqual(cck.word_list("it's fine"), ["it's", "fine"])

    def test_heading_and_code_marks_are_not_words(self) -> None:
        words = cck.word_list("# Title\n\nSee `git add` and **bold** text.")
        self.assertEqual(words, ["Title", "See", "git", "add", "and", "bold", "text"])

    def test_empty_text_has_no_words(self) -> None:
        self.assertEqual(cck.word_list(""), [])


class SentenceCountTests(unittest.TestCase):
    """sentence_count(): terminator runs, and the empty-text edge case."""

    def test_counts_sentence_terminators(self) -> None:
        self.assertEqual(cck.sentence_count("One. Two! Three?"), 3)

    def test_text_with_no_terminator_is_one_sentence(self) -> None:
        self.assertEqual(cck.sentence_count("one two three"), 1)

    def test_empty_text_is_zero_sentences(self) -> None:
        self.assertEqual(cck.sentence_count(""), 0)
        self.assertEqual(cck.sentence_count("   "), 0)

    def test_repeated_punctuation_counts_once(self) -> None:
        self.assertEqual(cck.sentence_count("Really?!"), 1)


class SyllableCountTests(unittest.TestCase):
    """syllable_count(): the vowel-group rule and the silent-e adjustment."""

    def test_single_vowel_group_is_one_syllable(self) -> None:
        self.assertEqual(cck.syllable_count("cat"), 1)

    def test_two_vowel_groups_is_two_syllables(self) -> None:
        self.assertEqual(cck.syllable_count("under"), 2)

    def test_silent_final_e_is_not_counted(self) -> None:
        self.assertEqual(cck.syllable_count("bike"), 1)

    def test_le_ending_keeps_its_syllable(self) -> None:
        self.assertEqual(cck.syllable_count("table"), 2)

    def test_never_below_one(self) -> None:
        self.assertEqual(cck.syllable_count("grr"), 1)


class ScoreTextTests(unittest.TestCase):
    """score_text(): counts and the two formulas, and the empty-text guard."""

    def test_known_counts_and_scores(self) -> None:
        scores = cck.score_text(sentences("cat", 5, 1))
        self.assertEqual(scores.words, 5)
        self.assertEqual(scores.sentences, 1)
        self.assertEqual(scores.syllables, 5)
        self.assertAlmostEqual(scores.grade, 0.39 * 5 + 11.8 * 1 - 15.59, places=6)
        self.assertAlmostEqual(scores.ease, 206.835 - 1.015 * 5 - 84.6 * 1, places=6)

    def test_empty_text_scores_are_zero(self) -> None:
        scores = cck.score_text("")
        self.assertEqual((scores.words, scores.sentences), (0, 0))
        self.assertEqual((scores.grade, scores.ease), (0.0, 0.0))


class BuildReportTests(unittest.TestCase):
    """build_report(): each of the three checks, hard in turn, the others pass."""

    def test_identical_pair_fails_only_the_ratio(self) -> None:
        text = sentences("cat", 5, 1)
        lines, hard = cck.build_report(text, text, 0.75, 0.85, 5.0, 1.0)
        self.assertEqual(hard, 1)
        self.assertIn(": hard", lines[0])
        self.assertIn(": pass", lines[1])
        self.assertIn(": pass", lines[2])

    def test_lower_syllables_per_word_fails_only_reading_ease(self) -> None:
        original = sentences("cat", 5, 4)
        condensed = sentences("cat", 5, 2) + " " + "cat cat cat cat under."
        lines, hard = cck.build_report(original, condensed, 0.75, 0.85, 5.0, 1.0)
        self.assertEqual(hard, 1)
        self.assertIn(": pass", lines[0])
        self.assertIn(": hard", lines[1])
        self.assertIn(": pass", lines[2])

    def test_longer_sentences_fails_only_grade_level(self) -> None:
        original = sentences("cat", 5, 8)
        condensed = sentences("cat", 8, 4)
        lines, hard = cck.build_report(original, condensed, 0.75, 0.85, 5.0, 1.0)
        self.assertEqual(hard, 1)
        self.assertIn(": pass", lines[0])
        self.assertIn(": pass", lines[1])
        self.assertIn(": hard", lines[2])

    def test_a_rise_in_reading_ease_always_passes(self) -> None:
        original = sentences("cat", 5, 4)
        condensed = sentences("cat", 5, 4)
        lines, hard = cck.build_report(original, condensed, 0.0, 2.0, 0.0, 0.0)
        self.assertEqual(hard, 0)
        self.assertIn(": pass", lines[1])

    def test_original_with_no_words_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cck.build_report("   ", "cat.", 0.75, 0.85, 5.0, 1.0)

    def test_exact_print_format(self) -> None:
        text = sentences("cat", 5, 1)
        lines, _ = cck.build_report(text, text, 0.75, 0.85, 5.0, 1.0)
        self.assertEqual(lines[0], "word-ratio 1.00, band 0.75-0.85: hard")
        self.assertEqual(lines[1], "reading-ease +0.00, limit -5: pass")
        self.assertEqual(lines[2], "grade-level +0.00, limit +1: pass")


class ReadCappedTests(unittest.TestCase):
    """read_capped(): decoding, the byte cap, and symlink refusal."""

    def test_reads_utf8_replacing_bad_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.md"
            path.write_bytes(b"good \xff\xfe text")
            text = cck.read_capped(str(path))
            self.assertIn(chr(0xFFFD), text)

    def test_caps_at_max_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "big.md"
            path.write_bytes(b"x" * (cck.MAX_BYTES + 10))
            with self.assertRaises(ValueError):
                cck.read_capped(str(path))

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.md"
            target.write_text("hello there", encoding="utf-8")
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks are not available on this file system")
            with self.assertRaises(OSError):
                cck.read_capped(str(link))


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ORIGINAL", result.stdout)
        self.assertIn("--grade-rise", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_clean_sample_exits_zero(self) -> None:
        result = run_cli(str(ORIGINAL_SAMPLE), str(CONDENSED_SAMPLE))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("checks=3 hard=0", result.stdout)

    def test_hard_ratio_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.md", sentences("cat", 5, 4))
            condensed = write(folder, "cond.md", sentences("cat", 5, 4))
            result = run_cli(str(original), str(condensed))
            self.assertEqual(result.returncode, 1)
            self.assertIn("checks=3 hard=1", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original = write(Path(tmp), "orig.md", "one two three.")
            missing = Path(tmp) / "missing.md"
            result = run_cli(str(original), str(missing))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("condensation_check.py: error:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_missing_arguments_is_a_usage_error(self) -> None:
        result = run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr.lower())

    def test_empty_original_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original = write(Path(tmp), "orig.md", "   ")
            condensed = write(Path(tmp), "cond.md", "one two three.")
            result = run_cli(str(original), str(condensed))
            self.assertEqual(result.returncode, 2)
            self.assertIn("no words", result.stderr)

    def test_flags_change_the_band(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.md", sentences("cat", 5, 4))
            condensed = write(folder, "cond.md", sentences("cat", 5, 4))
            narrow = run_cli(str(original), str(condensed))
            self.assertEqual(narrow.returncode, 1)
            wide = run_cli(
                str(original), str(condensed), "--word-low", "0.5", "--word-high", "1.5"
            )
            self.assertEqual(wide.returncode, 0)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.md", sentences("cat", 5, 4))
            condensed = write(folder, "cond.md", sentences("cat", 5, 3))
            before = sorted(p.name for p in folder.iterdir())
            run_cli(str(original), str(condensed))
            after = sorted(p.name for p in folder.iterdir())
            self.assertEqual(before, after)


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
        self.assertEqual(fields["ID"], "X-S2-02")
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


class SampleDataTests(unittest.TestCase):
    """The committed sample pair: ASCII, and a real, clean, all-pass run."""

    def test_sample_pair_is_ascii(self) -> None:
        for path in (ORIGINAL_SAMPLE, CONDENSED_SAMPLE):
            self.assertTrue(path.read_text(encoding="utf-8").isascii(), path)

    def test_sample_pair_is_all_pass_by_default(self) -> None:
        lines, hard = cck.build_report(
            ORIGINAL_SAMPLE.read_text(encoding="utf-8"),
            CONDENSED_SAMPLE.read_text(encoding="utf-8"),
            cck.DEFAULT_WORD_LOW,
            cck.DEFAULT_WORD_HIGH,
            cck.DEFAULT_RE_DROP,
            cck.DEFAULT_GRADE_RISE,
        )
        self.assertEqual(hard, 0, lines)

    def test_sample_pair_is_about_a_fifth_shorter(self) -> None:
        original_words = cck.word_list(ORIGINAL_SAMPLE.read_text(encoding="utf-8"))
        condensed_words = cck.word_list(CONDENSED_SAMPLE.read_text(encoding="utf-8"))
        ratio = len(condensed_words) / len(original_words)
        self.assertAlmostEqual(ratio, 0.80, delta=0.03)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-2/condensation.md: every pasted output line is real.

    The page shows two runs: the committed sample pair (all pass), and
    a break-on-purpose copy condensed much further than the band. This
    test rebuilds both, the second in a temporary directory, and never
    writes to the repository root.
    """

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected the clean run and the break-on-purpose run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_clean_run_lines_appear_in_a_real_run(self) -> None:
        result = run_cli(str(ORIGINAL_SAMPLE), str(CONDENSED_SAMPLE))
        clean_fence = self.fences[0]
        for line in [ln for ln in clean_fence.splitlines() if ln.strip()]:
            self.assertIn(line, result.stdout, clean_fence)

    def test_break_on_purpose_lines_appear_in_a_real_run(self) -> None:
        # The page's break-on-purpose step is "head -n 9 condensed.md",
        # keeping only the heading and the first paragraph; this test
        # applies the same edit to a temporary copy, never the
        # repository root.
        condensed_lines = CONDENSED_SAMPLE.read_text(encoding="utf-8").splitlines(
            keepends=True
        )
        broken_text = "".join(condensed_lines[:9])
        with tempfile.TemporaryDirectory() as tmp:
            broken = write(Path(tmp), "condensed.broken.md", broken_text)
            result = run_cli(str(ORIGINAL_SAMPLE), str(broken))
        broken_fence = self.fences[1]
        for line in [ln for ln in broken_fence.splitlines() if ln.strip()]:
            self.assertIn(line, result.stdout, broken_fence)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
