"""Regression tests for the duplicate-count defect found 2026-10-20
(codex review + probe-verified): a workflow whose `runs-on:` is fed by
`${{ matrix.runs-on }}` and whose `matrix.include:` has a `- runs-on:
<label>` entry was reported twice for that one physical line — once by
the assignment pass (the key is a referenced matrix key) and once by
the main `runs-on:` pass. Findings now dedupe on (line, rule, label)
per file; genuinely different findings (another line, another rule, or
another label on the same line) must still be reported separately.

Fleet-level duplicates (symlink aliases, hidden dot-directories) live
in fleet_audit.py, which is not part of this free-edition repo — it
ships in the Pro package repo (runner-drift-audit-pro); its regression
tests belong there.

Run: python3 -m unittest discover -s tests -v
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import runner_drift_audit as rda  # noqa: E402


def audit(text):
    with tempfile.NamedTemporaryFile(
            "w", suffix=".yml", delete=False, encoding="utf-8") as fh:
        fh.write(text)
        path = fh.name
    try:
        return rda.audit_file(path)
    finally:
        os.unlink(path)


INCLUDE_RUNS_ON = (
    "name: CI\n"                                   # 1
    "on: push\n"                                   # 2
    "jobs:\n"                                      # 3
    "  test:\n"                                    # 4
    "    runs-on: ${{ matrix.runs-on }}\n"         # 5
    "    strategy:\n"                              # 6
    "      matrix:\n"                              # 7
    "        include:\n"                           # 8
    "          - runs-on: {label}\n"               # 9
    "    steps:\n"
    "      - run: echo hi\n"
)


class MatrixIncludeRunsOnDedupeTests(unittest.TestCase):
    def test_floating_label_reported_once(self):
        findings = audit(INCLUDE_RUNS_ON.format(label="ubuntu-latest"))
        fl = [f for f in findings if f[2] == "FLOATING_LABEL"]
        self.assertEqual(len(fl), 1)
        self.assertEqual(fl[0][1], 9)
        self.assertEqual(
            len([f for f in findings if f[0] == "HIGH"]), 1)

    def test_retired_label_reported_once(self):
        findings = audit(INCLUDE_RUNS_ON.format(label="macos-14"))
        rt = [f for f in findings if f[2] == "RETIRED_LABEL"]
        self.assertEqual(len(rt), 1)
        self.assertEqual(rt[0][1], 9)


class DistinctFindingsPreservedTests(unittest.TestCase):
    def test_two_labels_on_one_line_both_reported(self):
        findings = audit(
            "jobs:\n  t:\n"
            "    runs-on: [ubuntu-latest, windows-latest]\n")
        fl = [f for f in findings if f[2] == "FLOATING_LABEL"]
        self.assertEqual(len(fl), 2)

    def test_same_label_on_different_lines_both_reported(self):
        findings = audit(
            "jobs:\n  t:\n    runs-on: [ubuntu-latest, windows-latest]\n"
            "  u:\n    runs-on: ubuntu-latest\n")
        fl = [f for f in findings if f[2] == "FLOATING_LABEL"]
        self.assertEqual(len(fl), 3)

    def test_different_rules_on_one_line_both_reported(self):
        findings = audit(
            "jobs:\n  t:\n"
            "    runs-on: [ubuntu-latest, macos-14]\n")
        self.assertEqual(
            len([f for f in findings if f[2] == "FLOATING_LABEL"]), 1)
        self.assertEqual(
            len([f for f in findings if f[2] == "RETIRED_LABEL"]), 1)


if __name__ == "__main__":
    unittest.main()
