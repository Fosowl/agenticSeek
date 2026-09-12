import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.tools.tools import Tools
from sources.tools.BashInterpreter import BashInterpreter


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

    def test_safe_mode_defaults_false_when_key_absent(self):
        self._write_config("")
        self.assertFalse(_SafeModeTool().safe_mode)

    def test_safe_mode_configured_true_rejects_unsafe_bash_command(self):
        """End-to-end: the safe_mode flag read from config.ini must reach the
        BashInterpreter's unsafe-command check. Before the fix, safe_mode was
        hardcoded False, so is_unsafe() never ran in the default bash path."""
        self._write_config("safe_mode = True\n")
        bash = BashInterpreter()
        self.assertTrue(bash.safe_mode)
        output = bash.execute(["rm -rf some_dir"])
        self.assertIn("Unsafe command: rm -rf some_dir", output)

    def test_safe_mode_configured_true_aborts_whole_batch(self):
        self._write_config("safe_mode = True\n")
        bash = BashInterpreter()
        marker = os.path.join(self._dir, "should_not_exist.txt")
        output = bash.execute([f"touch {marker}", "rm -rf some_dir"])
        self.assertIn("rm -rf some_dir", output)
        self.assertFalse(os.path.exists(marker))


if __name__ == "__main__":
    unittest.main()
