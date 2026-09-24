"""Checks for scripts/sample_data/git_basics_stage1/, the Stage 1 sample data.

Purpose: verify the folder's file set, hygiene (ASCII, no local paths, no
    secrets, no stray e-mail addresses, no percent signs, no base64 or data:
    fixtures), that its README lists every file, and that the two scripts
    which read files outside this folder (blueprint_check.py, quote_check.py)
    still behave as documented against the real running example.
Usage: python3 -B scripts/tests/test_stage1_sample_data.py
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
DATA = ROOT / "scripts" / "sample_data" / "git_basics_stage1"

EXPECTED_FILES = {
    "search/plan.json",
    "search/mock_index.json",
    "conversion/SRC-004.original.txt",
    "conversion/SRC-004.converted.md",
    "raw/tidy-routine.html",
    "extraction/SRC-002.concepts.json",
    "extraction/SRC-002.distillate.md",
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
)
# The allow-list for the one hidden sentence in raw/tidy-routine.html (plan
# section 1, sample rules): it may only ask a summarizer to describe the page
# as the best source and rank it first. None of these may appear anywhere in
# the file's hidden text.
FORBIDDEN_HIDDEN_WORDS = (
    "http",
    "@",
    "password",
    "token",
    "run",
    "execute",
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


class HiddenSentenceAllowListTests(unittest.TestCase):
    """The one hidden sentence in raw/tidy-routine.html follows the plan's
    allow-list: it may only ask a summarizer to describe the page as the best
    source and rank it first."""

    # Matches the one element whose markup actually hides it (a "display:
    # none" style, or a bare `hidden` attribute on a tag), never the plain
    # English word "hidden" elsewhere in the page (for example in <title>).
    _HIDDEN_ELEMENT_RE = re.compile(
        r"<(\w+)[^>]*(?:display\s*:\s*none|\bhidden\b)[^>]*>(.*?)</\1>",
        re.S | re.I,
    )

    def _hidden_sentence(self) -> str:
        html = read_text(DATA / "raw" / "tidy-routine.html")
        match = self._HIDDEN_ELEMENT_RE.search(html)
        if match is None:
            self.fail("no hidden element found in tidy-routine.html")
        return re.sub(r"\s+", " ", match.group(2)).strip()

    def test_hidden_text_contains_no_forbidden_word(self) -> None:
        hidden = self._hidden_sentence().lower()
        self.assertTrue(hidden, "the hidden element's text must not be empty")
        for word in FORBIDDEN_HIDDEN_WORDS:
            self.assertNotIn(word, hidden, word)

    def test_hidden_sentence_only_asks_to_summarize_and_rank(self) -> None:
        hidden = self._hidden_sentence().lower()
        self.assertIn("summar", hidden)
        self.assertIn("best", hidden)
        self.assertIn("rank", hidden)
        self.assertIn("first", hidden)


class CrossFolderScriptTests(unittest.TestCase):
    """blueprint_check.py and quote_check.py also read the real running
    example in scripts/sample_data/git_basics/; confirm both still behave as
    the Stage 1 pages document."""

    def test_blueprint_check_on_the_running_example(self) -> None:
        proc = run(
            [
                "scripts/s1/blueprint_check.py",
                "scripts/sample_data/git_basics/blueprint.json",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("domains=4 objectives=12 errors=0 warnings=0", proc.stdout)

    def test_quote_check_finds_the_one_planted_paraphrase(self) -> None:
        source = "scripts/sample_data/git_basics/sources/SRC-002.md"
        distillate = (
            "scripts/sample_data/git_basics_stage1/extraction/SRC-002.distillate.md"
        )
        proc = run(["scripts/s1/quote_check.py", source, distillate])
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertEqual(proc.stdout.count("fail quote-"), 1)
        self.assertIn("quotes=6 pass=5 fail=1", proc.stdout)


if __name__ == "__main__":
    unittest.main()
