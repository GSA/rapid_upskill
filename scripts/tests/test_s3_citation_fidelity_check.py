"""Unit tests for scripts/s3/citation_fidelity_check.py and
docs/stage-3/layer-3-audit-trail.md.

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

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "s3" / "citation_fidelity_check.py"
SOURCES_DIR = ROOT / "scripts" / "sample_data" / "git_basics" / "sources"
CITATIONS = (
    ROOT
    / "scripts"
    / "sample_data"
    / "git_basics_stage3"
    / "citations"
    / "citations.json"
)
PAGE = ROOT / "docs" / "stage-3" / "layer-3-audit-trail.md"

PARAPHRASE_QUOTE = (
    "A file you have not changed points to the same saved content it "
    "had in the earlier commit."
)
FIXED_QUOTE = (
    "a file you did not touch refers to the same stored content as in "
    "the previous commit"
)


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("citation_fidelity_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cfc = load_module()


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


def fixed_citations_text() -> str:
    """The real citations.json with the planted paraphrase corrected."""
    data = json.loads(CITATIONS.read_text(encoding="utf-8"))
    found = False
    for entry in data:
        if entry["quote"] == PARAPHRASE_QUOTE:
            entry["quote"] = FIXED_QUOTE
            found = True
    if not found:
        raise AssertionError("planted paraphrase quote not found in the fixture")
    return json.dumps(data)


class LoadCitationsTests(unittest.TestCase):
    """load_citations(): shape checks on the parsed JSON."""

    def test_parses_valid_list(self) -> None:
        data = [{"claim_id": "C1", "source_id": "SRC-001", "quote": "hello"}]
        result = cfc.load_citations(data)
        self.assertEqual(result, [cfc.Citation("C1", "SRC-001", "hello")])

    def test_not_a_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            cfc.load_citations({"claim_id": "C1"})

    def test_entry_not_an_object_raises(self) -> None:
        with self.assertRaises(ValueError):
            cfc.load_citations(["not an object"])

    def test_missing_claim_id_raises(self) -> None:
        with self.assertRaises(ValueError):
            cfc.load_citations([{"source_id": "SRC-001", "quote": "x"}])

    def test_missing_source_id_raises(self) -> None:
        with self.assertRaises(ValueError):
            cfc.load_citations([{"claim_id": "C1", "quote": "x"}])

    def test_missing_quote_raises(self) -> None:
        with self.assertRaises(ValueError):
            cfc.load_citations([{"claim_id": "C1", "source_id": "SRC-001"}])

    def test_empty_quote_raises(self) -> None:
        with self.assertRaises(ValueError):
            cfc.load_citations(
                [{"claim_id": "C1", "source_id": "SRC-001", "quote": ""}]
            )


class FindSourceFilesTests(unittest.TestCase):
    """find_source_files(): the zero-files loud-failure rule (X-S3-01's rule)."""

    def test_maps_stem_to_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SRC-001.md"
            path.write_text("text", encoding="utf-8")
            result = cfc.find_source_files(Path(tmp))
            self.assertEqual(result, {"SRC-001": path})

    def test_zero_files_raises_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError) as ctx:
                cfc.find_source_files(Path(tmp))
            self.assertIn("no admitted sources found", str(ctx.exception))

    def test_non_directory_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not_a_dir.md"
            path.write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError):
                cfc.find_source_files(path)

    def test_ignores_non_matching_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SRC-001.md").write_text("x", encoding="utf-8")
            (Path(tmp) / "README.md").write_text("x", encoding="utf-8")
            result = cfc.find_source_files(Path(tmp))
            self.assertEqual(list(result), ["SRC-001"])


class ReadSourceTextTests(unittest.TestCase):
    """read_source_text(): the symlink refusal and the byte cap."""

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.md"
            target.write_text("x", encoding="utf-8")
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                cfc.read_source_text(link)

    def test_oversized_file_is_truncated_not_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.md"
            big.write_text("a" * (cfc.MAX_BYTES + 100), encoding="utf-8")
            text = cfc.read_source_text(big)
            self.assertEqual(len(text), cfc.MAX_BYTES)


