import configparser
import json
import os
import shutil
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock

# Mock heavy dependencies (same pattern as test_browser_profile.py)
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

from sources.browser_session_import import (
    import_sessions, import_sessions_if_configured, import_needed,
)
from sources.errors import AgenticSeekError


def make_fake_user_data_dir(root: str, profile_name: str = "Default") -> str:
    """Build a minimal Chrome user-data-dir with session state and decoys."""
    udd = os.path.join(root, "Chrome")
    profile = os.path.join(udd, profile_name)
    os.makedirs(os.path.join(profile, "Local Storage", "leveldb"), exist_ok=True)
    os.makedirs(os.path.join(profile, "Session Storage"), exist_ok=True)
    os.makedirs(os.path.join(profile, "IndexedDB", "https_example.com_0"), exist_ok=True)
    os.makedirs(os.path.join(profile, "WebStorage"), exist_ok=True)
    os.makedirs(os.path.join(profile, "Cache"), exist_ok=True)
    os.makedirs(os.path.join(profile, "Sync Data"), exist_ok=True)
    for name in ("Cookies", "Cookies-journal", "Login Data", "Web Data",
                 "Preferences", "Secure Preferences"):
        with open(os.path.join(profile, name), "wb") as handle:
            handle.write(b"fake-" + name.encode())
    with open(os.path.join(profile, "Cache", "decoy.bin"), "wb") as handle:
        handle.write(b"cache-junk")
    with open(os.path.join(profile, "History"), "wb") as handle:
        handle.write(b"history-junk")
    local_state = {"profile": {"last_used": profile_name,
                               "info_cache": {profile_name: {"name": "Test"}}}}
    with open(os.path.join(udd, "Local State"), "w") as handle:
        json.dump(local_state, handle)
    return udd


