"""Tests for scripts/site/sitelib.py.

License: CC0-1.0. Every fixture is built in a temporary directory or in memory;
the real repository tree is never read or written. Fake credentials are
assembled at run time so this file holds no key-shaped literal.

Run from the repository root:
    python3 -B -m unittest discover -s scripts/tests -p 'test_sitelib.py'
"""

import ast
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SITE_DIR = Path(__file__).resolve().parents[1] / "site"
sys.path.insert(0, str(SITE_DIR))

import sitelib  # noqa: E402  # pylint: disable=wrong-import-position

FENCE4 = "`" * 4
FENCE3 = "`" * 3


def write(base: Path, rel: str, text: str) -> Path:
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


class ConstantsTests(unittest.TestCase):
    def test_vocabularies(self):
        self.assertEqual(len(sitelib.CAPABILITIES), 10)
        self.assertEqual(
            list(sitelib.STAGES), ["S1", "S2", "S3", "S4", "S5", "CA", "DL", "OP"]
        )
        self.assertEqual(sitelib.STAGES["S1"], ("Stage 1", "Knowledge acquisition"))
        self.assertEqual(sitelib.STAGES["CA"][0], "Certification alignment")
        self.assertEqual(sitelib.STAGES["OP"][1], "Operating practices")
        self.assertEqual(sitelib.STATUS_VALUES, ("draft", "reviewed", "stable"))
        for key in sitelib.PAGE_THEME_KEYS:
            self.assertIn(key, sitelib.PAGE_KEYS)
        for key in ("title", "nav_order", "parent", "generated", "stage"):
            self.assertIn(key, sitelib.PAGE_KEYS)
        self.assertNotIn("summary", sitelib.PAGE_KEYS)

    def test_finding_str(self):
        finding = sitelib.Finding("docs/a.md", 7, "R01", "E", "bad thing")
        self.assertEqual(str(finding), "docs/a.md:7 R01 bad thing")

    def test_secret_patterns_match_built_at_run_time(self):
        samples = [
            "-----BEGIN " + "RSA PRIVATE KEY-----",
            "AKIA" + "A" * 16,
            "ghp_" + "a" * 36,
            "hf_" + "b" * 34,
            "sk-" + "proj1234567890" + "abcdefghij",
            "xoxb-" + "1234567890" + "-abc",
            "AIza" + "c" * 35,
            "eyJ" + "a" * 12 + "." + "b" * 12 + "." + "c" * 12,
        ]
        for sample in samples:
            with self.subTest(sample=sample[:6]):
                hits = [p for p in sitelib.SECRET_PATTERNS if p.search(sample)]
                self.assertTrue(hits)

    def test_secret_patterns_ignore_ordinary_text(self):
        for text in (
            "task-management-pipeline-with-long-words",
            "sk-learn-preprocessing-pipeline",
            "The AKIA prefix alone",
            "hf_short",
            "-----BEGIN CERTIFICATE-----",
        ):
            with self.subTest(text=text):
                self.assertFalse(any(p.search(text) for p in sitelib.SECRET_PATTERNS))

    def test_email_allowlist(self):
        allowed = ["a@example.com", "b@Example.ORG", "c@mail.example.net"]
        allowed.append("git@github.com")
        for address in allowed:
            with self.subTest(address=address):
                self.assertTrue(sitelib.email_allowed(address))
        denied = ["a@" + "gmail.com", "x@not" + "example.com", "git@git" + "lab.com"]
        for address in denied:
            with self.subTest(address=address):
                self.assertFalse(sitelib.email_allowed(address))
        self.assertTrue(sitelib.EMAIL_RE.search("write to a@example.com now"))

    def test_module_sources_are_clean_for_the_public_scan(self):
        forbidden = ["/Us" + "ers/", "/ho" + "me/", "C:\\Us" + "ers\\", "file:" + "///"]
        for path in (SITE_DIR / "sitelib.py", Path(__file__)):
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                for pattern in sitelib.SECRET_PATTERNS:
                    self.assertIsNone(pattern.search(text), pattern.pattern)
                for match in sitelib.EMAIL_RE.finditer(text):
                    self.assertTrue(sitelib.email_allowed(match.group()), match.group())
                for needle in forbidden:
                    self.assertNotIn(needle, text)
                self.assertIn("CC0-1.0", text)


class ReadTextTests(unittest.TestCase):
    def test_bom_and_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = b'\xef\xbb\xbf---\r\ntitle: "x"\r\n---\rBody\r\n'
            path = Path(tmp) / "a.md"
            path.write_bytes(raw)
            self.assertEqual(sitelib.read_text(path), '---\ntitle: "x"\n---\nBody\n')
            hazards = sitelib.text_hazards(path)
            self.assertEqual(len(hazards), 2)
            self.assertIn("BOM", hazards[0])
            self.assertIn("4 carriage return", hazards[1])

    def test_clean_file_has_no_hazards(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "a.md", "plain\ntext\n")
            self.assertEqual(sitelib.text_hazards(path), [])
            self.assertEqual(sitelib.read_text(path), "plain\ntext\n")

    def test_invalid_utf8_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.md"
            path.write_bytes(b"\xff\xfe bad")
            with self.assertRaises(UnicodeDecodeError):
                sitelib.read_text(path)


