import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.llm_provider import Provider


class TestDeepseekProvider(unittest.TestCase):
    """Test cases for Deepseek provider integration."""

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'})
    def test_deepseek_forwards_configured_model(self, mock_openai_class):
        """deepseek_fn must send the configured model, not a hardcoded literal."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("deepseek", "deepseek-reasoner", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.deepseek_fn(history)

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_kwargs['model'], "deepseek-reasoner")

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'})
    def test_deepseek_local_not_supported(self, mock_openai_class):
        """Test that deepseek provider raises error when is_local=True."""
        provider = Provider("deepseek", "deepseek-chat", is_local=True)
        provider.api_key = 'test-key'
        history = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(Exception) as context:
            provider.deepseek_fn(history)
        self.assertIn("not available for local use", str(context.exception))

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'})
    def test_deepseek_returns_response_content(self, mock_openai_class):
        """Test that deepseek provider returns response content."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("deepseek", "deepseek-chat", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            result = provider.deepseek_fn(history)

            self.assertEqual(result, "Test response")


if __name__ == '__main__':
    unittest.main()
