"""Unit tests for scripts/op/citation_key_check.py and
docs/operating-practices/provenance-and-verification.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample files (read-only). The page-output tests re-run the real script
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
SCRIPT = ROOT / "scripts" / "op" / "citation_key_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_batch8" / "citations"
SAMPLE_TEXT = SAMPLE_DIR / "TEXT.md"
SAMPLE_REFERENCES = SAMPLE_DIR / "REFERENCES.json"
PAGE = ROOT / "docs" / "operating-practices" / "provenance-and-verification.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("citation_key_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ckc = load_module()


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


def write(tmp: Path, name: str, content: str) -> Path:
    """Write content to tmp/name and return the path."""
    path = tmp / name
    path.write_text(content, encoding="utf-8")
    return path


class FindUsedKeysTests(unittest.TestCase):
    """find_used_keys: bracket detection, dedup and first-seen order."""

    def test_finds_a_single_key(self) -> None:
        self.assertEqual(ckc.find_used_keys("see [alpha] for details"), ["alpha"])

    def test_dedupes_a_repeated_key_keeping_first_seen_order(self) -> None:
        text = "[beta] and again [alpha] and again [beta]"
        self.assertEqual(ckc.find_used_keys(text), ["beta", "alpha"])

    def test_no_brackets_finds_nothing(self) -> None:
        self.assertEqual(ckc.find_used_keys("no citations here"), [])

    def test_ignores_a_bracketed_phrase_with_a_space(self) -> None:
        # An ordinary Markdown link's visible text, not a citation key.
        text = "see [the Git manual](https://example.invalid/git)"
        self.assertEqual(ckc.find_used_keys(text), [])

    def test_matches_hyphens_underscores_and_periods(self) -> None:
        text = "[atomic-checkpoint] [snake_case] [v1.2]"
        self.assertEqual(
            ckc.find_used_keys(text), ["atomic-checkpoint", "snake_case", "v1.2"]
        )

    def test_key_must_start_with_a_letter_or_digit(self) -> None:
        self.assertEqual(ckc.find_used_keys("[-bad]"), [])

    def test_empty_brackets_find_nothing(self) -> None:
        self.assertEqual(ckc.find_used_keys("[]"), [])


class CheckCitationsTests(unittest.TestCase):
    """check_citations: every error, warning and clean path."""

    def test_clean_when_every_key_matches_both_ways(self) -> None:
        errors, warnings, used = ckc.check_citations(
            "[alpha] and [beta]",
            {"alpha": {"title": "A"}, "beta": {"title": "B"}},
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(used, 2)

    def test_undefined_key_is_an_error(self) -> None:
        errors, _, used = ckc.check_citations("[missing]", {})
        self.assertEqual(used, 1)
        self.assertTrue(
            any("undefined" in e and "missing" in e for e in errors), errors
        )

    def test_uncited_key_is_a_warning(self) -> None:
        _, warnings, _ = ckc.check_citations("no citations", {"unused": {}})
        self.assertTrue(
            any("uncited" in w and "unused" in w for w in warnings), warnings
        )

    def test_no_citations_and_no_references_is_clean(self) -> None:
        errors, warnings, used = ckc.check_citations("nothing to see", {})
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(used, 0)

    def test_each_undefined_key_reported_once_however_often_repeated(self) -> None:
        errors, _, used = ckc.check_citations("[gap] [gap] [gap]", {})
        self.assertEqual(used, 1)
        self.assertEqual(len(errors), 1)

    def test_a_key_can_be_both_defined_and_used_with_no_finding(self) -> None:
        errors, warnings, _ = ckc.check_citations("[alpha]", {"alpha": {"title": "A"}})
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_the_worked_illustration_produces_exactly_one_of_each(self) -> None:
        # The renamed-key scenario the page's own worked illustration uses.
        text = (
            "checkpoint [atomic-checkpoint] backoff [backoff-jitter] "
            "bucket [token-bucket] shutdown [drain-on-shutdown]"
        )
        references = {
            "atomic-checkpoint": {"title": "A"},
            "backoff-jitter": {"title": "B"},
            "token-bucket": {"title": "C"},
            "graceful-shutdown": {"title": "D"},
        }
        errors, warnings, used = ckc.check_citations(text, references)
        self.assertEqual(used, 4)
        self.assertEqual(len(errors), 1)
        self.assertIn("drain-on-shutdown", errors[0])
        self.assertEqual(len(warnings), 1)
        self.assertIn("graceful-shutdown", warnings[0])


class LoadReferencesTests(unittest.TestCase):
    """load_references: shape validation, the real sample, and refusals."""

    def test_reads_the_real_sample(self) -> None:
        data = ckc.load_references(SAMPLE_REFERENCES)
        self.assertIsInstance(data, dict)
        self.assertIn("atomic-checkpoint", data)

    def test_rejects_a_non_object_top_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "refs.json", "[1, 2, 3]")
            with self.assertRaises(ValueError):
                ckc.load_references(path)

    def test_rejects_a_non_object_reference_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "refs.json", '{"alpha": "not an object"}')
            with self.assertRaises(ValueError):
                ckc.load_references(path)

    def test_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "refs.json", "not json")
            with self.assertRaises(Exception):
                ckc.load_references(path)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE_REFERENCES)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                ckc.load_references(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("{" + '"a": 1,' * ckc.MAX_BYTES + "}", encoding="utf-8")
            with self.assertRaises(ValueError):
                ckc.load_references(big)


class LoadTextTests(unittest.TestCase):
    """load_text: reads the real sample and refuses a symlink."""

    def test_reads_the_real_sample(self) -> None:
        text = ckc.load_text(SAMPLE_TEXT)
        self.assertIn("atomic-checkpoint", text)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.md"
            try:
                link.symlink_to(SAMPLE_TEXT)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                ckc.load_text(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.md"
            big.write_text("a" * (ckc.MAX_BYTES + 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                ckc.load_text(big)

    def test_replaces_undecodable_bytes_instead_of_raising(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.md"
            path.write_bytes(b"[alpha] \xff\xfe end")
            text = ckc.load_text(path)
            self.assertIn("alpha", text)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input error."""

    def test_exit_zero_on_clean_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = write(tmp_path, "text.md", "[alpha]")
            refs_path = write(tmp_path, "refs.json", '{"alpha": {"title": "A"}}')
            self.assertEqual(ckc.main([str(text_path), str(refs_path)]), 0)

    def test_exit_one_on_undefined_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = write(tmp_path, "text.md", "[missing]")
            refs_path = write(tmp_path, "refs.json", "{}")
            self.assertEqual(ckc.main([str(text_path), str(refs_path)]), 1)

    def test_exit_zero_with_only_an_uncited_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = write(tmp_path, "text.md", "no citations")
            refs_path = write(tmp_path, "refs.json", '{"unused": {"title": "U"}}')
            self.assertEqual(ckc.main([str(text_path), str(refs_path)]), 0)

    def test_exit_two_on_missing_text_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            refs_path = write(tmp_path, "refs.json", "{}")
            missing = tmp_path / "nope.md"
            self.assertEqual(ckc.main([str(missing), str(refs_path)]), 2)

    def test_exit_two_on_missing_references_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = write(tmp_path, "text.md", "[alpha]")
            missing = tmp_path / "nope.json"
            self.assertEqual(ckc.main([str(text_path), str(missing)]), 2)

    def test_exit_two_on_malformed_references_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = write(tmp_path, "text.md", "[alpha]")
            refs_path = write(tmp_path, "refs.json", "not json")
            self.assertEqual(ckc.main([str(text_path), str(refs_path)]), 2)

    def test_exit_two_on_bad_references_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = write(tmp_path, "text.md", "[alpha]")
            refs_path = write(tmp_path, "refs.json", "[1, 2]")
            self.assertEqual(ckc.main([str(text_path), str(refs_path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real samples."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TEXT", result.stdout)
        self.assertIn("REFERENCES", result.stdout)

    def test_real_sample_pair_flags_exactly_one_error_and_one_warning(self) -> None:
        rel_text = SAMPLE_TEXT.relative_to(ROOT).as_posix()
        rel_refs = SAMPLE_REFERENCES.relative_to(ROOT).as_posix()
        result = run_cli(rel_text, rel_refs, cwd=ROOT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(
            "error undefined: citation key 'drain-on-shutdown' is used in "
            "TEXT.md but not defined in REFERENCES.json",
            result.stdout,
        )
        self.assertIn(
            "warning uncited: reference key 'graceful-shutdown' is defined "
            "in REFERENCES.json but never used in TEXT.md",
            result.stdout,
        )
        self.assertIn("keys_used=4 errors=1 warnings=1", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.md"), str(SAMPLE_REFERENCES))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("citation_key_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE_TEXT), str(SAMPLE_REFERENCES), cwd=Path(tmp))
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
        self.assertEqual(fields["ID"], "X-OP-03")
        self.assertEqual(fields["Stage"], "OP")
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

    def test_has_a_version_guard(self) -> None:
        self.assertIn("sys.version_info < (3, 10)", self.source)


TEXT_FENCE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s(`\"])(/[^\s`\"]+|[A-Za-z]:\\\\[^\s`\"]*)")


class PageOutputTests(unittest.TestCase):
    """docs/operating-practices/provenance-and-verification.md: every
    pasted output line is real, and the sample fixtures shown on the
    page match the real checked-in files.
    """

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_at_least_one_text_fence(self) -> None:
        self.assertGreaterEqual(len(self.fences), 1)

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_finding_line_appears_in_a_real_run(self) -> None:
        result = run_cli(str(SAMPLE_TEXT), str(SAMPLE_REFERENCES))
        real_output = result.stdout
        finding_fence = next(fence for fence in self.fences if "keys_used=" in fence)
        lines = [line for line in finding_fence.splitlines() if line.strip()]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn(line, real_output)

    def test_worked_illustration_excerpt_matches_the_real_sample_text(self) -> None:
        excerpt_fence = next(
            fence for fence in self.fences if "atomic-checkpoint" in fence
        )
        sample = SAMPLE_TEXT.read_text(encoding="utf-8")
        for key in (
            "atomic-checkpoint",
            "backoff-jitter",
            "token-bucket",
            "drain-on-shutdown",
        ):
            self.assertIn(f"[{key}]", excerpt_fence)
            self.assertIn(f"[{key}]", sample)

    def test_sample_references_match_the_keys_named_on_the_page(self) -> None:
        references = ckc.load_references(SAMPLE_REFERENCES)
        self.assertEqual(
            set(references.keys()),
            {
                "atomic-checkpoint",
                "backoff-jitter",
                "token-bucket",
                "graceful-shutdown",
            },
        )


if __name__ == "__main__":
    unittest.main()
