"""Shared parsing helpers and constants for the rapid_upskill site tools.

License: CC0-1.0 (public domain dedication,
https://creativecommons.org/publicdomain/zero/1.0/).

Standard library only. Imported by sync.py and check.py. No git call, no clock,
and the repository is never derived from the current directory: functions that
walk the tree take ``root: Path``.

PUBLIC API (frozen; signatures are exact)
-----------------------------------------
Issue = tuple[int, str]                (1-based line, message); always an error
Finding(path: str, line: int, rule: str, severity: str, message: str)
    str(f) == "path:line RULE message"; severity is ERROR "E" or WARNING "W"
Page(path: Path, rel: str, front: dict, body: str, body_line_offset: int,
     errors: list[Issue] = [], key_lines: dict[str, int] = {})
    rel is POSIX and relative to root, e.g. "docs/index.md"
FrontMatter(front, body, body_line_offset, errors, key_lines)
PromptDoc(front, body, notes, placeholders_used, errors, key_lines={})
ScriptHeader(path, fields, key_lines, imports, non_stdlib, errors)
Fence(line, end_line, marker, info, closed, content, indent) with .lang
Heading(line, level, text, id, explicit)

Constants: ERROR, WARNING, STAGES, CAPABILITIES, PROMPT_REQUIRED,
PROMPT_OPTIONAL, PROMPT_KINDS, SCRIPT_REQUIRED, SCRIPT_OPTIONAL, PAGE_KEYS,
PAGE_THEME_KEYS, STATUS_VALUES, SECRET_PATTERNS (tuple of compiled regexes),
EMAIL_ALLOWLIST, EMAIL_RE. STAGES maps code -> (label, name), e.g.
"S1" -> ("Stage 1", "Knowledge acquisition"); index titles are f"{label}
prompts". For "OP" the label is the singular "Operating practice" (S7 index
titles) and the name is "Operating practices".

read_text(path: Path) -> str
    UTF-8, BOM stripped, CRLF and CR become LF. Raises OSError or
    UnicodeDecodeError; the CLIs map those to exit 2.
text_hazards(path: Path) -> list[str]           BOM or CR, byte level (R17)
parse_front_matter(text: str) -> (front, body, body_line_offset, errors)
    Body line k is file line k + body_line_offset. Without a valid block the
    result is ({}, text, 0, errors). Unknown keys are not errors here.
parse_front_matter_full(text: str) -> FrontMatter    same, plus key_lines
unknown_keys(front: dict, known: Iterable[str]) -> list[str]
email_allowed(address: str) -> bool                  EMAIL_ALLOWLIST test
find_fences(text: str) -> list[Fence]                lines are 1-based
mask_code(text: str, inline: bool = True) -> str
    Blanks fences, HTML comments and (if inline) code spans with spaces. Every
    newline stays, so line numbers and columns do not move.
kramdown_slug(text: str) -> str
find_headings(body: str) -> list[Heading]            ATX headings only
headings_ids(body: str) -> list[tuple[int, str, str]]      (line, text, id)
    Both mask fences and comments themselves; pass the RAW body so a heading
    that holds inline code keeps its code text.
parse_prompt(path: Path) -> PromptDoc
parse_script_header(path: Path, common: Iterable[str] = ()) -> ScriptHeader
non_stdlib_imports(tree: ast.AST, common: Iterable[str] = ()) -> list[str]
common_modules(root: Path) -> list[str]     stems of scripts/common + "common"
parse_dependencies(value: str) -> list[str]          "stdlib" gives []
split_id(id_str: str) -> (prefix, code, [(int, suffix), ...]) or None
id_sort_key(id_str: str) -> tuple                    ValueError if invalid
read_config_scalar(config_text: str, key: str) -> str | None
walk_files(root, subdir="", suffixes=None, skip_dir=None) -> list[Path]
load_pages(root: Path) -> list[Page]

CHOICES WHERE THE PLAN IS SILENT OR AMBIGUOUS
* S6 shows a 3-tuple for parse_front_matter; this module returns 4 (errors).
* Front matter: blank lines are ignored; comments, trailing comments, single
  quotes, indentation and block lists are errors. Only lowercase true/false are
  booleans (True, Yes, on, null, ~ are errors). Integers are 0 or
  -?[1-9][0-9]*; other bare numbers and dates are errors. Keys match
  [A-Za-z_][A-Za-z0-9_-]*. Escapes are \\" and \\\\ only. A trailing comma in a
  list is an error. Line 1 must be exactly "---".
* Errors are (line, message) pairs. Unknown-key warnings are the caller's job
  (unknown_keys) because pages, prompts and scripts differ.
* Fences may be indented; a backtick opener whose info string holds a backtick
  is inline code. Indented code blocks are not masked. A code span ends at a
  blank line. An unclosed fence or comment runs to the end of the text.
* Headings: ATX only. An empty slug stays empty. Duplicates count per base slug
  as kramdown counts them, so "a", "a", "a-1" repeats "a-1".
* Prompt: the only four-backtick fence tagged text, at column 1. Text before it
  is an error (it would not be published). Every {{...}} in it must be
  {{UPPER_SNAKE}}. "{% endraw" is checked in the whole file.
* Script header: keys match [A-Z][A-Za-z]*( [A-Za-z]+)*; continuation lines are
  joined with one space; a blank line ends a field. Shell headers follow an
  optional shebang and end at the first non-comment line. Relative imports are
  ignored. Dependencies are compared by import name.
* load_pages skips directories starting with "_" or "." plus node_modules and
  vendor (the _config.yml excludes); files are not filtered.
"""

