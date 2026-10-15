"""Marketplace metadata guards for action.yml.

The GitHub Marketplace publish form rejects an action whose top-level
`description` is 125 characters or longer. That limit is only reported
on the release-edit page, so pin it here: v0.3.2 shipped a 147-char
description, which would have blocked the listing even after ticking
"Publish this Action to the GitHub Marketplace".

Run: python3 -m unittest discover -s tests -v
"""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
ACTION_YML = os.path.join(ROOT, "action.yml")


def read_action_yml():
    with open(ACTION_YML, encoding="utf-8") as fh:
        return fh.read()


def top_level_value(text, key):
    m = re.search(rf"^{key}:\s*\"([^\"]*)\"\s*$", text, re.MULTILINE)
    if m is None:
        m = re.search(rf"^{key}:\s*(\S.*)$", text, re.MULTILINE)
    return m.group(1) if m else None


class ActionMetadataTests(unittest.TestCase):
    def test_description_under_marketplace_limit(self):
        desc = top_level_value(read_action_yml(), "description")
        self.assertIsNotNone(desc)
        self.assertLess(
            len(desc), 125,
            f"action.yml description is {len(desc)} characters; "
            "the Marketplace limit is under 125.")

    def test_name_and_author_present(self):
        text = read_action_yml()
        self.assertIsNotNone(top_level_value(text, "name"))
        self.assertIsNotNone(top_level_value(text, "author"))

    def test_branding_icon_and_color_present(self):
        text = read_action_yml()
        self.assertRegex(text, r"(?m)^branding:\s*$")
        self.assertRegex(text, r"(?m)^  icon:\s*\"[^\"]+\"\s*$")
        self.assertRegex(text, r"(?m)^  color:\s*\"[^\"]+\"\s*$")


if __name__ == "__main__":
    unittest.main()