class FrontMatterTests(unittest.TestCase):
    ACCEPT = [
        ("empty block", "---\n---\nbody", {}, "body", 2),
        ("quoted with colon", '---\ntitle: "A: b"\n---\n', {"title": "A: b"}, "", 3),
        (
            "scalars",
            "---\nn: 3\nz: 0\nneg: -2\nyes_flag: true\nno_flag: false\n---\n",
            {"n": 3, "z": 0, "neg": -2, "yes_flag": True, "no_flag": False},
            "",
            7,
        ),
        (
            "lists",
            '---\na: [S1.4a, "x, y", P-S1-04]\nb: []\nc: [ ]\nd: [ "q" , r ]\n---\n',
            {"a": ["S1.4a", "x, y", "P-S1-04"], "b": [], "c": [], "d": ["q", "r"]},
            "",
            6,
        ),
        (
            "escapes",
            '---\nt: "say \\"hi\\" \\\\ ok"\n---\nB\n',
            {"t": 'say "hi" \\ ok'},
            "B\n",
            3,
        ),
        ("blank line ignored", "---\na: 1\n\nb: 2\n---\n", {"a": 1, "b": 2}, "", 5),
        ("unknown key parses", '---\nsummary: "x"\n---\n', {"summary": "x"}, "", 3),
        ("trailing spaces", '---\nt: "x"   \n---\n', {"t": "x"}, "", 3),
        ("hyphen key", "---\nnav-order: 2\n---\n", {"nav-order": 2}, "", 3),
    ]

    REJECT = [
        ("unquoted title with colon", "---\ntitle: Foo: bar\n---\n", 2, "double-quote"),
        ("bare yes", "---\nflag: yes\n---\n", 2, "ambiguous"),
        ("bare no", "---\nflag: No\n---\n", 2, "ambiguous"),
        ("capital True", "---\nflag: True\n---\n", 2, "ambiguous"),
        ("bare null", "---\nx: null\n---\n", 2, "ambiguous"),
        ("date", "---\nlast_reviewed: 2026-09-19\n---\n", 2, "double-quote"),
        ("bare word", "---\nstatus: draft\n---\n", 2, "double-quote"),
        ("float", "---\nx: 1.5\n---\n", 2, "double-quote"),
        ("leading zero", "---\nnav_order: 007\n---\n", 2, "double-quote"),
        ("duplicate key", "---\na: 1\nb: 2\na: 3\n---\n", 4, "duplicate key 'a'"),
        ("single quotes", "---\nt: 'x'\n---\n", 2, "single quotes"),
        ("bad escape", '---\nt: "a\\nb"\n---\n', 2, "unsupported escape"),
        ("unterminated string", '---\nt: "abc\n---\n', 2, "closing double quote"),
        ("text after string", '---\nt: "a" b\n---\n', 2, "after the closing quote"),
        ("empty value", "---\nt:\n---\n", 2, "no value"),
        ("no space after colon", '---\nt:"x"\n---\n', 2, "key: value"),
        ("comment line", "---\n# note\na: 1\n---\n", 2, "key: value"),
        ("indented line", "---\na: 1\n  b: 2\n---\n", 3, "key: value"),
        ("trailing comma", "---\na: [x,]\n---\n", 2, "empty or other items"),
        ("nested list", "---\na: [[x]]\n---\n", 2, "empty or other items"),
        ("reserved bare item", "---\na: [yes]\n---\n", 2, "ambiguous"),
        ("bare item digit start", "---\na: [1a]\n---\n", 2, "empty or other items"),
        ("unclosed list", "---\na: [x\n---\n", 2, "closing ']'"),
        ("text after list", '---\na: ["x"] y\n---\n', 2, "after the closing ']'"),
        ("missing comma", '---\na: ["x" "y"]\n---\n', 2, "between items"),
        ("bad key", "---\nbad key: 1\n---\n", 2, "key: value"),
    ]

    def test_accept_table(self):
        for name, text, front, body, offset in self.ACCEPT:
            with self.subTest(name):
                got_front, got_body, got_offset, errors = sitelib.parse_front_matter(
                    text
                )
                self.assertEqual(errors, [])
                self.assertEqual(got_front, front)
                self.assertEqual(got_body, body)
                self.assertEqual(got_offset, offset)

    def test_reject_table(self):
        for name, text, line, fragment in self.REJECT:
            with self.subTest(name):
                _, _, _, errors = sitelib.parse_front_matter(text)
                self.assertEqual(len(errors), 1, errors)
                self.assertEqual(errors[0][0], line)
                self.assertIn(fragment, errors[0][1])

    def test_block_list_is_rejected_twice(self):
        _, _, _, errors = sitelib.parse_front_matter("---\na:\n- x\n---\n")
        self.assertEqual([line for line, _ in errors], [2, 3])
        self.assertIn("no value", errors[0][1])

    def test_unclosed_front_matter(self):
        front, body, offset, errors = sitelib.parse_front_matter('---\na: "x"\n')
        self.assertEqual((front, offset), ({}, 0))
        self.assertEqual(body, '---\na: "x"\n')
        self.assertEqual(errors[0][0], 1)
        self.assertIn("not closed", errors[0][1])

    def test_front_matter_not_on_line_one(self):
        for text in (
            '\n---\ntitle: "x"\n---\n',
            '<!-- GENERATED -->\n---\ntitle: "x"\n---\n',
            '---   \ntitle: "x"\n---\n',
            "# Just a page\n",
            "",
        ):
            with self.subTest(text=text[:12]):
                front, body, offset, errors = sitelib.parse_front_matter(text)
                self.assertEqual((front, body, offset), ({}, text, 0))
                self.assertEqual(errors[0][0], 1)
                self.assertIn("no front matter", errors[0][1])

    def test_unknown_key_is_not_a_parse_error(self):
        text = '---\ntitle: "x"\nsummary: "y"\nsearch_exclude: true\n---\n'
        front, _, _, errors = sitelib.parse_front_matter(text)
        self.assertEqual(errors, [])
        self.assertEqual(
            sitelib.unknown_keys(front, sitelib.PAGE_KEYS),
            ["summary", "search_exclude"],
        )

    def test_body_offset_maps_to_file_lines(self):
        text = '---\ntitle: "x"\nnav_order: 1\n---\n\n# Heading\n'
        _, body, offset, _ = sitelib.parse_front_matter(text)
        line_in_body = body.split("\n").index("# Heading") + 1
        self.assertEqual(line_in_body + offset, 6)
        self.assertEqual(text.split("\n")[5], "# Heading")

    def test_full_returns_key_lines_and_keeps_first_duplicate(self):
        fm = sitelib.parse_front_matter_full('---\na: 1\nb: "x"\na: 2\n---\n')
        self.assertEqual(fm.front, {"a": 1, "b": "x"})
        self.assertEqual(fm.key_lines, {"a": 2, "b": 3})
        self.assertEqual(fm.errors, [(4, "duplicate key 'a'")])

    def test_bad_line_does_not_stop_later_keys(self):
        fm = sitelib.parse_front_matter_full('---\na: nope\nb: "ok"\nc: yes\n---\n')
        self.assertEqual(fm.front, {"b": "ok"})
        self.assertEqual([line for line, _ in fm.errors], [2, 4])


