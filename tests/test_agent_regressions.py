import unittest
import asyncio
import os
import shutil
import sys
import tempfile
from unittest.mock import MagicMock, AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path

# Mock heavy dependencies (same pattern as test_browser_agent_parsing.py)
for mod_name in [
    'torch', 'transformers', 'kokoro', 'adaptive_classifier', 'text2emotion',
    'ollama', 'openai', 'together', 'IPython', 'IPython.display',
    'playsound3', 'soundfile', 'pyaudio', 'librosa',
    'pypdf', 'langid', 'pypinyin', 'fake_useragent',
    'chromedriver_autoinstaller', 'num2words', 'sentencepiece', 'sacremoses',
    'scipy', 'numpy', 'selenium_stealth', 'undetected_chromedriver',
    'markdownify',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

os.environ.setdefault('WORK_DIR', '/tmp')

from sources.agents.agent import Agent
from sources.agents.file_agent import FileAgent, MAX_STEPS, STEP_LIMIT_MESSAGE
from sources.agents.mcp_agent import McpAgent
from sources.schemas import QueryRequest
from sources.tools.tools import Tools


def make_bare_agent(agent_class):
    """Build an agent without running its heavy __init__."""
    agent = agent_class.__new__(agent_class)
    agent.stop = False
    agent.tools = {}
    agent.blocks_result = []
    agent.memory = MagicMock()
    agent.work_dir = "/tmp"
    agent.status_message = ""
    agent.last_answer = ""
    agent.last_reasoning = ""
    return agent


class TestFileAgentLoop(unittest.TestCase):

    def _run_tool_calls(self, agent, answers_with_tools):
        """Make execute_modules record one tool result for the given answers."""
        def fake_execute(answer):
            if answer in answers_with_tools:
                agent.blocks_result.append(object())
            return True, ""
        agent.execute_modules = MagicMock(side_effect=fake_execute)

    def test_tool_calls_continue_until_plain_answer(self):
        """Regression: the agent stopped after the first tool call, or answered only 'done'."""
        agent = make_bare_agent(FileAgent)
        read_block = "```file_finder\naction=read\nname=a.pdf\n```"
        agent.llm_request = AsyncMock(side_effect=[(read_block, "r1"), ("The paper shows X.", "r2")])
        self._run_tool_calls(agent, {read_block})
        answer, reasoning = asyncio.run(agent.process("summarize <files>a.pdf</files>", None))
        self.assertEqual(agent.llm_request.await_count, 2)
        self.assertEqual((answer, reasoning), ("The paper shows X.", "r2"))

    def test_block_without_tool_is_not_the_final_answer(self):
        """Regression: a ```python block (no such tool) ended the task with 'block:0' as answer."""
        agent = make_bare_agent(FileAgent)
        agent.tools = {"file_finder": None, "bash": None}
        python_block = "Extracting.\n```python\nprint(1)\n```"
        agent.llm_request = AsyncMock(side_effect=[(python_block, "r1"), ("Summary.", "r2")])
        self._run_tool_calls(agent, set())
        answer, _ = asyncio.run(agent.process("summarize", None))
        self.assertEqual(answer, "Summary.")
        feedback = agent.memory.push.call_args_list[-1].args
        self.assertEqual(feedback[0], "user")
        self.assertIn("file_finder, bash", feedback[1])

    def test_step_loop_is_capped(self):
        """Regression: a model that never stops calling tools made process() spin forever."""
        agent = make_bare_agent(FileAgent)
        bash_block = "```bash\nls\n```"
        agent.llm_request = AsyncMock(return_value=(bash_block, "reasoning"))
        self._run_tool_calls(agent, {bash_block})
        answer, _ = asyncio.run(agent.process("do something", None))
        self.assertEqual(agent.llm_request.await_count, MAX_STEPS)
        self.assertTrue(answer.endswith(STEP_LIMIT_MESSAGE))

    def test_stop_before_first_attempt_returns_cleanly(self):
        """Regression: 'answer' was unbound when stop was requested early."""
        agent = make_bare_agent(FileAgent)
        agent.stop = True
        agent.llm_request = AsyncMock()
        answer, reasoning = asyncio.run(agent.process("do something", None))
        self.assertEqual(answer, "")
        agent.llm_request.assert_not_awaited()


class TestMcpAgentLoop(unittest.TestCase):

    def test_loop_terminates_once_no_new_blocks(self):
        agent = make_bare_agent(McpAgent)
        agent.enabled = True
        agent.llm_request = AsyncMock(return_value=("answer", "reasoning"))
        agent.execute_modules = MagicMock(return_value=(True, ""))
        answer, reasoning = asyncio.run(agent.process("use mcp", None))
        self.assertEqual(agent.llm_request.await_count, 1)

    def test_loop_is_capped_when_blocks_keep_coming(self):
        """Regression: blocks_result was never reset, so one executed block
        made the old `len(blocks_result) == 0` exit condition unreachable."""
        agent = make_bare_agent(McpAgent)
        agent.enabled = True
        agent.llm_request = AsyncMock(return_value=("answer", "reasoning"))

        def fake_execute(answer):
            agent.blocks_result.append(object())
            return True, ""
        agent.execute_modules = fake_execute
        asyncio.run(agent.process("use mcp", None))
        self.assertEqual(agent.llm_request.await_count, 5)

    def test_disabled_agent_returns_tuple(self):
        agent = make_bare_agent(McpAgent)
        agent.enabled = False
        answer, reasoning = asyncio.run(agent.process("use mcp", None))
        self.assertEqual(answer, "MCP Agent is disabled.")


class TestAgentAddTool(unittest.TestCase):

    def _agent(self):
        return Agent("tester", "prompts/base/casual_agent.txt", None)

    def test_add_tool_accepts_callable(self):
        """Regression: `tool is not Callable` was always true, so every call raised."""
        agent = self._agent()
        agent.add_tool("noop", lambda: None)
        self.assertIn("noop", agent.get_tools_name())

    def test_add_tool_rejects_non_callable(self):
        agent = self._agent()
        with self.assertRaises(TypeError):
            agent.add_tool("bad", 42)


class TestQueryRequestStr(unittest.TestCase):

    def test_str_uses_existing_fields_only(self):
        """Regression: __str__ referenced self.lang / self.stt_enabled which don't exist."""
        request = QueryRequest(query="hello")
        self.assertIn("hello", str(request))


class FakeBlockTool(Tools):
    """A tool that reports two blocks and one distinct output per block."""

    def __init__(self, failing_outputs=()):
        super().__init__()
        self.tag = "fake"
        self.name = "fake tool"
        self.description = "test tool"
        self.failing_outputs = set(failing_outputs)
        self.executed = []

    def load_exec_block(self, llm_text):
        return ["first block", "second block"], None

    def execute(self, blocks, safety=False):
        self.executed.extend(blocks)
        return f"output of {blocks[0]}"

    def execution_failure_check(self, output):
        return output in self.failing_outputs

    def interpreter_feedback(self, output):
        return f"feedback: {output}"


class TestExecuteModulesFeedback(unittest.TestCase):
    """execute_modules must hand the output of every executed block to the model."""

    def setUp(self):
        self.work_dir = tempfile.mkdtemp()
        env = patch.dict(os.environ, {"WORK_DIR": self.work_dir})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(shutil.rmtree, self.work_dir, True)

    def test_every_block_output_reaches_memory(self):
        """Regression: only the last block's feedback was pushed to memory, so the
        model never saw the output of the blocks it asked for before that one."""
        agent = make_bare_agent(Agent)
        agent.tools = {"fake": FakeBlockTool()}
        success, feedback = agent.execute_modules("run both blocks")
        self.assertTrue(success)
        pushed = "\n".join(call.args[1] for call in agent.memory.push.call_args_list)
        self.assertIn("output of first block", pushed)
        self.assertIn("output of second block", pushed)
        self.assertIn("output of first block", feedback)
        self.assertEqual(len(agent.blocks_result), 2)

    def test_failing_block_keeps_earlier_outputs_in_memory(self):
        """The failing block's feedback is returned, and the outputs that already
        ran stay in memory so the model can fix the code with them."""
        agent = make_bare_agent(Agent)
        agent.tools = {"fake": FakeBlockTool(failing_outputs={"output of second block"})}
        success, feedback = agent.execute_modules("run both blocks")
        self.assertFalse(success)
        self.assertIn("output of second block", feedback)
        pushed = "\n".join(call.args[1] for call in agent.memory.push.call_args_list)
        self.assertIn("output of first block", pushed)
        self.assertIn("output of second block", pushed)
        self.assertEqual(len(agent.blocks_result), 2)


if __name__ == "__main__":
    unittest.main()
