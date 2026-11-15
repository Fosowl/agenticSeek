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

    def test_named_scripts_are_saved_separately(self):
        blocks, groups = self.tool.load_exec_block_groups(
            '```python:first.py\nprint("first")\n```\n'
            '```python:second.py\nfrom __future__ import annotations\n'
            'print("second")\n```\n'
            '```python:first.py\nprint("more")\n```'
        )
        self.assertEqual(len(blocks), 3)
        for path, fragments in groups.items():
            self.tool.save_block(fragments, path)
        for path, expected in [("first.py", "first\nmore\n"), ("second.py", "second\n")]:
            result = subprocess.run(
                [sys.executable, self.tool.resolve_path(path)],
                capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, expected)

    def test_one_named_destination_keeps_unnamed_fragments(self):
        blocks, groups = self.tool.load_exec_block_groups(
            '```python\nfirst = 1\n```\n'
            '```python:values.py\nsecond = 2\n```\n'
            '```python\nthird = 3\n```'
        )
        self.assertEqual(len(blocks), 3)
        self.assertEqual(groups, {"values.py": blocks})

    def test_single_block_still_replaces_existing_file(self):
        self.tool.save_block(["old content"], "single.txt")
        self.tool.save_block(["new content\n"], "single.txt")
        self.assertEqual(Path(self.tool.resolve_path("single.txt")).read_text(), "new content\n")


if __name__ == "__main__":
    unittest.main()
