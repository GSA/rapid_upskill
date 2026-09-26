"""Unit tests for scripts/s3/claim_source_check.py and
docs/stage-3/layer-1-automated-detection.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, plus the real, already-published running
example's `claims/claims.json` and `sources/` folder (both read-only).
The page-output tests re-run the real script and compare its output
with the text pasted on the page, so the page can never drift from the
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
SCRIPT = ROOT / "scripts" / "s3" / "claim_source_check.py"
CLAIMS = (
    ROOT / "scripts" / "sample_data" / "git_basics_stage3" / "claims" / "claims.json"
)
SOURCES_DIR = ROOT / "scripts" / "sample_data" / "git_basics" / "sources"
PAGE = ROOT / "docs" / "stage-3" / "layer-1-automated-detection.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("claim_source_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


csc = load_module()


def base_claims() -> list[dict[str, Any]]:
    """Two clean claims, both citing sources present in base_sources()."""
    return [
        {"claim_id": "C1", "text": "a claim", "source_id": "SRC-001"},
        {"claim_id": "C2", "text": "another claim", "source_id": "SRC-002"},
    ]


def write_json(tmp: Path, name: str, data: Any) -> Path:
    """Write `data` as JSON to tmp/name and return its path."""
    path = tmp / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_sources(tmp: Path, names: list[str]) -> Path:
    """Create tmp/sources with one empty file per name and return its path."""
    sources = tmp / "sources"
    sources.mkdir()
    for name in names:
        (sources / name).write_text("stub", encoding="utf-8")
    return sources


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


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_claims_file(self) -> None:
        data = csc.load_json(CLAIMS)
        self.assertEqual(len(data), 4)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(CLAIMS)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                csc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * csc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                csc.load_json(big)


class LoadClaimsTests(unittest.TestCase):
    """load_claims: the structural checks that raise ValueError."""

    def test_accepts_a_clean_list(self) -> None:
        claims = csc.load_claims(base_claims())
        self.assertEqual(
            claims,
            [
                csc.Claim("C1", "a claim", "SRC-001"),
                csc.Claim("C2", "another claim", "SRC-002"),
            ],
        )

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            csc.load_claims({"not": "a list"})

    def test_rejects_a_non_object_entry(self) -> None:
        with self.assertRaises(ValueError):
            csc.load_claims(["not an object"])

    def test_rejects_a_missing_claim_id(self) -> None:
        data = base_claims()
        del data[0]["claim_id"]
        with self.assertRaises(ValueError):
            csc.load_claims(data)

    def test_rejects_a_missing_text(self) -> None:
        data = base_claims()
        del data[0]["text"]
        with self.assertRaises(ValueError):
            csc.load_claims(data)

    def test_rejects_a_missing_source_id(self) -> None:
        data = base_claims()
        del data[0]["source_id"]
        with self.assertRaises(ValueError):
            csc.load_claims(data)


class AdmittedSourceIdsTests(unittest.TestCase):
    """admitted_source_ids: which filenames count, symlinks, non-directory."""

    def test_matches_src_md_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = write_sources(
                Path(tmp), ["SRC-001.md", "SRC-002.md", "notes.txt", "SRC-003.txt"]
            )
            self.assertEqual(csc.admitted_source_ids(sources), {"SRC-001", "SRC-002"})

    def test_empty_directory_yields_empty_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = Path(tmp) / "sources"
            sources.mkdir()
            self.assertEqual(csc.admitted_source_ids(sources), set())

    def test_rejects_a_non_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            not_a_dir = Path(tmp) / "file.md"
            not_a_dir.write_text("stub", encoding="utf-8")
            with self.assertRaises(ValueError):
                csc.admitted_source_ids(not_a_dir)

    def test_skips_a_symlinked_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            real = Path(tmp) / "real"
            real.mkdir()
            (real / "SRC-001.md").write_text("stub", encoding="utf-8")
            sources = Path(tmp) / "sources"
            sources.mkdir()
            try:
                (sources / "SRC-002.md").symlink_to(real / "SRC-001.md")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            self.assertEqual(csc.admitted_source_ids(sources), set())

    def test_refuses_a_symlinked_sources_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            real = write_sources(Path(tmp), ["SRC-001.md"])
            link = Path(tmp) / "link"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                csc.admitted_source_ids(link)


class CheckClaimsTests(unittest.TestCase):
    """check_claims: pass and gap lines, on small fixtures."""

    def test_pass_when_source_is_admitted(self) -> None:
        claims = csc.load_claims(base_claims())
        lines = csc.check_claims(claims, {"SRC-001", "SRC-002"})
        self.assertEqual(
            lines,
            [
                'pass: claim "C1" cites "SRC-001", admitted',
                'pass: claim "C2" cites "SRC-002", admitted',
            ],
        )

    def test_gap_when_source_is_not_admitted(self) -> None:
        claims = csc.load_claims(
            [{"claim_id": "C4", "text": "a claim", "source_id": "SRC-009"}]
        )
        lines = csc.check_claims(claims, {"SRC-001"})
        self.assertEqual(
            lines,
            ['gap: claim "C4" cites "SRC-009", no such source is admitted'],
        )

    def test_real_sample_has_three_pass_and_one_gap(self) -> None:
        claims = csc.load_claims(json.loads(CLAIMS.read_text(encoding="utf-8")))
        admitted = csc.admitted_source_ids(SOURCES_DIR)
        lines = csc.check_claims(claims, admitted)
        self.assertEqual(
            lines,
            [
                'pass: claim "C1" cites "SRC-001", admitted',
                'pass: claim "C2" cites "SRC-002", admitted',
                'pass: claim "C3" cites "SRC-006", admitted',
                'gap: claim "C4" cites "SRC-009", no such source is admitted',
            ],
        )


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any gap, 2 for a usage or input error."""

    def test_exit_zero_on_clean_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = write_json(root, "claims.json", base_claims())
            sources = write_sources(root, ["SRC-001.md", "SRC-002.md"])
            self.assertEqual(csc.main([str(claims), str(sources)]), 0)

    def test_exit_one_on_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = write_json(
                root,
                "claims.json",
                [{"claim_id": "C1", "text": "a claim", "source_id": "SRC-009"}],
            )
            sources = write_sources(root, ["SRC-001.md"])
            self.assertEqual(csc.main([str(claims), str(sources)]), 1)

    def test_exit_two_on_missing_claims_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = write_sources(root, ["SRC-001.md"])
            self.assertEqual(csc.main([str(root / "nope.json"), str(sources)]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.json"
            bad.write_text("not json", encoding="utf-8")
            sources = write_sources(root, ["SRC-001.md"])
            self.assertEqual(csc.main([str(bad), str(sources)]), 2)

    def test_exit_two_on_bad_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = write_json(root, "claims.json", {"not": "a list"})
            sources = write_sources(root, ["SRC-001.md"])
            self.assertEqual(csc.main([str(claims), str(sources)]), 2)

    def test_exit_two_on_zero_admitted_sources(self) -> None:
        """The loud-failure requirement: an empty sources folder is exit 2."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = write_json(root, "claims.json", base_claims())
            empty_sources = root / "empty-sources"
            empty_sources.mkdir()
            self.assertEqual(csc.main([str(claims), str(empty_sources)]), 2)

    def test_zero_admitted_sources_does_not_report_gaps(self) -> None:
        """A stale-glob-style empty folder must not print a gap per claim."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = write_json(root, "claims.json", base_claims())
            empty_sources = root / "empty-sources"
            empty_sources.mkdir()
            result = run_cli(str(claims), str(empty_sources))
            self.assertNotIn("gap:", result.stdout)
            self.assertEqual(result.stdout, "")


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CLAIMS.json", result.stdout)
        self.assertIn("SOURCES_DIR", result.stdout)

    def test_real_fixtures_from_the_repository_root(self) -> None:
        claims_rel = CLAIMS.relative_to(ROOT).as_posix()
        sources_rel = SOURCES_DIR.relative_to(ROOT).as_posix()
        result = run_cli(claims_rel, sources_rel, cwd=ROOT)
        self.assertEqual(result.returncode, 1)
        self.assertIn('pass: claim "C1" cites "SRC-001", admitted', result.stdout)
        self.assertIn(
            'gap: claim "C4" cites "SRC-009", no such source is admitted',
            result.stdout,
        )
        self.assertIn("claims=4 gaps=1", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_loud_failure_on_an_empty_sources_folder(self) -> None:
        claims_rel = CLAIMS.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            empty_sources = Path(tmp) / "empty-sources"
            empty_sources.mkdir()
            result = run_cli(claims_rel, str(empty_sources), cwd=ROOT)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(
            result.stderr.strip(),
            "claim_source_check.py: error: no admitted sources found in " "SOURCES_DIR",
        )
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"), str(SOURCES_DIR))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("claim_source_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(
                CLAIMS.relative_to(ROOT).as_posix(),
                SOURCES_DIR.relative_to(ROOT).as_posix(),
                cwd=Path(tmp),
            )
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
        self.assertEqual(fields["ID"], "X-S3-01")
        self.assertEqual(fields["Stage"], "S3")
        self.assertEqual(fields["Dependencies"], "stdlib")
        self.assertEqual(fields["Writes files"], "no")
        self.assertEqual(fields["License"], "CC0-1.0")
        self.assertTrue(fields["Usage"].startswith("python3 "))

    def test_only_standard_library_imports(self) -> None:
        tree = ast.parse(self.source)
        names: set[str] = set()
        for tree_node in ast.walk(tree):
            if isinstance(tree_node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in tree_node.names)
            elif (
                isinstance(tree_node, ast.ImportFrom)
                and tree_node.module
                and not tree_node.level
            ):
                names.add(tree_node.module.split(".")[0])
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
    """docs/stage-3/layer-1-automated-detection.md: every pasted line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_two_output_fences(self) -> None:
        self.assertEqual(len(self.fences), 2)

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_first_fence_matches_the_real_clean_run(self) -> None:
        result = run_cli(
            CLAIMS.relative_to(ROOT).as_posix(),
            SOURCES_DIR.relative_to(ROOT).as_posix(),
            cwd=ROOT,
        )
        lines = [line for line in self.fences[0].splitlines() if line.strip()]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn(line, result.stdout, f"pasted line not found: {line!r}")

    def test_second_fence_matches_the_real_loud_failure(self) -> None:
        """The empty-folder demonstration, built with tempfile, never at the
        repository root."""
        claims_rel = CLAIMS.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            empty_sources = Path(tmp) / "empty-sources"
            empty_sources.mkdir()
            result = run_cli(claims_rel, str(empty_sources), cwd=ROOT)
        lines = [line for line in self.fences[1].splitlines() if line.strip()]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn(line, result.stderr, f"pasted line not found: {line!r}")


if __name__ == "__main__":
    unittest.main()
