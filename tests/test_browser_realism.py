import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock

for mod_name in [
    'torch', 'transformers', 'kokoro', 'adaptive_classifier', 'text2emotion',
    'ollama', 'openai', 'together', 'IPython', 'IPython.display',
    'playsound3', 'soundfile', 'pyaudio', 'librosa',
    'pypdf', 'langid', 'pypinyin', 'num2words', 'sentencepiece', 'sacremoses',
    'scipy', 'numpy', 'selenium_stealth', 'undetected_chromedriver',
    'markdownify', 'chromedriver_autoinstaller', 'fake_useragent',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

os.environ.setdefault('WORK_DIR', '/tmp')

from sources.browser import Browser


class FakeDriver:
    def __init__(self):
        self.cdp_calls = []
        self.scripts = []
        self.get_calls = []
        self.current_url = "http://start.example/"

    def execute_cdp_cmd(self, cmd, params):
        self.cdp_calls.append((cmd, params))

    def execute_script(self, script, *args):
        self.scripts.append((script, args))
        if "location.assign" in script:
            self.current_url = args[0]  # simulate navigation starting

    def get(self, url):
        self.get_calls.append(url)
        self.current_url = url


def bare_browser(driver):
    b = Browser.__new__(Browser)
    b.driver = driver
    b.logger = MagicMock()
    return b


class TestInputRealism(unittest.TestCase):
    """human typing, movement and wheel scrolling replace instant automation."""

    def _browser(self):
        self.driver = FakeDriver()
        return bare_browser(self.driver)

    def test_human_type_types_char_by_char_with_delays(self):
        b = self._browser()
        element = MagicMock()
        with patch("sources.browser.time.sleep") as mock_sleep:
            b.human_type(element, "hello")
        typed = "".join(c.args[0] for c in element.send_keys.call_args_list)
        self.assertEqual(typed, "hello")
        self.assertEqual(element.send_keys.call_count, 5)
        self.assertGreaterEqual(mock_sleep.call_count, 5)  # a delay per keystroke

    def test_human_type_falls_back_to_bulk_send(self):
        b = self._browser()
        element = MagicMock()
        element.send_keys.side_effect = [Exception("boom"), None]
        b.human_type(element, "hi")
        self.assertEqual(element.send_keys.call_count, 2)  # char attempt + bulk retry

    def test_wheel_scroll_uses_cdp_wheel_events(self):
        b = self._browser()
        b._wheel_scroll(180)
        self.assertTrue(any(cmd == "Input.dispatchMouseEvent" and
                            params.get("type") == "mouseWheel" and params.get("deltaY") == 180
                            for cmd, params in self.driver.cdp_calls))

    def test_human_move_never_raises(self):
        b = self._browser()
        with patch("sources.browser.ActionChains", side_effect=Exception("no mouse")):
            b.human_move(MagicMock())  # must swallow, not raise


class TestReferrerNavigation(unittest.TestCase):
    """_navigate keeps a plausible referrer chain instead of typed-URL jumps."""

    def test_navigate_uses_location_assign(self):
        driver = FakeDriver()
        b = bare_browser(driver)
        b._navigate("http://next.example/page")
        self.assertTrue(any("location.assign" in s for s, _ in driver.scripts))
        self.assertEqual(driver.get_calls, [])  # no driver.get fallback

    def test_navigate_falls_back_to_driver_get(self):
        driver = FakeDriver()
        driver.execute_script = MagicMock(side_effect=RuntimeError("no js"))
        b = bare_browser(driver)
        b._navigate("http://next.example/page")
        self.assertEqual(driver.get_calls, ["http://next.example/page"])


class TestWebSafetyRework(unittest.TestCase):
    """Safety lives at the CDP level now; no page-visible JS stubs."""

    def test_apply_web_safety_denies_downloads(self):
        driver = FakeDriver()
        b = bare_browser(driver)
        b.apply_web_safety()
        self.assertIn(("Browser.setDownloadBehavior", {"behavior": "deny"}), driver.cdp_calls)

    def test_blocked_urls_only_when_configured(self):
        driver = FakeDriver()
        b = bare_browser(driver)
        b.BLOCKED_URL_PATTERNS = ["*tracker.example/*"]
        b.apply_web_safety()
        self.assertTrue(any(cmd == "Network.setBlockedURLs" and
                            params == {"urls": ["*tracker.example/*"]}
                            for cmd, params in driver.cdp_calls))

    def test_safety_stub_script_is_gone(self):
        self.assertFalse(os.path.exists(os.path.join(
            os.path.dirname(__file__), "..", "sources", "web_scripts", "inject_safety_script.js")))


if __name__ == "__main__":
    unittest.main()
