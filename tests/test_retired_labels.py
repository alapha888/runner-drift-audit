"""Tests for RETIRED_LABEL detection: labels whose runner image is
removed on a published date (macos-14 family, retired November 2, 2026
per GitHub Changelog 2026-10-01). A pinned label does not drift, so
these must be caught on every path a floating label can appear on —
and supported pinned labels must stay silent.

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


def retired(findings):
    return [f for f in findings if f[2] == "RETIRED_LABEL"]


class RetiredLabelTests(unittest.TestCase):
    def test_direct_runs_on(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: macos-14\n"))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], "HIGH")
        self.assertIn("November 2, 2026", findings[0][3])
        self.assertIn("macos-15", findings[0][3])

    def test_all_three_labels(self):
        for lab in ("macos-14", "macos-14-large", "macos-14-xlarge"):
            findings = retired(audit(
                f"jobs:\n  t:\n    runs-on: {lab}\n"))
            self.assertEqual(len(findings), 1, lab)

    def test_quoted_and_inline_list(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: ['macos-14-large']\n"))
        self.assertEqual(len(findings), 1)

    def test_inline_matrix_axis(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.os }}\n"
            "    strategy:\n      matrix:\n"
            "        os: [macos-14-xlarge, macos-15]\n"))
        self.assertEqual(len(findings), 1)
        self.assertIn("matrix axis", findings[0][3])

    def test_block_matrix_axis_items(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.os }}\n"
            "    strategy:\n      matrix:\n        os:\n"
            "          - macos-14\n          - macos-15\n"))
        self.assertEqual(len(findings), 1)

    def test_multiline_runs_on_list(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on:\n      - macos-14\n"))
        self.assertEqual(len(findings), 1)

    def test_runner_key_assignment_referenced(self):
        findings = retired(audit(
            "env:\n  RUNNER_LABEL: macos-14\n"
            "jobs:\n  t:\n    runs-on: ${{ env.RUNNER_LABEL }}\n"))
        self.assertEqual(len(findings), 1)
        self.assertIn("RUNNER_LABEL", findings[0][3])

    def test_runs_on_trailing_comment(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: macos-14 # pinned for now\n"))
        self.assertEqual(len(findings), 1)

    def test_matrix_include_entry(self):
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: ${{ matrix.os }}\n"
            "    strategy:\n      matrix:\n        include:\n"
            "          - os: macos-14\n"))
        self.assertEqual(len(findings), 1)
        self.assertIn("matrix key", findings[0][3])

    def test_env_key_without_runner_in_name(self):
        findings = audit(
            "env:\n  OS: macos-14\n"
            "jobs:\n  t:\n    runs-on: ${{ env.OS }}\n")
        self.assertEqual(len(retired(findings)), 1)
        self.assertIn("env.OS", retired(findings)[0][3])
        self.assertEqual(
            [f for f in findings if f[2] == "INDIRECT_RUNS_ON"], [])


class CodexReviewRegressionTests(unittest.TestCase):
    """Companion fixes from the v0.3.7 code review: the same holes
    existed on the floating-label path."""

    def test_floating_runs_on_trailing_comment(self):
        findings = audit(
            "jobs:\n  t:\n    runs-on: ubuntu-latest # temp\n")
        self.assertEqual(
            len([f for f in findings if f[2] == "FLOATING_LABEL"]), 1)

    def test_env_key_floating_label(self):
        findings = audit(
            "env:\n  OS: ubuntu-latest\n"
            "jobs:\n  t:\n    runs-on: ${{ env.OS }}\n")
        self.assertEqual(
            len([f for f in findings if f[2] == "FLOATING_LABEL"]), 1)

    def test_env_key_supported_label_resolves_clean(self):
        findings = audit(
            "env:\n  OS: ubuntu-24.04\n"
            "jobs:\n  t:\n    runs-on: ${{ env.OS }}\n")
        self.assertEqual(findings, [])


class RetiredFalsePositiveGuardTests(unittest.TestCase):
    def test_supported_pinned_labels_not_flagged(self):
        for lab in ("macos-15", "macos-26", "macos-15-large",
                    "ubuntu-24.04", "windows-2022"):
            findings = retired(audit(
                f"jobs:\n  t:\n    runs-on: {lab}\n"))
            self.assertEqual(findings, [], lab)

    def test_unreferenced_runner_key_not_flagged(self):
        findings = retired(audit(
            "env:\n  BASELINE_RUNNER: macos-14\n"
            "jobs:\n  t:\n    runs-on: macos-15\n"))
        self.assertEqual(findings, [])

    def test_similar_names_not_flagged(self):
        # A step argument or a name merely containing the label text is
        # not a runner label.
        findings = retired(audit(
            "jobs:\n  t:\n    runs-on: macos-15\n"
            "    steps:\n      - run: echo macos-14\n"))
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
