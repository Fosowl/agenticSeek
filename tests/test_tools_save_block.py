import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sources.tools.tools import Tools


class TestSaveBlock(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = temporary.name
        env = patch.dict(os.environ, {
            "WORK_DIR": os.path.join(directory, "workspace"),
            "AGENT_RUNTIME_DIR": os.path.join(directory, "runtime"),
        })
        env.start()
        self.addCleanup(env.stop)
        self.tool = Tools()
        self.tool.tag = "python"

    def tearDown(self):
        for handler in self.tool.logger.logger.handlers[:]:
            handler.close()
            self.tool.logger.logger.removeHandler(handler)

    def test_saved_script_preserves_every_extracted_block(self):
        blocks, path = self.tool.load_exec_block(
            '```python:hello.py\ndef greeting():\n    return "hello"\n```\n'
            '```python:hello.py\nprint(greeting())\n```'
        )
        self.tool.save_block(blocks, path)
        result = subprocess.run(
            [sys.executable, self.tool.resolve_path(path)],
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "hello\n")

    def test_blocks_without_trailing_newlines_remain_separate(self):
        self.tool.save_block(["first = 1", "second = 2"], "values.py")
        namespace = {}
        exec(Path(self.tool.resolve_path("values.py")).read_text(), namespace)
        self.assertEqual((namespace["first"], namespace["second"]), (1, 2))

    def test_single_block_still_replaces_existing_file(self):
        self.tool.save_block(["old content"], "single.txt")
        self.tool.save_block(["new content\n"], "single.txt")
        self.assertEqual(Path(self.tool.resolve_path("single.txt")).read_text(), "new content\n")


if __name__ == "__main__":
    unittest.main()
