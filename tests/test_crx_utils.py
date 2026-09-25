import unittest
import os
import sys
import json
import tempfile
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.crx_utils import extract_crx, default_extract_dir, extension_installed

REAL_CRX = os.path.join(os.path.dirname(__file__), "..", "crx", "nopecha.crx")


class TestCrxExtraction(unittest.TestCase):
    """The anti-captcha CRX must unpack into a --load-extension-able dir."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dest = os.path.join(self.tmp.name, "nopecha")

    def tearDown(self):
        self.tmp.cleanup()

    def test_extracts_real_crx_with_manifest(self):
        out = extract_crx(REAL_CRX, dest_dir=self.dest)
        self.assertIsNotNone(out)
        manifest_path = os.path.join(out, "manifest.json")
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path) as f:
            manifest = json.load(f)
        self.assertEqual(manifest["name"], "NopeCHA: CAPTCHA Solver")

    def test_extraction_is_cached(self):
        first = extract_crx(REAL_CRX, dest_dir=self.dest)
        marker = os.path.join(self.dest, "manifest.json")
        os.remove(marker)
        second = extract_crx(REAL_CRX, dest_dir=self.dest)  # manifest gone -> re-extracts
        self.assertEqual(first, second)
        self.assertTrue(os.path.exists(marker))

    def test_missing_file_returns_none(self):
        self.assertIsNone(extract_crx("/nonexistent/nopecha.crx", dest_dir=self.dest))

    def test_garbage_returns_none(self):
        garbage = os.path.join(self.tmp.name, "garbage.crx")
        with open(garbage, "wb") as f:
            f.write(b"definitely not a zip")
        self.assertIsNone(extract_crx(garbage, dest_dir=os.path.join(self.tmp.name, "g")))

    def test_zip_slip_rejected(self):
        evil = os.path.join(self.tmp.name, "evil.crx")
        with zipfile.ZipFile(evil, "w") as zf:
            zf.writestr("../../evil.txt", "pwn")
        self.assertIsNone(extract_crx(evil, dest_dir=os.path.join(self.tmp.name, "e")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "evil.txt")))

    def test_default_dir_under_browser_profile(self):
        self.assertIn(os.path.join(".browser_profile", "extensions"),
                      default_extract_dir("./crx/nopecha.crx"))


if __name__ == "__main__":
    unittest.main()