class SlugTests(unittest.TestCase):
    SLUGS = [
        ("A & B", "a--b"),
        ("Hello, World!", "hello-world"),
        ("snake_case name", "snake_case-name"),
        ("Version 2.0", "version-20"),
        ("tab\tsep", "tab-sep"),
        ("  lead and trail  ", "--lead-and-trail--"),
        ("a - b", "a---b"),
        ("x--y", "x--y"),
        ("C++ & C#", "c--c"),
        ("100% done", "100-done"),
        ("Café Ünï", "café-ünï"),
        ("Q: what?", "q-what"),
        ("!!!", ""),
        ("", ""),
    ]

    def test_kramdown_slug_table(self):
        for text, expected in self.SLUGS:
            with self.subTest(text):
                self.assertEqual(sitelib.kramdown_slug(text), expected)


class HeadingTests(unittest.TestCase):
    def test_duplicates_get_numbered_suffixes(self):
        body = "# A\n\n## A\n\ntext\n\n## A\n\n## a\n"
        self.assertEqual(
            sitelib.headings_ids(body),
            [(1, "A", "a"), (3, "A", "a-1"), (7, "A", "a-2"), (9, "a", "a-3")],
        )

    def test_kramdown_counts_per_base_slug(self):
        body = "# a\n# a\n# a-1\n"
        ids = [heading_id for _, _, heading_id in sitelib.headings_ids(body)]
        self.assertEqual(ids, ["a", "a-1", "a-1"])

    def test_explicit_id_wins_and_is_not_counted(self):
        body = "# Intro {#start}\n# Intro\n# Intro\n"
        ids = [heading_id for _, _, heading_id in sitelib.headings_ids(body)]
        self.assertEqual(ids, ["start", "intro", "intro-1"])
        self.assertTrue(sitelib.find_headings(body)[0].explicit)
        self.assertEqual(sitelib.find_headings(body)[0].text, "Intro")

    def test_punctuation_closing_hashes_and_code_spans(self):
        body = "## A & B ##\n### Using `git add`\n"
        found = sitelib.find_headings(body)
        self.assertEqual([h.level for h in found], [2, 3])
        self.assertEqual(found[0].id, "a--b")
        self.assertEqual(found[1].text, "Using `git add`")
        self.assertEqual(found[1].id, "using-git-add")

    def test_headings_in_fences_comments_and_without_space_are_ignored(self):
        body = (
            f"{FENCE3}\n# not a heading\n{FENCE3}\n<!--\n# hidden\n-->\n"
            "#NoSpace\n    # indented four\n# Real\n"
        )
        self.assertEqual(sitelib.headings_ids(body), [(9, "Real", "real")])

    def test_masked_input_gives_same_lines(self):
        body = f"# One\n{FENCE3}\n# x\n{FENCE3}\n## Two\n"
        masked = sitelib.mask_code(body)
        self.assertEqual(sitelib.headings_ids(body), sitelib.headings_ids(masked))


