"""Tests for generate_report.py (stdlib unittest).

Run: python3 -m unittest discover -s tests -v
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import generate_report as gr  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
BAD = os.path.join(ROOT, "samples", "bad")
CLEAN = os.path.join(ROOT, "samples", "clean")


class CollectTests(unittest.TestCase):
    def test_bad_sample_counts(self):
        r = gr.collect_results(BAD)
        self.assertEqual(r["total_files"], 1)
        self.assertEqual(r["totals"]["HIGH"], 3)
        self.assertEqual(r["totals"]["WARN"], 3)
        self.assertEqual(r["total_findings"], 6)

    def test_clean_sample_counts(self):
        r = gr.collect_results(CLEAN)
        self.assertEqual(r["total_files"], 1)
        self.assertEqual(r["totals"]["HIGH"], 0)

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as d:
            r = gr.collect_results(d)
            self.assertEqual(r["total_files"], 0)
            self.assertEqual(r["total_findings"], 0)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.results = gr.collect_results(BAD)
        self.diffs = gr.load_differences()

    def test_differences_loaded(self):
        self.assertGreaterEqual(len(self.diffs), 22)
        self.assertIn("tool", self.diffs[0])

    def test_differences_schema_comment_skipped(self):
        # The CSV's first line is a "# schema-v1:" comment row; the loader
        # must skip it and still return exactly the 24 data rows.
        self.assertEqual(len(self.diffs), 24)
        self.assertEqual(self.diffs[0]["tool"], "mercurial (hg)")
        self.assertEqual(self.diffs[0]["change_type"], "removed")

    def test_markdown_sections(self):
        md = gr.render_markdown(self.results, self.diffs)
        for needle in ("Migration readiness report", "Findings by workflow",
                       "Toolset differences", "Fix checklist",
                       "FLOATING_LABEL", "REMOVED_TOOL", "mercurial"):
            self.assertIn(needle, md)

    def test_html_sections_and_escaping(self):
        page = gr.render_html(self.results, self.diffs)
        self.assertIn("<table>", page)
        self.assertIn('class="high"', page)
        fake = {"root": "<script>alert(1)</script>", "generated": "2026-10-13",
                "files": [], "totals": {"HIGH": 0, "WARN": 0},
                "total_files": 0, "total_findings": 0}
        page2 = gr.render_html(fake, [])
        self.assertNotIn("<script>alert(1)</script>", page2)
        self.assertIn("&lt;script&gt;", page2)

    def test_checklist_actions(self):
        items = gr.build_checklist(self.results)
        self.assertTrue(any("Pin the runner label" in i for i in items))
        self.assertTrue(any("Re-run the scanner" in i for i in items))
        # One checklist entry per finding plus inventory + final two items.
        self.assertEqual(len(items), self.results["total_findings"] + 3)


class MainTests(unittest.TestCase):
    def test_main_writes_both_files_and_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out")
            code = gr.main(["generate_report.py", BAD, "--out", out])
            self.assertEqual(code, 1)  # samples/bad has HIGH findings
            self.assertTrue(os.path.isfile(os.path.join(out, "migration-readiness-report.md")))
            self.assertTrue(os.path.isfile(os.path.join(out, "migration-readiness-report.html")))
            code = gr.main(["generate_report.py", CLEAN, "--out", out])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
