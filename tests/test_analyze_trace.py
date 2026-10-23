"""Tests for running the trace analyzer as a script."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "swiftui-expert-skill"
    / "scripts"
    / "analyze_trace.py"
)


class SafePathTests(unittest.TestCase):
    def test_runs_when_script_folder_is_not_on_sys_path(self) -> None:
        # `-P` matches PYTHONSAFEPATH=1: Python no longer puts the script's
        # folder on sys.path, so the sibling `instruments_parser` package
        # must still be found.
        result = subprocess.run(
            [sys.executable, "-P", str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("usage: analyze_trace.py", result.stdout)


if __name__ == "__main__":
    unittest.main()
