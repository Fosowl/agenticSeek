import unittest
import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SPOOFING = os.path.join(os.path.dirname(__file__), "..", "sources", "web_scripts", "spoofing.js")


class TestSpoofingScriptStatic(unittest.TestCase):
    """
    Static guards for the exact bugs the old spoofing.js shipped with:
    undefined original references, per-read randomness, deleted real APIs.
    """

    @classmethod
    def setUpClass(cls):
        with open(SPOOFING, "r", encoding="utf-8") as f:
            cls.src = f.read()

    def test_is_single_iife(self):
        no_comments = re.sub(r"/\*.*?\*/", "", self.src, flags=re.S).lstrip()
        self.assertTrue(no_comments.startswith("(() => {"))

    def test_reads_injected_identity(self):
        self.assertIn("__IDENTITY__", self.src)

    def test_does_not_delete_real_apis(self):
        self.assertNotIn("RTCPeerConnection = undefined", self.src)
        self.assertNotIn("webkitRTCPeerConnection = undefined", self.src)
        self.assertNotIn("class Notification", self.src)
        self.assertNotIn("defineProperty(document, 'fonts'", self.src.replace('"', "'"))
        self.assertNotIn("window.AudioContext = ", self.src)

    def test_native_tostring_cover(self):
        self.assertIn("[native code]", self.src)
        self.assertIn("Function.prototype.toString", self.src)

    def test_cdc_cleanup_is_pattern_based(self):
        self.assertIn("cdc_", self.src)
        self.assertNotIn("cdc_adoQpoasnfa76pfcZLmcfl_Array", self.src)

    def test_no_console_output(self):
        self.assertNotIn("console.", self.src)


if __name__ == "__main__":
    unittest.main()
