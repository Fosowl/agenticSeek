"""Exercise parameter parsing through real workspace file reads."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sources.tools.fileFinder import FileFinder


class TestFileFinderParameters(unittest.TestCase):
    def setUp(self):
        runtime = tempfile.TemporaryDirectory()
        self.addCleanup(runtime.cleanup)
        env = patch.dict(os.environ, {"AGENT_RUNTIME_DIR": runtime.name,
                                      "WORK_DIR": str(Path(runtime.name) / "workspace")})
        env.start()
        self.addCleanup(env.stop)
        self.tool = FileFinder()
        self.addCleanup(self.close_logger)

    def close_logger(self):
        for handler in self.tool.logger.logger.handlers[:]:
            handler.close()
            self.tool.logger.logger.removeHandler(handler)

    def test_read_filename_containing_equals(self):
        Path(self.tool.work_dir, "report").write_text("Wrong file", encoding="utf-8")
        Path(self.tool.work_dir, "report=final.txt").write_text("Complete report", encoding="utf-8")
        output = self.tool.execute(["action=read\nname=report=final.txt"])
        self.assertEqual(output, "Content:\nComplete report")

    def test_ignore_other_parameter_names_and_values(self):
        Path(self.tool.work_dir, "report.txt").write_text("Expected file", encoding="utf-8")
        block = "filename=missing.txt\nnote=name\naction=read\n name = report.txt"
        self.assertEqual(self.tool.execute([block]), "Content:\nExpected file")

    def test_ignore_prose_containing_parameter_name(self):
        Path(self.tool.work_dir, "report.txt").write_text("Expected file", encoding="utf-8")
        block = "Read the named file\naction=read\nname=report.txt"
        self.assertEqual(self.tool.execute([block]), "Content:\nExpected file")

    def test_missing_name_is_reported_without_exception(self):
        output = self.tool.execute(["action=read\nfilename=report.txt"])
        self.assertIn("Error: No filename provided", output)


if __name__ == "__main__":
    unittest.main()