import ast
import os
import re
import sys
import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

# ---- constants -------------------------------------------------------------
ERROR, WARNING = "E", "W"
STAGES: dict[str, tuple[str, str]] = {
    "S1": ("Stage 1", "Knowledge acquisition"),
    "S2": ("Stage 2", "Content development"),
    "S3": ("Stage 3", "Review and verification"),
    "S4": ("Stage 4", "AI-tutor coaching"),
    "S5": ("Stage 5", "Assessment development"),
    "CA": ("Certification alignment", "Certification alignment"),
    "DL": ("Delivery", "Delivery"),
    "OP": ("Operating practice", "Operating practices"),
}
CAPABILITIES = tuple(
    "llm long-context structured-output file-read file-write shell web-search "
    "web-fetch subagents human-approval".split()
)
PROMPT_REQUIRED = tuple("id title stage purpose placeholders capabilities".split())
PROMPT_OPTIONAL = tuple("kind sub_stage inputs outputs version".split())
PROMPT_KINDS = ("prompt", "template", "contract", "brief")
SCRIPT_REQUIRED = ("ID", "Purpose", "Usage", "Dependencies", "Writes files", "License")
SCRIPT_OPTIONAL = ("Title", "Stage", "Inputs", "Outputs")
PAGE_THEME_KEYS = ("layout", "permalink", "nav_exclude", "has_toc")
PAGE_KEYS = frozenset(
    "title nav_order parent grand_parent has_children status last_reviewed "
    "stage sub_stage prompts scripts generated".split()
) | frozenset(PAGE_THEME_KEYS)
STATUS_VALUES = ("draft", "reviewed", "stable")
SECRET_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----",
        r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
        r"\bgh[pousr]_[A-Za-z0-9]{36,}",
        r"\bgithub_pat_[A-Za-z0-9_]{22,}",
        r"\bhf_[A-Za-z0-9]{30,}",
        r"\bsk-(?=[A-Za-z0-9_-]*[0-9])[A-Za-z0-9_-]{20,}",
        r"\bxox[abposr]-[A-Za-z0-9-]{10,}",
        r"\bAIza[0-9A-Za-z_-]{35}",
        r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    )
)
EMAIL_ALLOWLIST = ("example.com", "example.org", "example.net", "git@github.com")
EMAIL_RE = re.compile(r"[\w.%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")


def email_allowed(address: str) -> bool:
    """True for an exact allowlist entry or a reserved domain and subdomains."""
    addr = address.lower()
    domain = addr.rpartition("@")[2]
    return any(
        (
            addr == entry
            if "@" in entry
            else domain == entry or domain.endswith("." + entry)
        )
        for entry in EMAIL_ALLOWLIST
    )


# ---- data classes ----------------------------------------------------------
Issue = tuple[int, str]


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line} {self.rule} {self.message}"


@dataclass
class FrontMatter:
    front: dict[str, Any]
    body: str
    body_line_offset: int
    errors: list[Issue]
    key_lines: dict[str, int]


