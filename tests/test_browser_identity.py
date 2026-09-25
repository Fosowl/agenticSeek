import unittest
import os
import sys
import json
import tempfile

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.browser_identity import (
    BrowserIdentity, DEVICE_PROFILES, load_or_create_identity, locale_for,
)


class TestBrowserIdentity(unittest.TestCase):
    """Consistency and persistence rules of the stealth identity."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = os.path.join(self.tmp.name, "identity.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_identity_is_persisted_and_reused(self):
        first = load_or_create_identity(state_file=self.state, chrome_major=137, lang="en")
        second = load_or_create_identity(state_file=self.state, chrome_major=137, lang="en")
        self.assertEqual(first.label, second.label)
        self.assertEqual(first.seed, second.seed)
        with open(self.state) as f:
            stored = json.load(f)
        self.assertEqual(stored["label"], first.label)

    def test_chrome_major_change_repicks_identity(self):
        first = load_or_create_identity(state_file=self.state, chrome_major=137, lang="en")
        upgraded = load_or_create_identity(state_file=self.state, chrome_major=140, lang="en")
        self.assertEqual(upgraded.chrome_major, 140)
        self.assertIn("Chrome/140.0.0.0", upgraded.user_agent)
        self.assertNotEqual(upgraded.label, first.label)

    def test_accept_lang_is_valid(self):
        for lang, expected in [("en", "en-US,en"), ("fr", "fr-FR,fr")]:
            ident = load_or_create_identity(
                state_file=os.path.join(self.tmp.name, f"{lang}.json"), chrome_major=137, lang=lang)
            self.assertEqual(ident.accept_lang, expected)
            self.assertEqual(ident.locale, expected.split(",")[0])

    def test_locale_map(self):
        self.assertEqual(locale_for("en"), "en-US")
        self.assertEqual(locale_for("zh"), "zh-CN")
        self.assertEqual(locale_for("xx"), "xx-XX")

    def test_ua_matches_platform_and_version(self):
        for profile in DEVICE_PROFILES:
            ident = BrowserIdentity(profile, 137, "137.0.7151.68", ["en-US", "en"], None, 42)
            ua = ident.user_agent
            self.assertIn(f"Chrome/137.0.0.0", ua)
            token = {"windows": "Windows NT", "macos": "Macintosh", "linux": "X11"}[profile["os"]]
            self.assertIn(token, ua)
            self.assertEqual(ident.navigator_platform, profile["navigator_platform"])

    def test_window_size_fits_screen(self):
        for profile in DEVICE_PROFILES:
            ident = BrowserIdentity(profile, 137, "137.0.7151.68", ["en-US", "en"], None, 42)
            w, h = ident.window_size
            self.assertLessEqual(w, profile["screen"]["width"])
            self.assertLessEqual(h, profile["screen"]["avail_height"])

    def test_cdp_metadata_consistent(self):
        for profile in DEVICE_PROFILES:
            ident = BrowserIdentity(profile, 137, "137.0.7151.68", ["en-US", "en"], None, 42)
            meta = ident.to_cdp_user_agent_metadata()
            self.assertEqual(meta["platform"], profile["client_hint_platform"])
            self.assertEqual(meta["platformVersion"], profile["platform_version"])
            self.assertFalse(meta["mobile"])
            versions = {b["version"] for b in meta["brands"]}
            self.assertIn("137", versions)

    def test_js_payload_shape(self):
        ident = load_or_create_identity(state_file=self.state, chrome_major=137, lang="en")
        js = ident.to_js()
        for key in ("navigator", "screen", "webgl", "seed"):
            self.assertIn(key, js)
        for key in ("platform", "vendor", "languages", "hardwareConcurrency",
                    "deviceMemory", "userAgentData"):
            self.assertIn(key, js["navigator"])
        # every WebGL enum the spoof intercepts must be provided
        for key in ("vendor", "renderer", "unmasked_vendor", "unmasked_renderer",
                    "version", "shading_language_version"):
            self.assertIn(key, js["webgl"])

    def test_persona_matches_host_os(self):
        import sources.browser_identity as bi
        with patch.object(bi, "host_os", return_value="windows"):
            ident = bi.load_or_create_identity(
                state_file=os.path.join(self.tmp.name, "h.json"), chrome_major=137, lang="en")
            self.assertEqual(ident.os, "windows")
        with patch.object(bi, "host_os", return_value="linux"):
            # a persona saved on another OS class must be re-picked
            ident2 = bi.load_or_create_identity(
                state_file=os.path.join(self.tmp.name, "h.json"), chrome_major=137, lang="en")
            self.assertEqual(ident2.os, "linux")

    def test_corrupt_state_does_not_crash(self):
        bad = os.path.join(self.tmp.name, "bad.json")
        with open(bad, "w") as f:
            f.write('{"schema_version": 1, "chrome_major": null}')
        ident = load_or_create_identity(state_file=bad, chrome_major=137, lang="en")
        self.assertEqual(ident.chrome_major, 137)

    def test_state_roundtrip(self):
        ident = load_or_create_identity(state_file=self.state, chrome_major=137, lang="en")
        restored = BrowserIdentity.from_state(json.loads(json.dumps(ident.to_state())))
        self.assertEqual(restored.label, ident.label)
        self.assertEqual(restored.seed, ident.seed)
        self.assertEqual(restored.navigator_platform, ident.navigator_platform)


if __name__ == "__main__":
    unittest.main()