class IdTests(unittest.TestCase):
    def test_sort_order(self):
        ids = ["OP.1", "DL.1", "CA.1", "S5", "S1.10", "S1.4a", "S1.4", "S1.4b", "S2.1"]
        ids += ["S1", "S1.1"]
        expected = [
            "S1", "S1.1", "S1.4", "S1.4a", "S1.4b", "S1.10", "S2.1", "S5",
            "CA.1", "DL.1", "OP.1",
        ]  # fmt: skip
        self.assertEqual(sorted(ids, key=sitelib.id_sort_key), expected)

    def test_pairwise_rules(self):
        key = sitelib.id_sort_key
        self.assertLess(key("S1.4"), key("S1.4a"))
        self.assertLess(key("S1.4a"), key("S1.10"))
        self.assertLess(key("S5.9"), key("CA.1"))
        self.assertLess(key("CA.9"), key("DL.1"))
        self.assertLess(key("DL.9"), key("OP.1"))
        self.assertLess(key("P-S1-04"), key("P-S1-10"))
        self.assertLess(key("P-S1-10"), key("P-S2-01"))
        self.assertLess(key("X-S5-01"), key("X-CA-01"))
        self.assertLess(key("S1.2"), key("S1.10"))

    def test_prompt_and_script_forms(self):
        self.assertEqual(sitelib.split_id("P-S1-04"), ("P", "S1", [(4, "")]))
        self.assertEqual(sitelib.split_id("X-OP-11"), ("X", "OP", [(11, "")]))
        self.assertEqual(sitelib.split_id("S1.4a"), ("", "S1", [(4, "a")]))
        self.assertEqual(sitelib.split_id("CA"), ("", "CA", []))
        self.assertEqual(
            sitelib.id_sort_key("P-S1-04")[:2], sitelib.id_sort_key("X-S1-04")[:2]
        )

    def test_invalid_ids(self):
        for bad in (
            "",
            "S6.1",
            "SRC-001",
            "p-s1-04",
            "P-S1",
            "S1.",
            "S1.4A",
            "Q-S1-01",
        ):
            with self.subTest(bad):
                if bad in ("P-S1",):
                    self.assertEqual(sitelib.split_id(bad), ("P", "S1", []))
                    continue
                self.assertIsNone(sitelib.split_id(bad))
                with self.assertRaises(ValueError):
                    sitelib.id_sort_key(bad)