@dataclass
class Page:
    path: Path
    rel: str
    front: dict[str, Any]
    body: str
    body_line_offset: int
    errors: list[Issue] = field(default_factory=list)
    key_lines: dict[str, int] = field(default_factory=dict)


@dataclass
class PromptDoc:
    front: dict[str, Any]
    body: str
    notes: str
    placeholders_used: list[str]
    errors: list[Issue]
    key_lines: dict[str, int] = field(default_factory=dict)


@dataclass
class ScriptHeader:
    path: Path
    fields: dict[str, str]
    key_lines: dict[str, int]
    imports: list[str]
    non_stdlib: list[str]
    errors: list[Issue]


@dataclass
class Fence:
    line: int
    end_line: int
    marker: str
    info: str
    closed: bool
    content: str
    indent: int

    @property
    def lang(self) -> str:
        return (self.info.split() or [""])[0]


@dataclass
class Heading:
    line: int
    level: int
    text: str
    id: str
    explicit: bool


# ---- text input ------------------------------------------------------------
def read_text(path: Path) -> str:
    text = Path(path).read_bytes().decode("utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def text_hazards(path: Path) -> list[str]:
    data = Path(path).read_bytes()
    found = []
    if data.startswith(b"\xef\xbb\xbf"):
        found.append("UTF-8 byte order mark (BOM) at the start of the file")
    crs = data.count(b"\r")
    if crs:
        found.append(f"{crs} carriage return (CR) character(s)")
    return found


# ---- front matter (S2) -----------------------------------------------------
_KEY_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*):(?: +(.*))?")
_INT_RE = re.compile(r"0|-?[1-9][0-9]*")
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9._-]*")
_RESERVED = frozenset("true false yes no on off null".split())
_NOT_KV = "not a 'key: value' line (no comments, nesting or multi-line values)"


class _Bad(ValueError):
    """A value the restricted subset rejects; the message is for the author."""


def _parse_string(raw: str, start: int) -> tuple[str, int]:
    """Read the double-quoted string at raw[start]; return (value, next index)."""
    out, i = [], start + 1
    while i < len(raw):
        char = raw[i]
        if char == "\\":
            nxt = raw[i + 1 : i + 2]
            if nxt not in ('"', "\\"):
                raise _Bad(f"unsupported escape '\\{nxt}'; only \\\" and \\\\ exist")
            out.append(nxt)
            i += 2
        elif char == '"':
            return "".join(out), i + 1
        else:
            out.append(char)
            i += 1
    raise _Bad("string is missing its closing double quote")


def _parse_list(raw: str) -> list[str]:
    def skip(i: int) -> int:
        while i < len(raw) and raw[i] in " \t":
            i += 1
        return i

    items: list[str] = []
    i = skip(1)
    if raw[i : i + 1] != "]":  # a non-empty list; "[]" falls through
        while True:
            i = skip(i)
            if raw[i : i + 1] == '"':
                value, i = _parse_string(raw, i)
            else:
                match = _TOKEN_RE.match(raw, i)
                if match is None:
                    raise _Bad(
                        "list items are double-quoted strings or bare tokens "
                        "like S1.4a; empty or other items are not allowed"
                    )
                value, i = match.group(), match.end()
                if value.lower() in _RESERVED:
                    raise _Bad(f"bare list item {value} is ambiguous; quote it")
            items.append(value)
            i = skip(i)
            if raw[i : i + 1] == "]":
                break
            if raw[i : i + 1] != ",":
                raise _Bad("list needs ',' between items and a closing ']'")
            i += 1
    if raw[i + 1 :].strip():
        raise _Bad("unexpected text after the closing ']'")
    return items


def _parse_value(key: str, raw: str) -> Any:
    if not raw:
        raise _Bad(f"'{key}' has no value; write \"\" or [] for an empty one")
    if raw[0] == '"':
        value, end = _parse_string(raw, 0)
        if raw[end:].strip():
            raise _Bad(f"'{key}': unexpected text after the closing quote")
        return value
    if raw[0] == "[":
        return _parse_list(raw)
    if raw in ("true", "false"):
        return raw == "true"
    if _INT_RE.fullmatch(raw):
        return int(raw)
    if raw[0] == "'":
        raise _Bad(f"'{key}': single quotes are not allowed; use double quotes")
    if raw.lower() in _RESERVED or raw == "~":
        raise _Bad(f"'{key}': bare {raw} is ambiguous in YAML; double-quote it")
    raise _Bad(f"'{key}' is an unquoted string: double-quote it, e.g. {key}: \"...\"")


