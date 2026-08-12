import unittest
import asyncio
import os
import sys
import json
from unittest.mock import MagicMock, AsyncMock

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
from sources.agents.file_agent import FileAgent
from sources.agents.mcp_agent import McpAgent
from sources.schemas import QueryRequest


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

    def test_retry_loop_is_capped(self):
        """Regression: persistent execution failures made process() loop forever."""
        agent = make_bare_agent(FileAgent)
        agent.llm_request = AsyncMock(return_value=("answer", "reasoning"))
        agent.execute_modules = MagicMock(return_value=(False, "failure"))
        answer, reasoning = asyncio.run(agent.process("do something", None))
        self.assertEqual(agent.llm_request.await_count, 5)
        self.assertEqual(answer, "answer")

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


class TestGetStatusMessage(unittest.TestCase):
    """Regression: `/latest_answer` serialises the agent status string (#496)."""

    def test_status_message_serialises_as_plain_string(self):
        """api.py reads the agent status as `status_message` for the
        `/latest_answer` response (the `get_status_message` property returns
        the same value); it must be a plain str so JSONResponse can serialise
        it — not a bound method object, which would raise `TypeError` during
        serialisation."""
        agent = make_bare_agent(Agent)
        agent.status_message = "In progress"
        self.assertIsInstance(agent.status_message, str)
        self.assertEqual(agent.status_message, "In progress")
        self.assertEqual(agent.get_status_message, "In progress")
        json.dumps(agent.status_message)  # must not raise


class TestQueryRequestStr(unittest.TestCase):

    def test_str_uses_existing_fields_only(self):
        """Regression: __str__ referenced self.lang / self.stt_enabled which don't exist."""
        request = QueryRequest(query="hello")
        self.assertIn("hello", str(request))


if __name__ == "__main__":
    unittest.main()