class TestSessionImport(unittest.TestCase):
    """Import of the user's Chrome sessions into the agent profile."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.prev_cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.source = make_fake_user_data_dir(self.tmp.name)
        os.environ["CHROME_USER_DATA_DIR"] = self.source
        self.patches = [
            patch("sources.browser_session_import.chrome_is_running", return_value=False),
            patch("sources.browser_session_import._agent_profile_in_use", return_value=False),
        ]
        for patched in self.patches:
            patched.start()

    def tearDown(self):
        for patched in self.patches:
            patched.stop()
        os.environ.pop("CHROME_USER_DATA_DIR", None)
        os.chdir(self.prev_cwd)
        self.tmp.cleanup()

    def agent_profile(self) -> str:
        return os.path.join(os.getcwd(), ".browser_profile", "chrome_data")

    def test_import_copies_only_session_state(self):
        report = import_sessions()
        target = self.agent_profile()
        self.assertIn("Cookies", report.copied)
        self.assertTrue(os.path.isfile(os.path.join(target, "Default", "Cookies")))
        self.assertTrue(os.path.isdir(os.path.join(target, "Default", "Local Storage")))
        self.assertTrue(os.path.isdir(os.path.join(target, "Default", "IndexedDB")))
        self.assertTrue(os.path.isfile(os.path.join(target, "Local State")))
        self.assertFalse(os.path.exists(os.path.join(target, "Default", "Cache")))
        self.assertFalse(os.path.exists(os.path.join(target, "Default", "History")))
        self.assertFalse(os.path.exists(os.path.join(target, "Default", "Sync Data")))

    def test_import_points_local_state_at_default_profile(self):
        import_sessions()
        with open(os.path.join(self.agent_profile(), "Local State")) as handle:
            state = json.load(handle)
        self.assertEqual(state["profile"]["last_used"], "Default")
        self.assertEqual(state["profile"]["last_active_profiles"], ["Default"])
        self.assertIn("Default", state["profile"]["info_cache"])

    def test_import_maps_named_profile_to_default(self):
        os.environ["CHROME_USER_DATA_DIR"] = make_fake_user_data_dir(self.tmp.name, "Profile 1")
        self.assertIn("Cookies", import_sessions(profile_name="Profile 1").copied)
        self.assertTrue(os.path.isfile(os.path.join(self.agent_profile(), "Default", "Cookies")))
        with open(os.path.join(self.agent_profile(), "Local State")) as handle:
            state = json.load(handle)
        self.assertIn("Default", state["profile"]["info_cache"])
        self.assertNotIn("Profile 1", state["profile"]["info_cache"])

    def test_import_rotates_previous_agent_profile(self):
        sentinel = os.path.join(self.agent_profile(), "old-login.txt")
        os.makedirs(os.path.dirname(sentinel), exist_ok=True)
        with open(sentinel, "w") as handle:
            handle.write("previous agent session")
        report = import_sessions()
        self.assertIsNotNone(report.backup_dir)
        self.assertTrue(os.path.isfile(os.path.join(report.backup_dir, "old-login.txt")))
        self.assertTrue(os.path.isfile(os.path.join(self.agent_profile(), "Default", "Cookies")))

    def test_import_blocked_when_chrome_is_running(self):
        self.patches[0].stop()
        with patch("sources.browser_session_import.chrome_is_running", return_value=True):
            with self.assertRaises(AgenticSeekError) as ctx:
                import_sessions()
        self.assertEqual(ctx.exception.title, "Google Chrome must be closed for session import")

    def test_import_blocked_when_agent_browser_running(self):
        self.patches[1].stop()
        with patch("sources.browser_session_import._agent_profile_in_use", return_value=True):
            with self.assertRaises(AgenticSeekError) as ctx:
                import_sessions()
        self.assertEqual(ctx.exception.title, "agenticSeek browser is already running")

    def test_helper_runs_once_then_skips_until_profile_changes(self):
        config = configparser.ConfigParser()
        config["BROWSER"] = {"import_user_profile": "True", "import_profile_name": "Default"}
        import_sessions_if_configured(config)
        self.assertFalse(import_needed("Default"))
        self.assertTrue(import_needed("Profile 1"))
        os.remove(os.path.join(self.source, "Default", "Cookies"))
        import_sessions_if_configured(config)  # marker blocks a second run
        self.assertTrue(os.path.isfile(os.path.join(self.agent_profile(), "Default", "Cookies")))

    def test_unknown_profile_name_raises_with_available_profiles(self):
        with self.assertRaises(AgenticSeekError) as ctx:
            import_sessions(profile_name="Profile 9")
        self.assertIn("Chrome profile not found", ctx.exception.title)
        self.assertTrue(any("Default" in fix for fix in ctx.exception.fixes))

    def test_missing_user_data_dir_raises(self):
        os.environ["CHROME_USER_DATA_DIR"] = os.path.join(self.tmp.name, "nowhere")
        with self.assertRaises(AgenticSeekError) as ctx:
            import_sessions()
        self.assertEqual(ctx.exception.title, "Chrome profile not found")

    def test_no_cookie_store_raises_before_touching_agent_profile(self):
        for name in ("Cookies", "Cookies-journal"):
            os.remove(os.path.join(self.source, "Default", name))
        sentinel = os.path.join(self.agent_profile(), "old-login.txt")
        os.makedirs(os.path.dirname(sentinel), exist_ok=True)
        with open(sentinel, "w") as handle:
            handle.write("keep")
        with self.assertRaises(AgenticSeekError) as ctx:
            import_sessions()
        self.assertEqual(ctx.exception.title, "No cookie store found in the Chrome profile")
        self.assertTrue(os.path.isfile(sentinel), "agent profile must not rotate on failure")
        self.assertFalse(os.path.exists(self.agent_profile() + ".bak-"
                          + time.strftime("%Y%m%d")))
        self.assertTrue(import_needed("Default"), "no marker after a failed import")

    def test_default_dir_follows_agent_binary(self):
        """No env override: the import source follows the browser the agent runs."""
        os.environ.pop("CHROME_USER_DATA_DIR", None)
        if sys.platform.startswith("win"):
            binary = os.path.join(self.tmp.name, "Google", "Chrome Beta",
                                  "Application", "chrome.exe")
            beta_udd = os.path.join(self.tmp.name, "Google", "Chrome Beta", "User Data")
        else:
            binary = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
            beta_udd = os.path.join(self.tmp.name, "Library",
                                    "Application Support", "Google", "Chrome Beta")
        os.makedirs(os.path.dirname(beta_udd), exist_ok=True)
        shutil.move(self.source, beta_udd)
        with patch.dict(os.environ, {"HOME": self.tmp.name, "LOCALAPPDATA": self.tmp.name}):
            with patch("sources.browser_session_import.get_chrome_path", return_value=binary):
                report = import_sessions()
        self.assertEqual(report.source_user_data_dir, os.path.abspath(beta_udd))
        self.assertTrue(os.path.isfile(os.path.join(self.agent_profile(), "Default", "Cookies")))

    def test_backups_are_kept_after_reimport(self):
        import_sessions()
        stale_backup = self.agent_profile() + ".bak-20200101-000000"
        os.makedirs(stale_backup)
        with open(os.path.join(stale_backup, "sentinel.txt"), "w") as handle:
            handle.write("original agent profile")
        import_sessions()
        self.assertTrue(os.path.isfile(os.path.join(stale_backup, "sentinel.txt")),
                        "backups must never be deleted automatically")


if __name__ == "__main__":
    unittest.main()
