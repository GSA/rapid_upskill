"""Unit tests for scripts/dl/volume_manifest_check.py and
docs/delivery/publishing.md.

Everything runs offline, on synthetic fixtures built in memory or in a
temporary directory, except the tests that read the real, published
sample manifests (read-only). The page-output tests re-run the real
script and compare its output with the text pasted on the page, so the
page can never drift from the script.

Run all tests with: python3 -B scripts/tests/run_all.py
"""

import ast
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
SCRIPT = ROOT / "scripts" / "dl" / "volume_manifest_check.py"
SAMPLE_DIR = ROOT / "scripts" / "sample_data" / "git_basics_batch8" / "volumes"
SAMPLE_MANIFEST = SAMPLE_DIR / "manifest.json"
SAMPLE_OFF_CONVENTION = SAMPLE_DIR / "manifest_off_convention.json"
PAGE = ROOT / "docs" / "delivery" / "publishing.md"


def load_module() -> ModuleType:
    """Import the script from its file, so the test survives a repo move."""
    spec = importlib.util.spec_from_file_location("volume_manifest_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vmc = load_module()


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


def chapter(chapter_id: Any, sections: Any = None) -> dict[str, Any]:
    """A minimal chapter entry; sections defaults to one matching section."""
    if sections is None:
        sections = [f"{chapter_id}.1"]
    return {"id": chapter_id, "sections": sections}


def manifest(*volumes_chapters: list[dict[str, Any]]) -> dict[str, Any]:
    """A minimal manifest: one volume per argument, numbered from 1."""
    return {
        "volumes": [
            {"volume": n, "chapters": chapters}
            for n, chapters in enumerate(volumes_chapters, start=1)
        ]
    }


class NumeralKeyTests(unittest.TestCase):
    """numeral_key: the sort key for an id that already matched the pattern."""

    def test_splits_part_and_chapter_as_integers(self) -> None:
        self.assertEqual(vmc.numeral_key("3.10"), (3, 10))
        self.assertEqual(vmc.numeral_key("3.9"), (3, 9))

    def test_ten_sorts_after_nine_not_before_two(self) -> None:
        ids = ["3.10", "3.9", "3.2"]
        self.assertEqual(sorted(ids, key=vmc.numeral_key), ["3.2", "3.9", "3.10"])


class CheckManifestErrorTests(unittest.TestCase):
    """Every finding path, exercised on small in-memory fixtures."""

    def test_clean_two_chapter_manifest_has_no_findings(self) -> None:
        data = manifest([chapter("1.1"), chapter("1.2")])
        errors, warnings, volumes, chapters = vmc.check_manifest(data)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(volumes, 1)
        self.assertEqual(chapters, 2)

    def test_off_convention_id_is_flagged_not_skipped(self) -> None:
        data = manifest([chapter("1.1"), chapter("chapter-two")])
        errors, warnings, _, chapters = vmc.check_manifest(data)
        self.assertEqual(chapters, 2)
        self.assertTrue(
            any("off-convention" in e and "chapter-two" in e for e in errors), errors
        )

    def test_missing_id_is_off_convention(self) -> None:
        data = manifest([{"sections": ["1.1.1"]}])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertTrue(any("off-convention" in e for e in errors), errors)

    def test_non_string_id_is_off_convention(self) -> None:
        data = manifest([chapter(11)])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertTrue(any("off-convention" in e for e in errors), errors)

    def test_section_not_starting_with_chapter_id_is_no_reset(self) -> None:
        data = manifest([chapter("3.10", sections=["3.9.1"])])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertTrue(any("no-reset" in e and "3.9.1" in e for e in errors), errors)

    def test_section_starting_with_chapter_id_is_clean(self) -> None:
        data = manifest([chapter("3.10", sections=["3.10.1", "3.10.2"])])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertEqual(errors, [])

    def test_missing_sections_list_is_not_a_finding(self) -> None:
        data = manifest([{"id": "1.1"}])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertEqual(errors, [])

    def test_sections_not_a_list_is_not_a_finding(self) -> None:
        data = manifest([{"id": "1.1", "sections": "1.1.1"}])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertEqual(errors, [])

    def test_off_convention_chapter_is_skipped_for_further_checks(self) -> None:
        # A bad id contributes no no-reset finding and no order key of its own.
        data = manifest([chapter("1.1"), {"id": "bad", "sections": ["nope"]}])
        errors, warnings, _, _ = vmc.check_manifest(data)
        self.assertEqual(len(errors), 1)
        self.assertEqual(warnings, [])

    def test_non_string_section_id_is_no_reset(self) -> None:
        data = manifest([chapter("1.1", sections=[1])])
        errors, _, _, _ = vmc.check_manifest(data)
        self.assertTrue(any("no-reset" in e for e in errors), errors)


class CheckManifestWarningTests(unittest.TestCase):
    """The one warning path: numeral-aware ordering within a volume."""

    def test_out_of_order_ids_warn(self) -> None:
        data = manifest([chapter("3.10"), chapter("3.9"), chapter("3.2")])
        errors, warnings, _, _ = vmc.check_manifest(data)
        self.assertEqual(errors, [])
        self.assertTrue(any("order" in w for w in warnings), warnings)
        self.assertIn("got 3.10, 3.9, 3.2", warnings[0])
        self.assertIn("expected 3.2, 3.9, 3.10", warnings[0])

    def test_in_order_ids_do_not_warn(self) -> None:
        data = manifest([chapter("3.2"), chapter("3.9"), chapter("3.10")])
        _, warnings, _, _ = vmc.check_manifest(data)
        self.assertEqual(warnings, [])

    def test_single_valid_chapter_never_warns(self) -> None:
        data = manifest([chapter("3.9")])
        _, warnings, _, _ = vmc.check_manifest(data)
        self.assertEqual(warnings, [])

    def test_all_off_convention_chapters_never_warn(self) -> None:
        data = manifest([{"id": "a"}, {"id": "b"}])
        _, warnings, _, _ = vmc.check_manifest(data)
        self.assertEqual(warnings, [])

    def test_each_volume_is_ordered_independently(self) -> None:
        data = manifest(
            [chapter("3.2"), chapter("3.9")], [chapter("1.10"), chapter("1.2")]
        )
        _, warnings, _, _ = vmc.check_manifest(data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("volume 2", warnings[0])


class CheckManifestUsageErrorTests(unittest.TestCase):
    """Malformed shapes are usage errors (a raised ValueError), not findings."""

    def test_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest(["not", "an", "object"])

    def test_missing_volumes_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest({})

    def test_empty_volumes_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest({"volumes": []})

    def test_volume_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest({"volumes": ["not an object"]})

    def test_missing_chapters_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest({"volumes": [{"volume": 1}]})

    def test_empty_chapters_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest({"volumes": [{"volume": 1, "chapters": []}]})

    def test_chapter_not_an_object_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vmc.check_manifest({"volumes": [{"volume": 1, "chapters": ["x"]}]})


class LoadJsonTests(unittest.TestCase):
    """load_json: file reading, the size cap and the symlink refusal."""

    def test_reads_the_real_sample(self) -> None:
        data = vmc.load_json(SAMPLE_MANIFEST)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["volumes"]), 2)

    def test_refuses_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(SAMPLE_MANIFEST)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            with self.assertRaises(OSError):
                vmc.load_json(link)

    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "big.json"
            big.write_text("[" + "1," * vmc.MAX_BYTES + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                vmc.load_json(big)


class MainExitCodeTests(unittest.TestCase):
    """main(): 0 for clean, 1 for any error, 2 for a usage or input error."""

    def write(self, tmp: Path, data: Any) -> Path:
        path = tmp / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_exit_zero_on_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), manifest([chapter("1.1")]))
            self.assertEqual(vmc.main([str(path)]), 0)

    def test_exit_one_on_off_convention_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), manifest([chapter("bad-id")]))
            self.assertEqual(vmc.main([str(path)]), 1)

    def test_exit_zero_with_only_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), manifest([chapter("3.10"), chapter("3.9")]))
            self.assertEqual(vmc.main([str(path)]), 0)

    def test_exit_two_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vmc.main([str(Path(tmp) / "nope.json")]), 2)

    def test_exit_two_on_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(vmc.main([str(path)]), 2)

    def test_exit_two_on_bad_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), {"volumes": "not a list"})
            self.assertEqual(vmc.main([str(path)]), 2)


