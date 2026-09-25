import unittest
import os
import sys
import tempfile

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock

# Mock heavy dependencies (same pattern as test_chromedriver_update.py)
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

from sources.browser import (
    persistent_profile_dir, profile_in_use, clone_profile, cleanup_legacy_profiles,
)


class TestPersistentProfile(unittest.TestCase):
    """Profile persistence helpers (WS4)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.profile = os.path.join(self.tmp.name, "chrome_data")
        os.makedirs(self.profile)

    def tearDown(self):
        self.tmp.cleanup()

    def test_persistent_dir_is_absolute_and_stable(self):
        d1 = persistent_profile_dir()
        d2 = persistent_profile_dir()
        self.assertEqual(d1, d2)
        self.assertTrue(os.path.isabs(d1))
        self.assertEqual(os.path.basename(d1), "chrome_data")

    def test_profile_not_in_use_without_lock(self):
        self.assertFalse(profile_in_use(self.profile))

    def test_profile_in_use_with_live_lock(self):
        import socket as _socket
        lock = os.path.join(self.profile, "SingletonLock")
        os.symlink(f"{_socket.gethostname()}-{os.getpid()}", lock)
        self.assertTrue(profile_in_use(self.profile))

    def test_lock_from_other_container_is_stale(self):
        # containers get fresh hostnames; a recycled small pid must not make
        # an old lock look alive
        lock = os.path.join(self.profile, "SingletonLock")
        os.symlink("oldcontainer-1", lock)  # pid 1 always exists
        self.assertFalse(profile_in_use(self.profile))
        self.assertFalse(os.path.lexists(lock))

    def test_stale_lock_is_cleared(self):
        lock = os.path.join(self.profile, "SingletonLock")
        os.symlink("fakehost-999999999", lock)  # no such pid
        self.assertFalse(profile_in_use(self.profile))
        self.assertFalse(os.path.lexists(lock), "stale lock should be removed")

    def test_clone_carries_state_but_not_locks(self):
        lock = os.path.join(self.profile, "SingletonLock")
        os.symlink(f"fakehost-{os.getpid()}", lock)
        cookie = os.path.join(self.profile, "Cookies")
        with open(cookie, "w") as f:
            f.write("nom")
        clone = clone_profile(self.profile)
        self.assertTrue(os.path.exists(os.path.join(clone, "Cookies")))
        self.assertFalse(os.path.lexists(os.path.join(clone, "SingletonLock")))
        self.assertNotEqual(clone, self.profile)

    def test_display_available_false_paths(self):
        from sources.browser import display_available
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(display_available())  # no DISPLAY
        with patch.dict(os.environ, {"DISPLAY": ":77"}, clear=True):
            self.assertFalse(display_available())  # no X server on :77

    def test_cleanup_legacy_removes_old_tmp_profiles(self):
        old_dir = os.path.join(tempfile.gettempdir(), "chrome_profile_testlegacy")
        os.makedirs(old_dir, exist_ok=True)
        import time as _time
        old = _time.time() - 48 * 3600
        os.utime(old_dir, (old, old))
        cleanup_legacy_profiles()
        self.assertFalse(os.path.exists(old_dir))


if __name__ == "__main__":
    unittest.main()
