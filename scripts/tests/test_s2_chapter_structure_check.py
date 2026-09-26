"""Unit tests for scripts/s2/chapter_structure_check.py and
docs/stage-2/structural-drafting.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
running-example chapter draft (read-only). The page-output tests re-run
the real script and compare its output with the text pasted on the
page, so the page can never drift from the script.

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
SCRIPT = ROOT / "scripts" / "s2" / "chapter_structure_check.py"
SAMPLE = (
    ROOT / "scripts" / "sample_data" / "git_basics_stage2" / "chapter-1" / "draft.md"
)
PAGE = ROOT / "docs" / "stage-2" / "structural-drafting.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("chapter_structure_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


csc = load_module()


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


CLEAN_CHAPTER = """---
chapter: 1
title: "Chapter 1: Snapshots, history and branches"
---

# Chapter 1: Snapshots, history and branches

## Overview

A short overview paragraph.

## Learning Objectives

By the end of this chapter, you will be able to:

- Explain that a commit is a snapshot.
- Build a commit on purpose.

## Content

### A commit is a snapshot

A short paragraph.

### Formative Check

A short question.

## Key Concepts

- **Commit**: a snapshot.

## Assessment

A short assessment paragraph.
"""


class StripFrontMatterTests(unittest.TestCase):
    """strip_front_matter: the delimited block is dropped, or left alone."""

    def test_drops_a_front_matter_block(self) -> None:
        text = '---\nchapter: 1\ntitle: "x"\n---\n# Body\n'
        self.assertEqual(csc.strip_front_matter(text), "# Body")

    def test_leaves_text_with_no_front_matter_alone(self) -> None:
        text = "# Body\nMore text.\n"
        self.assertEqual(csc.strip_front_matter(text), text)

    def test_leaves_text_with_an_unclosed_block_alone(self) -> None:
        text = "---\nchapter: 1\n# Body\n"
        self.assertEqual(csc.strip_front_matter(text), text)


class CollectH2SectionsTests(unittest.TestCase):
    """collect_h2_sections: order, section lines, and H3-versus-H2 telling."""

    def test_h3_heading_is_not_mistaken_for_h2(self) -> None:
        order, sections = csc.collect_h2_sections("## Content\n### Lab\nbody\n")
        self.assertEqual(order, ["Content"])
        self.assertEqual(sections["Content"], ["### Lab", "body"])

    def test_lines_before_the_first_h2_belong_to_no_section(self) -> None:
        order, sections = csc.collect_h2_sections("stray text\n## Overview\nbody\n")
        self.assertEqual(order, ["Overview"])
        self.assertEqual(sections, {"Overview": ["body"]})

    def test_two_headings_keep_their_own_lines(self) -> None:
        order, sections = csc.collect_h2_sections("## A\nx\n## B\ny\n")
        self.assertEqual(order, ["A", "B"])
        self.assertEqual(sections, {"A": ["x"], "B": ["y"]})


class CountObjectivesTests(unittest.TestCase):
    """count_objectives: bulleted and numbered list items, and non-items."""

    def test_counts_bulleted_items(self) -> None:
        self.assertEqual(csc.count_objectives(["- one", "- two", "* three"]), 3)

    def test_counts_numbered_items(self) -> None:
        self.assertEqual(csc.count_objectives(["1. one", "2) two"]), 2)

    def test_plain_text_is_not_counted(self) -> None:
        self.assertEqual(csc.count_objectives(["Just a sentence.", ""]), 0)

    def test_empty_section_is_zero(self) -> None:
        self.assertEqual(csc.count_objectives([]), 0)


class HasLabOrCheckTests(unittest.TestCase):
    """has_lab_or_check: only the two named H3 headings count."""

    def test_lab_heading_counts(self) -> None:
        self.assertTrue(csc.has_lab_or_check(["### Lab", "text"]))

    def test_formative_check_heading_counts(self) -> None:
        self.assertTrue(csc.has_lab_or_check(["### Formative Check", "text"]))

    def test_unrelated_h3_does_not_count(self) -> None:
        self.assertFalse(csc.has_lab_or_check(["### A commit is a snapshot"]))

    def test_empty_section_is_false(self) -> None:
        self.assertFalse(csc.has_lab_or_check([]))


class CheckChapterTests(unittest.TestCase):
    """check_chapter: each finding type, and the clean, no-finding case."""

    def test_clean_chapter_has_no_findings(self) -> None:
        findings, headings, objectives = csc.check_chapter(CLEAN_CHAPTER)
        self.assertEqual(findings, [])
        self.assertEqual(headings, 5)
        self.assertEqual(objectives, 2)

    def test_missing_heading(self) -> None:
        removed = "## Key Concepts\n\n- **Commit**: a snapshot.\n\n"
        text = CLEAN_CHAPTER.replace(removed, "")
        findings, headings, _ = csc.check_chapter(text)
        self.assertIn('missing-heading: "Key Concepts"', findings)
        self.assertEqual(headings, 4)

    def test_out_of_order(self) -> None:
        text = (
            "## Overview\nx\n"
            "## Learning Objectives\n- a\n"
            "## Content\n### Lab\ny\n"
            "## Assessment\nz\n"
            "## Key Concepts\nw\n"
        )
        findings, headings, _ = csc.check_chapter(text)
        self.assertIn(
            'out-of-order: "Assessment" appears before "Key Concepts"', findings
        )
        self.assertEqual(headings, 5)

    def test_no_objectives_when_list_is_empty(self) -> None:
        text = CLEAN_CHAPTER.replace(
            "- Explain that a commit is a snapshot.\n- Build a commit on purpose.\n",
            "No list here, just a sentence.\n",
        )
        findings, _, objectives = csc.check_chapter(text)
        self.assertIn("no-objectives", findings)
        self.assertEqual(objectives, 0)

    def test_no_objectives_when_section_is_missing(self) -> None:
        text = (
            "## Overview\nx\n"
            "## Content\n### Lab\ny\n"
            "## Key Concepts\nw\n"
            "## Assessment\nz\n"
        )
        findings, _, objectives = csc.check_chapter(text)
        self.assertIn("no-objectives", findings)
        self.assertEqual(objectives, 0)

    def test_no_lab_or_check_when_content_has_neither(self) -> None:
        text = CLEAN_CHAPTER.replace(
            "### Formative Check\n\nA short question.\n",
            "### Just a subsection\n\nSome text.\n",
        )
        findings, _, _ = csc.check_chapter(text)
        self.assertIn("no-lab-or-check", findings)

    def test_missing_content_section_also_reports_no_lab_or_check(self) -> None:
        text = (
            "## Overview\nx\n"
            "## Learning Objectives\n- a\n"
            "## Key Concepts\nw\n"
            "## Assessment\nz\n"
        )
        findings, _, _ = csc.check_chapter(text)
        self.assertIn("no-lab-or-check", findings)


class LoadChapterTests(unittest.TestCase):
    """load_chapter: file reading, the size cap and the symlink refusal."""

    def test_reads_a_real_file(self) -> None:
        text = csc.load_chapter(SAMPLE)
        self.assertIn("## Overview", text)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(SAMPLE)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                csc.load_chapter(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.md"
            big.write_text("x" * (csc.MAX_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                csc.load_chapter(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 clean, 1 with a finding, 2 for a usage or input error."""

    def write(self, tmp: Path, text: str, name: str = "draft.md") -> Path:
        path = Path(tmp) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_exit_zero_on_clean_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), CLEAN_CHAPTER)
            self.assertEqual(csc.main([str(path)]), 0)

    def test_exit_one_on_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken = CLEAN_CHAPTER.replace("## Assessment", "## Extra")
            path = self.write(Path(tmp), broken)
            self.assertEqual(csc.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(csc.main([str(Path(tmp) / "nope.md")]), 2)

    def test_exit_two_on_usage_error(self) -> None:
        with self.assertRaises(SystemExit) as cm:
            csc.main([])
        self.assertEqual(cm.exception.code, 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real sample."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CHAPTER", result.stdout)

    def test_clean_sample_run(self) -> None:
        rel = SAMPLE.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "headings=5 objectives=4 errors=0\n")

    def test_break_on_purpose_removes_a_required_heading(self) -> None:
        real_text = SAMPLE.read_text(encoding="utf-8")
        broken_text = "\n".join(
            line for line in real_text.splitlines() if line.strip() != "## Key Concepts"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draft.md"
            path.write_text(broken_text, encoding="utf-8")
            result = run_cli(str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn('missing-heading: "Key Concepts"', result.stdout)
        self.assertIn("headings=4 objectives=4 errors=1", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.md"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("chapter_structure_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-S2-01")
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

    def test_no_write_flag(self) -> None:
        self.assertNotIn("--write", self.source)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/stage-2/structural-drafting.md: every pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_output_fences(self) -> None:
        self.assertGreaterEqual(
            len(self.fences),
            2,
            "expected the clean run and the break-on-purpose run",
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean_run = run_cli(SAMPLE.relative_to(ROOT).as_posix(), cwd=ROOT)
        real_outputs = [clean_run.stdout]

        real_text = SAMPLE.read_text(encoding="utf-8")
        broken_text = "\n".join(
            line for line in real_text.splitlines() if line.strip() != "## Key Concepts"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draft.md"
            path.write_text(broken_text, encoding="utf-8")
            broken_run = run_cli(str(path))
        real_outputs.append(broken_run.stdout)

        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_page_does_not_state_the_old_smart_objective_count(self) -> None:
        self.assertNotIn("3 to 8", self.page_text)
        self.assertNotIn("3-8", self.page_text)


if __name__ == "__main__":
    unittest.main()
