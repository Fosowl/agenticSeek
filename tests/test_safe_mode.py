import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.tools.tools import Tools


class _SafeModeTool(Tools):
    def execute(self, blocks, safety=False):
        return "test execution"

    def execution_failure_check(self, output):
        return False

    def interpreter_feedback(self, output):
        return "test feedback"


class TestSafeMode(unittest.TestCase):
    """safe_mode must be read from config.ini so the BashInterpreter unsafe-command
    check can be enabled. Before this fix it was hardcoded False and unreachable."""

    def setUp(self):
        self._cwd = os.getcwd()
        self._dir = tempfile.mkdtemp()
        os.chdir(self._dir)

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self._dir, ignore_errors=True)

    def _write_config(self, safe_mode_line):
        with open(os.path.join(self._dir, "config.ini"), "w") as f:
            f.write("[MAIN]\n")
            f.write("work_dir = {}\n".format(self._dir))
            f.write(safe_mode_line)

    def test_safe_mode_enabled_when_configured_true(self):
        self._write_config("safe_mode = True\n")
        self.assertTrue(_SafeModeTool().safe_mode)

    def test_safe_mode_disabled_when_configured_false(self):
        self._write_config("safe_mode = False\n")
        self.assertFalse(_SafeModeTool().safe_mode)

    def test_safe_mode_defaults_true_when_key_absent(self):
        self._write_config("")
        self.assertTrue(_SafeModeTool().safe_mode)


if __name__ == "__main__":
    unittest.main()