def parse_front_matter_full(text: str) -> FrontMatter:
    lines = text.split("\n")
    if lines[0] != "---":
        return FrontMatter(
            {}, text, 0, [(1, "no front matter: line 1 must be '---'")], {}
        )
    close = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    if close is None:
        msg = "front matter is not closed by a line that is exactly '---'"
        return FrontMatter({}, text, 0, [(1, msg)], {})
    front: dict[str, Any] = {}
    key_lines: dict[str, int] = {}
    errors: list[Issue] = []
    seen: set[str] = set()
    for number, line in enumerate(lines[1:close], 2):
        line = line.rstrip()
        if not line:
            continue
        match = None if line[0] in " \t" else _KEY_RE.fullmatch(line)
        if match is None:
            errors.append((number, _NOT_KV))
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        if key in seen:
            errors.append((number, f"duplicate key '{key}'"))
            continue
        seen.add(key)
        try:
            front[key] = _parse_value(key, raw)
            key_lines[key] = number
        except _Bad as exc:
            errors.append((number, str(exc)))
    body = "\n".join(lines[close + 1 :])
    return FrontMatter(front, body, close + 1, errors, key_lines)


def parse_front_matter(text: str) -> tuple[dict[str, Any], str, int, list[Issue]]:
    fm = parse_front_matter_full(text)
    return fm.front, fm.body, fm.body_line_offset, fm.errors


def unknown_keys(front: dict[str, Any], known: Iterable[str]) -> list[str]:
    allowed = set(known)
    return [key for key in front if key not in allowed]


# ---- code masking, headings, slugs -----------------------------------------
_TOKEN_SCAN = re.compile(r"^[ \t]*(`{3,}|~{3,})|<!--|(`+)", re.M)
_BLANK_LINE = re.compile(r"\n[ \t]*\n")
_NOT_NEWLINE = re.compile(r"[^\n]")
_Span = tuple[str, int, int, Fence | None]


def _read_fence(text: str, m: re.Match[str], info: str, eol: int) -> tuple[Fence, int]:
    size, marker = len(text), m.group(1)
    closer = re.compile(r"^[ \t]*%s{%d,}[ \t]*$" % (marker[0], len(marker)), re.M)
    found = closer.search(text, min(eol + 1, size))
    end = found.end() if found else size
    body = text[eol + 1 : found.start() if found else size] if eol < size else ""
    fence = Fence(
        line=text.count("\n", 0, m.start()) + 1,
        end_line=text.count("\n", 0, max(end - 1, 0)) + 1,
        marker=marker,
        info=info,
        closed=found is not None,
        content=body.removesuffix("\n"),
        indent=m.end(1) - m.start() - len(marker),
    )
    return fence, end


def _scan(text: str) -> list[_Span]:
    """Locate fences, HTML comments and code spans as ordered, disjoint spans."""
    spans: list[_Span] = []
    size, pos = len(text), 0
    while (m := _TOKEN_SCAN.search(text, pos)) is not None:
        if m.group(1):
            eol = text.find("\n", m.end(1))
            eol = size if eol < 0 else eol
            info = text[m.end(1) : eol].strip()
            if m.group(1)[0] == "~" or "`" not in info:
                fence, pos = _read_fence(text, m, info, eol)
                spans.append(("fence", m.start(), pos, fence))
                continue
            start, run = m.start(1), len(m.group(1))
        elif m.group(2):
            start, run = m.start(2), len(m.group(2))
        else:
            close = text.find("-->", m.end())
            pos = size if close < 0 else close + 3
            spans.append(("comment", m.start(), pos, None))
            continue
        blank = _BLANK_LINE.search(text, start + run)
        limit = blank.start() if blank else size
        closer = re.compile(r"(?<!`)`{%d}(?!`)" % run).search(text, start + run, limit)
        pos = closer.end() if closer else start + run
        if closer:
            spans.append(("code", start, pos, None))
    return spans


def find_fences(text: str) -> list[Fence]:
    return [fence for _, _, _, fence in _scan(text) if fence is not None]


