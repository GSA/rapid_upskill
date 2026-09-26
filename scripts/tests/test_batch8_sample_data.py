"""Checks for scripts/sample_data/git_basics_batch8/, Batch 8's sample data.

Purpose: verify the folder's file set (Part A only, for now), hygiene (ASCII, no
    local paths, no secrets, no stray e-mail addresses, no percent signs, no
    base64 or data: fixtures), that its README lists every file, and that
    Part A's three scripts still behave as their pages document against the
    real committed sample data.
Usage: python3 -B scripts/tests/test_batch8_sample_data.py
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
DATA = ROOT / "scripts" / "sample_data" / "git_basics_batch8"

EXPECTED_FILES = {
    "schedule/schedule.json",
    "slide_notes/Ch1_slideNotes_v20260115.md",
    "slide_notes/Ch1_slideNotes_v20260115_broken.md",
    "volumes/manifest.json",
    "volumes/manifest_off_convention.json",
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
    def test_part_a_files_exist(self) -> None:
        found = {
            p.relative_to(DATA).as_posix() for p in all_files() if p.name != "README.md"
        }
        # Part B adds further sub-folders later; Part A's own files must all be present.
        self.assertTrue(EXPECTED_FILES.issubset(found), found)
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

    def test_no_email_addresses_outside_reserved_domains(self) -> None:
        for path in all_files():
            for domain in EMAIL.findall(read_text(path)):
                self.assertIn(domain.lower(), ALLOWED_HOSTS, path.name)

    def test_no_percentages(self) -> None:
        for path in all_files():
            self.assertNotIn("%", read_text(path), path.name)

    def test_no_base64_or_data_uri_fixtures(self) -> None:
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
    def test_readme_lists_every_part_a_file(self) -> None:
        text = read_text(DATA / "README.md")
        for name in sorted(EXPECTED_FILES):
            self.assertIn(f"`{name}`", text, name)

    def test_license_line(self) -> None:
        self.assertIn("CC0 1.0 Universal (CC0-1.0)", read_text(DATA / "README.md"))


class CrossFolderScriptTests(unittest.TestCase):
    """Each of Part A's three scripts, run exactly as its own page shows, against
    the real committed sample data."""

    def test_schedule_check_on_the_sample_schedule(self) -> None:
        proc = run(
            [
                "scripts/ca/schedule_check.py",
                "scripts/sample_data/git_basics_batch8/schedule/schedule.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("chapters=3 errors=0 warnings=0", proc.stdout)

    def test_slide_notes_check_on_the_clean_sample(self) -> None:
        proc = run(
            [
                "scripts/dl/slide_notes_check.py",
                "scripts/sample_data/git_basics_batch8/slide_notes/"
                "Ch1_slideNotes_v20260115.md",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("slides=2 errors=0", proc.stdout)

    def test_slide_notes_check_on_the_broken_sample(self) -> None:
        proc = run(
            [
                "scripts/dl/slide_notes_check.py",
                "scripts/sample_data/git_basics_batch8/slide_notes/"
                "Ch1_slideNotes_v20260115_broken.md",
            ]
        )
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("slides=2 errors=2", proc.stdout)

    def test_volume_manifest_check_on_the_clean_sample(self) -> None:
        proc = run(
            [
                "scripts/dl/volume_manifest_check.py",
                "scripts/sample_data/git_basics_batch8/volumes/manifest.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("volumes=2 chapters=9 errors=0 warnings=0", proc.stdout)

    def test_volume_manifest_check_on_the_broken_sample(self) -> None:
        proc = run(
            [
                "scripts/dl/volume_manifest_check.py",
                "scripts/sample_data/git_basics_batch8/volumes/"
                "manifest_off_convention.json",
            ]
        )
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("volumes=2 chapters=9 errors=1 warnings=0", proc.stdout)


if __name__ == "__main__":
    unittest.main()
