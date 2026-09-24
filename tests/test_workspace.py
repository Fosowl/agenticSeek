import os
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sources.workspace import (
    ensure_work_dir,
    get_runtime_dir,
    get_work_dir,
    is_within_directory,
    resolve_workspace_path,
    runtime_subdir,
)
from sources.tools.fileFinder import FileFinder


class WorkspaceTestCase(unittest.TestCase):
    def setUp(self):
        self._root = tempfile.mkdtemp()
        self._work_dir = os.path.join(self._root, "workspace")
        self._runtime_dir = os.path.join(self._root, "runtime")
        os.makedirs(self._work_dir)
        self._old_work_dir = os.environ.get("WORK_DIR")
        self._old_runtime_dir = os.environ.get("AGENT_RUNTIME_DIR")
        os.environ["WORK_DIR"] = self._work_dir
        os.environ["AGENT_RUNTIME_DIR"] = self._runtime_dir

    def tearDown(self):
        if self._old_work_dir is None:
            os.environ.pop("WORK_DIR", None)
        else:
            os.environ["WORK_DIR"] = self._old_work_dir
        if self._old_runtime_dir is None:
            os.environ.pop("AGENT_RUNTIME_DIR", None)
        else:
            os.environ["AGENT_RUNTIME_DIR"] = self._old_runtime_dir
        shutil.rmtree(self._root, ignore_errors=True)


class TestWorkspacePaths(WorkspaceTestCase):
    def test_work_dir_and_runtime_dir_are_separate(self):
        self.assertEqual(get_work_dir(), os.path.realpath(self._work_dir))
        self.assertEqual(get_runtime_dir(), os.path.realpath(self._runtime_dir))
        self.assertNotEqual(get_work_dir(), get_runtime_dir())

    def test_runtime_subdir_is_outside_work_dir(self):
        logs_dir = runtime_subdir("logs")
        self.assertTrue(logs_dir.startswith(get_runtime_dir()))
        self.assertFalse(is_within_directory(logs_dir, get_work_dir()))

    def test_resolve_workspace_path_blocks_traversal(self):
        with self.assertRaises(PermissionError):
            resolve_workspace_path("../../outside.txt")

    def test_resolve_workspace_path_allows_relative_file(self):
        target = os.path.join(self._work_dir, "notes.txt")
        open(target, "w").close()
        resolved = resolve_workspace_path("notes.txt")
        self.assertEqual(resolved, os.path.realpath(target))

    def test_ensure_work_dir_creates_missing_directory(self):
        nested = os.path.join(self._root, "new_workspace")
        os.environ["WORK_DIR"] = nested
        self.assertEqual(ensure_work_dir(), os.path.realpath(nested))
        self.assertTrue(os.path.isdir(nested))


class TestFileFinderWorkspaceIsolation(WorkspaceTestCase):
    def test_cannot_read_file_outside_workspace(self):
        outside = os.path.join(self._root, "secret.txt")
        with open(outside, "w") as handle:
            handle.write("secret")

        finder = FileFinder()
        result = finder.get_file_info(outside)
        self.assertIn("error", result)
        self.assertIn("outside the agent workspace", result["error"])


if __name__ == "__main__":
    unittest.main()
