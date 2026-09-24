"""Unit tests for scripts/s1/quote_check.py and
docs/stage-1/distillate-and-quote-bank.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory. The page-output tests re-run the real script and
compare its output with the text pasted on the page, so the page can never
drift from the script.

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
SCRIPT = ROOT / "scripts" / "s1" / "quote_check.py"
SOURCE = ROOT / "scripts" / "sample_data" / "git_basics" / "sources" / "SRC-002.md"
DISTILLATE = ROOT / "scripts" / "sample_data" / "git_basics_stage1" / "extraction" / (
    "SRC-002.distillate.md"
)
PAGE = ROOT / "docs" / "stage-1" / "distillate-and-quote-bank.md"
PARAPHRASE_NEEDLE = (
    "Git merges the two branches' changes together and writes one new "
    "commit that has two parent commits."
)
PARAPHRASE_FIX = (
    "Git combines the two sets of changes and records a new commit with "
    "two parents."
)


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("quote_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qc = load_module()


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


class NormalizeTests(unittest.TestCase):
    """normalize(): typography-only, both sides, case-sensitive by default."""

    def test_curly_quotes_become_straight(self) -> None:
        self.assertEqual(qc.normalize("‘a’ and “b”", False), "'a' and \"b\"")

    def test_dash_variants_become_a_hyphen(self) -> None:
        self.assertEqual(qc.normalize("a–b—c", False), "a-b-c")

    def test_wrapped_hyphen_is_joined_to_the_next_word(self) -> None:
        self.assertEqual(qc.normalize("exam-\nple word", False), "example word")

    def test_em_dash_at_a_line_end_is_not_joined(self) -> None:
        self.assertEqual(qc.normalize("end—\nnext", False), "end- next")

    def test_whitespace_runs_collapse_to_one_space(self) -> None:
        self.assertEqual(qc.normalize("a   b\t\tc", False), "a b c")

    def test_case_sensitive_by_default(self) -> None:
        self.assertEqual(qc.normalize("ABC", False), "ABC")

    def test_ignore_case_casefolds(self) -> None:
        self.assertEqual(qc.normalize("ABC", True), "abc")

    def test_no_unicode_compatibility_folding(self) -> None:
        # U+FB01 LATIN SMALL LIGATURE FI is left as is, not expanded to "fi".
        self.assertEqual(qc.normalize("ﬁle", False), "ﬁle")


class StripSourceExtrasTests(unittest.TestCase):
    """strip_source_extras(): front matter, backticks, emphasis marks."""

    def test_front_matter_is_removed(self) -> None:
        text = '---\nid: "X"\n---\n\nbody text\n'
        self.assertEqual(strip_and_trim(text), "body text")

    def test_backticks_are_removed(self) -> None:
        self.assertEqual(qc.strip_source_extras("run `git status` now"), "run git status now")

    def test_emphasis_marks_are_removed(self) -> None:
        self.assertEqual(qc.strip_source_extras("**bold** and _italic_"), "bold and italic")


def strip_and_trim(text: str) -> str:
    """strip_source_extras(), with the front matter's own blank line trimmed."""
    return qc.strip_source_extras(text).strip()


class FindSectionTests(unittest.TestCase):
    """find_section(): heading match, custom --heading, and the not-found error."""

    def test_finds_the_default_heading(self) -> None:
        text = "## Metadata\n\nx\n\n## Quote bank\n\n- \"a\" | loc\n"
        self.assertEqual(qc.find_section(text, "Quote bank"), '\n- "a" | loc')

    def test_stops_at_the_next_heading(self) -> None:
        text = "## Quote bank\n\nline one\n\n## Leads\n\nline two\n"
        self.assertEqual(qc.find_section(text, "Quote bank"), "\nline one\n")

    def test_runs_to_end_of_file_when_last(self) -> None:
        text = "## Quote bank\n\nonly line\n"
        self.assertEqual(qc.find_section(text, "Quote bank"), "\nonly line")

    def test_custom_heading_text(self) -> None:
        text = "## My Bank\n\ncontent\n"
        self.assertEqual(qc.find_section(text, "My Bank"), "\ncontent")

    def test_missing_heading_raises(self) -> None:
        with self.assertRaises(ValueError):
            qc.find_section("## Something else\n\nx\n", "Quote bank")


class ParseQuoteLinesTests(unittest.TestCase):
    """parse_quote_lines(): only '- "..." | locator' lines are kept."""

    def test_parses_quote_and_locator(self) -> None:
        section = '- "hello world" | page 3\nnot a quote line\n'
        self.assertEqual(qc.parse_quote_lines(section), [("hello world", "page 3")])

    def test_ignores_blank_and_non_matching_lines(self) -> None:
        section = "\nsome prose\n- \"a b c\" | loc 1\n"
        self.assertEqual(qc.parse_quote_lines(section), [("a b c", "loc 1")])

    def test_no_lines_gives_empty_list(self) -> None:
        self.assertEqual(qc.parse_quote_lines("no quotes here\n"), [])


