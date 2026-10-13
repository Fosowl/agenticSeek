import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.llm_provider import Provider


class TestCheaperInferenceProvider(unittest.TestCase):
    """Test cases for Cheaper Inference provider integration."""

    def test_cheaperinference_provider_registered(self):
        """Test that cheaperinference provider is registered in available_providers."""
        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("cheaperinference", "gpt-5.4-mini", is_local=False)
            self.assertIn("cheaperinference", provider.available_providers)

    def test_cheaperinference_in_unsafe_providers(self):
        """Test that cheaperinference is in unsafe_providers list."""
        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("cheaperinference", "gpt-5.4-mini", is_local=False)
            self.assertIn("cheaperinference", provider.unsafe_providers)

    def test_cheaperinference_api_key_required(self):
        """Test that API key is fetched for cheaperinference provider."""
        with patch.object(Provider, 'get_api_key', return_value='test-ci-key') as mock_get_key:
            provider = Provider("cheaperinference", "gpt-5.4-mini", is_local=False)
            mock_get_key.assert_called_with("cheaperinference")
            self.assertEqual(provider.api_key, 'test-ci-key')

    @patch('sources.llm_provider.OpenAI')
    def test_cheaperinference_local_not_supported(self, mock_openai_class):
        """Test that cheaperinference provider raises error when is_local=True."""
        provider = Provider("cheaperinference", "gpt-5.4-mini", is_local=True)
        provider.api_key = 'test-key'
        history = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(Exception) as context:
            provider.cheaperinference_fn(history)
        self.assertIn("not available for local use", str(context.exception))

    @patch('sources.llm_provider.OpenAI')
    def test_cheaperinference_uses_correct_base_url(self, mock_openai_class):
        """Test that cheaperinference provider uses correct base URL and model."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("cheaperinference", "gpt-5.4-mini", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            result = provider.cheaperinference_fn(history)

            mock_openai_class.assert_called_with(
                api_key='test-key',
                base_url='https://api.cheaperinference.com/v1'
            )
            mock_client.chat.completions.create.assert_called_with(
                model="gpt-5.4-mini",
                messages=history,
            )
            self.assertEqual(result, "Hello!")


if __name__ == '__main__':
    unittest.main()
