import os
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

for mod_name in [
    "torch", "transformers", "kokoro", "adaptive_classifier", "text2emotion",
    "ollama", "openai", "together", "IPython", "IPython.display",
    "playsound3", "soundfile", "pyaudio", "librosa",
    "pypdf", "langid", "pypinyin", "fake_useragent",
    "chromedriver_autoinstaller", "num2words", "sentencepiece", "sacremoses",
    "scipy", "numpy", "selenium_stealth", "undetected_chromedriver",
    "markdownify", "termcolor",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

os.environ.setdefault("WORK_DIR", "/tmp")

from sources.agents.planner_agent import PlannerAgent, SUB_AGENT_KEYS


class TestPlannerAgentStateless(unittest.TestCase):
    def setUp(self):
        self.planner = PlannerAgent.__new__(PlannerAgent)
        self.planner.llm = MagicMock()
        self.planner.verbose = False
        self.planner.browser = MagicMock()
        self.planner.personality_folder = "jarvis"
        self.planner.casual_agent_name = "Jarvis"
        self.planner.stop = False
        self.planner._active_sub_agent = None

    def test_personality_from_prompt(self):
        self.assertEqual(
            PlannerAgent.personality_from_prompt("prompts/jarvis/planner_agent.txt"),
            "jarvis",
        )
        self.assertEqual(
            PlannerAgent.personality_from_prompt("prompts/base/planner_agent.txt"),
            "base",
        )

    def test_create_sub_agent_uses_personality_folder(self):
        with patch("sources.agents.code_agent.CoderAgent") as coder_cls:
            coder_cls.return_value = MagicMock()
            self.planner.create_sub_agent("coder")

        coder_cls.assert_called_once_with(
            "coder",
            "prompts/jarvis/coder_agent.txt",
            self.planner.llm,
            self.planner.verbose,
        )

    def test_create_sub_agent_casual_uses_configured_name(self):
        with patch("sources.agents.casual_agent.CasualAgent") as casual_cls:
            casual_cls.return_value = MagicMock()
            self.planner.create_sub_agent("casual")

        casual_cls.assert_called_once_with(
            "Jarvis",
            "prompts/jarvis/casual_agent.txt",
            self.planner.llm,
            self.planner.verbose,
        )

    def test_create_sub_agent_rejects_unknown_agent(self):
        with self.assertRaises(ValueError):
            self.planner.create_sub_agent("unknown")

    def test_start_agent_process_spawns_fresh_agent_each_call(self):
        self.planner.make_prompt = MagicMock(return_value="do work")
        self.planner.status_message = ""
        self.planner.logger = MagicMock()
        self.planner.last_answer = ""
        self.planner.last_reasoning = ""
        self.planner.blocks_result = []

        def make_agent(_key):
            agent = MagicMock()
            agent.process = AsyncMock(return_value=("done", ""))
            agent.blocks_result = []
            agent.get_success = True
            agent.raw_answer_blocks = MagicMock(return_value="done")
            return agent

        with patch.object(self.planner, "create_sub_agent", side_effect=make_agent) as create_mock:
            import asyncio

            task = {"agent": "coder", "task": "write code"}
            asyncio.run(self.planner.start_agent_process(task, None))
            asyncio.run(self.planner.start_agent_process(task, None))

        self.assertEqual(create_mock.call_count, 2)

    def test_supported_sub_agents_matches_keys(self):
        self.assertEqual(self.planner.supported_sub_agents(), SUB_AGENT_KEYS)

    def test_request_stop_propagates_to_active_sub_agent(self):
        sub_agent = MagicMock()
        self.planner._active_sub_agent = sub_agent
        self.planner.status_message = ""
        PlannerAgent.request_stop(self.planner)
        sub_agent.request_stop.assert_called_once()
        self.assertTrue(self.planner.stop)

    def test_start_agent_process_propagates_stop_to_sub_agent(self):
        self.planner.make_prompt = MagicMock(return_value="do work")
        self.planner.status_message = ""
        self.planner.logger = MagicMock()
        self.planner.stop = True

        sub_agent = MagicMock()
        sub_agent.process = AsyncMock(return_value=("stopped", ""))
        sub_agent.blocks_result = []
        sub_agent.get_success = False
        sub_agent.raw_answer_blocks = MagicMock(return_value="stopped")

        with patch.object(self.planner, "create_sub_agent", return_value=sub_agent):
            import asyncio

            task = {"agent": "coder", "task": "write code"}
            asyncio.run(self.planner.start_agent_process(task, None))

        sub_agent.request_stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