def mask_code(text: str, inline: bool = True) -> str:
    out, last = [], 0
    for kind, start, end, _ in _scan(text):
        if kind == "code" and not inline:
            continue
        out += [text[last:start], _NOT_NEWLINE.sub(" ", text[start:end])]
        last = end
    return "".join(out) + text[last:]


def _is_word(char: str) -> bool:
    category = unicodedata.category(char)
    return category[0] in "LM" or category in ("Nd", "Nl", "Pc")


def kramdown_slug(text: str) -> str:
    return "".join(
        "-" if c in " \t" else c for c in text.lower() if c in " \t-" or _is_word(c)
    )


_ATX_RE = re.compile(r" {0,3}(#{1,6})[ \t]+(\S.*?)[ \t]*")
_ID_ATTR_RE = re.compile(r"(.*?)[ \t]+\{#(\S+?)\}")
_CLOSING_RE = re.compile(r"(.*?)[ \t]+#+")


def find_headings(body: str) -> list[Heading]:
    used: dict[str, int] = {}
    found = []
    for number, line in enumerate(mask_code(body, inline=False).split("\n"), 1):
        match = _ATX_RE.fullmatch(line)
        if match is None:
            continue
        text, explicit = match.group(2), None
        attr = _ID_ATTR_RE.fullmatch(text)  # "Title {#custom-id}"
        if attr:
            text, explicit = attr.group(1), attr.group(2)
        closing = _CLOSING_RE.fullmatch(text)  # "Title ##"
        if closing:
            text = closing.group(1)
        text = text.strip()
        slug = explicit if explicit is not None else kramdown_slug(text)
        if explicit is None and slug in used:
            used[slug] += 1
            slug = f"{slug}-{used[slug]}"
        elif explicit is None:
            used[slug] = 0
        found.append(
            Heading(number, len(match.group(1)), text, slug, explicit is not None)
        )
    return found


def headings_ids(body: str) -> list[tuple[int, str, str]]:
    return [(h.line, h.text, h.id) for h in find_headings(body)]


# ---- IDs (S3) --------------------------------------------------------------
_ID_RE = re.compile(r"(?:([PX])-)?(S[1-5]|CA|DL|OP)((?:[.-][0-9]+[a-z]*)*)")
_ID_PART_RE = re.compile(r"[.-]([0-9]+)([a-z]*)")


def split_id(id_str: str) -> tuple[str, str, list[tuple[int, str]]] | None:
    match = _ID_RE.fullmatch(id_str)
    if match is None:
        return None
    parts = [(int(n), s) for n, s in _ID_PART_RE.findall(match.group(3))]
    return match.group(1) or "", match.group(2), parts


def id_sort_key(id_str: str) -> tuple[int, tuple[tuple[int, str], ...], str]:
    split = split_id(id_str)
    if split is None:
        raise ValueError(f"not a valid ID: {id_str!r}")
    prefix, code, parts = split
    return list(STAGES).index(code), tuple(parts), prefix


# ---- prompt files (S4) -----------------------------------------------------
_PLACEHOLDER_RE = re.compile(r"\{\{(.*?)\}\}")
_UPPER_SNAKE_RE = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*")
_ENDRAW_RE = re.compile(r"\{%-?\s*endraw")


def _check_prompt_front(front: dict[str, Any], lines: dict[str, int]) -> list[Issue]:
    errors: list[Issue] = [
        (1, f"missing required key '{k}'") for k in PROMPT_REQUIRED if k not in front
    ]
    for key in ("id", "title", "stage", "purpose", "kind", "sub_stage"):
        if key in front and not (isinstance(front[key], str) and front[key].strip()):
            errors.append((lines[key], f"'{key}' must be a non-empty quoted string"))
    if isinstance(front.get("kind"), str) and front["kind"] not in PROMPT_KINDS:
        errors.append((lines["kind"], f"kind must be one of {', '.join(PROMPT_KINDS)}"))
    for key in ("placeholders", "capabilities"):
        if key not in front:
            continue
        if not isinstance(front[key], list):
            errors.append((lines[key], f"'{key}' must be an inline list"))
            continue
        for item in front[key]:
            if key == "capabilities" and item not in CAPABILITIES:
                errors.append((lines[key], f"unknown capability '{item}'"))
            if key == "placeholders" and not _UPPER_SNAKE_RE.fullmatch(item):
                errors.append((lines[key], f"'{item}' is not UPPER_SNAKE_CASE"))
    return errors


