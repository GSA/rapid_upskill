"""Checks for the running-example sample data and its documentation page.

Purpose: verify that blueprint.json, cert_blueprint.json, the seven sources and
    docs/running-example.md are complete, consistent with each other, and free
    of local paths, e-mail addresses and key patterns.
Usage: python3 -B scripts/tests/test_running_example.py
Dependencies: stdlib
Writes files: no
License: CC0-1.0
"""

import datetime
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlsplit

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "scripts" / "sample_data" / "git_basics"
SOURCES = DATA / "sources"
PAGE = ROOT / "docs" / "running-example.md"
BASE_URL = (
    "https://github.com/GSA/rapid_upskill/tree/master/scripts/sample_data/git_basics"
)

SOURCE_IDS = [f"SRC-{n:03d}" for n in range(1, 8)]
BLOOM_LEVELS = {"remember", "understand", "apply", "analyze", "evaluate", "create"}
ALLOWED_HOSTS = {"example.com", "example.org", "example.net"}
SOURCE_KEYS = {"id", "title", "author", "date", "url", "license", "synthetic"}
PHRASES = ("A common mistake is", "Many newcomers believe")
EXPECTED_FILES = {
    "README.md",
    "blueprint.json",
    "cert_blueprint.json",
    *(f"sources/{sid}.md" for sid in SOURCE_IDS),
}

