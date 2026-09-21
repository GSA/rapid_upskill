"""Checks that facts stated in more than one place stay identical.

License: CC0-1.0 (public domain dedication,
https://creativecommons.org/publicdomain/zero/1.0/).

The site states some facts on several pages. This test keeps each fact in
step with the code or page that owns it:

* the capability names and their meanings (authoring conventions, platform
  requirements and ``sitelib.CAPABILITIES``);
* the glossary ids;
* the stage names used on the overview page (``sitelib.STAGES``);
* the rule numbers in the docs against the rules in ``check.py``;
* words the site avoids because the evidence does not support them.

Standard library only. It reads the real documentation, so it fails when a
page drifts from its owner.
"""

import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "site"))

import sitelib  # noqa: E402  # pylint: disable=wrong-import-position

DOCS = REPO / "docs"
CONVENTIONS = DOCS / "contributing" / "authoring-conventions.md"
CHECKLIST = DOCS / "contributing" / "release-checklist.md"
PLATFORM = DOCS / "platform-requirements.md"
OVERVIEW = DOCS / "pipeline-overview.md"
GLOSSARY = DOCS / "glossary.md"
CHECK_TOOL = REPO / "scripts" / "site" / "check.py"

GLOSSARY_IDS = frozenset(
    """agent agentic-platform alignment-matrix audit-trail batch blueprint
    capability certification-alignment certification-outline condensation
    context-window distractor dry-run exam-skill gate grounding hallucination
    hand-off-document human-in-the-loop integrity-guardrail item-bank
    job-task-analysis knowledge-base knowledge-item misconception
    misconception-catalog orchestrator placeholder prerequisite-hierarchy prompt
    prompt-injection protocol-tutor provenance rate-limit reference-implementation
    stage stem sub-stage subagent upskilling-program verification-layer
    confused-pairs""".split()
)
BATCH_1_PAGES = (
    "index.md",
    "pipeline-overview.md",
    "how-to-use-this-guide.md",
    "human-roles-gates-and-batching.md",
    "platform-requirements.md",
    "glossary.md",
)
# Words the evidence does not support. A sentence that also holds one of the
# ALLOWED phrases is a negation or a statement of a design aim, so it passes.
AVOIDED = (
    r"\bverified\b",
    r"\bvalidated\b",
    r"\bproven\b",
    r"\bfaster\b",
    r"portable to any platform",
)
ALLOWED = (
    "design aim",
    "not measured",
    "not a measured",
    "no timing baseline",
    "not a validated instrument",
    "unverified",
    "not verified",
    "not been verified",
)
RULE_RE = re.compile(r"\bR\d{2}[a-z]?\b")
GLOSSARY_HEADING_RE = re.compile(r"^## .+ \{#([a-z0-9-]+)\}\s*$", re.M)


def read(path: Path) -> str:
    """Return the text of a documentation file."""
    return sitelib.read_text(path)


def table_after(text: str, header_cell: str) -> list[list[str]]:
    """Return the body rows of the first table whose header starts with a cell.

    Cells are stripped. The separator row is skipped. An empty list means the
    table was not found.
    """
    lines = text.splitlines()
    for start, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and cells[0].lower() == header_cell.lower():
            rows: list[list[str]] = []
            for row in lines[start + 2 :]:
                if not row.lstrip().startswith("|"):
                    break
                rows.append([c.strip() for c in row.strip().strip("|").split("|")])
            return rows
    return []


def capability_meanings(path: Path) -> dict[str, str]:
    """Map capability name to meaning from the table in a page."""
    result: dict[str, str] = {}
    for row in table_after(read(path), "Capability"):
        if len(row) >= 2:
            result[row[0].strip("`")] = row[1]
    return result


def sentences(text: str) -> list[str]:
    """Split text into rough sentences, one per line or full stop."""
    parts: list[str] = []
    for line in text.splitlines():
        parts.extend(re.split(r"(?<=[.!?])\s+", line))
    return parts


