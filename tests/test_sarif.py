"""Tests for SARIF 2.1.0 export (runner_drift_audit --sarif).

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


def sarif_for(root):
    per_file = [(p, rda.audit_file(p)) for p in rda.find_workflows(root)]
    return rda.build_sarif(per_file, root)


class BuildSarifTests(unittest.TestCase):
    def test_structure(self):
        log = sarif_for(BAD)
        self.assertEqual(log["version"], "2.1.0")
        run = log["runs"][0]
        self.assertEqual(run["tool"]["driver"]["name"], "RunnerDriftAudit")
        rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
        self.assertEqual(rule_ids, set(rda.SARIF_RULES))

    def test_bad_sample_results(self):
        log = sarif_for(BAD)
        results = log["runs"][0]["results"]
        # samples/bad is pinned by the report tests at 3 HIGH + 3 WARN.
        self.assertEqual(len(results), 6)
        levels = [r["level"] for r in results]
        self.assertEqual(levels.count("error"), 3)
        self.assertEqual(levels.count("warning"), 3)
        for r in results:
            self.assertIn(r["ruleId"], rda.SARIF_RULES)
            loc = r["locations"][0]["physicalLocation"]
            # URI must be repo-relative so Code Scanning can map it.
            self.assertEqual(loc["artifactLocation"]["uri"],
                             ".github/workflows/ci.yml")
            self.assertGreaterEqual(loc["region"]["startLine"], 1)
            self.assertTrue(r["message"]["text"])

    def test_clean_sample_has_no_errors_but_lists_rules(self):
        # "clean" means 0 HIGH; it still carries 1 WARN (an action
        # referenced by a mutable tag), pinned by the report tests.
        log = sarif_for(CLEAN)
        results = log["runs"][0]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["level"], "warning")
        self.assertEqual(results[0]["ruleId"], "UNPINNED_ACTION")
        self.assertTrue(log["runs"][0]["tool"]["driver"]["rules"])


class CliSarifTests(unittest.TestCase):
    def run_cli(self, root):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.sarif")
            proc = subprocess.run(
                [sys.executable, SCANNER, root, "--sarif", out],
                capture_output=True, text=True)
            with open(out, encoding="utf-8") as fh:
                log = json.load(fh)
            return proc, log

    def test_cli_bad_sample_exit_1_and_valid_json(self):
        proc, log = self.run_cli(BAD)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(len(log["runs"][0]["results"]), 6)

    def test_cli_clean_sample_exit_0(self):
        proc, log = self.run_cli(CLEAN)
        self.assertEqual(proc.returncode, 0)
        results = log["runs"][0]["results"]
        self.assertEqual(len(results), 1)
        self.assertNotIn("error", [r["level"] for r in results])


if __name__ == "__main__":
    unittest.main()
