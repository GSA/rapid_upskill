"""Regression tests for two behaviors found while following the docs as a novice.

License: CC0-1.0 (public domain dedication,
https://creativecommons.org/publicdomain/zero/1.0/).

1. On Python older than 3.10 every tool must stop with a one-line message and
   exit code 2, never with a traceback. The tests fake an old version by
   patching ``sys.version_info`` in a child process.
2. When a prompt or script cannot be turned into a page, check.py must report
   rule R11 at the file that is wrong, not at scripts/site/sync.py.

Standard library only. Fixtures live in a temporary directory.
"""

# The tests run this repository's own scripts in child processes.
import subprocess  # nosec B404
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[2]
OLD_PYTHON = (
    "import collections, runpy, sys\n"
    "V = collections.namedtuple('V', 'major minor micro releaselevel serial')\n"
    "sys.version_info = V(3, 9, 6, 'final', 0)\n"
    "runpy.run_path(sys.argv[1], run_name='__main__')\n"
)
NEEDS_NEWER = "Python 3.10 or newer"

CONFIG = 'source_repo_url: "https://example.com/r"\nsource_branch: "main"\n'
HOME = """---
title: "Home"
nav_order: 1
status: "draft"
last_reviewed: "2026-09-19"
---

# Home

A short page that exists only so the fixture repository has a home page.
"""
BAD_PROMPT = """---
id: "P-S1-01"
title: "Bad prompt"
stage: "S1"
purpose: "A prompt with a capability that is not in the vocabulary."
placeholders: []
capabilities: ["gpu"]
---
````text
Say hello.
````
"""


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command with the current interpreter and capture its output."""
    # The arguments are fixed paths inside this repository, never user input.
    return subprocess.run(  # nosec B603
        [sys.executable, "-B", *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


class PythonVersionGuardTests(unittest.TestCase):
    """Old Python gives a clean message and exit code 2."""

    def check_guard(self, script: str) -> None:
        result = run(["-c", OLD_PYTHON, str(REPO / script)])
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(NEEDS_NEWER, result.stderr)
        self.assertIn("3.9", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_check_tool(self) -> None:
        self.check_guard("scripts/site/check.py")

    def test_sync_tool(self) -> None:
        self.check_guard("scripts/site/sync.py")

    def test_run_all(self) -> None:
        self.check_guard("scripts/tests/run_all.py")

    def test_llm_adapter(self) -> None:
        self.check_guard("scripts/common/llm_adapter.py")

    def test_blueprint_check(self) -> None:
        self.check_guard("scripts/s1/blueprint_check.py")

    def test_dedupe_candidates(self) -> None:
        self.check_guard("scripts/s1/dedupe_candidates.py")

    def test_run_queue(self) -> None:
        self.check_guard("scripts/s1/run_queue.py")

    def test_check_conversion(self) -> None:
        self.check_guard("scripts/s1/check_conversion.py")

    def test_scan_injection(self) -> None:
        self.check_guard("scripts/s1/scan_injection.py")

    def test_concept_lint(self) -> None:
        self.check_guard("scripts/s1/concept_lint.py")

    def test_quote_check(self) -> None:
        self.check_guard("scripts/s1/quote_check.py")

    def test_ki_dedupe(self) -> None:
        self.check_guard("scripts/s1/ki_dedupe.py")

    def test_check_concept_graph(self) -> None:
        self.check_guard("scripts/s1/check_concept_graph.py")

    def test_gap_check(self) -> None:
        self.check_guard("scripts/s1/gap_check.py")

    def test_chapter_structure_check(self) -> None:
        self.check_guard("scripts/s2/chapter_structure_check.py")

    def test_condensation_check(self) -> None:
        self.check_guard("scripts/s2/condensation_check.py")

    def test_readability_report(self) -> None:
        self.check_guard("scripts/s2/readability_report.py")

    def test_prerequisite_check(self) -> None:
        self.check_guard("scripts/s2/prerequisite_check.py")

    def test_claim_source_check(self) -> None:
        self.check_guard("scripts/s3/claim_source_check.py")

    def test_review_record_check(self) -> None:
        self.check_guard("scripts/s3/review_record_check.py")

    def test_citation_fidelity_check(self) -> None:
        self.check_guard("scripts/s3/citation_fidelity_check.py")

    def test_source_tier_check(self) -> None:
        self.check_guard("scripts/s3/source_tier_check.py")

    def test_concept_item_check(self) -> None:
        self.check_guard("scripts/s5/concept_item_check.py")

    def test_stem_plan_check(self) -> None:
        self.check_guard("scripts/s5/stem_plan_check.py")

    def test_format_rules_check(self) -> None:
        self.check_guard("scripts/s5/format_rules_check.py")

    def test_bank_composition_check(self) -> None:
        self.check_guard("scripts/s5/bank_composition_check.py")

    def test_answer_key_check(self) -> None:
        self.check_guard("scripts/s5/answer_key_check.py")

    def test_delivery_coverage_check(self) -> None:
        self.check_guard("scripts/s5/delivery_coverage_check.py")

    def test_current_python_is_not_blocked(self) -> None:
        result = run([str(REPO / "scripts/site/sync.py"), "--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(NEEDS_NEWER, result.stderr)


class GenerationErrorLocationTests(unittest.TestCase):
    """An input that cannot become a page is reported where it lives."""

    def test_r11_names_the_bad_prompt_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "_config.yml").write_text(CONFIG, encoding="utf-8")
            (root / "docs" / "index.md").write_text(HOME, encoding="utf-8")
            prompt_dir = root / "prompts" / "s1"
            prompt_dir.mkdir(parents=True)
            (prompt_dir / "bad.md").write_text(BAD_PROMPT, encoding="utf-8")

            result = run([str(REPO / "scripts/site/check.py"), "--root", str(root)])

        self.assertEqual(result.returncode, 1, result.stderr)
        lines = [ln for ln in result.stdout.splitlines() if " R11 " in ln]
        self.assertTrue(lines, result.stdout)
        self.assertTrue(all(ln.startswith("prompts/s1/bad.md:") for ln in lines), lines)
        self.assertTrue(all("cannot generate pages:" in ln for ln in lines), lines)
        self.assertFalse(any("scripts/site/sync.py" in ln for ln in lines), lines)


if __name__ == "__main__":
    unittest.main()