class CapabilityConsistencyTests(unittest.TestCase):
    """The ten capabilities read the same everywhere."""

    def test_conventions_match_the_code(self) -> None:
        names = set(capability_meanings(CONVENTIONS))
        self.assertEqual(names, set(sitelib.CAPABILITIES))

    def test_platform_page_matches_the_code(self) -> None:
        if not PLATFORM.exists():
            self.skipTest("platform-requirements.md has not been written yet")
        names = set(capability_meanings(PLATFORM))
        self.assertEqual(names, set(sitelib.CAPABILITIES))

    def test_meanings_are_identical(self) -> None:
        if not PLATFORM.exists():
            self.skipTest("platform-requirements.md has not been written yet")
        conventions = capability_meanings(CONVENTIONS)
        platform = capability_meanings(PLATFORM)
        for name in sitelib.CAPABILITIES:
            self.assertEqual(platform.get(name), conventions.get(name), name)


class GlossaryTests(unittest.TestCase):
    """The glossary defines exactly the agreed ids, in alphabetical order."""

    def setUp(self) -> None:
        if not GLOSSARY.exists():
            self.skipTest("glossary.md has not been written yet")
        self.text = read(GLOSSARY)
        self.ids = GLOSSARY_HEADING_RE.findall(self.text)

    def test_ids_are_the_agreed_set(self) -> None:
        self.assertEqual(sorted(self.ids), sorted(GLOSSARY_IDS))
        self.assertEqual(len(self.ids), len(set(self.ids)), "duplicate ids")

    def test_terms_are_alphabetical(self) -> None:
        headings = re.findall(r"^## (.+?) \{#([a-z0-9-]+)\}\s*$", self.text, re.M)
        terms = [text.lower() for text, ident in headings if ident != "confused-pairs"]
        self.assertEqual(terms, sorted(terms))

    def test_links_into_the_glossary_use_agreed_ids(self) -> None:
        link = re.compile(r"glossary\.md#([a-z0-9-]+)")
        for name in BATCH_1_PAGES:
            path = DOCS / name
            if not path.exists():
                continue
            for ident in link.findall(read(path)):
                self.assertIn(ident, GLOSSARY_IDS, f"{name} links #{ident}")


class StageNameTests(unittest.TestCase):
    """The overview uses the stage names the tools use."""

    def test_overview_names_every_stage(self) -> None:
        if not OVERVIEW.exists():
            self.skipTest("pipeline-overview.md has not been written yet")
        text = read(OVERVIEW).lower()
        for code in ("S1", "S2", "S3", "S4", "S5"):
            name = sitelib.STAGES[code][1].lower()
            self.assertIn(name, text, f"{code}: {name}")


class RuleNumberTests(unittest.TestCase):
    """Rule numbers in the docs match the rules the checker implements."""

    def test_docs_and_checker_agree(self) -> None:
        in_code = set(RULE_RE.findall(read(CHECK_TOOL)))
        checklist = set(RULE_RE.findall(read(CHECKLIST)))
        conventions = set(RULE_RE.findall(read(CONVENTIONS)))
        self.assertEqual(checklist - in_code, set(), "checklist names unknown rules")
        self.assertEqual(conventions - in_code, set(), "conventions name unknown rules")
        self.assertEqual(in_code - checklist, set(), "checklist misses rules")


class AvoidedWordTests(unittest.TestCase):
    """Front matter pages do not use words the evidence does not support."""

    def test_no_unsupported_claims(self) -> None:
        problems: list[str] = []
        for name in BATCH_1_PAGES:
            path = DOCS / name
            if not path.exists():
                continue
            for sentence in sentences(read(path)):
                low = sentence.lower()
                if any(phrase in low for phrase in ALLOWED):
                    continue
                for pattern in AVOIDED:
                    if re.search(pattern, low):
                        problems.append(f"{name}: {sentence.strip()[:100]}")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
