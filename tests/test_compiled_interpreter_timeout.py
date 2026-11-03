import subprocess
from unittest.mock import patch

import pytest

from sources.tools.C_Interpreter import CInterpreter
from sources.tools.GoInterpreter import GoInterpreter
from sources.tools.JavaInterpreter import JavaInterpreter


@pytest.fixture(params=[CInterpreter, GoInterpreter, JavaInterpreter])
def tool(request, tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_DIR", str(tmp_path / "workspace"))
    monkeypatch.setenv("AGENT_RUNTIME_DIR", str(tmp_path / "runtime"))
    interpreter = request.param()
    yield interpreter
    for handler in interpreter.logger.logger.handlers[:]:
        handler.close()
        interpreter.logger.logger.removeHandler(handler)


@pytest.mark.parametrize("stage", ["compile", "run"])
def test_compile_and_run_timeouts_are_reported_as_failures(tool, stage):
    completed = subprocess.CompletedProcess(["compiler"], 0, stdout="", stderr="")
    timeout = subprocess.TimeoutExpired([stage], 10)
    responses = [timeout] if stage == "compile" else [completed, timeout]
    with patch("subprocess.run", side_effect=responses):
        output = tool.execute(["placeholder source"])
    assert "timed out" in output
    assert tool.execution_failure_check(output)
    assert tool.interpreter_feedback(output).startswith("[failure]")


def test_successful_execution_is_still_reported_as_success(tool):
    completed = subprocess.CompletedProcess(["compiler"], 0, stdout="hello\n", stderr="")
    with patch("subprocess.run", return_value=completed):
        output = tool.execute(["placeholder source"])
    assert output == "hello\n"
    assert not tool.execution_failure_check(output)
    assert tool.interpreter_feedback(output).startswith("[success]")
