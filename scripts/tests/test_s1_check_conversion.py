"""Unit tests for scripts/s1/check_conversion.py.

Everything runs offline, on synthetic text held in this file or in
temporary files. Run all tests with: python3 -B scripts/tests/run_all.py
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

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "s1" / "check_conversion.py"
PAGE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "stage-1"
    / "screening-and-conversion.md"
)
SAMPLE_DIR = (
    Path(__file__).resolve().parent.parent
    / "sample_data"
    / "git_basics_stage1"
    / "conversion"
)
ORIGINAL_SAMPLE = SAMPLE_DIR / "SRC-004.original.txt"
CONVERTED_SAMPLE = SAMPLE_DIR / "SRC-004.converted.md"


def load_module() -> ModuleType:
    """Import the script from its file, relative to this test file."""
    spec = importlib.util.spec_from_file_location("check_conversion", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cc = load_module()


def write(folder: Path, name: str, text: str) -> Path:
    """Write text to folder/name as UTF-8 and return the path."""
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


class StripMarkdownTests(unittest.TestCase):
    """strip_markdown() and word_list() on small, hand-built text."""

    def test_removes_front_matter_once(self) -> None:
        text = '---\nid: "SRC-999"\ntitle: "x"\n---\nHello there world today\n'
        self.assertEqual(cc.strip_markdown(text).strip(), "Hello there world today")

    def test_removes_heading_and_inline_marks(self) -> None:
        text = "## A heading\n\nThis has `code`, **bold** and _italic_ text.\n"
        cleaned = cc.strip_markdown(text)
        self.assertNotIn("#", cleaned)
        self.assertNotIn("`", cleaned)
        self.assertIn("bold", cleaned)
        self.assertIn("italic", cleaned)

    def test_removes_list_markers_keeps_words(self) -> None:
        text = "- one two three\n1. four five six\n42) seven eight nine\n"
        words = cc.word_list(text)
        self.assertEqual(len(words), 9)
        self.assertNotIn("1.", words)
        self.assertNotIn("42)", words)

    def test_link_and_image_keep_visible_text_only(self) -> None:
        text = "See [the guide](https://example.org/g) and ![a diagram](x.png)."
        cleaned = cc.strip_markdown(text)
        self.assertIn("the guide", cleaned)
        self.assertIn("a diagram", cleaned)
        self.assertNotIn("example.org", cleaned)

    def test_drops_fence_marker_lines_keeps_fenced_words(self) -> None:
        text = "before\n```text\ninside words here\n```\nafter\n"
        words = cc.word_list(text)
        self.assertEqual(words, ["before", "inside", "words", "here", "after"])

    def test_no_front_matter_is_unchanged(self) -> None:
        text = "Just plain words, no marks at all.\n"
        self.assertEqual(cc.strip_markdown(text), text)


class CheckFunctionTests(unittest.TestCase):
    """Each named check, in isolation, with both a pass and a failing case."""

    def test_empty(self) -> None:
        self.assertEqual(cc.check_empty([]).status, "hard")
        self.assertEqual(cc.check_empty(["one"]).status, "pass")

    def test_ratio_pass_and_hard(self) -> None:
        original = ["w"] * 100
        self.assertEqual(
            cc.check_ratio(original, ["w"] * 100, 0.85, 1.15).status, "pass"
        )
        self.assertEqual(
            cc.check_ratio(original, ["w"] * 10, 0.85, 1.15).status, "hard"
        )
        self.assertEqual(cc.check_ratio([], ["w"], 0.85, 1.15).status, "hard")

    def test_garble_pass_and_hard(self) -> None:
        clean = "clean text with no garble in it at all, said plainly."
        self.assertEqual(cc.check_garble(clean).status, "pass")
        garbled = "\ufffd" * 5 + "x" * 95
        self.assertEqual(cc.check_garble(garbled).status, "hard")
        self.assertEqual(cc.check_garble("").status, "hard")

    def test_character_mix_pass_hard_and_skip(self) -> None:
        clean = "Ordinary prose made of ordinary ASCII words and sentences."
        self.assertEqual(cc.check_character_mix(clean, False).status, "pass")
        symbols = "#$%^&*()_+={}[]|:;<>,.?/~ " * 20
        self.assertEqual(cc.check_character_mix(symbols, False).status, "hard")
        self.assertIsNone(cc.check_character_mix(symbols, True))

    def test_repeats_pass_and_soft(self) -> None:
        clean = "one line here\nanother line there\n"
        self.assertEqual(cc.check_repeats(clean).status, "pass")
        line = "this line has four words\n"
        repeated = line * 3 + "a different closing line\n"
        result = cc.check_repeats(repeated)
        self.assertEqual(result.status, "soft")
        self.assertIn("this line has four words", result.detail)

    def test_repeats_ignores_short_lines(self) -> None:
        short = "hi\n" * 5
        self.assertEqual(cc.check_repeats(short).status, "pass")

    def test_expected_text_none_pass_and_soft(self) -> None:
        text = "the quick fox jumps"
        self.assertIsNone(cc.check_expected_text(text, []))
        self.assertEqual(cc.check_expected_text(text, ["quick fox"]).status, "pass")
        result = cc.check_expected_text(text, ["quick fox", "slow snail"])
        self.assertEqual(result.status, "soft")
        self.assertIn("slow snail", result.detail)

    def test_words_per_page_none_pass_and_soft(self) -> None:
        words = ["w"] * 500
        self.assertIsNone(cc.check_words_per_page(words, None))
        self.assertEqual(cc.check_words_per_page(words, 2).status, "pass")
        self.assertEqual(cc.check_words_per_page(words, 50).status, "soft")

    def test_words_per_page_rejects_non_positive(self) -> None:
        with self.assertRaises(ValueError):
            cc.check_words_per_page(["w"], 0)

    def test_excerpt_is_ascii_and_capped(self) -> None:
        text = "a" * 200 + "\u00e9"
        result = cc.excerpt(text)
        self.assertTrue(result.isascii())
        self.assertLessEqual(len(result), cc.EXCERPT_CHARS + 4)


class RunChecksTests(unittest.TestCase):
    """run_checks() end to end, including which lines are omitted."""

    def test_clean_pair_is_all_pass(self) -> None:
        original = "Four short plain sentences make up this whole original file."
        checks = cc.run_checks(original, original)
        self.assertTrue(all(c.status == "pass" for c in checks))
        self.assertEqual(
            [c.name for c in checks],
            ["empty", "ratio", "garble", "character-mix", "repeats"],
        )

    def test_pages_and_expect_are_omitted_when_not_given(self) -> None:
        checks = cc.run_checks("some words here", "some words here")
        names = [c.name for c in checks]
        self.assertNotIn("words-per-page", names)
        self.assertNotIn("expected-text", names)

    def test_pages_and_expect_appear_when_given(self) -> None:
        checks = cc.run_checks(
            "some words here", "some words here", pages=1, expect=["some"]
        )
        names = [c.name for c in checks]
        self.assertIn("words-per-page", names)
        self.assertIn("expected-text", names)

    def test_allow_non_latin_skips_character_mix(self) -> None:
        checks = cc.run_checks("w", "w", allow_non_latin=True)
        self.assertNotIn("character-mix", [c.name for c in checks])


class ReadCappedTests(unittest.TestCase):
    """read_capped(): decoding, the byte cap, and symlink refusal."""

    def test_reads_utf8_replacing_bad_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.txt"
            path.write_bytes(b"good \xff\xfe text")
            text = cc.read_capped(str(path))
            self.assertIn("\ufffd", text)

    def test_caps_at_max_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "big.txt"
            path.write_bytes(b"x" * (cc.MAX_BYTES + 10))
            text = cc.read_capped(str(path))
            self.assertEqual(len(text), cc.MAX_BYTES)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.txt"
            target.write_text("hello", encoding="utf-8")
            link = Path(tmp) / "link.txt"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks are not available on this file system")
            with self.assertRaises(ValueError):
                cc.read_capped(str(link))


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process."""

    def run_cli(self, *args: str) -> "subprocess.CompletedProcess[str]":
        return subprocess.run(  # nosec B603
            [sys.executable, "-B", str(SCRIPT_PATH), *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def test_help_exits_zero(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ORIGINAL", result.stdout)
        self.assertIn("--allow-non-latin", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_clean_pair_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.txt", "one two three four five six\n")
            converted = write(folder, "conv.md", "one two three four five six\n")
            result = self.run_cli(str(original), str(converted))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("pass ratio", result.stdout)

    def test_hard_failure_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.txt", "one two three four five six\n")
            converted = write(folder, "conv.md", "")
            result = self.run_cli(str(original), str(converted))
            self.assertEqual(result.returncode, 1)
            self.assertIn("hard empty", result.stdout)

    def test_missing_file_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.txt", "one two three\n")
            missing = folder / "missing.md"
            result = self.run_cli(str(original), str(missing))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn(str(missing), result.stderr)

    def test_missing_arguments_is_argparse_usage_error(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr.lower())

    def test_ratio_flags_change_the_band(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.txt", "one two three four five six\n")
            converted = write(folder, "conv.md", "one two three\n")
            narrow = self.run_cli(str(original), str(converted))
            self.assertEqual(narrow.returncode, 1)
            wide = self.run_cli(str(original), str(converted), "--ratio-low", "0.1")
            self.assertEqual(wide.returncode, 0)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = write(folder, "orig.txt", "one two three\n")
            converted = write(folder, "conv.md", "one two three\n")
            before = sorted(p.name for p in folder.iterdir())
            self.run_cli(str(original), str(converted), "--pages", "1")
            after = sorted(p.name for p in folder.iterdir())
            self.assertEqual(before, after)


KEY_LINE = re.compile(r"^([A-Za-z][A-Za-z ]*):[ \t]*(.*)$")
REQUIRED_KEYS = ("ID", "Purpose", "Usage", "Dependencies", "Writes files", "License")


class HeaderTests(unittest.TestCase):
    """The module docstring is a valid script header (as in test_llm_adapter.py)."""

    source = SCRIPT_PATH.read_text(encoding="utf-8")

    def parse_header(self) -> dict[str, str]:
        docstring = ast.get_docstring(ast.parse(self.source)) or ""
        fields: dict[str, str] = {}
        current = ""
        for line in docstring.splitlines():
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

    def test_required_fields_and_values(self) -> None:
        fields = self.parse_header()
        for key in REQUIRED_KEYS:
            self.assertTrue(fields.get(key), f"missing header field {key}")
        self.assertEqual(fields["ID"], "X-S1-04")
        self.assertEqual(fields["Stage"], "S1")
        self.assertEqual(fields["Dependencies"], "stdlib")
        self.assertEqual(fields["Writes files"], "no")
        self.assertEqual(fields["License"], "CC0-1.0")
        self.assertTrue(fields["Usage"].startswith("python3 "))

    def test_only_standard_library_imports(self) -> None:
        names: set[str] = set()
        for node in ast.walk(ast.parse(self.source)):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names.add(node.module.split(".")[0])
        self.assertTrue(names)
        self.assertEqual(names - set(sys.stdlib_module_names), set())

    def test_source_is_ascii(self) -> None:
        self.assertTrue(self.source.isascii())

    def test_disables_bytecode_writing(self) -> None:
        self.assertIn("sys.dont_write_bytecode = True", self.source)


class SampleDataTests(unittest.TestCase):
    """The committed sample pair, run for real."""

    def test_sample_pair_is_ascii(self) -> None:
        for path in (ORIGINAL_SAMPLE, CONVERTED_SAMPLE):
            self.assertTrue(path.read_text(encoding="utf-8").isascii(), path)

    def test_sample_pair_hard_fails_on_ratio_only(self) -> None:
        checks = cc.run_checks(
            ORIGINAL_SAMPLE.read_text(encoding="utf-8"),
            CONVERTED_SAMPLE.read_text(encoding="utf-8"),
        )
        hard = [c.name for c in checks if c.status == "hard"]
        self.assertEqual(hard, ["ratio"])


class PageOutputTests(unittest.TestCase):
    """Every real-output line pasted on the page reproduces for real.

    The page shows two runs: the sample pair as committed (ratio hard
    fails, showing the missing section), and a break-on-purpose copy with
    a run of symbol characters appended (the ratio then passes, but the
    character-mix check catches the corruption). This test rebuilds both
    and compares.
    """

    ABS_PATH_RE = re.compile(r"(?:^|[\s(`\"'])(?:/[^\s`\"')]+|[A-Za-z]:\\\S+)")
    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE_PATH.read_text(encoding="utf-8")
        cls.fences = re.findall(r"```text\n(.*?)```", cls.page_text, re.S)
        if len(cls.fences) < 2:
            raise AssertionError("expected at least two output fences on the page")

    def test_no_absolute_path_in_any_pasted_output(self) -> None:
        for fence in self.fences:
            match = self.ABS_PATH_RE.search(fence)
            self.assertIsNone(match, f"absolute path in pasted output: {fence!r}")

    def test_primary_run_lines_appear_in_a_fresh_run(self) -> None:
        checks = cc.run_checks(
            ORIGINAL_SAMPLE.read_text(encoding="utf-8"),
            CONVERTED_SAMPLE.read_text(encoding="utf-8"),
        )
        real_lines = {f"{c.status} {c.name} {c.detail}" for c in checks}
        fence = self.fences[0]
        for line in [ln for ln in fence.splitlines() if ln.strip()]:
            self.assertIn(line, real_lines, fence)

    def test_break_on_purpose_lines_appear_in_a_fresh_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken = write(
                Path(tmp),
                "SRC-004.broken.md",
                CONVERTED_SAMPLE.read_text(encoding="utf-8") + ("#$%^&*()_+ " * 190),
            )
            checks = cc.run_checks(
                ORIGINAL_SAMPLE.read_text(encoding="utf-8"),
                broken.read_text(encoding="utf-8"),
            )
        real_lines = {f"{c.status} {c.name} {c.detail}" for c in checks}
        fence = self.fences[1]
        for line in [ln for ln in fence.splitlines() if ln.strip()]:
            self.assertIn(line, real_lines, fence)

    def test_break_on_purpose_flips_the_failing_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken = write(
                Path(tmp),
                "SRC-004.broken.md",
                CONVERTED_SAMPLE.read_text(encoding="utf-8") + ("#$%^&*()_+ " * 190),
            )
            checks = cc.run_checks(
                ORIGINAL_SAMPLE.read_text(encoding="utf-8"),
                broken.read_text(encoding="utf-8"),
            )
        by_name = {c.name: c.status for c in checks}
        self.assertEqual(by_name["ratio"], "pass")
        self.assertEqual(by_name["character-mix"], "hard")


if __name__ == "__main__":
    unittest.main()
