"""Tests for Markdown summary export (runner_drift_audit --summary-file).

Run: python3 -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import runner_drift_audit as rda  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
BAD = os.path.join(ROOT, "samples", "bad")
CLEAN = os.path.join(ROOT, "samples", "clean")
SCANNER = os.path.join(ROOT, "runner_drift_audit.py")


def summary_for(root):
    per_file = [(p, rda.audit_file(p)) for p in rda.find_workflows(root)]
    return rda.build_markdown_summary(per_file, root)


class BuildSummaryTests(unittest.TestCase):
    def test_bad_sample_counts_and_table(self):
        md = summary_for(BAD)
        self.assertIn("## Runner Drift Audit", md)
        # samples/bad is pinned at 3 HIGH + 3 WARN by the report tests.
        self.assertIn("**3 HIGH**, **3 WARN**", md)
        self.assertIn("`.github/workflows/ci.yml`", md)
        self.assertIn("| Severity | Line | Rule | Finding |", md)
        self.assertEqual(md.count("| HIGH |"), 3)
        self.assertEqual(md.count("| WARN |"), 3)

    def test_clean_sample_listed(self):
        md = summary_for(CLEAN)
        self.assertIn("**0 HIGH**", md)
        self.assertIn("ci.yml", md)

    def test_empty_scan(self):
        md = rda.build_markdown_summary([], ".")
        self.assertIn("Scanned 0 workflow file(s)", md)
        self.assertIn("No workflow files were found", md)

    def test_pipe_in_message_escaped(self):
        per_file = [("x/.github/workflows/a.yml",
                     [("HIGH", 1, "RULE", "a | b")])]
        md = rda.build_markdown_summary(per_file, "x")
        self.assertIn("a \\| b", md)


class CliSummaryTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, SCANNER, *args],
            capture_output=True, text=True)

    def test_summary_file_written_and_exit_code_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "summary.md")
            proc = self.run_cli(BAD, "--summary-file", out)
            self.assertEqual(proc.returncode, 1)  # HIGH findings present
            with open(out, encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("**3 HIGH**, **3 WARN**", md)
            self.assertIn("Markdown summary written to", proc.stdout)

    def test_summary_file_equals_form_clean(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "summary.md")
            proc = self.run_cli(CLEAN, f"--summary-file={out}")
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(os.path.exists(out))

    def test_summary_file_requires_argument(self):
        proc = self.run_cli(BAD, "--summary-file")
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
