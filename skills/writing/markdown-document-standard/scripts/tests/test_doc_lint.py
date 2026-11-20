#!/usr/bin/env python3
"""Tests for doc_lint.py. Run: python3 test_doc_lint.py"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "doc_lint.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPT.parent))

import doc_lint  # noqa: E402


def lint(name, **kwargs):
    cfg = doc_lint.Config(**kwargs)
    return doc_lint.lint_file(FIXTURES / name, cfg)


def codes(findings):
    return [f.code for f in findings]


class CleanDocumentTests(unittest.TestCase):
    def test_clean_document_has_no_findings(self):
        findings = lint("good/clean.md", doctype="design")
        self.assertEqual(findings, [], [f.__dict__ for f in findings])

    def test_clean_document_passes_strict_cli(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--strict", str(FIXTURES / "good/clean.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_legacy_profile_downgrades_h1_and_jump(self):
        findings = lint("good/legacy.md", profile="legacy")
        self.assertEqual(set(codes(findings)), {"MD001", "MD002"})
        self.assertTrue(all(f.severity == "warn" for f in findings))

    def test_json_report_shape(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "-", str(FIXTURES / "good/clean.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], doc_lint.SCHEMA_VERSION)
        self.assertEqual(payload["summary"]["errors"], 0)
        self.assertEqual(len(payload["files"]), 1)


class ErrorRuleTests(unittest.TestCase):
    def test_md001_multiple_h1(self):
        findings = lint("bad/h1.md")
        self.assertIn("MD001", codes(findings))

    def test_md002_heading_jump(self):
        findings = lint("bad/jump.md")
        self.assertIn("MD002", codes(findings))

    def test_md005_unclosed_fence(self):
        findings = lint("bad/fence.md")
        self.assertIn("MD005", codes(findings))

    def test_md007_bad_separator(self):
        findings = lint("bad/table-separator.md")
        self.assertIn("MD007", codes(findings))

    def test_md008_column_mismatch(self):
        findings = lint("bad/table-columns.md")
        self.assertIn("MD008", codes(findings))

    def test_md012_missing_relative_link(self):
        findings = lint("bad/link.md")
        self.assertIn("MD012", codes(findings))

    def test_md014_ascii_too_wide(self):
        findings = lint("bad/ascii.md")
        self.assertIn("MD014", codes(findings))

    def test_md015_tab_in_ascii(self):
        findings = lint("bad/ascii.md")
        self.assertIn("MD015", codes(findings))

    def test_md018_missing_metadata(self):
        findings = lint("bad/metadata.md", doctype="design")
        missing = [f for f in findings if f.code == "MD018"]
        self.assertEqual(len(missing), 1)
        self.assertIn("适用版本", missing[0].message)

    def test_bad_document_exits_one(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "bad/h1.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_strict_warning_exits_one(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--strict", "--doctype", "design",
             str(FIXTURES / "bad/metadata.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_ignore_suppresses_code(self):
        findings = lint("bad/h1.md", ignore={"MD001"})
        self.assertNotIn("MD001", codes(findings))


if __name__ == "__main__":
    unittest.main()
