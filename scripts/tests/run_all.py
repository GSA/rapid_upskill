"""Run every test_*.py in this folder and print a one-line summary.

Usage: python3 -B scripts/tests/run_all.py

The folder is found relative to this file, so the command works from any
working directory. Tests use only the standard library and run offline.
A test module that cannot be imported is reported as an error, never skipped
silently. Exit code 0 means every test passed; 1 means a failure, an error, or
no tests at all.
"""

import io
import sys
import time
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

TESTS_DIR = Path(__file__).resolve().parent


def main() -> int:
    """Discover and run the tests; return the process exit code."""
    suite = unittest.TestLoader().discover(
        str(TESTS_DIR), pattern="test_*.py", top_level_dir=str(TESTS_DIR)
    )
    report = io.StringIO()
    runner = unittest.TextTestRunner(stream=report, verbosity=1)
    started = time.perf_counter()
    result = runner.run(suite)
    seconds = time.perf_counter() - started

    failed = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = result.testsRun - failed - errors - skipped
    ok = result.wasSuccessful() and result.testsRun > 0
    if not ok:
        print(report.getvalue(), file=sys.stderr)
    if result.testsRun == 0:
        print(f"No tests found in {TESTS_DIR}", file=sys.stderr)
    print(
        f"run_all: {result.testsRun} tests, {passed} passed, {failed} failed, "
        f"{errors} errors, {skipped} skipped in {seconds:.2f}s - "
        f"{'OK' if ok else 'FAILED'}"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
