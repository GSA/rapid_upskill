"""Unit tests for scripts/s3/review_record_check.py and
docs/stage-3/layer-2-expert-review.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, plus the real, published Stage 3 sample flags
file (read-only). The page-output test re-runs the real script and
compares its output with the text pasted on the page, so the page can
never drift from the script. The break-on-purpose edit is applied to a
temporary copy of the sample file, never to the repository's own file.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import ast
import copy
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
SCRIPT = ROOT / "scripts" / "s3" / "review_record_check.py"
FLAGS = ROOT / "scripts" / "sample_data" / "git_basics_stage3" / "review" / "flags.json"
PAGE = ROOT / "docs" / "stage-3" / "layer-2-expert-review.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("review_record_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rrc = load_module()


def base_flag(claim_id: str = "C1", status: str = "accurate") -> dict[str, Any]:
    """A minimal, otherwise-valid flag entry."""
    entry: dict[str, Any] = {
        "claim_id": claim_id,
        "status": status,
        "reason": "a stated reason",
    }
    if status in rrc.STATUSES_NEEDING_SUGGESTION:
        entry["suggestion"] = "a stated suggestion"
    return entry


def base_flags() -> list[dict[str, Any]]:
    """A small, clean list: one of each allowed status."""
    return [
        base_flag("C1", "accurate"),
        base_flag("C2", "needs-review"),
        base_flag("C3", "reject"),
        base_flag("C4", "unverifiable"),
    ]


def load_real_flags() -> list[dict[str, Any]]:
    """A deep copy of the real, published Stage 3 sample flags list."""
    return copy.deepcopy(json.loads(FLAGS.read_text(encoding="utf-8")))


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


def write_json(tmp: Path, name: str, data: Any) -> Path:
    """Write `data` as JSON to tmp/name and return its path."""
    path = tmp / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_sample(self) -> None:
        data = rrc.load_json(FLAGS)
        self.assertEqual(len(data), 4)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(FLAGS)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                rrc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * rrc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                rrc.load_json(big)


class LoadFlagsTests(unittest.TestCase):
    """load_flags: the structural checks that raise ValueError."""

    def test_accepts_a_clean_list(self) -> None:
        flags = rrc.load_flags(base_flags())
        self.assertEqual(len(flags), 4)

    def test_rejects_a_non_list(self) -> None:
        with self.assertRaises(ValueError):
            rrc.load_flags({"not": "a list"})

    def test_rejects_a_non_object_entry(self) -> None:
        with self.assertRaises(ValueError):
            rrc.load_flags(["not an object"])

    def test_rejects_a_missing_claim_id(self) -> None:
        data = base_flags()
        del data[0]["claim_id"]
        with self.assertRaises(ValueError):
            rrc.load_flags(data)

    def test_rejects_an_empty_claim_id(self) -> None:
        data = base_flags()
        data[0]["claim_id"] = ""
        with self.assertRaises(ValueError):
            rrc.load_flags(data)

    def test_accepts_an_empty_list(self) -> None:
        self.assertEqual(rrc.load_flags([]), [])


class CheckFlagsTests(unittest.TestCase):
    """check_flags: every finding kind, on small fixtures."""

    def test_clean_flags_have_no_findings(self) -> None:
        flags = rrc.load_flags(base_flags())
        self.assertEqual(rrc.check_flags(flags), [])

    def test_bad_status_is_flagged(self) -> None:
        data = [base_flag("C2", "accurate")]
        data[0]["status"] = "wrong"
        flags = rrc.load_flags(data)
        self.assertEqual(
            rrc.check_flags(flags),
            ['bad-status: claim "C2" has status "wrong", not in the allowed set'],
        )

    def test_missing_status_is_flagged_as_bad_status(self) -> None:
        data = [base_flag("C1", "accurate")]
        del data[0]["status"]
        flags = rrc.load_flags(data)
        self.assertEqual(
            rrc.check_flags(flags),
            ['bad-status: claim "C1" has status null, not in the allowed set'],
        )

    def test_missing_reason_is_flagged(self) -> None:
        data = [base_flag("C3", "accurate")]
        del data[0]["reason"]
        flags = rrc.load_flags(data)
        self.assertEqual(rrc.check_flags(flags), ['missing-reason: claim "C3"'])

    def test_empty_reason_is_flagged(self) -> None:
        data = [base_flag("C3", "accurate")]
        data[0]["reason"] = ""
        flags = rrc.load_flags(data)
        self.assertEqual(rrc.check_flags(flags), ['missing-reason: claim "C3"'])

    def test_missing_suggestion_is_flagged_when_status_needs_one(self) -> None:
        data = [base_flag("C1", "reject")]
        del data[0]["suggestion"]
        flags = rrc.load_flags(data)
        self.assertEqual(
            rrc.check_flags(flags),
            ['missing-suggestion: claim "C1" status "reject" needs one'],
        )

    def test_missing_suggestion_is_flagged_for_needs_review_too(self) -> None:
        data = [base_flag("C1", "needs-review")]
        del data[0]["suggestion"]
        flags = rrc.load_flags(data)
        self.assertEqual(
            rrc.check_flags(flags),
            ['missing-suggestion: claim "C1" status "needs-review" needs one'],
        )

    def test_missing_suggestion_is_not_required_for_accurate(self) -> None:
        flags = rrc.load_flags([base_flag("C1", "accurate")])
        self.assertEqual(rrc.check_flags(flags), [])

    def test_missing_suggestion_is_not_required_for_unverifiable(self) -> None:
        flags = rrc.load_flags([base_flag("C1", "unverifiable")])
        self.assertEqual(rrc.check_flags(flags), [])

    def test_multiple_findings_on_one_entry_are_all_reported(self) -> None:
        data = [{"claim_id": "C9", "status": "wrong"}]
        flags = rrc.load_flags(data)
        self.assertEqual(
            rrc.check_flags(flags),
            [
                'bad-status: claim "C9" has status "wrong", not in the allowed set',
                'missing-reason: claim "C9"',
            ],
        )

    def test_real_sample_is_clean(self) -> None:
        flags = rrc.load_flags(load_real_flags())
        self.assertEqual(rrc.check_flags(flags), [])

    def test_real_sample_with_suggestion_removed_shows_the_miss(self) -> None:
        data = load_real_flags()
        for entry in data:
            if entry["claim_id"] == "C3":
                del entry["suggestion"]
        flags = rrc.load_flags(data)
        self.assertEqual(
            rrc.check_flags(flags),
            ['missing-suggestion: claim "C3" status "reject" needs one'],
        )


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any finding, 2 for a usage or input error."""

    def test_exit_zero_on_clean_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "flags.json", base_flags())
            self.assertEqual(rrc.main([str(path)]), 0)

    def test_exit_one_on_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = [base_flag("C1", "accurate")]
            data[0]["status"] = "wrong"
            path = write_json(Path(tmp), "flags.json", data)
            self.assertEqual(rrc.main([str(path)]), 1)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rrc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("not json", encoding="utf-8")
            self.assertEqual(rrc.main([str(bad)]), 2)

    def test_exit_two_on_bad_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp), "flags.json", {"not": "a list"})
            self.assertEqual(rrc.main([str(path)]), 2)

    def test_exit_two_on_missing_claim_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = base_flags()
            del data[0]["claim_id"]
            path = write_json(Path(tmp), "flags.json", data)
            self.assertEqual(rrc.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, exactly as the page shows."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("FLAGS", result.stdout)

    def test_real_sample_from_the_repository_root(self) -> None:
        rel = FLAGS.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "claims=4 errors=0\n")
        self.assertEqual(result.stderr, "")

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("review_record_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        rel = FLAGS.relative_to(ROOT).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(rel, cwd=ROOT)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_break_on_purpose_copy_shows_the_miss(self) -> None:
        """Removing C3's suggestion on a temporary copy shows the finding.

        The edit is applied to a copy in a temporary directory; the
        repository's own sample file is never touched.
        """
        data = load_real_flags()
        for entry in data:
            if entry["claim_id"] == "C3":
                del entry["suggestion"]
        with tempfile.TemporaryDirectory() as tmp:
            broken = write_json(Path(tmp), "flags.json", data)
            result = run_cli(str(broken))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            'missing-suggestion: claim "C3" status "reject" needs one\n'
            "claims=4 errors=1\n",
        )
        # the repository's own sample file is unchanged
        self.assertEqual(
            json.loads(FLAGS.read_text(encoding="utf-8")), load_real_flags()
        )


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
        self.assertEqual(fields["ID"], "X-S3-02")
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
    """docs/stage-3/layer-2-expert-review.md: every pasted line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_an_output_fence(self) -> None:
        self.assertGreaterEqual(len(self.fences), 2)

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        """Every pasted output line appears either in the clean run or in
        the break-on-purpose run (the page shows both)."""
        clean = run_cli(FLAGS.relative_to(ROOT).as_posix(), cwd=ROOT)
        data = load_real_flags()
        for entry in data:
            if entry["claim_id"] == "C3":
                del entry["suggestion"]
        with tempfile.TemporaryDirectory() as tmp:
            broken = write_json(Path(tmp), "flags.json", data)
            broken_run = run_cli(str(broken))
        combined = clean.stdout + broken_run.stdout
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertIn(line, combined, f"pasted line not found: {line!r}")


if __name__ == "__main__":
    unittest.main()
