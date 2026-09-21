"""Site checker: runs every documentation rule offline and reports findings.

License: CC0-1.0 (public domain dedication,
https://creativecommons.org/publicdomain/zero/1.0/).

Usage: python3 -B scripts/site/check.py [--root DIR] [--extra-forbidden FILE]

Standard library only. Reads the repository under --root (default: two levels
above this file) and never writes to it. No git call, no clock, no network.
Output is one line per finding, "path:line RULE message", sorted by path, line
and rule, then a summary line "check: N errors, M warnings". Exit code 0 means
no errors (warnings never change it), 1 means at least one error, 2 means a
usage error or an input that cannot be read.

RULES (E error, W warning; see plans/batch0.md S8)
    R01 E front matter subset, required keys, title characters (unknown keys W)
    R02 E titles unique, parent and grand_parent resolve, no has_children: false
    R03 E nav_order is an integer and unique among siblings
    R04 E internal links resolve; a leading "/" is an error
    R04a E/W anchors match a heading id (W when the id is uncertain)
    R05 E link target is outside docs/       R06 E images exist and have alt text
    R07 E IDs, folders, slugs, stage and references agree
    R08 E prompt file rules                  R09 E script header and imports
    R10 E local paths, keys, emails and private terms
    R11 E generated files match sync.compute_outputs(root)
    R16 E Liquid delimiters outside raw blocks
    R17 E CR or BOM in a text source         R18 E symlinks, case-fold clashes
    R22 E root-relative src or href in docs/_includes
    R12 R13 R14 R15 R19 R20 R21 W style, on hand-written pages only

CHOICES WHERE THE PLAN IS SILENT OR AMBIGUOUS
* Front matter: hand-written pages need title, status, last_reviewed and
  nav_order (unless nav_exclude is true); generated pages need only title.
  status must be draft, reviewed or stable; last_reviewed must be a real
  YYYY-MM-DD date (shape only, the clock is never read). Keys are type-checked
  (strings, booleans, inline lists). When a page has a front matter error the
  missing-key check and the style warnings are skipped for it, so one mistake
  does not cascade.
* R02: a page may not be its own parent. A grand_parent is required when the
  parent page is itself nested, and must equal the parent's parent.
* R03: every page with an integer nav_order takes part, nav_exclude or not.
* R04: reference definitions "[id]: target" are checked once, at the
  definition; a "[t][id]" with no definition is an error. Targets that hold
  Liquid ({{ or {%) are not resolved. A directory target is accepted when it
  exists. A leading "/" is R04 for images too; a missing image file is R06 and
  an existing image outside docs/ is R05. HTML ids and names count as anchors.
* R04a: heading ids come from sitelib.find_headings (the source of
  headings_ids), so explicit {#id} wins. The finding is a warning when the
  target heading has code spans, entities, "--", "..." or non-ASCII characters
  and either the anchor equals another plausible reading of the id or the
  readings disagree; it is an error when no reading matches.
* R06: an image with empty or missing alt text is an error. Image files are
  looked up only for internal targets.
* R07: prompt IDs are P-<code>-<nn> and script IDs X-<code>-<nn>, two digits.
  A page's stage must agree with the stage of every prompt or script it lists,
  except OP items (cross-cutting). The generated page for an ID is
  docs/prompts|scripts/<code lowercase>/<id lowercase>.md (plan S7).
* R08: unknown prompt front matter keys are warnings. Library sources are only
  prompts/<code>/*.md, scripts/<code>/*.py|*.sh and scripts/common/*.py; names
  that start with "_" or "test_" and README.md files are ignored.
* R09: key or token patterns in a library script are reported as R09, not R10
  (the plan lists them under R09); every other R10 check still covers scripts.
  Unknown script header fields are not reported (prose can look like a field).
* R10: scans md, py, sh, json, yml, yaml, svg, html, js, scss and txt files under
  docs/, images/, prompts/ and scripts/ (never the repository root files), and
  skips this tool and scripts/tests/. Every match reports the category or the
  term ordinal, never the text. The private list is --extra-forbidden or the
  environment variable named in FORBIDDEN_ENV (a file path; the flag wins). An
  invalid or empty-matching regex in the list is exit code 2.
* R17 covers the same files as R10, this tool and the tests included.
* R11: a file the mapping omits is stale, whatever its name. A drifted or
  missing file is reported at line 1.
* R14: words are whitespace-separated tokens with a letter or digit, counted
  in the body; sentences are counted in prose (no headings, tables, code).
* R21: template sections are matched by H2 text, case-insensitively; a
  section is reported when it appears after a later template section.
* Input problems (an unreadable or non-UTF-8 file, an invalid list) are exit
  code 2, and so is a --root without a docs/ folder. Symlinked files are never
  read by R10 or R17; R18 reports them.
* Not checked: the target of a {% link %} tag (R16 only allows the form).
"""

import argparse
import datetime
import functools
import html
import importlib
import os
import posixpath
import re
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import unquote

sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    print(
        "check: this tool needs Python 3.10 or newer, but this is "
        f"{sys.version_info.major}.{sys.version_info.minor}. "
        "Run it with a newer python3.",
        file=sys.stderr,
    )
    sys.exit(2)
SITE_DIR = Path(__file__).resolve().parent
if str(SITE_DIR) not in sys.path:
    sys.path.insert(0, str(SITE_DIR))

import sitelib  # noqa: E402  # pylint: disable=wrong-import-position

_T = TypeVar("_T")

# ---- constants -------------------------------------------------------------
SCAN_DIRS = ("docs", "images", "prompts", "scripts")
TEXT_SUFFIXES = (
    ".md",
    ".py",
    ".sh",
    ".json",
    ".yml",
    ".yaml",
    ".svg",
    ".html",
    ".js",
    ".scss",
    ".txt",
)
SKIP_DIRS = frozenset(
    "__pycache__ .git .bundle .jekyll-cache .sass-cache _site node_modules "
    "vendor".split()
)
GENERATED_DIRS = ("docs/assets/images", "docs/prompts", "docs/scripts")
SELF_REL = "scripts/site/check.py"
TESTS_PREFIX = "scripts/tests/"
FORBIDDEN_ENV = "RAPID_UPSKILL_FORBIDDEN"
NOTICE = "R10 private-term check skipped: no list supplied"
SECTIONS = (
    "Outcome",
    "Where it fits",
    "Why this way",
    "Steps",
    "Artifacts and formats",
    "Prompts",
    "Scripts",
    "Definition of done",
    "Common failures",
    "Adapting to your platform",
    "Where humans decide",
)
MAX_WORDS, MIN_WORDS = 2500, 60
LONG_SENTENCE, LONG_SHARE = 35, 0.10