def parse_prompt(path: Path) -> PromptDoc:
    text = read_text(path)
    fm = parse_front_matter_full(text)
    front, key_lines, off = fm.front, fm.key_lines, fm.body_line_offset
    errors: list[Issue] = list(fm.errors)
    if front or not fm.errors:
        errors += _check_prompt_front(front, key_lines)
    for number, line in enumerate(text.split("\n"), 1):
        if _ENDRAW_RE.search(line):
            errors.append((number, "'{% endraw' would end the generated raw block"))
    lines = fm.body.split("\n")
    fences = [
        f for f in find_fences(fm.body) if f.marker == "````" and f.lang == "text"
    ]
    if not fences:
        errors.append((off + 1, "no prompt: need one four-backtick fence tagged text"))
        return PromptDoc(front, "", "", [], errors, key_lines)
    fence = fences[0]
    if len(fences) > 1:
        errors.append((off + fences[1].line, "more than one prompt fence; use one"))
    if not fence.closed:
        errors.append((off + fence.line, "the prompt fence is never closed"))
    if fence.indent:
        errors.append((off + fence.line, "the prompt fence must start at column 1"))
    for index, line in enumerate(lines[: fence.line - 1]):
        if line.strip():
            msg = "text before the prompt fence is not published; use notes after it"
            errors.append((off + index + 1, msg))
            break
    notes = "\n".join(lines[fence.end_line :]).strip() if fence.closed else ""
    used: list[str] = []
    for index, line in enumerate(fence.content.split("\n")):
        for name in _PLACEHOLDER_RE.findall(line):
            if not _UPPER_SNAKE_RE.fullmatch(name):
                msg = f"malformed placeholder {{{{{name}}}}}; use {{{{UPPER_SNAKE}}}}"
                errors.append((off + fence.line + 1 + index, msg))
            elif name not in used:
                used.append(name)
    declared = front.get("placeholders")
    if isinstance(declared, list):
        where = key_lines.get("placeholders", 1)
        errors += [
            (where, f"placeholder {n} is used but not declared")
            for n in used
            if n not in declared
        ]
        errors += [
            (where, f"placeholder {n} is declared but never used")
            for n in declared
            if n not in used
        ]
    return PromptDoc(front, fence.content, notes, used, errors, key_lines)


# ---- script headers (S5) ---------------------------------------------------
_FIELD_RE = re.compile(r"([A-Z][A-Za-z]*(?: [A-Za-z]+)*):[ \t]*(.*)")


def _import_names(tree: ast.AST) -> list[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return sorted(names)


def non_stdlib_imports(tree: ast.AST, common: Iterable[str] = ()) -> list[str]:
    skip = set(common) | set(sys.stdlib_module_names)
    return [name for name in _import_names(tree) if name not in skip]


def common_modules(root: Path) -> list[str]:
    folder = Path(root) / "scripts" / "common"
    stems = [p.stem for p in folder.glob("*.py") if p.stem != "__init__"]
    return sorted(stems + ["common"]) if stems else []


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "_", name.lower())


def parse_dependencies(value: str) -> list[str]:
    names = (
        re.split(r"[<>=!~\[]", t, maxsplit=1)[0].lower()
        for t in re.split(r"[,;\s]+", value)
    )
    return [name for name in names if name and name != "stdlib"]


def _docstring_lines(raw: str, first: int) -> list[tuple[int, str]]:
    """Dedent like inspect.cleandoc but keep file line numbers."""
    parts = raw.expandtabs().split("\n")
    margin = min((len(p) - len(p.lstrip()) for p in parts[1:] if p.strip()), default=0)
    out = [(first, parts[0].strip())]
    return out + [(first + i, p[margin:].rstrip()) for i, p in enumerate(parts[1:], 1)]


