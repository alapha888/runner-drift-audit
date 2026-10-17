"""Tests for plain JSON export (runner_drift_audit --json).

Run: python3 -m unittest discover -s tests -v
"""
import json
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


def json_for(root):
    per_file = [(p, rda.audit_file(p)) for p in rda.find_workflows(root)]
    return rda.build_json_report(per_file, root)


class BuildJsonTests(unittest.TestCase):
    def test_structure(self):
        rep = json_for(BAD)
        self.assertEqual(rep["tool"], "RunnerDriftAudit")
        self.assertEqual(rep["schema_version"], 1)
        self.assertEqual(rep["summary"]["files_scanned"], 1)
        # samples/bad is pinned by the report tests at 3 HIGH + 3 WARN.
        self.assertEqual(rep["summary"]["high"], 3)
        self.assertEqual(rep["summary"]["warn"], 3)
        self.assertEqual(rep["summary"]["findings"], 6)

    def test_bad_sample_entries(self):
        rep = json_for(BAD)
        self.assertEqual(len(rep["files"]), 1)
        entry = rep["files"][0]
        # Path must be repo-relative, matching the SARIF export.
        self.assertEqual(entry["path"], ".github/workflows/ci.yml")
        self.assertEqual(len(entry["findings"]), 6)
        for f in entry["findings"]:
            self.assertIn(f["severity"], ("HIGH", "WARN"))
            self.assertIn(f["rule"], rda.SARIF_RULES)
            self.assertGreaterEqual(f["line"], 1)
            self.assertTrue(f["message"])

    def test_clean_sample_lists_file_with_no_high(self):
        # "clean" means 0 HIGH; it still carries 1 WARN (an action
        # referenced by a mutable tag), pinned by the report tests.
        rep = json_for(CLEAN)
        self.assertEqual(rep["summary"]["high"], 0)
        self.assertEqual(rep["summary"]["warn"], 1)
        self.assertEqual(len(rep["files"]), 1)
        self.assertEqual(len(rep["files"][0]["findings"]), 1)

    def test_empty_scan(self):
        rep = rda.build_json_report([], ".")
        self.assertEqual(rep["summary"],
                         {"files_scanned": 0, "high": 0, "warn": 0,
                          "findings": 0})
        self.assertEqual(rep["files"], [])


class CliJsonTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, SCANNER, *args],
            capture_output=True, text=True)

    def test_cli_writes_json_and_keeps_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "report.json")
            proc = self.run_cli(BAD, "--json", out)
            # bad sample has HIGH findings: exit code stays 1.
            self.assertEqual(proc.returncode, 1)
            self.assertIn("JSON report written to", proc.stdout)
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
            self.assertEqual(rep["summary"]["high"], 3)
            self.assertEqual(rep["summary"]["findings"], 6)

    def test_cli_json_equals_form(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "report.json")
            proc = self.run_cli(CLEAN, f"--json={out}")
            self.assertEqual(proc.returncode, 0)
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
            self.assertEqual(rep["summary"]["high"], 0)

    def test_cli_no_workflows_still_writes_json(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "report.json")
            proc = self.run_cli(td, "--json", out)
            self.assertEqual(proc.returncode, 0)
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
            self.assertEqual(rep["summary"]["files_scanned"], 0)

    def test_cli_json_requires_path(self):
        proc = self.run_cli(BAD, "--json")
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