class MaskCodeTests(unittest.TestCase):
    def assert_shape(self, text, masked):
        self.assertEqual(len(masked), len(text))
        self.assertEqual(masked.count("\n"), text.count("\n"))
        for original, blanked in zip(text.split("\n"), masked.split("\n")):
            self.assertEqual(len(original), len(blanked))

    def test_plain_fence(self):
        text = f"before\n{FENCE3}python\nx = [a](b)\n{FENCE3}\nafter\n"
        masked = sitelib.mask_code(text)
        self.assert_shape(text, masked)
        self.assertEqual(masked.split("\n")[0], "before")
        self.assertEqual(masked.split("\n")[4], "after")
        self.assertEqual(masked.split("\n")[1:4], [" " * 9, " " * 10, " " * 3])

    def test_fence_lengths_and_nesting(self):
        cases = [
            (
                "four around three",
                f"{FENCE4}\n{FENCE3}\n[a](b)\n{FENCE3}\n{FENCE4}\nout",
            ),
            ("longer closer", f"{FENCE3}\n[a](b)\n{FENCE4}\nout"),
            ("tilde ignores backticks", "~~~\n```\n[a](b)\n~~~\nout"),
            ("backtick ignores tildes", f"{FENCE3}\n~~~\n[a](b)\n{FENCE3}\nout"),
            ("indented fence", f"  {FENCE3}\n[a](b)\n  {FENCE3}\nout"),
        ]
        for name, text in cases:
            with self.subTest(name):
                masked = sitelib.mask_code(text)
                self.assert_shape(text, masked)
                self.assertEqual(masked.strip(), "out")

    def test_shorter_closer_does_not_close(self):
        text = (
            f"{FENCE4}\n{FENCE3}\nstill code\n{FENCE3}\nstill code too\n{FENCE4}\nout"
        )
        masked = sitelib.mask_code(text)
        self.assertEqual(masked.strip(), "out")
        self.assertEqual(len(sitelib.find_fences(text)), 1)

    def test_unclosed_fence_runs_to_end(self):
        text = f"a\n{FENCE3}\nb\nc\n"
        masked = sitelib.mask_code(text)
        self.assert_shape(text, masked)
        self.assertEqual(masked.strip(), "a")
        fence = sitelib.find_fences(text)[0]
        self.assertFalse(fence.closed)
        self.assertEqual((fence.line, fence.end_line, fence.content), (2, 4, "b\nc"))

    def test_inline_code(self):
        text = "a `x [l](t)` b ``y ` z`` c ` lone\n\nnew `p` q"
        masked = sitelib.mask_code(text)
        self.assert_shape(text, masked)
        self.assertEqual(
            masked,
            "a " + " " * 10 + " b " + " " * 9 + " c ` lone\n\nnew " + "   " + " q",
        )
        self.assertEqual(sitelib.mask_code(text, inline=False), text)

    def test_backtick_line_with_backtick_info_is_inline_code(self):
        text = f"{FENCE3}foo{FENCE3} [a](b)\nnext"
        masked = sitelib.mask_code(text)
        self.assertEqual(masked, " " * 9 + " [a](b)\nnext")
        self.assertEqual(sitelib.find_fences(text), [])

    def test_comments(self):
        text = "a <!-- [x](y) --> b\n<!--\n" + FENCE3 + "\nmore\n-->\nout <!-- open"
        masked = sitelib.mask_code(text)
        self.assert_shape(text, masked)
        self.assertEqual(masked.split("\n")[0], "a " + " " * 15 + " b")
        self.assertEqual(masked.split("\n")[5], "out " + " " * 9)
        self.assertEqual(sitelib.find_fences(text), [])

    def test_comment_marker_inside_code_is_code(self):
        text = "x `<!--` y\n[a](b)\n"
        masked = sitelib.mask_code(text)
        self.assertEqual(masked, "x " + " " * 6 + " y\n[a](b)\n")

    def test_comment_inside_fence_stays_inside(self):
        text = f"{FENCE3}\n<!--\n{FENCE3}\n[a](b)\n-->\n"
        masked = sitelib.mask_code(text)
        self.assertIn("[a](b)", masked.split("\n")[3])

    def test_fence_details(self):
        text = (
            f"intro\n{FENCE4}text\nbody {{{{X}}}}\n{FENCE4}\n"
            f"{FENCE3}\nplain\n{FENCE3}\n"
        )
        first, second = sitelib.find_fences(text)
        self.assertEqual((first.line, first.end_line), (2, 4))
        self.assertEqual(
            (first.marker, first.lang, first.closed), (FENCE4, "text", True)
        )
        self.assertEqual(first.content, "body {{X}}")
        self.assertEqual((second.line, second.lang, second.indent), (5, "", 0))

    def test_no_code_no_change(self):
        text = "# Title\n\nPlain [link](a.md) text.\n"
        self.assertEqual(sitelib.mask_code(text), text)
        self.assertEqual(sitelib.mask_code(""), "")


class ConfigScalarTests(unittest.TestCase):
    CONFIG = (
        "# comment: not a key\n"
        'title: "Rapid Upskilling Pipeline"\n'
        'url: "https://example.org"          # assumption\n'
        "source_branch: master # trailing\n"
        "plain: some words here\n"
        "single: 'it''s ok'\n"
        'escaped: "a \\"q\\" b"\n'
        "empty:\n"
        "plugins: [a, b]\n"
        "search:\n"
        "  tokenizer_separator: /[\\s/]+/\n"
        "hash_inside: http://x/#frag\n"
        "  indented: nope\n"
        "twice: one\n"
        "twice: two\n"
        'unclosed: "abc\n'
        "novalue_colon:x\n"
    )

    def test_table(self):
        table = [
            ("title", "Rapid Upskilling Pipeline"),
            ("url", "https://example.org"),
            ("source_branch", "master"),
            ("plain", "some words here"),
            ("single", "it's ok"),
            ("escaped", 'a "q" b'),
            ("hash_inside", "http://x/#frag"),
            ("twice", "one"),
            ("empty", None),
            ("plugins", None),
            ("search", None),
            ("tokenizer_separator", None),
            ("indented", None),
            ("missing", None),
            ("comment", None),
            ("unclosed", None),
            ("novalue_colon", None),
        ]
        for key, expected in table:
            with self.subTest(key):
                self.assertEqual(sitelib.read_config_scalar(self.CONFIG, key), expected)


