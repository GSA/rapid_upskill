"""Syntax-check every JavaScript file under docs/assets/js with ``node --check``.

``node --check`` parses a file without running it and writes nothing to disk.
If Node.js is not installed, the tests are skipped and say so.

Run from the repository root:

    python3 scripts/tests/test_js_syntax.py
"""

import shutil
import subprocess  # nosec B404
import sys
import unittest
from pathlib import Path
from typing import List

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
JS_DIR = REPO_ROOT / "docs" / "assets" / "js"
TIMEOUT_SECONDS = 30
SKIP_MESSAGE = (
    "Node.js ('node') is not installed; skipping the JavaScript syntax check."
)


def js_files(js_dir: Path) -> List[Path]:
    """Return the JavaScript files directly inside ``js_dir``, sorted."""
    return sorted(js_dir.glob("*.js"))


class JavaScriptSyntaxTest(unittest.TestCase):
    """Run ``node --check`` on each JavaScript file the site ships."""

    node: str

    def setUp(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest(SKIP_MESSAGE)
        self.node = node

    def test_js_directory_has_files(self) -> None:
        """A missing folder or an empty one would make the syntax check vacuous."""
        self.assertTrue(JS_DIR.is_dir(), f"missing folder: {JS_DIR}")
        self.assertTrue(js_files(JS_DIR), f"no .js files found in {JS_DIR}")

    def test_each_file_parses(self) -> None:
        """Every .js file must pass ``node --check``."""
        for path in js_files(JS_DIR):
            name = path.relative_to(REPO_ROOT).as_posix()
            with self.subTest(file=name):
                result = subprocess.run(  # nosec B603
                    [self.node, "--check", str(path)],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=TIMEOUT_SECONDS,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"node --check failed for {name}:\n{result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
