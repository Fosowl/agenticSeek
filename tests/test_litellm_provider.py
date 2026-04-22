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
        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("litellm", "gpt-4o-mini", is_local=False)
            self.assertIn("litellm", provider.available_providers)

    def test_litellm_in_unsafe_providers(self):
        """Test that litellm is in unsafe_providers list."""
        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("litellm", "gpt-4o-mini", is_local=False)
            self.assertIn("litellm", provider.unsafe_providers)

    def test_litellm_api_key_required(self):
        """Test that API key is fetched for litellm provider."""
        with patch.object(Provider, 'get_api_key', return_value='test-litellm-key') as mock_get_key:
            provider = Provider("litellm", "gpt-4o-mini", is_local=False)
            mock_get_key.assert_called_with("litellm")
            self.assertEqual(provider.api_key, 'test-litellm-key')

    def test_litellm_local_not_supported(self):
        """Test that litellm provider raises error when is_local=True."""
        provider = Provider("litellm", "gpt-4o-mini", is_local=True)
        provider.api_key = 'test-key'
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

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
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

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
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

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("litellm", "anthropic/claude-sonnet-4", is_local=False)
            provider.litellm_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_completion.call_args[1]
        self.assertEqual(call_kwargs["model"], "anthropic/claude-sonnet-4")

    @patch('litellm.completion')
    def test_litellm_fn_passes_api_key(self, mock_completion):
        """Test that litellm_fn forwards the API key."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
        mock_completion.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='sk-test-123'):
            provider = Provider("litellm", "gpt-4o", is_local=False)
            provider.litellm_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_completion.call_args[1]
        self.assertEqual(call_kwargs["api_key"], "sk-test-123")

    @patch('litellm.completion')
    def test_litellm_fn_raises_on_empty_response(self, mock_completion):
        """Test that litellm_fn raises on empty response."""
        mock_completion.return_value = None

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("litellm", "gpt-4o-mini", is_local=False)
            with self.assertRaises(Exception) as ctx:
                provider.litellm_fn([{"role": "user", "content": "hi"}])
            self.assertIn("empty", str(ctx.exception).lower())

    @patch('litellm.completion')
    def test_litellm_fn_raises_on_api_error(self, mock_completion):
        """Test that litellm_fn wraps API errors."""
        mock_completion.side_effect = Exception("rate limit exceeded")

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("litellm", "gpt-4o-mini", is_local=False)
            with self.assertRaises(Exception) as ctx:
                provider.litellm_fn([{"role": "user", "content": "hi"}])
            self.assertIn("LiteLLM API error", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