class PromptTests(unittest.TestCase):
    FRONT = (
        "---\n"
        'id: "P-S1-04"\n'
        'title: "Search plan"\n'
        'stage: "S1"\n'
        'purpose: "Plan a search."\n'
        'placeholders: ["OBJECTIVE_ID", "TOPIC"]\n'
        "capabilities: [llm, web-search]\n"
        "---\n"
    )
    FENCE = (
        f"{FENCE4}text\n"
        "Plan {{OBJECTIVE_ID}} about {{TOPIC}} and {{TOPIC}}.\n"
        f"{FENCE3}\ninner fence\n{FENCE3}\n"
        f"{FENCE4}\n"
    )
    NOTES = "\nKeep it short.\n"

    def parse(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            return sitelib.parse_prompt(write(Path(tmp), "prompts/s1/p.md", text))

    def test_good_prompt(self):
        doc = self.parse(self.FRONT + self.FENCE + self.NOTES)
        self.assertEqual(doc.errors, [])
        self.assertEqual(doc.front["id"], "P-S1-04")
        self.assertEqual(doc.placeholders_used, ["OBJECTIVE_ID", "TOPIC"])
        self.assertEqual(doc.notes, "Keep it short.")
        self.assertTrue(doc.body.startswith("Plan {{OBJECTIVE_ID}}"))
        self.assertIn(f"{FENCE3}\ninner fence\n{FENCE3}", doc.body)
        self.assertNotIn(FENCE4, doc.body)
        self.assertEqual(doc.key_lines["placeholders"], 6)

    def test_no_fence(self):
        doc = self.parse(self.FRONT + "Just words {{TOPIC}}.\n")
        self.assertEqual(doc.body, "")
        messages = [m for _, m in doc.errors]
        self.assertTrue(any("no prompt" in m for m in messages))

    def test_wrong_fence_shapes_are_not_prompts(self):
        for name, fence in (
            ("untagged", f"{FENCE4}\nx\n{FENCE4}\n"),
            ("three backticks", f"{FENCE3}text\nx\n{FENCE3}\n"),
            ("other tag", f"{FENCE4}python\nx\n{FENCE4}\n"),
            ("five backticks", f"{'`' * 5}text\nx\n{'`' * 5}\n"),
        ):
            with self.subTest(name):
                doc = self.parse(self.FRONT + fence)
                self.assertTrue(any("no prompt" in m for _, m in doc.errors))

    def test_two_fences(self):
        second = f"{FENCE4}text\nagain {{{{TOPIC}}}}\n{FENCE4}\n"
        doc = self.parse(self.FRONT + self.FENCE + "\n" + second)
        errors = [(line, m) for line, m in doc.errors if "more than one" in m]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 8 + 8)  # offset 8, second fence on body line 8

    def test_undeclared_and_unused_placeholders(self):
        front = self.FRONT.replace('["OBJECTIVE_ID", "TOPIC"]', '["OBJECTIVE_ID"]')
        doc = self.parse(front + self.FENCE)
        self.assertEqual(
            doc.errors, [(6, "placeholder TOPIC is used but not declared")]
        )
        front = self.FRONT.replace('"TOPIC"]', '"TOPIC", "UNUSED"]')
        doc = self.parse(front + self.FENCE)
        self.assertEqual(
            doc.errors, [(6, "placeholder UNUSED is declared but never used")]
        )

    def test_malformed_placeholder_and_line_number(self):
        text = (
            self.FRONT
            + f"{FENCE4}text\nok {{{{TOPIC}}}}\nbad {{{{ topic }}}}\n{FENCE4}\n"
        )
        doc = self.parse(text.replace('["OBJECTIVE_ID", "TOPIC"]', '["TOPIC"]'))
        self.assertEqual(len(doc.errors), 1, doc.errors)
        self.assertEqual(doc.errors[0][0], 8 + 3)
        self.assertIn("malformed placeholder", doc.errors[0][1])

    def test_front_matter_checks(self):
        cases = [
            (
                "unknown capability",
                "capabilities: [llm, web-search]",
                "capabilities: [llm, magic]",
                7,
                "unknown capability 'magic'",
            ),
            (
                "missing key",
                'purpose: "Plan a search."\n',
                "",
                1,
                "missing required key 'purpose'",
            ),
            (
                "bad kind",
                'stage: "S1"\n',
                'stage: "S1"\nkind: "poem"\n',
                5,
                "kind must be one of",
            ),
            (
                "lowercase name",
                '["OBJECTIVE_ID", "TOPIC"]',
                '["objective_id", "TOPIC"]',
                6,
                "not UPPER_SNAKE_CASE",
            ),
            (
                "not a list",
                "capabilities: [llm, web-search]",
                'capabilities: "llm"',
                7,
                "must be an inline list",
            ),
            (
                "non-string title",
                'title: "Search plan"',
                "title: 5",
                3,
                "non-empty quoted string",
            ),
        ]
        for name, old, new, line, fragment in cases:
            with self.subTest(name):
                doc = self.parse(self.FRONT.replace(old, new) + self.FENCE)
                hits = [(n, m) for n, m in doc.errors if fragment in m]
                self.assertTrue(hits, doc.errors)
                self.assertEqual(hits[0][0], line)

    def test_broken_front_matter_reports_only_the_real_problem(self):
        doc = self.parse(self.FENCE)
        self.assertEqual(len(doc.errors), 1)
        self.assertIn("no front matter", doc.errors[0][1])

    def test_text_before_fence_and_unclosed_fence(self):
        doc = self.parse(self.FRONT + "Intro text\n" + self.FENCE)
        self.assertEqual(len(doc.errors), 1)
        self.assertEqual(doc.errors[0][0], 9)
        self.assertIn("before the prompt fence", doc.errors[0][1])
        doc = self.parse(
            self.FRONT + f"{FENCE4}text\nPlan {{{{TOPIC}}}} {{{{OBJECTIVE_ID}}}}\n"
        )
        self.assertTrue(any("never closed" in m for _, m in doc.errors))

    def test_indented_fence_is_reported(self):
        doc = self.parse(self.FRONT + f" {FENCE4}text\nPlan {{{{TOPIC}}}}\n {FENCE4}\n")
        self.assertTrue(any("column 1" in m for _, m in doc.errors))

    def test_endraw_anywhere_is_reported(self):
        doc = self.parse(self.FRONT + self.FENCE + "\nNote {% endraw %} here\n")
        hits = [(n, m) for n, m in doc.errors if "endraw" in m]
        self.assertEqual([n for n, _ in hits], [8 + 6 + 2])
        doc = self.parse(self.FRONT + self.FENCE.replace("Plan", "{%- endraw -%}"))
        self.assertTrue(any("endraw" in m for _, m in doc.errors))


