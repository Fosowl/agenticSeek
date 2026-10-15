import unittest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path

from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.PyInterpreter import PyInterpreter


class InterpreterTestCase(unittest.TestCase):
    """Base fixture: run interpreters against a temporary work directory."""

    def setUp(self):
        self._work_dir = tempfile.mkdtemp()
        self._old_work_dir = os.environ.get('WORK_DIR')
        os.environ['WORK_DIR'] = self._work_dir

    def tearDown(self):
        if self._old_work_dir is None:
            os.environ.pop('WORK_DIR', None)
        else:
            os.environ['WORK_DIR'] = self._old_work_dir
        shutil.rmtree(self._work_dir, ignore_errors=True)


class TestBashInterpreter(InterpreterTestCase):

    def test_multiline_block_preserves_newlines(self):
        """Regression: newlines were stripped, gluing lines into one broken command."""
        bash = BashInterpreter()
        output = bash.execute(["echo first\necho second"])
        self.assertIn("first", output)
        self.assertIn("second", output)

    def test_shebang_block_still_executes(self):
        """Regression: after newline-stripping, a shebang commented out the whole block."""
        bash = BashInterpreter()
        output = bash.execute(["#!/usr/bin/env bash\necho shebang_ok"])
        self.assertIn("shebang_ok", output)

    def test_commands_run_in_work_dir(self):
        bash = BashInterpreter()
        marker = "marker_file.txt"
        open(os.path.join(self._work_dir, marker), 'w').close()
        output = bash.execute(["ls"])
        self.assertIn(marker, output)

    def test_unsafe_command_message_names_the_command(self):
        """Regression: the rejection message printed a literal '{command}'."""
        bash = BashInterpreter()
        bash.safe_mode = True
        output = bash.execute(["rm -rf some_dir"])
        self.assertIn("rm -rf some_dir", output)
        self.assertNotIn("{command}", output)

    def test_unsafe_command_anywhere_aborts_whole_batch(self):
        """Regression: a per-command check let earlier commands in a batch run
        before a later unsafe command was rejected."""
        bash = BashInterpreter()
        bash.safe_mode = True
        marker = os.path.join(self._work_dir, "should_not_exist.txt")
        output = bash.execute([f"touch {marker}", "rm -rf some_dir"])
        self.assertIn("rm -rf some_dir", output)
        self.assertFalse(os.path.exists(marker))

    def test_timeout_kills_long_running_command(self):
        """Regression: timeout was only applied after stdout closed, so silent
        long-running commands hung forever."""
        bash = BashInterpreter()
        output = bash.execute(["sleep 5"], timeout=1)
        self.assertIn("timed out", output)

    def test_failing_command_reports_return_code(self):
        bash = BashInterpreter()
        output = bash.execute(["exit 3"])
        self.assertIn("return code 3", output)

    def test_skipped_language_command_is_reported_as_failure(self):
        """Regression: python from bash was skipped silently and reported as success with no output."""
        bash = BashInterpreter()
        output = bash.execute(["python3 -c 'print(1)'"])
        self.assertIn("not allowed", output)
        self.assertTrue(bash.execution_failure_check(output))


class TestPyInterpreter(InterpreterTestCase):

    def test_output_has_no_stray_none(self):
        """Regression: print(exec(...)) appended a stray 'None' to every output."""
        py = PyInterpreter()
        output = py.execute(['print("hello")'])
        self.assertEqual(output, "hello\n")

    def test_exception_reports_failure(self):
        py = PyInterpreter()
        output = py.execute(['raise ValueError("boom")'])
        self.assertTrue(output.startswith("code execution failed:"))
        self.assertIn("ValueError", output)
        self.assertTrue(py.execution_failure_check(output))

    def test_timeout_kills_infinite_loop(self):
        """Regression: exec() ran in-process with no timeout, freezing the backend."""
        py = PyInterpreter()
        output = py.execute(['while True:\n    pass'], timeout=1)
        self.assertIn("timed out", output)
        self.assertTrue(py.execution_failure_check(output))

    def test_code_runs_in_work_dir(self):
        py = PyInterpreter()
        output = py.execute(['import os; print(os.path.realpath(os.getcwd()))'])
        self.assertEqual(output.strip(), os.path.realpath(self._work_dir))

    def test_clean_output_is_not_flagged_as_failure(self):
        py = PyInterpreter()
        self.assertFalse(py.execution_failure_check("hello\n"))

    def test_curses_import_is_refused_with_actionable_message(self):
        """Regression: curses code died with a cryptic 'cbreak() returned ERR'
        traceback the agent could not act on, so it retried forever."""
        py = PyInterpreter()
        output = py.execute(['import curses\n\ncurses.wrapper(lambda s: None)'], timeout=5)
        self.assertIn("terminal", output)
        self.assertIn("curses", output)
        self.assertNotIn("Traceback", output)
        self.assertTrue(py.execution_failure_check(output))

    def test_from_curses_import_is_refused(self):
        py = PyInterpreter()
        output = py.execute(['from curses import wrapper'], timeout=5)
        self.assertIn("curses", output)
        self.assertNotIn("Traceback", output)

    def test_input_call_is_refused_with_actionable_message(self):
        """Regression: input() either hit EOFError or hung until the timeout,
        since the sandbox has no terminal to read from."""
        py = PyInterpreter()
        output = py.execute(['name = input("your name: ")\nprint(name)'], timeout=5)
        self.assertIn("terminal", output)
        self.assertIn("input()", output)
        self.assertTrue(py.execution_failure_check(output))

    def test_input_method_call_is_not_refused(self):
        """A .input() method or my_input() helper is not the builtin input()."""
        py = PyInterpreter()
        code = ('class Reader:\n'
                '    def input(self, value):\n'
                '        return value\n'
                'print(Reader().input("ok"))')
        output = py.execute([code])
        self.assertEqual(output, "ok\n")


if __name__ == "__main__":
    unittest.main()
