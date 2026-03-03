import unittest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch

# Mock heavy dependencies to allow import without installing them all
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

from sources.agents.planner_agent import PlannerAgent


class TestPlannerAgentParsing(unittest.TestCase):
    """Test suite for PlannerAgent.parse_agent_tasks JSON parsing robustness."""

    def setUp(self):
        self.agent = PlannerAgent.__new__(PlannerAgent)
        self.agent.tools = {"json": MagicMock()}
        self.agent.tools["json"].tag = "json"
        self.agent.logger = MagicMock()
        self.agent.agents = {
            "coder": MagicMock(),
            "file": MagicMock(),
            "web": MagicMock(),
            "casual": MagicMock()
        }

    def test_parse_valid_json(self):
        """Test that valid JSON plan is parsed correctly."""
        valid_json = '{"plan": [{"agent": "web", "id": "1", "task": "Search info", "need": []}]}'
        self.agent.tools["json"].load_exec_block.return_value = ([valid_json], None)

        with patch.object(self.agent, 'get_task_names', return_value=["Task 1: Search info"]):
            result = self.agent.parse_agent_tasks("dummy text")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1]['agent'], 'web')

    def test_parse_malformed_json_returns_empty(self):
        """Test that malformed JSON returns empty list instead of crashing."""
        malformed_json = '{"plan": [{"agent": "web", "id": "1" "task": "missing comma"}]}'
        self.agent.tools["json"].load_exec_block.return_value = ([malformed_json], None)

        with patch.object(self.agent, 'get_task_names', return_value=[]):
            result = self.agent.parse_agent_tasks("dummy text")

        self.assertEqual(result, [])
        self.agent.logger.warning.assert_called_once()

    def test_parse_truncated_json_returns_empty(self):
        """Test that truncated JSON returns empty list instead of crashing."""
        truncated_json = '{"plan": [{"agent": "web", "id": "1", "task": "Search'
        self.agent.tools["json"].load_exec_block.return_value = ([truncated_json], None)

        with patch.object(self.agent, 'get_task_names', return_value=[]):
            result = self.agent.parse_agent_tasks("dummy text")

        self.assertEqual(result, [])
        self.agent.logger.warning.assert_called_once()

    def test_parse_no_blocks_returns_empty(self):
        """Test that missing blocks returns empty list."""
        self.agent.tools["json"].load_exec_block.return_value = (None, None)

        with patch.object(self.agent, 'get_task_names', return_value=[]):
            result = self.agent.parse_agent_tasks("no json here")

        self.assertEqual(result, [])

    def test_parse_invalid_agent_returns_empty(self):
        """Test that an unknown agent name returns empty list."""
        valid_json = '{"plan": [{"agent": "unknown_agent", "id": "1", "task": "Do something", "need": []}]}'
        self.agent.tools["json"].load_exec_block.return_value = ([valid_json], None)

        with patch.object(self.agent, 'get_task_names', return_value=["Task 1"]):
            result = self.agent.parse_agent_tasks("dummy text")

        self.assertEqual(result, [])

    def test_parse_multiple_tasks(self):
        """Test parsing a plan with multiple tasks."""
        multi_task_json = '{"plan": [{"agent": "web", "id": "1", "task": "Search", "need": []}, {"agent": "coder", "id": "2", "task": "Code it", "need": ["1"]}]}'
        self.agent.tools["json"].load_exec_block.return_value = ([multi_task_json], None)

        with patch.object(self.agent, 'get_task_names', return_value=["Task 1: Search", "Task 2: Code it"]):
            result = self.agent.parse_agent_tasks("dummy text")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1]['agent'], 'web')
        self.assertEqual(result[1][1]['agent'], 'coder')


if __name__ == '__main__':
    unittest.main()