PY_HEADER = (
    "#!/usr/bin/env python3\n"
    '"""Search planner.\n'
    "\n"
    "ID: X-S1-04\n"
    "Title: Search plan\n"
    "Purpose: Build a search plan\n"
    "    from a blueprint file.\n"
    "Usage: python3 scripts/s1/search_plan.py --write\n"
    "Dependencies: {deps}\n"
    "Writes files: {writes}\n"
    "License: {license}\n"
    '"""\n'
    "{imports}"
)
SH_HEADER = (
    "#!/usr/bin/env bash\n"
    "# Build a checklist.\n"
    "#\n"
    "# ID: X-S1-05\n"
    "# Purpose: Print a checklist\n"
    "#   from standard input.\n"
    "# Usage: bash scripts/s1/checklist.sh\n"
    "# Dependencies: stdlib\n"
    "# Writes files: no\n"
    "# License: CC0-1.0\n"
    "\n"
    "# ID: X-S9-99 (not part of the header)\n"
    "set -eu\n"
)


class ScriptHeaderTests(unittest.TestCase):
    def py(self, imports="import json\nimport os.path\n", **kw):
        values = {"deps": "stdlib", "writes": "no", "license": "CC0-1.0"}
        values.update(kw)
        return PY_HEADER.format(imports=imports, **values)

    def parse(self, text, name="s.py", common=()):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), name, text)
            return sitelib.parse_script_header(path, common)

    def test_python_header_with_continuation(self):
        head = self.parse(self.py())
        self.assertEqual(head.errors, [])
        self.assertEqual(head.fields["ID"], "X-S1-04")
        self.assertEqual(
            head.fields["Purpose"], "Build a search plan from a blueprint file."
        )
        self.assertEqual(head.fields["Writes files"], "no")
        self.assertEqual(head.key_lines["ID"], 4)
        self.assertEqual(head.key_lines["Usage"], 8)
        self.assertEqual(head.imports, ["json", "os"])
        self.assertEqual(head.non_stdlib, [])

    def test_python_non_stdlib_import_must_be_declared(self):
        text = self.py("import json\nimport yaml\nfrom a.b import c\n")
        head = self.parse(text)
        self.assertEqual(head.non_stdlib, ["a", "yaml"])
        self.assertEqual(len(head.errors), 2)
        self.assertEqual(head.errors[0][0], 9)
        self.assertIn("'a'", head.errors[0][1])
        declared = self.parse(self.py("import yaml\n", deps="PyYAML, yaml>=6"))
        self.assertEqual(declared.errors, [])
        self.assertEqual(declared.non_stdlib, ["yaml"])

    def test_common_modules_count_as_declared(self):
        text = self.py("import json\nfrom llm_adapter import complete\n")
        self.assertEqual(len(self.parse(text).errors), 1)
        head = self.parse(text, common=["llm_adapter"])
        self.assertEqual(head.errors, [])
        self.assertEqual(head.non_stdlib, [])
        self.assertEqual(head.imports, ["json", "llm_adapter"])

    def test_relative_and_nested_imports(self):
        text = self.py(
            "from . import sibling\nfrom .pkg import x\n\ndef f():\n    import csv\n"
        )
        head = self.parse(text)
        self.assertEqual(head.imports, ["csv"])
        self.assertEqual(head.errors, [])

    def test_required_fields_and_values(self):
        head = self.parse(self.py(writes="maybe", license="MIT"))
        messages = [m for _, m in head.errors]
        self.assertEqual(len(messages), 2)
        self.assertTrue(any("yes or no" in m for m in messages))
        self.assertTrue(any("CC0-1.0" in m for m in messages))
        head = self.parse('"""Only prose.\n\nID: X-S1-01\n"""\n')
        missing = [m for _, m in head.errors if "missing required field" in m]
        self.assertEqual(len(missing), 5)
        self.assertEqual(head.errors[0][0], 1 + 0)

    def test_duplicate_field(self):
        text = self.py().replace("Title: Search plan\n", "ID: X-S1-99\n")
        head = self.parse(text)
        self.assertEqual(head.fields["ID"], "X-S1-04")
        self.assertEqual(head.errors, [(5, "duplicate field 'ID'")])

    def test_python_without_docstring_and_with_syntax_error(self):
        head = self.parse("import json\n")
        self.assertIn("no module docstring", head.errors[0][1])
        head = self.parse("x = (\n")
        self.assertIn("syntax error", head.errors[0][1])
        self.assertEqual(head.fields, {})

    def test_shell_header(self):
        head = self.parse(SH_HEADER, name="s.sh")
        self.assertEqual(head.errors, [])
        self.assertEqual(head.fields["ID"], "X-S1-05")
        self.assertEqual(
            head.fields["Purpose"], "Print a checklist from standard input."
        )
        self.assertEqual(head.key_lines["ID"], 4)
        self.assertEqual(head.imports, [])

    def test_shell_without_header_and_unsupported_suffix(self):
        head = self.parse("echo hi\n", name="s.sh")
        self.assertEqual(len([m for _, m in head.errors if "missing" in m]), 6)
        head = self.parse("whatever", name="s.rb")
        self.assertIn("unsupported script type", head.errors[0][1])

    def test_non_stdlib_imports_helper(self):
        tree = ast.parse(
            "import os, requests.adapters\n"
            "from yaml import safe_load\nimport __future__\n"
        )
        self.assertEqual(sitelib.non_stdlib_imports(tree), ["requests", "yaml"])
        self.assertEqual(sitelib.non_stdlib_imports(tree, ["yaml"]), ["requests"])

    def test_parse_dependencies(self):
        table = [
            ("stdlib", []),
            ("", []),
            ("requests, PyYAML", ["requests", "pyyaml"]),
            ("requests>=2.31; yaml", ["requests", "yaml"]),
            ("stdlib, numpy", ["numpy"]),
        ]
        for value, expected in table:
            with self.subTest(value):
                self.assertEqual(sitelib.parse_dependencies(value), expected)

    def test_common_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(sitelib.common_modules(root), [])
            for name in ("llm_adapter.py", "__init__.py", "notes.txt", "aa.py"):
                write(root, f"scripts/common/{name}", "")
            expected = ["aa", "common", "llm_adapter"]
            self.assertEqual(sitelib.common_modules(root), expected)


