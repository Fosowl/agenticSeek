import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.llm_provider import Provider


class TestLiteLLMProvider(unittest.TestCase):
    """Test cases for LiteLLM provider integration."""

    def test_litellm_provider_registered(self):
        """Test that litellm provider is registered in available_providers."""
        provider = Provider("litellm", "gpt-4o-mini", is_local=False)
        self.assertIn("litellm", provider.available_providers)

    def test_litellm_not_in_unsafe_providers(self):
        """LiteLLM is not in unsafe_providers because it resolves API keys itself."""
        provider = Provider("litellm", "gpt-4o-mini", is_local=False)
        self.assertNotIn("litellm", provider.unsafe_providers)

    def test_litellm_no_api_key_required_at_init(self):
        """LiteLLM does not require LITELLM_API_KEY at init."""
        provider = Provider("litellm", "gpt-4o-mini", is_local=False)
        self.assertIsNone(provider.api_key)

    def test_litellm_local_not_supported(self):
        """Test that litellm provider raises error when is_local=True."""
        provider = Provider("litellm", "gpt-4o-mini", is_local=True)
        history = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(Exception) as context:
            provider.litellm_fn(history)
        self.assertIn("not available for local use", str(context.exception))

    @patch('litellm.completion')
    def test_litellm_fn_returns_content(self, mock_completion):
        """Test that litellm_fn returns response content."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="42"))]
        mock_completion.return_value = mock_response

        provider = Provider("litellm", "gpt-4o-mini", is_local=False)
        history = [{"role": "user", "content": "What is 2+2?"}]
        result = provider.litellm_fn(history)

        self.assertEqual(result, "42")

    @patch('litellm.completion')
    def test_litellm_fn_passes_drop_params(self, mock_completion):
        """Test that litellm_fn sets drop_params=True."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
        mock_completion.return_value = mock_response

        provider = Provider("litellm", "anthropic/claude-sonnet-4", is_local=False)
        provider.litellm_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_completion.call_args[1]
        self.assertTrue(call_kwargs["drop_params"])

    @patch('litellm.completion')
    def test_litellm_fn_passes_model(self, mock_completion):
        """Test that litellm_fn passes the correct model string."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
        mock_completion.return_value = mock_response

        provider = Provider("litellm", "anthropic/claude-sonnet-4", is_local=False)
        provider.litellm_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_completion.call_args[1]
        self.assertEqual(call_kwargs["model"], "anthropic/claude-sonnet-4")

    @patch.dict(os.environ, {"LITELLM_API_KEY": "sk-test-123"})
    @patch('litellm.completion')
    def test_litellm_fn_passes_api_key_from_env(self, mock_completion):
        """Test that litellm_fn forwards LITELLM_API_KEY when set."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
        mock_completion.return_value = mock_response

        provider = Provider("litellm", "gpt-4o", is_local=False)
        provider.litellm_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_completion.call_args[1]
        self.assertEqual(call_kwargs["api_key"], "sk-test-123")

    @patch.dict(os.environ, {}, clear=True)
    @patch('litellm.completion')
    def test_litellm_fn_omits_api_key_when_not_set(self, mock_completion):
        """Test that litellm_fn omits api_key when LITELLM_API_KEY is not set."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
        mock_completion.return_value = mock_response

        provider = Provider("litellm", "gpt-4o", is_local=False)
        provider.litellm_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_completion.call_args[1]
        self.assertNotIn("api_key", call_kwargs)

    @patch('litellm.completion')
    def test_litellm_fn_raises_on_empty_response(self, mock_completion):
        """Test that litellm_fn raises on empty response."""
        mock_completion.return_value = None

        provider = Provider("litellm", "gpt-4o-mini", is_local=False)
        with self.assertRaises(Exception) as ctx:
            provider.litellm_fn([{"role": "user", "content": "hi"}])
        self.assertIn("empty", str(ctx.exception).lower())

    @patch('litellm.completion')
    def test_litellm_fn_raises_on_api_error(self, mock_completion):
        """Test that litellm_fn wraps API errors."""
        mock_completion.side_effect = Exception("rate limit exceeded")

        provider = Provider("litellm", "gpt-4o-mini", is_local=False)
        with self.assertRaises(Exception) as ctx:
            provider.litellm_fn([{"role": "user", "content": "hi"}])
        self.assertIn("LiteLLM API error", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
