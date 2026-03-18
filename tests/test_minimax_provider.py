import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.llm_provider import Provider


class TestMiniMaxProvider(unittest.TestCase):
    """Test cases for MiniMax provider integration."""

    def test_minimax_provider_registered(self):
        """Test that minimax provider is registered in available_providers."""
        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            self.assertIn("minimax", provider.available_providers)

    def test_minimax_in_unsafe_providers(self):
        """Test that minimax is in unsafe_providers list."""
        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            self.assertIn("minimax", provider.unsafe_providers)

    def test_minimax_api_key_required(self):
        """Test that API key is fetched for minimax provider."""
        with patch.object(Provider, 'get_api_key', return_value='test-minimax-key') as mock_get_key:
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            mock_get_key.assert_called_with("minimax")
            self.assertEqual(provider.api_key, 'test-minimax-key')

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_local_not_supported(self, mock_openai_class):
        """Test that minimax provider raises error when is_local=True."""
        provider = Provider("minimax", "MiniMax-M2.5", is_local=True)
        provider.api_key = 'test-key'
        history = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(Exception) as context:
            provider.minimax_fn(history)
        self.assertIn("not available for local use", str(context.exception))

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_uses_correct_base_url(self, mock_openai_class):
        """Test that minimax provider uses correct base URL."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            mock_openai_class.assert_called_with(
                api_key='test-key',
                base_url='https://api.minimax.io/v1'
            )

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {
        'MINIMAX_API_KEY': 'test-key',
        'MINIMAX_BASE_URL': 'https://api.minimaxi.com/v1'
    })
    def test_minimax_custom_base_url(self, mock_openai_class):
        """Test that minimax provider uses custom base URL from env."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            mock_openai_class.assert_called_with(
                api_key='test-key',
                base_url='https://api.minimaxi.com/v1'
            )

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_uses_temperature_one(self, mock_openai_class):
        """Test that minimax provider uses temperature=1.0."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_kwargs['temperature'], 1.0)

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_returns_response_content(self, mock_openai_class):
        """Test that minimax provider returns response content."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            result = provider.minimax_fn(history)

            self.assertEqual(result, "Test response")

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_handles_empty_response(self, mock_openai_class):
        """Test that minimax provider handles empty response."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = None

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]

            with self.assertRaises(Exception) as context:
                provider.minimax_fn(history)
            self.assertIn("response is empty", str(context.exception))

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_handles_api_error(self, mock_openai_class):
        """Test that minimax provider handles API errors."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]

            with self.assertRaises(Exception) as context:
                provider.minimax_fn(history)
            self.assertIn("MiniMax API error", str(context.exception))


class TestMiniMaxProviderModels(unittest.TestCase):
    """Test cases for MiniMax provider model configurations."""

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_m27_model(self, mock_openai_class):
        """Test MiniMax-M2.7 model."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.7", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_kwargs['model'], "MiniMax-M2.7")

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_m27_highspeed_model(self, mock_openai_class):
        """Test MiniMax-M2.7-highspeed model."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.7-highspeed", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_kwargs['model'], "MiniMax-M2.7-highspeed")

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_m25_model(self, mock_openai_class):
        """Test MiniMax-M2.5 model."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_kwargs['model'], "MiniMax-M2.5")

    @patch('sources.llm_provider.OpenAI')
    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_minimax_m25_highspeed_model(self, mock_openai_class):
        """Test MiniMax-M2.5-highspeed model."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(Provider, 'get_api_key', return_value='test-key'):
            provider = Provider("minimax", "MiniMax-M2.5-highspeed", is_local=False)
            history = [{"role": "user", "content": "Hello"}]
            provider.minimax_fn(history)

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_kwargs['model'], "MiniMax-M2.5-highspeed")


if __name__ == '__main__':
    unittest.main()