class InputError(Exception):
    """An input the checker cannot read; the CLI turns it into exit code 2."""


def _guard(rel: str, func: Callable[[], _T]) -> _T:
    try:
        return func()
    except UnicodeDecodeError as exc:
        raise InputError(f"cannot read {rel}: not valid UTF-8 text") from exc
    except OSError as exc:
        why = exc.strerror or type(exc).__name__
        raise InputError(f"cannot read {rel}: {why}") from exc


class Report:
    """Collects findings; result() returns them unique and sorted."""

    def __init__(self) -> None:
        self.items: list[sitelib.Finding] = []

    def error(self, path: str, line: int, rule: str, message: str) -> None:
        self.items.append(sitelib.Finding(path, line, rule, sitelib.ERROR, message))

    def warn(self, path: str, line: int, rule: str, message: str) -> None:
        self.items.append(sitelib.Finding(path, line, rule, sitelib.WARNING, message))

    def result(self) -> list[sitelib.Finding]:
        unique = {
            (f.path, f.line, f.rule, f.severity, f.message): f for f in self.items
        }
        return sorted(
            unique.values(), key=lambda f: (f.path, f.line, f.rule, f.message)
        )


@dataclass
class Ref:
    """A link, image or reference use found in a page body."""

    kind: str  # "link", "image" or "undef" (a reference with no definition)
    line: int  # 1-based file line
    target: str
    text: str | None  # link text or alt text; None for an HTML image without alt
    check: bool = True  # False for a use of a reference-style definition


@dataclass
class Item:
    """A prompt or script found under prompts/ or scripts/."""

    kind: str
    id: str
    code: str
    rel: str


@dataclass
class Term:
    """One active line of the private list. It is never printed."""

    number: int
    needle: str = ""
    pattern: re.Pattern[str] | None = None

    def matches(self, line: str) -> bool:
        if self.pattern is not None:
            return self.pattern.search(line) is not None
        return self.needle in line.casefold()


@dataclass
class Site:
    """What every rule shares: the root, the pages, caches and the findings."""

    root: Path
    pages: list[sitelib.Page]
    report: Report = field(default_factory=Report)
    by_rel: dict[str, sitelib.Page] = field(default_factory=dict)
    linked: dict[str, set[str]] = field(default_factory=dict)
    script_rels: set[str] = field(default_factory=set)
    _entries: dict[str, frozenset[str]] = field(default_factory=dict)
    _anchors: dict[str, tuple[list[sitelib.Heading], set[str]]] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.by_rel = {page.rel: page for page in self.pages}

    def names(self, rel_dir: str) -> frozenset[str]:
        """Exact directory entries, so lookups are case-sensitive on every OS."""
        if rel_dir not in self._entries:
            try:
                found = frozenset(os.listdir(self.root / rel_dir))
            except OSError:
                found = frozenset()
            self._entries[rel_dir] = found
        return self._entries[rel_dir]

    def lookup(self, rel: str) -> tuple[str, str]:
        """("ok", ""), ("case", real name) or ("missing", "") for a POSIX path."""
        current = ""
        for part in filter(None, rel.split("/")):
            entries = self.names(current)
            if part not in entries:
                same = sorted(n for n in entries if n.casefold() == part.casefold())
                return ("case", same[0]) if same else ("missing", "")
            current = f"{current}/{part}" if current else part
        return "ok", ""

    def anchors(self, page: sitelib.Page) -> tuple[list[sitelib.Heading], set[str]]:
        if page.rel not in self._anchors:
            masked = sitelib.mask_code(page.body)
            ids = {a or b for a, b in _HTML_ID.findall(masked)}
            self._anchors[page.rel] = (sitelib.find_headings(page.body), ids)
        return self._anchors[page.rel]