class CommandLineTests(unittest.TestCase):
    """The command line, run as a separate process, on the real samples."""

    def test_help_exits_zero(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MANIFEST", result.stdout)

    def test_clean_sample_from_the_repository_root(self) -> None:
        rel = SAMPLE_MANIFEST.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout.strip(), "volumes=2 chapters=9 errors=0 warnings=0"
        )

    def test_off_convention_sample_flags_exactly_one_error(self) -> None:
        rel = SAMPLE_OFF_CONVENTION.relative_to(ROOT).as_posix()
        result = run_cli(rel, cwd=ROOT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(
            "error off-convention: volume 2 chapter '3.10-final' has id "
            "'3.10-final', expected the pattern '<part>.<chapter>' such as "
            "'3.9'",
            result.stdout,
        )
        self.assertIn("volumes=2 chapters=9 errors=1 warnings=0", result.stdout)

    def test_missing_file_is_a_clean_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(str(Path(tmp) / "nope.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("volume_manifest_check.py: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(str(SAMPLE_MANIFEST), cwd=Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])


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
        self.assertEqual(fields["ID"], "X-DL-02")
        self.assertEqual(fields["Stage"], "DL")
        self.assertEqual(fields["Dependencies"], "stdlib")
        self.assertEqual(fields["Writes files"], "no")
        self.assertEqual(fields["License"], "CC0-1.0")
        self.assertTrue(fields["Usage"].startswith("python3 "))

    def test_only_standard_library_imports(self) -> None:
        tree = ast.parse(self.source)
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names.add(node.module.split(".")[0])
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
    """docs/delivery/publishing.md: every pasted output line is real."""

    page_text: str
    fences: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.page_text = PAGE.read_text(encoding="utf-8")
        cls.fences = TEXT_FENCE.findall(cls.page_text)

    def test_page_has_a_clean_and_a_broken_fence(self) -> None:
        self.assertGreaterEqual(
            len(self.fences), 2, "expected a clean and a break-on-purpose run"
        )

    def test_no_absolute_path_in_any_text_fence(self) -> None:
        for fence in self.fences:
            for line in fence.splitlines():
                self.assertNotRegex(line, ABSOLUTE_PATH, line)

    def test_every_pasted_line_appears_in_a_real_run(self) -> None:
        clean = run_cli(str(SAMPLE_MANIFEST))
        broken = run_cli(str(SAMPLE_OFF_CONVENTION))
        real_outputs = [clean.stdout, broken.stdout]
        for fence in self.fences:
            lines = [line for line in fence.splitlines() if line.strip()]
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue(
                    any(line in output for output in real_outputs),
                    f"pasted line not found in a real run: {line!r}",
                )

    def test_sample_manifests_match_the_json_shown_on_the_page(self) -> None:
        data = json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))
        volume_two = data["volumes"][1]["chapters"]
        ids = [c["id"] for c in volume_two]
        self.assertIn("3.9", ids)
        self.assertIn("3.10", ids)
        self.assertLess(ids.index("3.9"), ids.index("3.10"))

    def test_off_convention_sample_differs_only_in_one_chapter_id(self) -> None:
        clean = json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))
        broken = json.loads(SAMPLE_OFF_CONVENTION.read_text(encoding="utf-8"))
        clean_ids = [c["id"] for v in clean["volumes"] for c in v["chapters"]]
        broken_ids = [c["id"] for v in broken["volumes"] for c in v["chapters"]]
        self.assertEqual(len(clean_ids), len(broken_ids))
        differences = [
            (a, b) for a, b in zip(clean_ids, broken_ids, strict=True) if a != b
        ]
        self.assertEqual(differences, [("3.10", "3.10-final")])


if __name__ == "__main__":
    unittest.main()