def _shell_header_lines(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for number, line in enumerate(text.split("\n"), 1):
        if number == 1 and line.startswith("#!"):
            continue
        if not line.startswith("#"):
            if out or line.strip():
                break
            continue
        out.append((number, line[1:].removeprefix(" ").rstrip()))
    return out


def _fields(
    lines: list[tuple[int, str]],
) -> tuple[dict[str, str], dict[str, int], list[Issue]]:
    fields: dict[str, str] = {}
    key_lines: dict[str, int] = {}
    errors: list[Issue] = []
    current: str | None = None
    for number, text in lines:
        match = _FIELD_RE.fullmatch(text)
        if text[:1] in (" ", "\t"):
            if current is not None and text.strip():
                fields[current] = f"{fields[current]} {text.strip()}".strip()
        elif match is None:
            current = None
        elif match.group(1) in fields:
            errors.append((number, f"duplicate field '{match.group(1)}'"))
            current = None
        else:
            current = match.group(1)
            fields[current] = match.group(2).strip()
            key_lines[current] = number
    return fields, key_lines, errors


def parse_script_header(path: Path, common: Iterable[str] = ()) -> ScriptHeader:
    path = Path(path)
    text = read_text(path)
    lines: list[tuple[int, str]] = []
    imports: list[str] = []
    non_std: list[str] = []
    errors: list[Issue] = []
    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            msg = f"syntax error: {exc.msg}"
            return ScriptHeader(path, {}, {}, [], [], [(exc.lineno or 1, msg)])
        imports, non_std = _import_names(tree), non_stdlib_imports(tree, common)
        doc = ast.get_docstring(tree, clean=False)
        if doc is None:
            errors.append((1, "no module docstring to read the header from"))
        else:
            lines = _docstring_lines(doc, tree.body[0].lineno)
    elif path.suffix == ".sh":
        lines = _shell_header_lines(text)
    else:
        errors.append((1, f"unsupported script type '{path.suffix}'"))
    fields, key_lines, field_errors = _fields(lines)
    errors += field_errors
    top = lines[0][0] if lines else 1
    errors += [
        (top, f"missing required field '{k}'")
        for k in SCRIPT_REQUIRED
        if k not in fields
    ]
    if fields.get("Writes files", "yes") not in ("yes", "no"):
        errors.append((key_lines["Writes files"], "'Writes files' must be yes or no"))
    if fields.get("License", "CC0-1.0") != "CC0-1.0":
        errors.append((key_lines["License"], "'License' must be CC0-1.0"))
    if "Dependencies" in fields:
        declared = {_norm(n) for n in parse_dependencies(fields["Dependencies"])}
        for name in non_std:
            if _norm(name) not in declared:
                msg = f"imports '{name}': not stdlib and not under Dependencies"
                errors.append((key_lines["Dependencies"], msg))
    return ScriptHeader(path, fields, key_lines, imports, non_std, errors)


# ---- configuration and files -----------------------------------------------
def read_config_scalar(config_text: str, key: str) -> str | None:
    pattern = r"^" + re.escape(key) + r"[ \t]*:(?:[ \t]+(.*))?$"
    match = re.search(pattern, config_text, re.M)
    raw = (match.group(1) or "").strip() if match else ""
    if not raw or raw[0] in "[{|>&*!#%@`":
        return None
    if raw[0] == '"':
        try:
            return _parse_string(raw, 0)[0]
        except _Bad:
            return None
    if raw[0] == "'":
        quoted = re.match(r"'((?:[^']|'')*)'", raw)
        return quoted.group(1).replace("''", "'") if quoted else None
    return re.split(r"[ \t]#", raw, maxsplit=1)[0].strip()


def walk_files(
    root: Path,
    subdir: str = "",
    suffixes: Iterable[str] | None = None,
    skip_dir: Callable[[str], bool] | None = None,
) -> list[Path]:
    """Sorted files under root/subdir; symlinked directories are not followed."""
    root = Path(root)
    wanted = None if suffixes is None else set(suffixes)
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root / subdir if subdir else root):
        dirnames[:] = [d for d in dirnames if not (skip_dir and skip_dir(d))]
        paths = (Path(dirpath) / name for name in filenames)
        found += [p for p in paths if wanted is None or p.suffix in wanted]
    return sorted(found, key=lambda p: p.relative_to(root).as_posix())


def _skip_docs_dir(name: str) -> bool:
    return name.startswith(("_", ".")) or name in ("node_modules", "vendor")


def load_pages(root: Path) -> list[Page]:
    root, pages = Path(root), []
    for path in walk_files(root, "docs", (".md",), _skip_docs_dir):
        fm = parse_front_matter_full(read_text(path))
        rel = path.relative_to(root).as_posix()
        args = (fm.front, fm.body, fm.body_line_offset, fm.errors, fm.key_lines)
        pages.append(Page(path, rel, *args))
    return pages
