import os
import sys
import tempfile
import shutil
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path

from sources.tools.GoInterpreter import GoInterpreter
from sources.tools.C_Interpreter import CInterpreter
from sources.tools.JavaInterpreter import JavaInterpreter


class _CompletedStep:
    """Minimal stand-in for the fields the interpreters read off a subprocess result."""

    def __init__(self, stdout=""):
        self.returncode = 0
        self.stdout = stdout
        self.stderr = ""


class _CompilerStub:
    """Record the raw bytes of the source file an interpreter writes.

    The stub replaces subprocess.run so the regression can assert the on-disk
    encoding without go, gcc or javac being installed.
    """

    def __init__(self, source_suffix):
        self.source_suffix = source_suffix
        self.source_bytes = None

    def __call__(self, command, **kwargs):
        for arg in command:
            if isinstance(arg, str) and arg.endswith(self.source_suffix):
                with open(arg, 'rb') as f:
                    self.source_bytes = f.read()
                break
        return _CompletedStep(stdout="ok")


class InterpreterWorkDirTestCase(unittest.TestCase):
    """Base fixture: point WORK_DIR at a temporary directory like the other tool tests."""

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


class TestCompiledInterpreterSourceEncoding(InterpreterWorkDirTestCase):
    """Regression: compiled-language interpreters wrote agent-generated source
    files with the platform locale encoding. On Windows (cp936/cp1252) a code
    block with non-ASCII text either crashed with UnicodeEncodeError (the write
    happens before the try block) or reached the compiler as mojibake — Go
    sources must be UTF-8, so `go build` fails with a confusing error."""

    def _check_source_roundtrip(self, interpreter, source_suffix, code):
        stub = _CompilerStub(source_suffix)
        with mock.patch('subprocess.run', stub):
            output = interpreter.execute(code)
        self.assertEqual(output, "ok",
                         "execute should reach the stubbed compiler and report success")
        self.assertIsNotNone(stub.source_bytes, "the source file was never written")
        # Strict UTF-8 decode is the point of the regression; Windows text mode
        # may still translate '\n' to '\r\n', so compare newline-normalized.
        decoded = stub.source_bytes.decode('utf-8', errors='strict')
        self.assertEqual(
            decoded.replace('\r\n', '\n'), code,
            "source file bytes must decode as strict UTF-8 to the code block")

    def test_go_source_file_is_utf8(self):
        code = 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("你好, 世界")\n}\n'
        self._check_source_roundtrip(GoInterpreter(), ".go", code)

    def test_c_source_file_is_utf8(self):
        code = '#include <stdio.h>\n\nint main(void) {\n    printf("你好, 世界\\n");\n    return 0;\n}\n'
        self._check_source_roundtrip(CInterpreter(), ".c", code)

    def test_java_source_file_is_utf8(self):
        code = 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("你好, 世界");\n    }\n}\n'
        self._check_source_roundtrip(JavaInterpreter(), ".java", code)

    def test_unrepresentable_source_does_not_crash(self):
        """Emoji cannot be encoded in cp936/cp1252; the old locale write raised an
        unhandled UnicodeEncodeError out of execute() before any compiler ran."""
        code = 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("🚀 launch")\n}\n'
        stub = _CompilerStub(".go")
        with mock.patch('subprocess.run', stub):
            output = GoInterpreter().execute(code)
        self.assertEqual(output, "ok")
        decoded = stub.source_bytes.decode('utf-8', errors='strict')
        self.assertEqual(decoded.replace('\r\n', '\n'), code)


if __name__ == "__main__":
    unittest.main()
