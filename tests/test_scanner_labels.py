"""Tests for floating-label detection beyond a plain `runs-on:` line:
matrix axes (inline bracket lists and block list items), multi-line
`runs-on:` lists, and per-OS message wording.

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


def floating(findings):
    return [f for f in findings if f[2] == "FLOATING_LABEL"]


class MatrixLabelTests(unittest.TestCase):
    def test_inline_matrix_axis(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.os }}\n"
            "    strategy:\n      matrix:\n"
            "        os: [ubuntu-latest, windows-latest]\n"))
        self.assertEqual(len(findings), 2)
        msgs = " ".join(f[3] for f in findings)
        self.assertIn("ubuntu-latest", msgs)
        self.assertIn("windows-latest", msgs)
        self.assertIn("matrix axis", msgs)

    def test_block_matrix_axis_items(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.os }}\n"
            "    strategy:\n      matrix:\n        os:\n"
            "          - ubuntu-latest\n          - macos-latest\n"))
        self.assertEqual(len(findings), 2)

    def test_multiline_runs_on_list(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on:\n      - ubuntu-latest\n"))
        self.assertEqual(len(findings), 1)

    def test_pinned_matrix_not_flagged(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.os }}\n"
            "    strategy:\n      matrix:\n"
            "        os: [ubuntu-24.04, windows-2022]\n"))
        self.assertEqual(findings, [])

    def test_runs_on_inline_list_not_double_counted(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: [ubuntu-latest]\n"))
        self.assertEqual(len(findings), 1)


class FalsePositiveGuardTests(unittest.TestCase):
    def test_unrelated_bracket_axis_not_flagged(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ubuntu-24.04\n"
            "    strategy:\n      matrix:\n"
            "        browser: [chrome-latest, edge-latest]\n"))
        self.assertEqual(findings, [])

    def test_non_runner_list_items_not_flagged(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ubuntu-24.04\n"
            "    steps:\n      - uses: actions/checkout@v4\n"
            "      - run: echo hi\n        with:\n"
            "          args:\n            - docker-latest\n"))
        self.assertEqual(findings, [])

    def test_custom_runner_axis_referenced_via_matrix(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.runner }}\n"
            "    strategy:\n      matrix:\n"
            "        runner: [ubuntu-latest]\n"))
        self.assertEqual(len(findings), 1)


class MessageWordingTests(unittest.TestCase):
    def test_ubuntu_message_names_the_migration(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: ubuntu-latest\n"))
        self.assertEqual(len(findings), 1)
        self.assertIn("24.04 -> 26.04", findings[0][3])

    def test_windows_message_does_not_claim_ubuntu_move(self):
        findings = floating(audit(
            "jobs:\n  t:\n    runs-on: windows-latest\n"))
        self.assertEqual(len(findings), 1)
        self.assertNotIn("24.04 -> 26.04", findings[0][3])
        self.assertIn("floating label", findings[0][3])


if __name__ == "__main__":
    unittest.main()
