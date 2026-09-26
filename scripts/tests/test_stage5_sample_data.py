"""Checks for scripts/sample_data/git_basics_stage5/, the Stage 5 sample data.

Purpose: verify the folder's file set, hygiene (ASCII, no local paths, no
    secrets, no stray e-mail addresses, no percent signs, no base64 or data:
    fixtures), that its README lists every file, and that all six Stage 5
    scripts still behave as their pages document against the real running
    example, including the one real cross-file dependency on
    scripts/sample_data/git_basics/blueprint.json.
Usage: python3 -B scripts/tests/test_stage5_sample_data.py
Dependencies: stdlib
Writes files: no
License: CC0-1.0
"""

import re
import subprocess  # nosec B404
import sys
import unittest
from pathlib import Path
from typing import List
from urllib.parse import urlsplit

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "sample_data" / "git_basics_stage5"

EXPECTED_FILES = {
    "concept_items/items.json",
    "stem_plan/plan.json",
    "stems/stems.json",
    "bank/composition.json",
    "answer_key/key.json",
    "delivery/manifest.json",
}
ALLOWED_HOSTS = {"example.com", "example.org", "example.net"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
# Built from parts so this file does not itself contain the strings it forbids.
LOCAL_PATH_MARKERS = (
    "/" + "Users" + "/",
    "C:" + "\\" + "Users" + "\\",
    "/" + "home" + "/",
    "file:" + "///",
    "/" + "private" + "/",
    "/" + "var" + "/" + "folders",
)
SECRET_PATTERNS = (
    re.compile(r"hf_[A-Za-z0-9]{10,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"oauth", re.I),
)
# This batch's own extra rule (plan section 2): the real target certification
# and the two real delivery products this stage's private sources use must
# never appear in this folder, under any spelling.
FORBIDDEN_TERMS = (
    "google form",
    "google forms",
    "jira",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def all_files() -> List[Path]:
    return sorted(
        p
        for p in DATA.rglob("*")
        if p.is_file() and not p.name.startswith(".") and "__pycache__" not in p.parts
    )


def run(args: List[str]) -> "subprocess.CompletedProcess[str]":
    """Run a script with the current interpreter and capture its output."""
    # The arguments are fixed paths inside this repository, never user input.
    return subprocess.run(  # nosec B603
        [sys.executable, "-B", *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
        timeout=60,
    )


class FileSetTests(unittest.TestCase):
    def test_exactly_the_planned_files_exist(self) -> None:
        found = {
            p.relative_to(DATA).as_posix() for p in all_files() if p.name != "README.md"
        }
        self.assertEqual(found, EXPECTED_FILES)
        self.assertTrue((DATA / "README.md").is_file())


class HygieneTests(unittest.TestCase):
    def test_readme_and_data_files_are_ascii_lf(self) -> None:
        for path in all_files():
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), path.name)
            self.assertNotIn(b"\r", raw, path.name)
            self.assertTrue(raw.isascii(), path.name)

    def test_no_local_paths_or_secrets(self) -> None:
        for path in all_files():
            text = read_text(path)
            for marker in LOCAL_PATH_MARKERS:
                self.assertNotIn(marker, text, f"{path.name}: {marker}")
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(pattern.search(text), path.name)

    def test_no_real_certification_or_product_names(self) -> None:
        for path in all_files():
            lowered = read_text(path).lower()
            for term in FORBIDDEN_TERMS:
                self.assertNotIn(term, lowered, f"{path.name}: {term}")

    def test_no_email_addresses_outside_reserved_domains(self) -> None:
        for path in all_files():
            for domain in EMAIL.findall(read_text(path)):
                self.assertIn(domain.lower(), ALLOWED_HOSTS, path.name)

    def test_no_percentages(self) -> None:
        for path in all_files():
            self.assertNotIn("%", read_text(path), path.name)

    def test_no_base64_or_data_uri_fixtures(self) -> None:
        # A real data: URI, not the ordinary English phrase "sample data:".
        data_uri = re.compile(r"data:[\w.+-]+/[\w.+-]+;base64,", re.I)
        for path in all_files():
            text = read_text(path)
            self.assertIsNone(data_uri.search(text), path.name)
            self.assertNotIn(";base64,", text, path.name)

    def test_urls_use_reserved_example_hosts(self) -> None:
        url_re = re.compile(r"https?://[^\s\"'<>)]+")
        for path in all_files():
            for url in url_re.findall(read_text(path)):
                host = urlsplit(url).hostname
                if host is not None:
                    self.assertIn(host.lower(), ALLOWED_HOSTS, f"{path.name}: {url}")


class ReadmeTests(unittest.TestCase):
    def test_readme_lists_every_file(self) -> None:
        text = read_text(DATA / "README.md")
        for name in sorted(EXPECTED_FILES):
            self.assertIn(f"`{name}`", text, name)

    def test_license_line(self) -> None:
        self.assertIn("CC0 1.0 Universal (CC0-1.0)", read_text(DATA / "README.md"))

    def test_not_affiliated_notice(self) -> None:
        self.assertIn(
            "not affiliated with or endorsed by the Git project",
            read_text(DATA / "README.md"),
        )


class CrossFolderScriptTests(unittest.TestCase):
    """Each of the six Stage 5 scripts, run exactly as its own page shows,
    against the real committed sample data. Output is checked against the
    page's own pasted transcript, not just a script's own exit code."""

    def test_concept_item_check_on_the_sample_items(self) -> None:
        proc = run(
            [
                "scripts/s5/concept_item_check.py",
                "scripts/sample_data/git_basics_stage5/concept_items/items.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("items=3 errors=0", proc.stdout)

    def test_stem_plan_check_on_the_sample_plan(self) -> None:
        proc = run(
            [
                "scripts/s5/stem_plan_check.py",
                "scripts/sample_data/git_basics_stage5/stem_plan/plan.json",
                "scripts/sample_data/git_basics_stage5/concept_items/items.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(
            "warning mix: plan is easy=50% medium=50% hard=0%, "
            "target is 30/50/20 (off by up to 20 points)",
            proc.stdout,
        )
        self.assertIn("rows=2 errors=0 warnings=1", proc.stdout)

    def test_format_rules_check_skips_the_broken_fixture_by_default(self) -> None:
        proc = run(
            [
                "scripts/s5/format_rules_check.py",
                "scripts/sample_data/git_basics_stage5/stems/stems.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("STEM-2.1-BROKEN", proc.stdout)
        self.assertIn("broken_on_purpose", proc.stdout)
        self.assertIn("stems=2 errors=0", proc.stdout)

    def test_format_rules_check_finds_every_planted_violation(self) -> None:
        proc = run(
            [
                "scripts/s5/format_rules_check.py",
                "scripts/sample_data/git_basics_stage5/stems/stems.json",
                "--include-broken-examples",
            ]
        )
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("stems=3 errors=4", proc.stdout)

    def test_bank_composition_check_on_the_real_blueprint(self) -> None:
        proc = run(
            [
                "scripts/s5/bank_composition_check.py",
                "scripts/sample_data/git_basics_stage5/bank/composition.json",
                "scripts/sample_data/git_basics/blueprint.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("domains=4 warnings=0", proc.stdout)

    def test_answer_key_check_on_the_sample_key(self) -> None:
        proc = run(
            [
                "scripts/s5/answer_key_check.py",
                "scripts/sample_data/git_basics_stage5/answer_key/key.json",
                "scripts/sample_data/git_basics_stage5/stems/stems.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("entries=2 errors=0", proc.stdout)

    def test_delivery_coverage_check_finds_the_one_planted_gap(self) -> None:
        proc = run(
            [
                "scripts/s5/delivery_coverage_check.py",
                "scripts/sample_data/git_basics_stage5/delivery/manifest.json",
                "scripts/sample_data/git_basics_stage5/stems/stems.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(
            'gap: "STEM-2.1-002" is in the bank but not assigned to any deliverable',
            proc.stdout,
        )
        self.assertIn("stems=2 unassigned=1", proc.stdout)


if __name__ == "__main__":
    unittest.main()
