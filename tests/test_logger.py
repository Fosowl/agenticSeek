import unittest
import os
import sys
import shutil
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.logger import Logger


class TestLogger(unittest.TestCase):
    """Test suite for the Logger class."""

    def setUp(self):
        self.logger = Logger("test_logger.log")

    def tearDown(self):
        if os.path.exists('.logs'):
            for handler in self.logger.logger.handlers[:]:
                handler.close()
                self.logger.logger.removeHandler(handler)
            log_path = os.path.join('.logs', 'test_logger.log')
            if os.path.exists(log_path):
                os.remove(log_path)

    def test_initialization(self):
        """Test logger initializes correctly."""
        self.assertTrue(self.logger.enabled)
        self.assertIsNotNone(self.logger.logger)
        self.assertTrue(os.path.exists('.logs'))

    def test_log_creates_file(self):
        """Test that logging creates a log file."""
        self.logger.info("test message")
        self.assertTrue(os.path.exists(self.logger.log_path))

    def test_log_writes_message(self):
        """Test that log messages are written to file."""
        self.logger.info("hello world")
        with open(self.logger.log_path, 'r') as f:
            content = f.read()
        self.assertIn("hello world", content)

    def test_log_deduplication(self):
        """Test that consecutive identical messages are not duplicated."""
        self.logger.info("duplicate message")
        self.logger.info("duplicate message")
        with open(self.logger.log_path, 'r') as f:
            content = f.read()
        self.assertEqual(content.count("duplicate message"), 1)

    def test_log_different_messages(self):
        """Test that different messages are all written."""
        self.logger.info("message one")
        self.logger.info("message two")
        with open(self.logger.log_path, 'r') as f:
            content = f.read()
        self.assertIn("message one", content)
        self.assertIn("message two", content)

    def test_error_level(self):
        """Test error level logging."""
        self.logger.error("error occurred")
        with open(self.logger.log_path, 'r') as f:
            content = f.read()
        self.assertIn("ERROR", content)
        self.assertIn("error occurred", content)

    def test_warning_level(self):
        """Test warning level logging."""
        self.logger.warning("warning issued")
        with open(self.logger.log_path, 'r') as f:
            content = f.read()
        self.assertIn("WARNING", content)
        self.assertIn("warning issued", content)

    def test_create_folder(self):
        """Test folder creation."""
        test_path = ".test_log_folder"
        result = self.logger.create_folder(test_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_path))
        os.rmdir(test_path)

    def test_create_folder_already_exists(self):
        """Test folder creation when folder already exists."""
        result = self.logger.create_folder('.logs')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