class FilesystemTests(unittest.TestCase):
    def build(self, root: Path):
        page = '---\ntitle: "T"\n---\nBody\n'
        write(root, "docs/index.md", page)
        write(root, "docs/Zeta.md", "no front matter\n")
        write(root, "docs/a-b.md", page)
        write(root, "docs/a/b.md", page)
        write(root, "docs/notes.txt", "x")
        write(root, "docs/_includes/hidden.md", page)
        write(root, "docs/.cache/hidden.md", page)
        write(root, "docs/vendor/gem/README.md", page)
        write(root, "docs/node_modules/pkg/README.md", page)
        write(root, "other/outside.md", page)

    def test_load_pages_order_skips_and_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            pages = sitelib.load_pages(root)
            self.assertEqual(
                [p.rel for p in pages],
                ["docs/Zeta.md", "docs/a-b.md", "docs/a/b.md", "docs/index.md"],
            )
            zeta, index = pages[0], pages[3]
            self.assertEqual(zeta.path, root / "docs" / "Zeta.md")
            self.assertEqual(zeta.errors[0][0], 1)
            self.assertEqual(zeta.body, "no front matter\n")
            self.assertEqual(index.errors, [])
            self.assertEqual(index.front, {"title": "T"})
            self.assertEqual((index.body, index.body_line_offset), ("Body\n", 3))
            self.assertEqual(index.key_lines, {"title": 2})

    def test_load_pages_without_docs_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(sitelib.load_pages(Path(tmp)), [])

    def test_walk_files_filters_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            everything = [
                p.relative_to(root).as_posix() for p in sitelib.walk_files(root)
            ]
            self.assertEqual(everything, sorted(everything))
            self.assertIn("other/outside.md", everything)
            docs_txt = sitelib.walk_files(root, "docs", [".txt"])
            self.assertEqual([p.name for p in docs_txt], ["notes.txt"])
            skipped = sitelib.walk_files(root, "docs", [".md"], lambda n: n == "a")
            names = [p.relative_to(root).as_posix() for p in skipped]
            self.assertNotIn("docs/a/b.md", names)
            self.assertIn("docs/a-b.md", names)
            self.assertEqual(sitelib.walk_files(root, "missing"), [])

    def test_walk_files_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            self.assertEqual(
                sitelib.walk_files(root, "docs"), sitelib.walk_files(root, "docs")
            )


if __name__ == "__main__":
    unittest.main()