class CheckQuoteTests(unittest.TestCase):
    """check_quote(): length, fragment split, and the presence check."""

    SOURCE_NORM = qc.normalize("Hello world, this is a small test source.", False)

    def test_exact_match_passes(self) -> None:
        passed, detail = qc.check_quote("Hello world, this is", self.SOURCE_NORM, False)
        self.assertTrue(passed, detail)

    def test_not_present_fails(self) -> None:
        passed, detail = qc.check_quote("Goodbye world, this is", self.SOURCE_NORM, False)
        self.assertFalse(passed)
        self.assertIn("not found in the source", detail)

    def test_over_40_words_fails(self) -> None:
        long_quote = " ".join(["word"] * 41)
        passed, detail = qc.check_quote(long_quote, self.SOURCE_NORM, False)
        self.assertFalse(passed)
        self.assertIn("over the 40-word limit", detail)

    def test_40_words_is_allowed(self) -> None:
        source_norm = qc.normalize(" ".join(["word"] * 40), False)
        passed, _ = qc.check_quote(" ".join(["word"] * 40), source_norm, False)
        self.assertTrue(passed)

    def test_bracketed_fragment_is_removed_before_checking(self) -> None:
        passed, detail = qc.check_quote(
            "Hello world, this is [note] a small test", self.SOURCE_NORM, False
        )
        self.assertTrue(passed, detail)

    def test_fragment_under_three_words_fails(self) -> None:
        passed, detail = qc.check_quote(
            "Hello world, [note] this", self.SOURCE_NORM, False
        )
        self.assertFalse(passed)
        self.assertIn("under 3", detail)

    def test_only_bracketed_text_fails(self) -> None:
        passed, detail = qc.check_quote("[only a note]", self.SOURCE_NORM, False)
        self.assertFalse(passed)
        self.assertIn("no text remains", detail)

    def test_case_sensitive_by_default_fails(self) -> None:
        passed, _ = qc.check_quote("HELLO WORLD, this is", self.SOURCE_NORM, False)
        self.assertFalse(passed)

    def test_ignore_case_passes(self) -> None:
        source_norm = qc.normalize("Hello world, this is a small test source.", True)
        passed, _ = qc.check_quote("HELLO WORLD, this is", source_norm, True)
        self.assertTrue(passed)


class ReadCappedTests(unittest.TestCase):
    """read_capped(): the symlink refusal and the byte cap."""

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.md"
            target.write_text("x", encoding="utf-8")
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(ValueError):
                qc.read_capped(str(link))

    def test_oversized_file_is_truncated_not_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.md"
            big.write_text("a" * (qc.MAX_BYTES + 100), encoding="utf-8")
            text = qc.read_capped(str(big))
            self.assertEqual(len(text), qc.MAX_BYTES)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 all pass, 1 any fail, 2 for a usage or input error."""

    def write_pair(self, tmp: Path, quote_line: str) -> tuple[Path, Path]:
        source = tmp / "source.md"
        source.write_text("Hello world, this is a small test source.\n", encoding="utf-8")
        distillate = tmp / "distillate.md"
        distillate.write_text(f"## Quote bank\n\n{quote_line}\n", encoding="utf-8")
        return source, distillate

    def test_exit_zero_when_every_quote_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, distillate = self.write_pair(
                Path(tmp), '- "Hello world, this is" | loc'
            )
            self.assertEqual(qc.main([str(source), str(distillate)]), 0)

    def test_exit_one_when_a_quote_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, distillate = self.write_pair(
                Path(tmp), '- "Goodbye world" | loc'
            )
            self.assertEqual(qc.main([str(source), str(distillate)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                qc.main([str(Path(tmp) / "nope.md"), str(Path(tmp) / "nope2.md")]), 2
            )

    def test_exit_two_on_missing_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.md"
            source.write_text("hello\n", encoding="utf-8")
            distillate = Path(tmp) / "distillate.md"
            distillate.write_text("## Something else\n\nx\n", encoding="utf-8")
            self.assertEqual(qc.main([str(source), str(distillate)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SOURCE", result.stdout)
        self.assertIn("--ignore-case", result.stdout)

    def test_sample_run_has_one_planted_failure(self) -> None:
        rel_source = SOURCE.relative_to(ROOT).as_posix()
        rel_distillate = DISTILLATE.relative_to(ROOT).as_posix()
        result = run_cli(rel_source, rel_distillate, cwd=ROOT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(result.stdout.count("pass quote-"), 5)
        self.assertEqual(result.stdout.count("fail quote-"), 1)
        self.assertIn("quotes=6 pass=5 fail=1", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SOURCE), str(DISTILLATE), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class BreakOnPurposeTests(unittest.TestCase):
    """The page's fix-on-purpose edit: correcting the planted paraphrase."""

    def test_fixing_the_paraphrase_makes_every_quote_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "distillate.md"
            original = DISTILLATE.read_text(encoding="utf-8")
            self.assertEqual(original.count(PARAPHRASE_NEEDLE), 1)
            copy_path.write_text(
                original.replace(PARAPHRASE_NEEDLE, PARAPHRASE_FIX, 1), encoding="utf-8"
            )
            result = run_cli(str(SOURCE), str(copy_path))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("pass quote-"), 6)
        self.assertIn("quotes=6 pass=6 fail=0", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S1-07")
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
    """docs/stage-1/distillate-and-quote-bank.md: every pasted line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected a failing and a fixed run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        failing = run_cli(str(SOURCE), str(DISTILLATE))
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "distillate.md"
            original = DISTILLATE.read_text(encoding="utf-8")
            copy_path.write_text(
                original.replace(PARAPHRASE_NEEDLE, PARAPHRASE_FIX, 1), encoding="utf-8"
            )
            fixed = run_cli(str(SOURCE), str(copy_path))
        real_outputs = [failing.stdout, fixed.stdout]
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
