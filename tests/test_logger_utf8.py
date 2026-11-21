import logging
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.logger import Logger

# Covers scripts (Arabic), CJK (Chinese) and emoji: the emoji and Arabic
# runs cannot be encoded on legacy ANSI code pages (cp936/cp1252), so a
# FileHandler opened with the platform locale loses the whole record.
NON_ASCII_MESSAGE = "مرحبا 世界 🚀 café"


class TestLoggerUtf8(unittest.TestCase):
    """Logger must persist log records as UTF-8 on every platform."""

    def setUp(self):
        runtime = tempfile.mkdtemp(prefix="ags-logger-utf8-")
        self._old_runtime = os.environ.get("AGENT_RUNTIME_DIR")
        os.environ["AGENT_RUNTIME_DIR"] = runtime
        self.runtime = runtime
        self.logger = Logger("utf8_check.log")

    def tearDown(self):
        for handler in self.logger.logger.handlers[:]:
            handler.close()
            self.logger.logger.removeHandler(handler)
        if self._old_runtime is None:
            os.environ.pop("AGENT_RUNTIME_DIR", None)
        else:
            os.environ["AGENT_RUNTIME_DIR"] = self._old_runtime

    def test_file_handler_uses_utf8(self):
        """The log file handler declares UTF-8 instead of the platform locale."""
        self.assertTrue(self.logger.enabled)
        handlers = [h for h in self.logger.logger.handlers
                    if isinstance(h, logging.FileHandler)]
        self.assertEqual(len(handlers), 1)
        self.assertEqual(handlers[0].encoding, "utf-8")

    def test_non_ascii_message_round_trip(self):
        """A record with Arabic, CJK and emoji survives the log file."""
        self.logger.info(NON_ASCII_MESSAGE)
        self.logger.logger.handlers[0].flush()
        with open(self.logger.log_path, "rb") as handle:
            content = handle.read().decode("utf-8")
        self.assertIn(NON_ASCII_MESSAGE, content)


if __name__ == '__main__':
    unittest.main()
