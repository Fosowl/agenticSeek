import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock

# Mock heavy dependencies
for mod_name in [
    'torch', 'transformers', 'kokoro', 'adaptive_classifier', 'text2emotion',
    'ollama', 'openai', 'together', 'IPython', 'IPython.display',
    'playsound3', 'soundfile', 'pyaudio', 'librosa',
    'pypdf', 'langid', 'pypinyin', 'fake_useragent',
    'num2words', 'sentencepiece', 'sacremoses',
    'scipy', 'numpy', 'selenium_stealth', 'undetected_chromedriver',
    'markdownify', 'chromedriver_autoinstaller',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

os.environ.setdefault('WORK_DIR', '/tmp')

from sources.browser import get_chromedriver_version, is_chromedriver_compatible


class TestChromedriverVersionCheck(unittest.TestCase):
    """Test suite for ChromeDriver version checking and auto-update logic."""

    @patch('sources.browser.subprocess.run')
    def test_get_chromedriver_version_success(self, mock_run):
        """Test extracting major version from chromedriver --version output."""
        mock_run.return_value = MagicMock(
            stdout="ChromeDriver 125.0.6422.78 (abc123)\n"
        )
        self.assertEqual(get_chromedriver_version("/usr/bin/chromedriver"), "125")

    @patch('sources.browser.subprocess.run')
    def test_get_chromedriver_version_failure(self, mock_run):
        """Test graceful failure when chromedriver --version fails."""
        mock_run.side_effect = FileNotFoundError("not found")
        self.assertEqual(get_chromedriver_version("/nonexistent"), "")

    @patch('sources.browser.subprocess.run')
    def test_get_chromedriver_version_timeout(self, mock_run):
        """Test graceful failure on timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="chromedriver", timeout=10)
        self.assertEqual(get_chromedriver_version("/usr/bin/chromedriver"), "")

    @patch('sources.browser.chromedriver_autoinstaller.get_chrome_version')
    @patch('sources.browser.get_chromedriver_version')
    def test_compatible_versions(self, mock_driver_ver, mock_chrome_ver):
        """Test that matching major versions are compatible."""
        mock_chrome_ver.return_value = "125.0.6422.78"
        mock_driver_ver.return_value = "125"
        self.assertTrue(is_chromedriver_compatible("/usr/bin/chromedriver"))

    @patch('sources.browser.chromedriver_autoinstaller.get_chrome_version')
    @patch('sources.browser.get_chromedriver_version')
    def test_incompatible_versions(self, mock_driver_ver, mock_chrome_ver):
        """Test that mismatched major versions are incompatible."""
        mock_chrome_ver.return_value = "126.0.6478.55"
        mock_driver_ver.return_value = "125"
        self.assertFalse(is_chromedriver_compatible("/usr/bin/chromedriver"))

    @patch('sources.browser.chromedriver_autoinstaller.get_chrome_version')
    def test_no_chrome_version_assumes_compatible(self, mock_chrome_ver):
        """Test that missing Chrome version defaults to compatible."""
        mock_chrome_ver.return_value = None
        self.assertTrue(is_chromedriver_compatible("/usr/bin/chromedriver"))

    @patch('sources.browser.chromedriver_autoinstaller.get_chrome_version')
    @patch('sources.browser.get_chromedriver_version')
    def test_no_driver_version_assumes_compatible(self, mock_driver_ver, mock_chrome_ver):
        """Test that missing driver version defaults to compatible."""
        mock_chrome_ver.return_value = "125.0.6422.78"
        mock_driver_ver.return_value = ""
        self.assertTrue(is_chromedriver_compatible("/usr/bin/chromedriver"))


if __name__ == '__main__':
    unittest.main()