def _line(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


_NOT_NEWLINE = re.compile(r"[^\n]")


def _blank(text: str) -> str:
    return _NOT_NEWLINE.sub(" ", text)


def _words(text: str) -> int:
    return sum(1 for token in text.split() if any(c.isalnum() for c in token))


def _is_generated(page: sitelib.Page) -> bool:
    return page.front.get("generated") is True


# ---- R01 front matter, R02 titles, R03 nav_order ---------------------------
_STR_KEYS = frozenset(
    "title parent grand_parent status last_reviewed stage sub_stage layout "
    "permalink".split()
)
_BOOL_KEYS = frozenset("has_children nav_exclude has_toc generated".split())
_LIST_KEYS = frozenset("prompts scripts".split())
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _type_problem(key: str, value: Any) -> str | None:
    if key in _STR_KEYS and not isinstance(value, str):
        return "must be a double-quoted string"
    if key in _BOOL_KEYS and not isinstance(value, bool):
        return "must be true or false"
    if key in _LIST_KEYS and not isinstance(value, list):
        return "must be an inline list"
    return None


def _valid_date(text: str) -> bool:
    if not _DATE_RE.fullmatch(text):
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def check_front(site: Site, page: sitelib.Page) -> None:
    rep, rel, front = site.report, page.rel, page.front

    def at(key: str) -> int:
        return page.key_lines.get(key, 1)

    for number, message in page.errors:
        rep.error(rel, number, "R01", message)
    for key in sitelib.unknown_keys(front, sitelib.PAGE_KEYS):
        rep.warn(rel, at(key), "R01", f"unknown key '{key}'; check the spelling")
    for key, value in front.items():
        problem = _type_problem(key, value)
        if problem:
            rep.error(rel, at(key), "R01", f"'{key}' {problem}")
    title = front.get("title")
    if isinstance(title, str) and (not title.strip() or set("&<>") & set(title)):
        rep.error(rel, at("title"), "R01", "title is empty or holds & < >; write 'and'")
    if front.get("generated") is False:
        rep.error(rel, at("generated"), "R01", "'generated' must be true or omitted")
    if page.errors:
        return  # a missing key may be a malformed one; report it after the fix
    generated = _is_generated(page)
    required = ["title"]
    if not generated:
        required += ["status", "last_reviewed"]
        if front.get("nav_exclude") is not True:
            required.append("nav_order")
    for key in required:
        if key not in front:
            hint = " (or set nav_exclude: true)" if key == "nav_order" else ""
            rep.error(rel, 1, "R01", f"missing required key '{key}'{hint}")
    status = front.get("status")
    if isinstance(status, str) and status not in sitelib.STATUS_VALUES:
        allowed = ", ".join(sitelib.STATUS_VALUES)
        rep.error(rel, at("status"), "R01", f"status must be one of {allowed}")
    reviewed = front.get("last_reviewed")
    if isinstance(reviewed, str) and not _valid_date(reviewed):
        rep.error(rel, at("last_reviewed"), "R01", "last_reviewed must be YYYY-MM-DD")


def check_titles(site: Site) -> None:
    """R02: unique titles, resolvable parent and grand_parent."""
    rep = site.report
    titles: dict[str, list[sitelib.Page]] = defaultdict(list)
    for page in site.pages:
        title = page.front.get("title")
        if isinstance(title, str) and title:
            titles[title].append(page)
    for title, group in titles.items():
        for page in group[1:]:
            line = page.key_lines.get("title", 1)
            msg = f"title '{title}' is also used by {group[0].rel}; titles are unique"
            rep.error(page.rel, line, "R02", msg)
    for page in site.pages:
        _check_parents(site, page, titles)


def _check_parents(
    site: Site, page: sitelib.Page, titles: Mapping[str, list[sitelib.Page]]
) -> None:
    rep, rel, front = site.report, page.rel, page.front
    parent, grand = front.get("parent"), front.get("grand_parent")
    if front.get("has_children") is False:
        line = page.key_lines.get("has_children", 1)
        rep.error(rel, line, "R02", "has_children: false hides the children; remove it")
    grand = grand if isinstance(grand, str) else None
    if not isinstance(parent, str):
        if grand is not None:
            line = page.key_lines.get("grand_parent", 1)
            rep.error(rel, line, "R02", "grand_parent is set but parent is not")
        return
    line = page.key_lines.get("parent", 1)
    if parent == front.get("title"):
        rep.error(rel, line, "R02", "a page cannot be its own parent")
    elif parent not in titles:
        msg = f"parent '{parent}' matches no page title; the page would vanish"
        rep.error(rel, line, "R02", msg)
    else:
        above = {p.front.get("parent") for p in titles[parent]}
        above = {a for a in above if a is None or isinstance(a, str)}
        gline = page.key_lines.get("grand_parent", line)
        if grand is None and None not in above:
            msg = f"parent '{parent}' is nested, so this page needs a grand_parent"
            rep.error(rel, line, "R02", msg)
        elif grand is not None and grand not in above:
            msg = f"grand_parent '{grand}' is not the parent of '{parent}'"
            rep.error(rel, gline, "R02", msg)


def check_nav_order(site: Site) -> None:
    """R03: nav_order is an integer and unique among siblings."""
    rep = site.report
    seen: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    for page in site.pages:
        front = page.front
        if "nav_order" not in front:
            continue
        value, line = front["nav_order"], page.key_lines.get("nav_order", 1)
        if isinstance(value, bool) or not isinstance(value, int):
            rep.error(page.rel, line, "R03", "nav_order must be an integer")
            continue
        group = (str(front.get("grand_parent", "")), str(front.get("parent", "")))
        if value in seen[group]:
            msg = f"nav_order {value} is already used by sibling {seen[group][value]}"
            rep.error(page.rel, line, "R03", msg)
        else:
            seen[group][value] = page.rel


# ---- R04 R04a R05 R06 links, images and anchors ----------------------------
_TEXT = r"((?:\\.|[^\[\]\\]|\[(?:\\.|[^\[\]\\])*\])*)"  # one level of nesting
_INLINE = re.compile(r"(!?)\[" + _TEXT + r"\]\(", re.S)
_REFERENCE = re.compile(r"(!?)\[" + _TEXT + r"\]\[([^\]\n]*)\]", re.S)
_DEFINITION = re.compile(
    r"^ {0,3}\[([^\]\n]+)\]:[ \t]*(<[^>\n]*>|\S+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?[ \t]*$",
    re.M,
)
_HTML_LINK = re.compile(r"<a\b([^>]*)>(.*?)</a\s*>", re.I | re.S)
_HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.I)
_HTML_ID = re.compile(r"""(?<![\w-])(?:id|name)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
_TITLE = re.compile(
    r"""[ \t\n]+(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^)\\])*\))"""
)
_ESCAPED = re.compile(r"\\([!-/:-@\[-`{-~])")
_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
_UNCERTAIN = re.compile(r"`|&#?\w+;|--|\.\.\.|[^\x00-\x7f]")


def _label(text: str) -> str:
    return " ".join(text.split()).casefold()


def _attribute(tag: str, name: str) -> str | None:
    pattern = rf"""(?<![\w-]){name}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))"""
    match = re.search(pattern, tag, re.I | re.S)
    if match is None:
        return None
    return next(group for group in match.groups() if group is not None)


def _parse_destination(text: str, start: int) -> str | None:
    """Read 'target "title")' after '](' ; None when it is not a link."""
    size, i = len(text), start
    while i < size and text[i] in " \t\n":
        i += 1
    if i < size and text[i] == "<":
        end = text.find(">", i)
        if end < 0 or "\n" in text[i:end]:
            return None
        target, i = text[i + 1 : end], end + 1
    else:
        depth, j = 0, i
        while j < size and text[j] not in " \t\n":
            char = text[j]
            if char == "\\":
                j += 2
                continue
            if text.startswith(("{{", "{%"), j):  # Liquid runs before Markdown
                closer = "}}" if text[j + 1] == "{" else "%}"
                end = text.find(closer, j + 2)
                if end >= 0:
                    j = end + 2
                    continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            j += 1
        target, i = text[i:j], j
    title = _TITLE.match(text, i)
    if title:
        i = title.end()
    while i < size and text[i] in " \t\n":
        i += 1
    if i >= size or text[i] != ")":
        return None
    return _ESCAPED.sub(r"\1", target)


def extract_refs(page: sitelib.Page) -> list[Ref]:
    """Links, images and references in the masked body, with file line numbers."""
    raw, offset = page.body, page.body_line_offset
    masked = sitelib.mask_code(raw)

    def at(pos: int) -> int:
        return offset + _line(masked, pos)

    refs: list[Ref] = []
    defined: dict[str, str] = {}
    for m in _DEFINITION.finditer(masked):
        label = _label(m.group(1))
        target = m.group(2)
        if label.startswith("^"):
            continue
        if target.startswith("<"):
            target = target[1:-1]
        defined.setdefault(label, target)
        refs.append(Ref("link", at(m.start()), target, ""))

    def inline(start: int, end: int) -> None:
        """Inline links and images in masked[start:end]; nested ones too."""
        for found in _INLINE.finditer(masked, start, end):
            target_text = _parse_destination(masked, found.end())
            if target_text is None:
                continue
            kind = "image" if found.group(1) else "link"
            text = raw[found.start(2) : found.end(2)]
            refs.append(Ref(kind, at(found.start()), target_text, text))
            if "[" in text:
                inline(found.start(2), found.end(2))

    inline(0, len(masked))
    for m in _REFERENCE.finditer(masked):
        label = _label(m.group(3) or m.group(2))
        if label.startswith("^"):
            continue
        kind = "image" if m.group(1) else "link"
        text = raw[m.start(2) : m.end(2)]
        if label in defined:
            refs.append(Ref(kind, at(m.start()), defined[label], text, False))
        else:
            refs.append(Ref("undef", at(m.start()), label, text))
    for m in _HTML_LINK.finditer(masked):
        href = _attribute(m.group(1), "href")
        if href is not None:
            inner = re.sub(r"<[^>]*>", "", raw[m.start(2) : m.end(2)])
            refs.append(Ref("link", at(m.start()), html.unescape(href), inner))
    for m in _HTML_IMAGE.finditer(masked):
        src = _attribute(m.group(), "src") or ""
        alt = _attribute(m.group(), "alt")
        refs.append(Ref("image", at(m.start()), html.unescape(src), alt))
    return refs


def _normalize(page_rel: str, path: str) -> str | None:
    """Lexically resolve a relative path against the page; None leaves the root."""
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(page_rel), path))
    if joined == ".." or joined.startswith("../"):
        return None
    return "" if joined == "." else joined


def _variants(heading: sitelib.Heading) -> set[str]:
    """Ids other readings of the Markdown engine could give this heading."""
    base = sitelib.kramdown_slug(heading.text)
    suffix = heading.id[len(base) :] if heading.id.startswith(base) else ""
    text = heading.text
    readings = (
        re.sub(r"`[^`]*`", "", text),
        html.unescape(text),
        re.sub(r"&#?\w+;", "", text),
        text.replace("--", "\u2013").replace("...", "\u2026"),
        "".join(c for c in unicodedata.normalize("NFKD", text) if ord(c) < 128),
    )
    return {sitelib.kramdown_slug(reading) + suffix for reading in readings}


def _anchor_problem(
    headings: list[sitelib.Heading], html_ids: set[str], fragment: str
) -> tuple[str, str] | None:
    """(severity, message) when the anchor is wrong or uncertain, else None."""
    if fragment in html_ids:
        return None
    uncertain = [h for h in headings if not h.explicit and _UNCERTAIN.search(h.text)]
    for heading in headings:
        if heading.id == fragment:
            if heading in uncertain and _variants(heading) - {heading.id}:
                msg = f"heading '{heading.text}' has an id that may differ on the site"
                return sitelib.WARNING, f"{msg}; add an explicit {{#id}}"
            return None
    for heading in uncertain:
        if fragment in _variants(heading):
            msg = f"anchor '#{fragment}' matches heading '{heading.text}' only under "
            return (
                sitelib.WARNING,
                msg + "another reading of its id; add an explicit {#id}",
            )
    return sitelib.ERROR, f"no heading has the id '{fragment}'"


def _check_anchor(
    site: Site, source: sitelib.Page, target: sitelib.Page, fragment: str, line: int
) -> None:
    if not fragment:
        return
    headings, html_ids = site.anchors(target)
    problem = _anchor_problem(headings, html_ids, fragment)
    if problem is None:
        return
    severity, message = problem
    where = "" if target is source else f" in {target.rel}"
    finding = sitelib.Finding(source.rel, line, "R04a", severity, message + where)
    site.report.items.append(finding)


def _check_target(site: Site, page: sitelib.Page, ref: Ref) -> None:
    rep, rel, target = site.report, page.rel, ref.target
    image = ref.kind == "image"
    missing_rule = "R06" if image else "R04"
    if not target.strip():
        rep.error(rel, ref.line, missing_rule, "empty link target")
        return
    if "{{" in target or "{%" in target or target.startswith("//"):
        return
    if _SCHEME.match(target):
        return
    if target.startswith("/"):
        msg = f"root-relative target '{target}' breaks under a base path; "
        rep.error(rel, ref.line, "R04", msg + "use a relative link or relative_url")
        return
    path, _, fragment = target.partition("#")
    path, fragment = unquote(path.partition("?")[0]), unquote(fragment)
    if not path:
        _check_anchor(site, page, page, fragment, ref.line)
        return
    resolved = _normalize(rel, path)
    if resolved is None:
        rep.error(
            rel, ref.line, missing_rule, f"target '{target}' leaves the repository"
        )
        return
    site.linked[rel].add(resolved)
    state, actual = site.lookup(resolved)
    if state == "missing":
        rep.error(rel, ref.line, missing_rule, f"target '{target}' does not exist")
    elif state == "case":
        msg = f"target '{target}' differs in letter case from the file name '{actual}'"
        rep.error(rel, ref.line, missing_rule, msg)
    elif resolved != "docs" and not resolved.startswith("docs/"):
        msg = f"target '{target}' is outside docs/; link to the site page instead"
        rep.error(rel, ref.line, "R05", msg)
    elif fragment and resolved in site.by_rel:
        _check_anchor(site, page, site.by_rel[resolved], fragment, ref.line)


def check_refs(site: Site, page: sitelib.Page, refs: list[Ref]) -> None:
    rep = site.report
    site.linked.setdefault(page.rel, set())
    for ref in refs:
        if ref.kind == "undef":
            msg = f"link reference [{ref.target}] has no definition"
            rep.error(page.rel, ref.line, "R04", msg)
            continue
        if ref.kind == "image" and not (ref.text or "").strip():
            msg = "image has no alt text; describe it, and do not add decorative images"
            rep.error(page.rel, ref.line, "R06", msg)
        if ref.check:
            _check_target(site, page, ref)


# ---- R16 Liquid ------------------------------------------------------------
_RAW_TAG = re.compile(r"\{%-?\s*(raw|endraw)\s*-?%\}")
_ALLOWED_LIQUID = re.compile(
    r"""\{\{\s*(?:'[^'\n]*'|"[^"\n]*")\s*\|\s*relative_url\s*\}\}"""
    r"|\{%-?\s*link\s+[^%\n]+?\s*-?%\}"
)
_LIQUID = re.compile(r"\{\{|\{%")


def strip_raw(text: str) -> tuple[str, list[tuple[int, str]]]:
    """Blank raw blocks (newlines kept); return the text and tag problems."""
    segments: list[str] = []
    problems: list[tuple[int, str]] = []
    pos, opened = 0, None
    for m in _RAW_TAG.finditer(text):
        is_raw = m.group(1) == "raw"
        if opened is None and is_raw:
            segments.append(text[pos : m.start()])
            opened = m.start()
        elif opened is None:
            problems.append((_line(text, m.start()), "endraw has no matching raw"))
        elif not is_raw:
            segments.append(_blank(text[opened : m.end()]))
            pos, opened = m.end(), None
    if opened is not None:
        problems.append((_line(text, opened), "raw block is never closed by endraw"))
        segments.append(_blank(text[opened:]))
        pos = len(text)
    segments.append(text[pos:])
    return "".join(segments), problems


def check_liquid(site: Site, page: sitelib.Page) -> None:
    rep, offset = site.report, page.body_line_offset
    text, problems = strip_raw(page.body)
    for number, message in problems:
        rep.error(page.rel, offset + number, "R16", message)
    text = _ALLOWED_LIQUID.sub(lambda m: _blank(m.group()), text)
    lines = {_line(text, m.start()) for m in _LIQUID.finditer(text)}
    for number in sorted(lines):
        msg = "Liquid delimiter outside a raw block; wrap it in a raw block"
        rep.error(page.rel, offset + number, "R16", msg)


# ---- R07 R08 R09 prompt and script sources ---------------------------------
_ID_SHAPE = {
    "prompt": re.compile(r"P-(S[1-5]|CA|DL|OP)-[0-9]{2}"),
    "script": re.compile(r"X-(S[1-5]|CA|DL|OP)-[0-9]{2}"),
}
_SLUG = re.compile(r"[a-z0-9_-]+")
_PAIR = tuple[str, int]


def _library_files(root: Path, kind: str) -> list[tuple[Path, str]]:
    """(path, folder) for prompts/<code>/*.md, scripts/<code>/*.py|*.sh, common."""
    codes = {code.lower() for code in sitelib.STAGES}
    base = root / kind
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return []
    folders = [n for n in entries if n in codes and (base / n).is_dir()]
    if kind == "scripts" and (base / "common").is_dir():
        folders.append("common")
    suffixes = (".md",) if kind == "prompts" else (".py", ".sh")
    found = []
    for folder in folders:
        allowed = (".py",) if folder == "common" else suffixes
        for name in sorted(os.listdir(base / folder)):
            path = base / folder / name
            ignored = name.startswith(("_", "test_")) or name.casefold() == "readme.md"
            if ignored or path.suffix not in allowed:
                continue
            if path.is_file():
                found.append((path, folder))
    return found


def _check_identity(
    site: Site,
    rel: str,
    kind: str,
    folder: str,
    fields: tuple[_PAIR | None, _PAIR | None, _PAIR | None],
    registry: dict[str, Item],
) -> None:
    """R07 for one source: fields are the (value, line) of ID, stage, sub_stage."""
    rep = site.report
    ident, stage, sub = fields
    stem = Path(rel).stem
    if not _SLUG.fullmatch(stem):
        msg = f"file name '{stem}' must be a slug of a-z, 0-9, '-' and '_'"
        rep.error(rel, 1, "R07", msg)
    expected = "OP" if folder == "common" else folder.upper()
    code = None
    if ident is not None:
        value, line = ident
        match = _ID_SHAPE[kind].fullmatch(value)
        if match is None:
            shape = "P-S1-04" if kind == "prompt" else "X-S1-04"
            rep.error(rel, line, "R07", f"ID '{value}' must look like {shape}")
        else:
            code = match.group(1)
            if code != expected:
                msg = f"ID code {code} does not match the folder '{folder}'"
                rep.error(rel, line, "R07", msg)
            if value in registry:
                msg = f"duplicate ID {value}; also used by {registry[value].rel}"
                rep.error(rel, line, "R07", msg)
            else:
                registry[value] = Item(kind, value, code, rel)
    reference = code or expected
    if stage is not None:
        value, line = stage
        if value not in sitelib.STAGES:
            rep.error(rel, line, "R07", f"stage '{value}' is not a stage code")
        elif value != reference:
            msg = f"stage {value} does not match the {'ID code' if code else 'folder'}"
            rep.error(rel, line, "R07", f"{msg} {reference}")
    if sub is not None:
        value, line = sub
        split = sitelib.split_id(value)
        if split is None or split[0] or not split[2] or split[1] != reference:
            msg = (
                f"sub_stage '{value}' must look like {reference}.4a and match the stage"
            )
            rep.error(rel, line, "R07", msg)


def _pair(front: Mapping[str, Any], lines: Mapping[str, int], key: str) -> _PAIR | None:
    value = front.get(key)
    return (value, lines.get(key, 1)) if isinstance(value, str) else None


def _check_prompt(
    site: Site, path: Path, folder: str, registry: dict[str, Item]
) -> None:
    rel = path.relative_to(site.root).as_posix()
    doc = _guard(rel, functools.partial(sitelib.parse_prompt, path))
    for number, message in doc.errors:
        site.report.error(rel, number, "R08", message)
    known = sitelib.PROMPT_REQUIRED + sitelib.PROMPT_OPTIONAL
    for key in sitelib.unknown_keys(doc.front, known):
        msg = f"unknown key '{key}'"
        site.report.warn(rel, doc.key_lines.get(key, 1), "R08", msg)
    fields = (
        _pair(doc.front, doc.key_lines, "id"),
        _pair(doc.front, doc.key_lines, "stage"),
        _pair(doc.front, doc.key_lines, "sub_stage"),
    )
    _check_identity(site, rel, "prompt", folder, fields, registry)


def _check_script(
    site: Site, path: Path, folder: str, registry: dict[str, Item], common: list[str]
) -> None:
    rel = path.relative_to(site.root).as_posix()
    site.script_rels.add(rel)
    header = _guard(rel, functools.partial(sitelib.parse_script_header, path, common))
    for number, message in header.errors:
        site.report.error(rel, number, "R09", message)
    text = _guard(rel, functools.partial(sitelib.read_text, path))
    for number, line in enumerate(text.split("\n"), 1):
        if any(pattern.search(line) for pattern in sitelib.SECRET_PATTERNS):
            msg = "key or token pattern; keys come only from environment variables"
            site.report.error(rel, number, "R09", msg)
    lines = header.key_lines

    def field_pair(name: str) -> _PAIR | None:
        value = header.fields.get(name)
        return (value, lines.get(name, 1)) if value else None

    fields = (field_pair("ID"), field_pair("Stage"), None)
    _check_identity(site, rel, "script", folder, fields, registry)


def check_library(site: Site) -> tuple[dict[str, Item], dict[str, Item]]:
    """R07 to R09 for prompts and scripts; returns the ID registries."""
    prompts: dict[str, Item] = {}
    scripts: dict[str, Item] = {}
    common = sitelib.common_modules(site.root)
    for path, folder in _library_files(site.root, "prompts"):
        _check_prompt(site, path, folder, prompts)
    for path, folder in _library_files(site.root, "scripts"):
        _check_script(site, path, folder, scripts, common)
    return prompts, scripts


def check_stage_fields(
    site: Site,
    page: sitelib.Page,
    registries: tuple[dict[str, Item], dict[str, Item]],
) -> None:
    """R07 for a page's stage, sub_stage and listed IDs; R21 missing links."""
    rep, rel, front = site.report, page.rel, page.front
    lines = page.key_lines
    stage, sub = front.get("stage"), front.get("sub_stage")
    if isinstance(stage, str) and stage not in sitelib.STAGES:
        rep.error(rel, lines["stage"], "R07", f"stage '{stage}' is not a stage code")
    if isinstance(sub, str):
        split = sitelib.split_id(sub)
        if split is None or split[0] or not split[2]:
            msg = f"sub_stage '{sub}' must look like S1.4a"
            rep.error(rel, lines["sub_stage"], "R07", msg)
        elif split[1] != stage:
            msg = f"sub_stage {sub} does not match the stage of this page"
            rep.error(rel, lines["sub_stage"], "R07", msg)
    for key, registry, kind in (
        ("prompts", registries[0], "prompt"),
        ("scripts", registries[1], "script"),
    ):
        ids = front.get(key)
        for ident in ids if isinstance(ids, list) else []:
            item = registry.get(ident)
            if item is None:
                msg = f"lists {ident}, but no {kind} file has that ID"
                rep.error(rel, lines[key], "R07", msg)
            elif isinstance(stage, str) and item.code not in (stage, "OP"):
                msg = f"lists {ident} of stage {item.code}; this page is stage {stage}"
                rep.error(rel, lines[key], "R07", msg)
            elif not _is_generated(page):
                target = f"docs/{key}/{item.code.lower()}/{ident.lower()}.md"
                if target not in site.linked.get(rel, set()):
                    msg = f"lists {ident} but does not link to {target}"
                    rep.warn(rel, lines[key], "R21", msg)


# ---- R12 to R15, R19 to R21 style warnings ---------------------------------
_MARKER = re.compile(r"\b(?:TODO|FIXME)\b")
_LIST_ITEM = re.compile(r"(?:[-*+]|[0-9]+[.)])[ \t]+")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_MD_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


def _plain(text: str) -> str:
    return re.sub(r"[\s*_`.,:;!]+", " ", text).strip().casefold()


def _sentences(masked: str) -> list[tuple[int, str]]:
    """(body line, sentence) for prose; headings, tables, HTML and code skipped."""
    paragraphs: list[tuple[int, list[str]]] = []
    current: list[str] | None = None
    for number, raw in enumerate(masked.split("\n"), 1):
        line = raw.strip().removeprefix(">").strip()
        if not line or line.startswith(("#", "|", "<")):
            current = None
            continue
        item = _LIST_ITEM.match(line)
        if item or current is None:
            current = []
            paragraphs.append((number, current))
        current.append(line[item.end() :] if item else line)
    found = []
    for number, parts in paragraphs:
        text = _MD_LINK.sub(r"\1", " ".join(parts)).replace("*", " ")
        found += [(number, s) for s in _SENTENCE_END.split(text) if s.strip()]
    return found


def _style_headings(site: Site, page: sitelib.Page) -> list[sitelib.Heading]:
    rep, rel, offset = site.report, page.rel, page.body_line_offset
    headings = sitelib.find_headings(page.body)
    previous: int | None = None
    ones = [h for h in headings if h.level == 1]
    for heading in headings:
        if previous is not None and heading.level > previous + 1:
            msg = f"heading level jumps from H{previous} to H{heading.level}"
            rep.warn(rel, offset + heading.line, "R12", msg)
        previous = heading.level
    for heading in ones[1:]:
        msg = "more than one H1; a page has a single H1"
        rep.warn(rel, offset + heading.line, "R12", msg)
    seen: dict[str, int] = {}
    for heading in headings:
        key = " ".join(heading.text.split()).casefold()
        if key in seen:
            msg = f"heading '{heading.text}' repeats the heading on line {seen[key]}"
            rep.warn(rel, offset + heading.line, "R20", msg)
        else:
            seen[key] = offset + heading.line
    return headings


def _style_sections(
    site: Site, page: sitelib.Page, headings: list[sitelib.Heading]
) -> None:
    """R21: template sections of a stage page appear in the template order."""
    if "stage" not in page.front or "sub_stage" not in page.front:
        return
    order = [name.casefold() for name in SECTIONS]
    highest = -1
    for heading in headings:
        name = " ".join(heading.text.split()).casefold()
        if heading.level != 2 or name not in order:
            continue
        index = order.index(name)
        if index < highest:
            msg = f"section '{heading.text}' is out of order; the template order is "
            line = page.body_line_offset + heading.line
            site.report.warn(page.rel, line, "R21", msg + ", ".join(SECTIONS))
        else:
            highest = index


def check_style(site: Site, page: sitelib.Page, refs: list[Ref]) -> None:
    rep, rel, offset = site.report, page.rel, page.body_line_offset
    body = page.body
    headings = _style_headings(site, page)
    for fence in sitelib.find_fences(body):
        if not fence.lang:
            msg = "code fence has no language; use text when none applies"
            rep.warn(rel, offset + fence.line, "R13", msg)
    for ref in refs:
        if ref.kind == "link" and _plain(ref.text or "") in ("here", "click here"):
            rep.warn(
                rel, ref.line, "R13", "link text says where the link goes, not here"
            )
    words = _words(body)
    if words > MAX_WORDS:
        rep.warn(rel, 1, "R14", f"page has {words} words; keep it under {MAX_WORDS}")
    sentences = _sentences(sitelib.mask_code(body))
    overlong = [(n, s) for n, s in sentences if len(s.split()) > LONG_SENTENCE]
    if sentences and len(overlong) / len(sentences) > LONG_SHARE:
        msg = f"advisory: {len(overlong)} of {len(sentences)} sentences run over "
        rep.warn(rel, offset + overlong[0][0], "R14", msg + f"{LONG_SENTENCE} words")
    if page.front.get("status") != "draft":
        for number, line in enumerate(body.split("\n"), 1):
            if _MARKER.search(line):
                msg = "unfinished-work marker in a page that is not a draft"
                rep.warn(rel, offset + number, "R15", msg)
    if words < MIN_WORDS:
        rep.warn(
            rel, 1, "R19", f"page has {words} body words; write at least {MIN_WORDS}"
        )
    if not any(h.level == 1 for h in headings):
        rep.warn(rel, 1, "R19", "page has no H1 heading")
    _style_sections(site, page, headings)


# ---- R10 R17 R18 text sources ----------------------------------------------
_PUBLIC = (
    ("macOS user folder path", re.compile(re.escape("/Us" + "ers/"))),
    ("Linux home folder path", re.compile(re.escape("/ho" + "me/"))),
    ("Windows user folder path", re.compile(r"[A-Za-z]:\\{1,2}Users\\")),
    ("file URL", re.compile(re.escape("file:" + "///"))),
)
_LOCAL_CHAR = re.compile(r"[\w.%+-]")
_NEWLINE = re.compile(rb"\r\n|\r|\n")


def emails(line: str) -> list[str]:
    """Email addresses, found around each '@' so a very long line stays fast."""
    found = []
    at = line.find("@")
    while at >= 0:
        start = at
        while start > 0 and _LOCAL_CHAR.fullmatch(line[start - 1]):
            start -= 1
        match = sitelib.EMAIL_RE.match(line, start) if start < at else None
        if match and match.end() > at:
            found.append(match.group())
        at = line.find("@", at + 1)
    return found


def public_hits(line: str, secrets: bool) -> list[str]:
    """Categories only; the matched text is never returned."""
    hits = [label for label, pattern in _PUBLIC if pattern.search(line)]
    if any(not sitelib.email_allowed(address) for address in emails(line)):
        hits.append("email address outside the reserved example domains")
    if secrets and any(p.search(line) for p in sitelib.SECRET_PATTERNS):
        hits.append("key or token pattern")
    return hits


def load_terms(path: Path, origin: str) -> list[Term]:
    """Read the private list. Errors never quote a term."""
    text = _guard(
        f"the private term list ({origin})", functools.partial(sitelib.read_text, path)
    )
    terms: list[Term] = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        number = len(terms) + 1
        if not line.lower().startswith("re:"):
            terms.append(Term(number, needle=line.casefold()))
            continue
        try:
            pattern = re.compile(line[3:], re.I)
        except re.error as exc:
            raise InputError(
                f"private term #{number} is not a valid regex: {exc.msg}"
            ) from None
        if pattern.search(""):
            raise InputError(
                f"private term #{number} is a regex that matches empty text"
            )
        terms.append(Term(number, pattern=pattern))
    return terms


def _text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for sub in SCAN_DIRS:
        files += sitelib.walk_files(root, sub, TEXT_SUFFIXES, SKIP_DIRS.__contains__)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def _first_cr_line(path: Path) -> int:
    data = path.read_bytes()
    index = data.find(b"\r")
    return len(_NEWLINE.findall(data[:index])) + 1 if index >= 0 else 1


def check_text_files(site: Site, terms: list[Term]) -> None:
    """R17 for every text source; R10 for all but this tool and the tests."""
    rep = site.report
    for path in _text_files(site.root):
        rel = path.relative_to(site.root).as_posix()
        if path.is_symlink():
            continue  # R18 reports symlinks; never read through them
        hazards = _guard(rel, functools.partial(sitelib.text_hazards, path))
        cr_line = _first_cr_line(path) if hazards else 1
        for message in hazards:
            line = 1 if "byte order mark" in message else cr_line
            rep.error(rel, line, "R17", message)
        if rel == SELF_REL or rel.startswith(TESTS_PREFIX):
            continue
        text = _guard(rel, functools.partial(sitelib.read_text, path))
        secrets = rel not in site.script_rels
        for number, line_text in enumerate(text.split("\n"), 1):
            for label in public_hits(line_text, secrets):
                rep.error(rel, number, "R10", f"{label}; remove it")
            for term in terms:
                if term.matches(line_text):
                    rep.error(rel, number, "R10", f"private-term #{term.number}")


def casefold_clashes(names: list[str]) -> list[tuple[str, list[str]]]:
    """Groups of names that are equal once letter case is ignored."""
    groups: dict[str, list[str]] = defaultdict(list)
    for name in sorted(names):
        groups[name.casefold()].append(name)
    return [(key, group) for key, group in sorted(groups.items()) if len(group) > 1]


def check_docs_tree(site: Site) -> None:
    """R18: symlinks and names that differ only by case under docs/."""
    rep, root = site.report, site.root
    for base, dirnames, filenames in os.walk(root / "docs"):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        folder = Path(base)
        names = sorted(dirnames + filenames)
        for name in names:
            if (folder / name).is_symlink():
                rel = (folder / name).relative_to(root).as_posix()
                rep.error(
                    rel, 1, "R18", "symlink; symlinks are not allowed under docs/"
                )
        for _, group in casefold_clashes(names):
            for name in group:
                rel = (folder / name).relative_to(root).as_posix()
                others = ", ".join(n for n in group if n != name)
                rep.error(
                    rel, 1, "R18", f"name differs only by letter case from {others}"
                )


# ---- R22 includes ----------------------------------------------------------
_URL_ATTRIBUTE = re.compile(
    r"""(?<![\w-])(?:src|href)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", re.I
)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def check_includes(site: Site) -> None:
    for path in sitelib.walk_files(site.root, "docs/_includes", (".html",)):
        rel = path.relative_to(site.root).as_posix()
        text = _guard(rel, functools.partial(sitelib.read_text, path))
        text = _HTML_COMMENT.sub(lambda m: _blank(m.group()), text)
        for m in _URL_ATTRIBUTE.finditer(text):
            value = next(g for g in m.groups() if g is not None)
            if value.startswith("/") and not value.startswith("//"):
                if "relative_url" not in value:
                    msg = "root-relative src or href without the relative_url filter"
                    site.report.error(rel, _line(text, m.start()), "R22", msg)


# ---- R11 generated files ---------------------------------------------------
def _import_sync() -> Any:
    if str(SITE_DIR) not in sys.path:
        sys.path.insert(0, str(SITE_DIR))
    return importlib.import_module("sync")


def check_generated(site: Site) -> None:
    """R11: generated files equal sync.compute_outputs(root); extras are stale."""
    rep, root = site.report, site.root
    sync_rel = "scripts/site/sync.py"
    try:
        outputs = _import_sync().compute_outputs(root)
    except (Exception, SystemExit) as exc:  # pylint: disable=broad-exception-caught
        issues = getattr(exc, "issues", None)
        if isinstance(issues, list) and issues:
            # sync names the file that is wrong ("path: message"); report it there.
            for issue in issues[:5]:
                where, _sep, message = str(issue).partition(": ")
                text = f"cannot generate pages: {message or where}"
                rep.error(where if message else sync_rel, 1, "R11", text)
            return
        why = (str(exc).splitlines() or [""])[0][:160]
        rep.error(
            sync_rel, 1, "R11", f"cannot compute outputs: {type(exc).__name__} {why}"
        )
        return
    if not isinstance(outputs, Mapping):
        rep.error(sync_rel, 1, "R11", "compute_outputs did not return a mapping")
        return
    expected: dict[str, bytes] = {}
    for key, data in outputs.items():
        parts = key.split("/") if isinstance(key, str) else []
        inside = (
            any(key.startswith(d + "/") for d in GENERATED_DIRS) if parts else False
        )
        if not inside or not isinstance(data, bytes) or {"", ".", ".."} & set(parts):
            rep.error(sync_rel, 1, "R11", f"sync returned an unusable entry: {key!r}")
        else:
            expected[key] = data
    for key in sorted(expected):
        path = root / key
        try:
            actual = path.read_bytes() if path.is_file() else None
        except OSError:
            actual = None
        if actual is None:
            rep.error(key, 1, "R11", "generated file is missing; run sync.py --write")
        elif actual != expected[key]:
            rep.error(
                key,
                1,
                "R11",
                "generated file differs from sync output; run sync.py --write",
            )
    for sub in GENERATED_DIRS:
        for base, _dirs, files in os.walk(root / sub):
            for name in files:
                rel = (Path(base) / name).relative_to(root).as_posix()
                if rel not in expected:
                    rep.error(
                        rel,
                        1,
                        "R11",
                        "stale generated file; sync.py does not produce it",
                    )


# ---- orchestration and CLI -------------------------------------------------
def _load_pages(root: Path) -> list[sitelib.Page]:
    try:
        return sitelib.load_pages(root)
    except (OSError, UnicodeDecodeError) as exc:
        for path in sitelib.walk_files(root, "docs", (".md",)):
            rel = path.relative_to(root).as_posix()
            _guard(rel, functools.partial(sitelib.read_text, path))
        raise InputError(
            f"cannot read a page under docs/: {type(exc).__name__}"
        ) from exc


def run(
    root: Path, forbidden: Path | None = None, origin: str = "--extra-forbidden"
) -> list[sitelib.Finding]:
    """Run every rule against root; raises InputError for unreadable input."""
    root = Path(root)
    terms = load_terms(forbidden, origin) if forbidden is not None else []
    site = Site(root, _load_pages(root))
    registries = check_library(site)
    check_titles(site)
    check_nav_order(site)
    for page in site.pages:
        refs = extract_refs(page)
        check_front(site, page)
        check_refs(site, page, refs)
        check_liquid(site, page)
        check_stage_fields(site, page, registries)
        if not page.errors and not _is_generated(page):
            check_style(site, page, refs)
    check_text_files(site, terms)
    check_docs_tree(site)
    check_includes(site)
    check_generated(site)
    return site.report.result()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check.py",
        description="Check the docs, prompts and scripts against every site rule.",
        epilog="Exit codes: 0 no errors, 1 errors, 2 usage error or unreadable input.",
    )
    parser.add_argument(
        "--root", help="repository root (default: two levels above this file)"
    )
    parser.add_argument(
        "--extra-forbidden",
        metavar="FILE",
        help=f"private term list; {FORBIDDEN_ENV} is the fallback",
    )
    return parser


def main(
    argv: list[str] | None = None, environ: Mapping[str, str] | None = None
) -> int:
    args = build_parser().parse_args(argv)
    env = os.environ if environ is None else environ
    root = Path(args.root) if args.root else Path(__file__).resolve().parents[2]
    if not (root / "docs").is_dir():
        print(
            "check: --root must be a repository root that holds a docs folder",
            file=sys.stderr,
        )
        return 2
    forbidden, origin = None, "--extra-forbidden"
    if args.extra_forbidden is not None:
        forbidden = Path(args.extra_forbidden)
    elif env.get(FORBIDDEN_ENV):
        forbidden, origin = Path(env[FORBIDDEN_ENV]), FORBIDDEN_ENV
    else:
        print(NOTICE, file=sys.stderr)
    try:
        findings = run(root, forbidden, origin)
    except InputError as exc:
        print(f"check: {exc}", file=sys.stderr)
        return 2
    for finding in findings:
        print(finding)
    errors = sum(1 for f in findings if f.severity == sitelib.ERROR)
    print(f"check: {errors} errors, {len(findings) - errors} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