class CheckCitationsTests(unittest.TestCase):
    """check_citations(): pass, quote-not-found, and unknown-source lines."""

    def test_exact_substring_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SRC-001.md"
            path.write_text("Hello small world.", encoding="utf-8")
            lines = cfc.check_citations(
                [cfc.Citation("C1", "SRC-001", "small world")], {"SRC-001": path}
            )
            self.assertEqual(lines, ["pass quote-C1: found in SRC-001.md"])

    def test_missing_substring_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SRC-001.md"
            path.write_text("Hello small world.", encoding="utf-8")
            lines = cfc.check_citations(
                [cfc.Citation("C2", "SRC-001", "large world")], {"SRC-001": path}
            )
            self.assertEqual(lines, ["fail quote-C2: not found verbatim in SRC-001.md"])

    def test_unknown_source_id_fails(self) -> None:
        lines = cfc.check_citations([cfc.Citation("C3", "SRC-404", "anything")], {})
        self.assertEqual(
            lines,
            ['fail quote-C3: source "SRC-404" not present in SOURCES_DIR'],
        )

    def test_case_sensitive_no_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SRC-001.md"
            path.write_text("Hello World.", encoding="utf-8")
            lines = cfc.check_citations(
                [cfc.Citation("C4", "SRC-001", "hello world")], {"SRC-001": path}
            )
            self.assertEqual(lines, ["fail quote-C4: not found verbatim in SRC-001.md"])


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 all pass, 1 any fail, 2 for a usage or input error."""

    def write_source(self, tmp: Path) -> Path:
        sources = tmp / "sources"
        sources.mkdir()
        (sources / "SRC-001.md").write_text("Hello small world.", encoding="utf-8")
        return sources

    def write_citations(self, tmp: Path, quote: str) -> Path:
        path = tmp / "citations.json"
        path.write_text(
            json.dumps([{"claim_id": "C1", "source_id": "SRC-001", "quote": quote}]),
            encoding="utf-8",
        )
        return path

    def test_exit_zero_when_every_quote_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = self.write_source(Path(tmp))
            citations = self.write_citations(Path(tmp), "small world")
            self.assertEqual(cfc.main([str(citations), str(sources)]), 0)

    def test_exit_one_when_a_quote_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = self.write_source(Path(tmp))
            citations = self.write_citations(Path(tmp), "large world")
            self.assertEqual(cfc.main([str(citations), str(sources)]), 1)

    def test_exit_two_on_missing_citations_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = self.write_source(Path(tmp))
            self.assertEqual(cfc.main([str(Path(tmp) / "nope.json"), str(sources)]), 2)

    def test_exit_two_on_zero_admitted_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            citations = self.write_citations(Path(tmp), "small world")
            self.assertEqual(cfc.main([str(citations), str(empty)]), 2)

    def test_exit_two_on_malformed_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = self.write_source(Path(tmp))
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps([{"claim_id": "C1"}]), encoding="utf-8")
            self.assertEqual(cfc.main([str(bad), str(sources)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CITATIONS", result.stdout)
        self.assertIn("SOURCES_DIR", result.stdout)

    def test_sample_run_has_one_planted_failure(self) -> None:
        rel_citations = CITATIONS.relative_to(ROOT).as_posix()
        rel_sources = SOURCES_DIR.relative_to(ROOT).as_posix()
        result = run_cli(rel_citations, rel_sources, cwd=ROOT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(result.stdout.count("pass quote-"), 4)
        self.assertEqual(result.stdout.count("fail quote-"), 1)
        self.assertIn("quotes=5 pass=4 fail=1", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(CITATIONS), str(SOURCES_DIR), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class FixOnPurposeTests(unittest.TestCase):
    """The page's fix-on-purpose edit: correcting the planted paraphrase."""

    def test_fixing_the_paraphrase_makes_every_quote_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "citations.json"
            copy_path.write_text(fixed_citations_text(), encoding="utf-8")
            result = run_cli(str(copy_path), str(SOURCES_DIR))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("pass quote-"), 5)
        self.assertIn("quotes=5 pass=5 fail=0", result.stdout)


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
        self.assertEqual(fields["ID"], "X-S3-03")
        self.assertEqual(fields["Stage"], "S3")
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
    """docs/stage-3/layer-3-audit-trail.md: every pasted line is real."""

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
        rel_citations = CITATIONS.relative_to(ROOT).as_posix()
        rel_sources = SOURCES_DIR.relative_to(ROOT).as_posix()
        failing = run_cli(rel_citations, rel_sources, cwd=ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / "citations.json"
            copy_path.write_text(fixed_citations_text(), encoding="utf-8")
            fixed = run_cli(str(copy_path), str(SOURCES_DIR))
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
