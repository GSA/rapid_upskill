"""Unit tests for scripts/dl/slide_notes_check.py and
docs/delivery/slides-and-infographics.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, checked-in
sample slide-notes files (read-only). The page-output tests re-run the
real script and compare its output with the text pasted on the page, so
the page can never drift from the script.

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
SCRIPT = ROOT / "scripts" / "dl" / "slide_notes_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_batch8" / "slide_notes"
CLEAN_SAMPLE = SAMPLE_DIR / "Ch1_slideNotes_v20260115.md"
BROKEN_SAMPLE = SAMPLE_DIR / "Ch1_slideNotes_v20260115_broken.md"
PAGE = ROOT / "docs" / "delivery" / "slides-and-infographics.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("slide_notes_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


snc = load_module()


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


def clean_slide(bullets: int = 4, words: int = 180) -> str:
    """One well-formed "## Slide 1:" section, as a body-lines string."""
    bullet_lines = "\n".join(f"- bullet {i}" for i in range(1, bullets + 1))
    script = " ".join(["word"] * words)
    body = f"## Slide 1: Title\n{bullet_lines}\n\n"
    return body + f"**Presenter Script:**\n{script}\n"


CLEAN_NOTES = "# Chapter 1: Title\n\n" + clean_slide()


class HasChapterHeadingTests(unittest.TestCase):
    """has_chapter_heading: the first non-blank line only."""

    def test_true_for_a_single_hash_heading(self) -> None:
        self.assertTrue(snc.has_chapter_heading("# Chapter 1: Title\n\nbody\n"))

    def test_false_for_an_h2_heading_first(self) -> None:
        self.assertFalse(snc.has_chapter_heading("## Slide 1: Title\nbody\n"))

    def test_false_for_no_heading_at_all(self) -> None:
        self.assertFalse(snc.has_chapter_heading("just some text\n"))

    def test_blank_lines_before_the_heading_are_skipped(self) -> None:
        self.assertTrue(snc.has_chapter_heading("\n\n# Chapter 1: Title\n"))

    def test_empty_file_is_false(self) -> None:
        self.assertFalse(snc.has_chapter_heading(""))


class SplitSlidesTests(unittest.TestCase):
    """split_slides: heading recognition, ordering, and non-matching lines."""

    def test_one_slide(self) -> None:
        slides = snc.split_slides("## Slide 1: Title\nline one\nline two\n")
        self.assertEqual(slides, [("Slide 1", ["line one", "line two"])])

    def test_two_slides_keep_their_own_lines(self) -> None:
        slides = snc.split_slides("## Slide 1: A\nx\n## Slide 2: B\ny\n")
        self.assertEqual(slides, [("Slide 1", ["x"]), ("Slide 2", ["y"])])

    def test_lines_before_the_first_slide_belong_to_no_slide(self) -> None:
        slides = snc.split_slides("# Chapter 1: T\nstray\n## Slide 1: A\nx\n")
        self.assertEqual(slides, [("Slide 1", ["x"])])

    def test_a_non_matching_h2_heading_is_not_a_slide(self) -> None:
        slides = snc.split_slides("## Not A Slide\nx\n## Slide 1: A\ny\n")
        self.assertEqual(slides, [("Slide 1", ["y"])])

    def test_no_slides_gives_an_empty_list(self) -> None:
        self.assertEqual(snc.split_slides("# Chapter 1: T\nbody only\n"), [])


class FindPresenterMarkerTests(unittest.TestCase):
    """find_presenter_marker: exact match, a near-miss, and neither."""

    def test_exact_marker_is_found(self) -> None:
        index, attempted = snc.find_presenter_marker(
            ["- a", "**Presenter Script:**", "text"]
        )
        self.assertEqual(index, 1)
        self.assertFalse(attempted)

    def test_missing_colon_is_an_attempt_not_a_match(self) -> None:
        index, attempted = snc.find_presenter_marker(["**Presenter Script**", "text"])
        self.assertIsNone(index)
        self.assertTrue(attempted)

    def test_wrong_case_is_an_attempt(self) -> None:
        index, attempted = snc.find_presenter_marker(["**presenter script:**", "text"])
        self.assertIsNone(index)
        self.assertTrue(attempted)

    def test_no_marker_at_all(self) -> None:
        index, attempted = snc.find_presenter_marker(["- a", "- b"])
        self.assertIsNone(index)
        self.assertFalse(attempted)

    def test_unbolded_text_is_not_an_attempt(self) -> None:
        index, attempted = snc.find_presenter_marker(["Presenter Script:", "text"])
        self.assertIsNone(index)
        self.assertFalse(attempted)


class CountBulletsTests(unittest.TestCase):
    """count_bullets: flat "- " bullets only, no leading whitespace."""

    def test_counts_flat_bullets(self) -> None:
        self.assertEqual(snc.count_bullets(["- a", "- b", "- c"]), 3)

    def test_indented_dash_does_not_count(self) -> None:
        self.assertEqual(snc.count_bullets(["- a", "  - nested"]), 1)

    def test_a_dash_with_no_space_does_not_count(self) -> None:
        self.assertEqual(snc.count_bullets(["-nospace"]), 0)

    def test_prose_lines_do_not_count(self) -> None:
        self.assertEqual(snc.count_bullets(["Just a sentence."]), 0)


class PresenterScriptTextTests(unittest.TestCase):
    """presenter_script_text: joins lines, stops at a References: line."""

    def test_joins_and_strips(self) -> None:
        self.assertEqual(snc.presenter_script_text(["", "one", "two", ""]), "one\ntwo")

    def test_stops_before_references(self) -> None:
        text = snc.presenter_script_text(["script text", "References:", "- a"])
        self.assertEqual(text, "script text")

    def test_no_references_uses_every_line(self) -> None:
        self.assertEqual(snc.presenter_script_text(["a", "b"]), "a\nb")


class CheckReferencesTests(unittest.TestCase):
    """check_references: absence, a well-formed block, and each bad shape."""

    def test_no_references_line_is_no_finding(self) -> None:
        self.assertEqual(snc.check_references(["- a", "- b"], "Slide 1"), [])

    def test_well_formed_block_is_no_finding(self) -> None:
        lines = ["References:", "- one", "- two"]
        self.assertEqual(snc.check_references(lines, "Slide 1"), [])

    def test_prose_instead_of_a_bullet_is_malformed(self) -> None:
        findings = snc.check_references(["References:", "not a bullet"], "Slide 1")
        self.assertEqual(len(findings), 1)
        self.assertIn("references:", findings[0])

    def test_a_stray_non_bullet_line_inside_the_block_is_malformed(self) -> None:
        lines = ["References:", "- one", "stray line", "- two"]
        findings = snc.check_references(lines, "Slide 1")
        self.assertEqual(len(findings), 1)

    def test_nothing_after_the_line_is_malformed(self) -> None:
        findings = snc.check_references(["References:"], "Slide 1")
        self.assertEqual(len(findings), 1)

    def test_a_blank_line_immediately_after_is_malformed(self) -> None:
        findings = snc.check_references(["References:", "", "- one"], "Slide 1")
        self.assertEqual(len(findings), 1)


class CheckSlideTests(unittest.TestCase):
    """check_slide: each finding kind, and the clean, no-finding case."""

    def test_clean_slide_has_no_findings(self) -> None:
        _, lines = snc.split_slides(clean_slide())[0]
        self.assertEqual(snc.check_slide("Slide 1", lines), [])

    def test_too_few_bullets(self) -> None:
        _, lines = snc.split_slides(clean_slide(bullets=3))[0]
        findings = snc.check_slide("Slide 1", lines)
        self.assertIn("bullet-count: Slide 1 has 3 bullets, needs 4 to 7", findings)

    def test_too_many_bullets(self) -> None:
        _, lines = snc.split_slides(clean_slide(bullets=8))[0]
        findings = snc.check_slide("Slide 1", lines)
        self.assertIn("bullet-count: Slide 1 has 8 bullets, needs 4 to 7", findings)

    def test_presenter_script_missing(self) -> None:
        _, lines = snc.split_slides("## Slide 1: T\n- a\n- b\n- c\n- d\n")[0]
        findings = snc.check_slide("Slide 1", lines)
        expected = (
            "presenter-script-missing: Slide 1 has no '**Presenter Script:**' block"
        )
        self.assertIn(expected, findings)

    def test_presenter_script_malformed(self) -> None:
        text = "## Slide 1: T\n- a\n- b\n- c\n- d\n\n**Presenter Script**\nx\n"
        _, lines = snc.split_slides(text)[0]
        findings = snc.check_slide("Slide 1", lines)
        self.assertTrue(
            any(f.startswith("presenter-script-malformed:") for f in findings)
        )

    def test_presenter_script_too_short(self) -> None:
        _, lines = snc.split_slides(clean_slide(words=10))[0]
        findings = snc.check_slide("Slide 1", lines)
        self.assertIn(
            "presenter-script-words: Slide 1 presenter script has 10 words, "
            "needs 150 to 250",
            findings,
        )

    def test_presenter_script_too_long(self) -> None:
        _, lines = snc.split_slides(clean_slide(words=300))[0]
        findings = snc.check_slide("Slide 1", lines)
        self.assertIn(
            "presenter-script-words: Slide 1 presenter script has 300 words, "
            "needs 150 to 250",
            findings,
        )

    def test_malformed_references_is_reported_alongside_a_good_script(self) -> None:
        text = (
            "## Slide 1: T\n- a\n- b\n- c\n- d\n\n**Presenter Script:**\n"
            + " ".join(["word"] * 180)
            + "\n\nReferences:\nnot a bullet\n"
        )
        _, lines = snc.split_slides(text)[0]
        findings = snc.check_slide("Slide 1", lines)
        self.assertEqual(len(findings), 1)
        self.assertIn("references:", findings[0])


class CheckNotesTests(unittest.TestCase):
    """check_notes: the whole-file pass, chapter heading, and slide count."""

    def test_clean_notes_has_no_findings(self) -> None:
        findings, slide_count = snc.check_notes(CLEAN_NOTES)
        self.assertEqual(findings, [])
        self.assertEqual(slide_count, 1)

    def test_missing_chapter_heading(self) -> None:
        text = clean_slide()
        findings, slide_count = snc.check_notes(text)
        self.assertIn("chapter-heading: the chapter heading is missing", findings)
        self.assertEqual(slide_count, 1)

    def test_two_slides_are_both_counted_and_checked(self) -> None:
        text = "# Chapter 1: T\n\n" + clean_slide() + "\n" + clean_slide(bullets=2)
        findings, slide_count = snc.check_notes(text)
        self.assertEqual(slide_count, 2)
        self.assertTrue(any("bullet-count: Slide 1" in f for f in findings))


class LoadNotesTests(unittest.TestCase):
    """load_notes: reads a real file, refuses a symlink, caps the size."""

    def test_reads_a_real_file(self) -> None:
        text = snc.load_notes(CLEAN_SAMPLE)
        self.assertIn("# Chapter 1:", text)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(CLEAN_SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                snc.load_notes(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.md"
            big.write_text("x" * (snc.MAX_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                snc.load_notes(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 clean, 1 with a finding, 2 for a usage or input error."""

    def write(self, tmp: Path, text: str) -> Path:
        path = Path(tmp) / "notes.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_exit_zero_on_clean_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), CLEAN_NOTES)
            self.assertEqual(snc.main([str(path)]), 0)

    def test_exit_one_on_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken = "# Chapter 1: T\n\n" + clean_slide(bullets=2)
            path = self.write(Path(tmp), broken)
            self.assertEqual(snc.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(snc.main([str(Path(tmp) / "nope.md")]), 2)

    def test_exit_two_on_usage_error(self) -> None:
        with self.assertRaises(SystemExit) as cm:
            snc.main([])
        self.assertEqual(cm.exception.code, 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real samples."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("NOTES", result.stdout)

    def test_clean_sample_run(self) -> None:
        rel = CLEAN_SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "slides=2 errors=0\n")

    def test_broken_sample_run(self) -> None:
        rel = BROKEN_SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "bullet-count: Slide 1 has 3 bullets, needs 4 to 7", result.stdout
        )
        self.assertIn(
            "presenter-script-words: Slide 2 presenter script has 61 words, "
            "needs 150 to 250",
            result.stdout,
        )
        self.assertIn("slides=2 errors=2", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.md"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("slide_notes_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(CLEAN_SAMPLE.as_posix(), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-DL-01")
        self.assertEqual(fields["Stage"], "DL")
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


class SampleDataTests(unittest.TestCase):
    """The checked-in sample files are ASCII and differ only as intended."""

    def test_clean_sample_is_ascii_only(self) -> None:
        self.assertTrue(CLEAN_SAMPLE.read_text(encoding="utf-8").isascii())

    def test_broken_sample_is_ascii_only(self) -> None:
        self.assertTrue(BROKEN_SAMPLE.read_text(encoding="utf-8").isascii())

    def test_broken_sample_still_has_a_chapter_heading(self) -> None:
        text = BROKEN_SAMPLE.read_text(encoding="utf-8")
        self.assertTrue(snc.has_chapter_heading(text))
        findings, _ = snc.check_notes(text)
        self.assertNotIn("chapter-heading: the chapter heading is missing", findings)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/delivery/slides-and-infographics.md: every pasted line is real."""

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

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean_run = run_cli(CLEAN_SAMPLE.relative_to(ROOT).as_posix(), cwd=ROOT)
        broken_run = run_cli(BROKEN_SAMPLE.relative_to(ROOT).as_posix(), cwd=ROOT)
        real_outputs = [clean_run.stdout, broken_run.stdout]
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