FRONT_MATTER_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*): (.+)$")
GIT_VERSION = re.compile(r"[Gg]it (?:version )?(\d+\.\d+\.\d+)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
# Built from parts so that this file does not itself contain the strings it forbids.
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


def read_text(path: Path) -> str:
    """Read a file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def load_json(name: str) -> Dict[str, Any]:
    """Load a JSON object from the sample-data folder."""
    data = json.loads(read_text(DATA / name))
    if not isinstance(data, dict):
        raise TypeError(f"{name} must hold a JSON object")
    return data


def is_int(value: Any) -> bool:
    """Return True for real integers (booleans do not count)."""
    return isinstance(value, int) and not isinstance(value, bool)


def parse_value(raw: str) -> Any:
    """Parse one front-matter value: quoted string, integer or boolean."""
    if re.fullmatch(r'"[^"\\]*"', raw):
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if raw in ("true", "false"):
        return raw == "true"
    raise ValueError(f"unsupported front-matter value: {raw!r}")


def split_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    """Split a page into its front-matter dict and its body text."""
    lines = text.split("\n")
    if lines[0] != "---":
        raise ValueError("front matter must open on line 1")
    end = lines.index("---", 1)
    meta: Dict[str, Any] = {}
    for line in lines[1:end]:
        match = FRONT_MATTER_LINE.match(line)
        if match is None:
            raise ValueError(f"bad front-matter line: {line!r}")
        key, raw = match.groups()
        if key in meta:
            raise ValueError(f"duplicate front-matter key: {key}")
        meta[key] = parse_value(raw)
    start = end + 1
    return meta, "\n".join(lines[start:])


def split_fences(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Blank out fenced code blocks; return masked text and (language, code)."""
    masked: List[str] = []
    fences: List[Tuple[str, str]] = []
    marker = ""
    language = ""
    code: List[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not marker:
            opener = re.match(r"^(`{3,})\s*(\S*)", stripped)
            if opener:
                marker, language, code = opener.group(1), opener.group(2), []
                masked.append("")
            else:
                masked.append(line)
        elif stripped.startswith(marker) and set(stripped) == {"`"}:
            fences.append((language, "\n".join(code)))
            marker = ""
            masked.append("")
        else:
            code.append(line)
            masked.append("")
    if marker:
        raise ValueError("unclosed code fence")
    return "\n".join(masked), fences


def table_rows(text: str) -> List[List[str]]:
    """Return the cells of every Markdown table row, minus separator rows."""
    rows: List[List[str]] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def all_public_files() -> List[Path]:
    """List every file this test guards: the sample folder plus the page."""
    found = [
        p
        for p in DATA.rglob("*")
        if p.is_file() and not p.name.startswith(".") and "__pycache__" not in p.parts
    ]
    return sorted(found) + [PAGE]


class BlueprintTests(unittest.TestCase):
    """blueprint.json: shape, weights, tiers, coverage gap and arithmetic."""

    bp: Dict[str, Any]
    domains: List[Dict[str, Any]]
    objectives: List[Dict[str, Any]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.bp = load_json("blueprint.json")
        cls.domains = cls.bp["domains"]
        cls.objectives = [o for d in cls.domains for o in d["objectives"]]

    def test_top_level_fields_and_types(self) -> None:
        expected = {
            "schema_version",
            "license",
            "synthetic",
            "program",
            "difficulty_split",
            "bank_size",
            "domains",
        }
        self.assertEqual(set(self.bp), expected)
        self.assertEqual(self.bp["schema_version"], "1.0.0")
        self.assertEqual(self.bp["license"], "CC0-1.0")
        self.assertIs(self.bp["synthetic"], True)
        self.assertEqual(self.bp["program"], "Git Basics for New Team Members")
        self.assertEqual(self.bp["difficulty_split"], [30, 50, 20])
        self.assertTrue(all(is_int(n) for n in self.bp["difficulty_split"]))
        self.assertTrue(is_int(self.bp["bank_size"]))
        self.assertEqual(self.bp["bank_size"], 20)

    def test_four_domains_with_weights_summing_to_100(self) -> None:
        self.assertEqual(len(self.domains), 4)
        self.assertEqual([d["id"] for d in self.domains], ["D1", "D2", "D3", "D4"])
        weights = [d["weight"] for d in self.domains]
        self.assertTrue(all(is_int(w) for w in weights))
        self.assertEqual(weights, [25, 30, 25, 20])
        self.assertEqual(sum(weights), 100)
        names = [d["name"] for d in self.domains]
        self.assertTrue(all(isinstance(n, str) and n for n in names))
        self.assertEqual(len(set(names)), 4)
        for domain in self.domains:
            self.assertEqual(
                set(domain), {"id", "name", "weight", "objectives"}, domain["id"]
            )
            self.assertEqual(len(domain["objectives"]), 3, domain["id"])

    def test_twelve_objectives_with_valid_fields(self) -> None:
        self.assertEqual(len(self.objectives), 12)
        expected = {"id", "text", "bloom", "tier", "chapter", "supported_by"}
        for domain in self.domains:
            for index, obj in enumerate(domain["objectives"], start=1):
                oid = obj["id"]
                self.assertEqual(set(obj), expected, oid)
                self.assertEqual(oid, f"{domain['id']}.{index}")
                self.assertTrue(isinstance(obj["text"], str) and obj["text"], oid)
                self.assertIn(obj["bloom"], BLOOM_LEVELS, oid)
                self.assertTrue(is_int(obj["tier"]), oid)
                self.assertIn(obj["tier"], (1, 2, 3, 4), oid)
                self.assertTrue(is_int(obj["chapter"]), oid)
                self.assertIn(obj["chapter"], (1, 2, 3), oid)
                support = obj["supported_by"]
                self.assertIsInstance(support, list, oid)
                self.assertEqual(len(support), len(set(support)), oid)
                for sid in support:
                    self.assertRegex(sid, r"^SRC-\d{3}$")

    def test_each_tier_used_at_least_twice(self) -> None:
        tiers = [o["tier"] for o in self.objectives]
        for tier in (1, 2, 3, 4):
            self.assertGreaterEqual(tiers.count(tier), 2, f"tier {tier}")

    def test_every_chapter_is_used(self) -> None:
        self.assertEqual({o["chapter"] for o in self.objectives}, {1, 2, 3})

    def test_exactly_one_objective_has_no_support(self) -> None:
        empty = [o["id"] for o in self.objectives if not o["supported_by"]]
        self.assertEqual(empty, ["D4.2"])

    def test_every_supported_by_id_exists(self) -> None:
        for obj in self.objectives:
            for sid in obj["supported_by"]:
                self.assertTrue((SOURCES / f"{sid}.md").is_file(), sid)

    def test_the_gap_is_a_real_gap(self) -> None:
        gap = next(o for o in self.objectives if not o["supported_by"])
        self.assertIn("reflog", gap["text"])
        for sid in SOURCE_IDS:
            text = read_text(SOURCES / f"{sid}.md").lower()
            self.assertNotIn("reflog", text, sid)

    def test_stem_arithmetic_is_whole_numbers(self) -> None:
        size = self.bp["bank_size"]
        by_difficulty = [size * s for s in self.bp["difficulty_split"]]
        self.assertTrue(all(n % 100 == 0 for n in by_difficulty))
        self.assertEqual([n // 100 for n in by_difficulty], [6, 10, 4])
        by_domain = [size * d["weight"] for d in self.domains]
        self.assertTrue(all(n % 100 == 0 for n in by_domain))
        self.assertEqual([n // 100 for n in by_domain], [5, 6, 5, 4])


class CertBlueprintTests(unittest.TestCase):
    """cert_blueprint.json: weights, skills and the two planted gaps."""

    cert: Dict[str, Any]
    skill_ids: List[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.cert = load_json("cert_blueprint.json")
        cls.skill_ids = [s["id"] for d in cls.cert["domains"] for s in d["skills"]]

    def test_top_level_fields(self) -> None:
        expected = {
            "schema_version",
            "license",
            "synthetic",
            "certification",
            "domains",
            "chapters",
        }
        self.assertEqual(set(self.cert), expected)
        self.assertEqual(self.cert["schema_version"], "1.0.0")
        self.assertEqual(self.cert["license"], "CC0-1.0")
        self.assertIs(self.cert["synthetic"], True)
        self.assertEqual(
            self.cert["certification"], "Team Git Practitioner (fictional)"
        )

    def test_three_domains_and_eight_skills(self) -> None:
        domains = self.cert["domains"]
        self.assertEqual(len(domains), 3)
        self.assertEqual([d["number"] for d in domains], [1, 2, 3])
        weights = [d["weight"] for d in domains]
        self.assertTrue(all(is_int(w) for w in weights))
        self.assertEqual(sum(weights), 100)
        self.assertEqual(len(self.skill_ids), 8)
        self.assertEqual(len(set(self.skill_ids)), 8)

    def test_skill_ids_and_weights(self) -> None:
        for domain in self.cert["domains"]:
            skills = domain["skills"]
            for index, skill in enumerate(skills, start=1):
                self.assertEqual(skill["id"], f"CB-{domain['number']}.{index}")
                self.assertTrue(isinstance(skill["text"], str) and skill["text"])
                self.assertTrue(is_int(skill["weight"]), skill["id"])
            total = sum(s["weight"] for s in skills)
            self.assertEqual(total, 100, f"domain {domain['number']}")

    def test_outline_differs_from_the_program(self) -> None:
        program = load_json("blueprint.json")
        program_names = {d["name"] for d in program["domains"]}
        cert_names = {d["name"] for d in self.cert["domains"]}
        self.assertFalse(program_names & cert_names)
        self.assertNotEqual(len(program_names), len(cert_names))

    def test_chapters_map_to_existing_skills(self) -> None:
        chapters = self.cert["chapters"]
        self.assertEqual([c["number"] for c in chapters], [1, 2, 3])
        program = load_json("blueprint.json")
        used = {o["chapter"] for d in program["domains"] for o in d["objectives"]}
        self.assertEqual({c["number"] for c in chapters}, used)
        for chapter in chapters:
            self.assertTrue(isinstance(chapter["title"], str) and chapter["title"])
            self.assertIsInstance(chapter["skills"], list)
            for skill_id in chapter["skills"]:
                self.assertIn(skill_id, self.skill_ids)

    def test_exactly_one_uncovered_skill_and_one_unmatched_chapter(self) -> None:
        chapters = self.cert["chapters"]
        covered = {sid for c in chapters for sid in c["skills"]}
        uncovered = [sid for sid in self.skill_ids if sid not in covered]
        self.assertEqual(uncovered, ["CB-3.1"])
        unmatched = [c["number"] for c in chapters if not c["skills"]]
        self.assertEqual(unmatched, [3])


class SourceTests(unittest.TestCase):
    """The seven sources: front matter, length, roles and content flags."""

    meta: Dict[str, Dict[str, Any]]
    body: Dict[str, str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.meta = {}
        cls.body = {}
        for sid in SOURCE_IDS:
            meta, body = split_front_matter(read_text(SOURCES / f"{sid}.md"))
            cls.meta[sid] = meta
            cls.body[sid] = body

    def test_exactly_the_seven_source_files_exist(self) -> None:
        found = sorted(p.name for p in SOURCES.iterdir() if not p.name.startswith("."))
        self.assertEqual(found, [f"{sid}.md" for sid in SOURCE_IDS])

    def test_front_matter(self) -> None:
        for sid, meta in self.meta.items():
            self.assertEqual(set(meta), SOURCE_KEYS, sid)
            self.assertEqual(meta["id"], sid)
            self.assertEqual(meta["license"], "CC0-1.0", sid)
            self.assertIs(meta["synthetic"], True, sid)
            for key in ("title", "author", "date", "url"):
                self.assertTrue(isinstance(meta[key], str) and meta[key], sid)
            datetime.date.fromisoformat(meta["date"])
            parts = urlsplit(meta["url"])
            self.assertEqual(parts.scheme, "https", sid)
            self.assertIn(parts.hostname, ALLOWED_HOSTS, sid)
        titles = [m["title"] for m in self.meta.values()]
        self.assertEqual(len(set(titles)), len(titles))

    def test_body_length_is_300_to_500_words(self) -> None:
        for sid, body in self.body.items():
            count = len(body.split())
            self.assertGreaterEqual(count, 300, f"{sid} has {count} words")
            self.assertLessEqual(count, 500, f"{sid} has {count} words")

    def test_older_source_conflicts_with_the_newer_one(self) -> None:
        older = datetime.date.fromisoformat(self.meta["SRC-005"]["date"])
        newer = datetime.date.fromisoformat(self.meta["SRC-004"]["date"])
        self.assertLess(older, newer)
        self.assertIn("never touches the files", self.body["SRC-005"])
        self.assertNotIn("never touches the files", self.body["SRC-004"])
        for command in ("git fetch", "git pull", "git push"):
            self.assertIn(command, self.body["SRC-004"])
        self.assertIn("git pull", self.body["SRC-005"])

    def test_misconception_sentences_are_followed_by_the_correction(self) -> None:
        for sid in ("SRC-001", "SRC-002", "SRC-003"):
            found = 0
            for paragraph in re.split(r"\n\s*\n", self.body[sid]):
                text = " ".join(paragraph.split())
                sentences = re.split(r"(?<=[.!?])\s+", text)
                for index, sentence in enumerate(sentences):
                    if sentence.startswith(PHRASES):
                        found += 1
                        self.assertLess(
                            index + 1, len(sentences), f"{sid}: no correction"
                        )
            self.assertGreaterEqual(found, 2, sid)

    def test_only_the_injection_source_addresses_an_ai_assistant(self) -> None:
        pattern = re.compile(r"\bAI assistants?\b", re.IGNORECASE)
        for sid, body in self.body.items():
            expected = 1 if sid == "SRC-006" else 0
            self.assertEqual(len(pattern.findall(body)), expected, sid)
        self.assertIn("ignore all earlier instructions", self.body["SRC-006"])

    def test_promotional_source_has_no_git_commands(self) -> None:
        self.assertNotIn("`git ", self.body["SRC-007"])

    def test_corrected_statements_stay_corrected(self) -> None:
        self.assertIn("time-zone offsets", self.body["SRC-001"])
        self.assertIn("After the commit", self.body["SRC-001"])
        self.assertIn("merge.ff=false", self.body["SRC-002"])
        self.assertIn("nothing to merge", self.body["SRC-002"])
        self.assertIn("Git 2.23 or later", self.body["SRC-002"])
        self.assertIn("neighboring lines", self.body["SRC-003"])
        self.assertIn("a file both branches edited", self.body["SRC-003"])
        self.assertIn("git diff --cached --check", self.body["SRC-003"])
        self.assertIn("(commit form)", self.body["SRC-003"])
        self.assertIn("Git 2.19 or later", self.body["SRC-003"])
        self.assertIn("Git 2.23 or later", self.body["SRC-003"])
        self.assertNotIn("worry new team members", self.body["SRC-003"])
        self.assertIn("push.default=current", self.body["SRC-004"])
        self.assertIn("a safeguard, not a guarantee", self.body["SRC-004"])
        self.assertIn("A common reason a push is rejected", self.body["SRC-005"])
        self.assertIn("diverged", self.body["SRC-005"])

    def test_accurate_sources_avoid_unverified_universal_words(self) -> None:
        pattern = re.compile(r"\b(always|never|every|exactly)\b", re.IGNORECASE)
        for sid in ("SRC-001", "SRC-002", "SRC-003", "SRC-004"):
            self.assertEqual(pattern.findall(self.body[sid]), [], sid)

    def test_version_mentions_match_the_readme_pin(self) -> None:
        pinned = GIT_VERSION.search(read_text(DATA / "README.md"))
        if pinned is None:
            self.fail("README.md does not pin a Git version")
        for sid, body in self.body.items():
            for version in GIT_VERSION.findall(body):
                self.assertEqual(version, pinned.group(1), sid)


class HygieneTests(unittest.TestCase):
    """No local paths, addresses, keys or numeric claims in any public file."""

    def test_file_set_is_exactly_the_planned_set(self) -> None:
        found = {
            p.relative_to(DATA).as_posix() for p in all_public_files() if p != PAGE
        }
        self.assertEqual(found, EXPECTED_FILES)
        self.assertTrue(PAGE.is_file())

    def test_plain_ascii_lf_text(self) -> None:
        for path in all_public_files():
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), path.name)
            self.assertNotIn(b"\r", raw, path.name)
            self.assertTrue(raw.isascii(), path.name)

    def test_no_local_paths_or_secrets(self) -> None:
        for path in all_public_files():
            text = read_text(path)
            for marker in LOCAL_PATH_MARKERS:
                self.assertNotIn(marker, text, f"{path.name}: {marker}")
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(pattern.search(text), path.name)

    def test_no_email_addresses_outside_reserved_domains(self) -> None:
        for path in all_public_files():
            for domain in EMAIL.findall(read_text(path)):
                self.assertIn(domain.lower(), ALLOWED_HOSTS, path.name)

    def test_no_percentages_or_statistics(self) -> None:
        for path in all_public_files():
            text = read_text(path).lower()
            self.assertNotIn("%", text, path.name)
            self.assertNotIn("percent", text, path.name)
            self.assertNotIn("statistic", text, path.name)


class ReadmeTests(unittest.TestCase):
    """The folder README documents the pin, the files, the IDs and the license."""

    text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_text(DATA / "README.md")

    def test_pinned_version_and_notice(self) -> None:
        self.assertRegex(self.text, r"git version \d+\.\d+\.\d+")
        self.assertIn("not affiliated with or endorsed by the Git project", self.text)

    def test_every_file_and_source_role_is_listed(self) -> None:
        for name in sorted(EXPECTED_FILES - {"README.md"}):
            self.assertIn(f"`{name}`", self.text, name)

    def test_reserved_id_formats_and_arithmetic(self) -> None:
        for fmt in ("SRC-001", "KI-c.n-NNN", "MC-c-NNN", "STEM-c.n-NNN", "CB-d.n"):
            self.assertIn(f"`{fmt}`", self.text, fmt)
        self.assertIn("6/10/4", self.text)
        self.assertIn("5/6/5/4", self.text)

    def test_license_line(self) -> None:
        self.assertIn("CC0 1.0 Universal (CC0-1.0)", self.text)

    def test_promotional_source_is_labelled_as_such(self) -> None:
        self.assertIn("Promotional, low quality", self.text)
        self.assertNotIn("Off-topic", self.text)

    def test_testing_claims_are_modest(self) -> None:
        self.assertNotIn("disabled", self.text)
        self.assertIn("release notes", self.text)
        self.assertIn("were not run", self.text)


class PageTests(unittest.TestCase):
    """docs/running-example.md: front matter, structure and data agreement."""

    meta: Dict[str, Any]
    body: str
    masked: str
    fences: List[Tuple[str, str]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.meta, cls.body = split_front_matter(read_text(PAGE))
        cls.masked, cls.fences = split_fences(cls.body)

    def test_front_matter(self) -> None:
        expected = {
            "title": "The running example",
            "nav_order": 2,
            "status": "draft",
            "last_reviewed": "2026-09-19",
        }
        self.assertEqual(self.meta, expected)
        self.assertTrue(is_int(self.meta["nav_order"]))

    def test_headings_do_not_skip_levels(self) -> None:
        levels = [
            len(m.group(1))
            for m in re.finditer(r"^(#{1,6})\s+\S", self.masked, re.MULTILINE)
        ]
        self.assertEqual(levels.count(1), 1)
        self.assertEqual(levels[0], 1)
        for before, after in zip(levels, levels[1:]):
            self.assertLessEqual(after, before + 1)

    def test_code_fences_have_languages_and_no_template_syntax(self) -> None:
        self.assertGreaterEqual(len(self.fences), 1)
        for language, _ in self.fences:
            self.assertTrue(language)
        self.assertNotIn("{{", self.body)
        self.assertNotIn("{%", self.body)

    def test_links_are_absolute_https_and_point_at_the_sample_data(self) -> None:
        prose = re.sub(r"`[^`\n]*`", "", self.masked)
        links = re.findall(r"\[([^\]]+)\]\(([^)\s]+)[^)]*\)", prose)
        self.assertGreaterEqual(len(links), 1)
        for text, target in links:
            self.assertTrue(target.startswith("https://"), target)
            self.assertNotIn(text.strip().lower(), ("here", "click here"))
            if "sample_data" in target:
                self.assertTrue(target.startswith(BASE_URL), target)
        self.assertIn(BASE_URL, [target for _, target in links])
        self.assertNotRegex(prose, r"\]\((?!https://|#)")

    def test_domain_table_matches_blueprint(self) -> None:
        blueprint = load_json("blueprint.json")
        expected = [(d["id"], d["name"], d["weight"]) for d in blueprint["domains"]]
        rows = [r for r in table_rows(self.masked) if re.fullmatch(r"D\d", r[0])]
        found = []
        for row in rows:
            self.assertEqual(len(row), 3, row)
            found.append((row[0], row[1], int(row[2])))
        self.assertEqual(found, expected)
        self.assertEqual(sum(w for _, _, w in found), 100)

    def test_source_table_matches_the_sources(self) -> None:
        rows = [r for r in table_rows(self.masked) if r[0].startswith("SRC-")]
        self.assertEqual([r[0] for r in rows], SOURCE_IDS)
        for row in rows:
            self.assertEqual(len(row), 3, row)
            meta, _ = split_front_matter(read_text(SOURCES / f"{row[0]}.md"))
            self.assertEqual(row[1], meta["title"], row[0])
            self.assertTrue(row[2], row[0])

    def test_json_example_matches_the_blueprint(self) -> None:
        blueprint = load_json("blueprint.json")
        objectives = {o["id"]: o for d in blueprint["domains"] for o in d["objectives"]}
        snippets = [code for lang, code in self.fences if lang == "json"]
        self.assertEqual(len(snippets), 1)
        example = json.loads(snippets[0])
        self.assertEqual(example, objectives[example["id"]])

    def test_testing_claims_are_modest(self) -> None:
        self.assertNotIn("Each Git behavior", self.body)
        self.assertIn("release notes", self.body)

    def test_version_and_notice_match_the_readme(self) -> None:
        readme = read_text(DATA / "README.md")
        pinned = GIT_VERSION.search(readme)
        if pinned is None:
            self.fail("README.md does not pin a Git version")
        self.assertIn(
            f"git version {pinned.group(1)}", "\n".join(code for _, code in self.fences)
        )
        self.assertIn("not affiliated with or endorsed by the Git project", self.body)


if __name__ == "__main__":
    unittest.main()
