import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.llm_provider import Provider


class TestAtlasCloudProvider(unittest.TestCase):
    """Test cases for Atlas Cloud provider integration."""

    def setUp(self):
        self._saved = {
            key: os.environ.get(key)
            for key in ("ATLASCLOUD_API_KEY", "ATLASCLOUD_BASE_URL")
        }
        os.environ["ATLASCLOUD_API_KEY"] = "apikey-test"
        os.environ.pop("ATLASCLOUD_BASE_URL", None)

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_atlascloud_provider_registered(self):
        """Test that atlascloud provider is registered in available_providers."""
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        self.assertIn("atlascloud", provider.available_providers)

    def test_atlascloud_in_unsafe_providers(self):
        """It is a cloud API, so the user must get the data-leaves-your-machine warning."""
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        self.assertIn("atlascloud", provider.unsafe_providers)

    def test_api_key_is_read_from_env(self):
        """The key comes from ATLASCLOUD_API_KEY via the shared get_api_key path."""
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        self.assertEqual(provider.api_key, "apikey-test")

    def test_missing_api_key_raises_with_the_env_var_name(self):
        os.environ.pop("ATLASCLOUD_API_KEY", None)
        with patch("sources.llm_provider.load_dotenv"):
            with self.assertRaises(ValueError) as context:
                Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        self.assertIn("ATLASCLOUD_API_KEY", str(context.exception))

    def test_atlascloud_local_not_supported(self):
        """A remote gateway cannot be served from the local machine."""
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=True)
        history = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(Exception) as context:
            provider.atlascloud_fn(history)
        self.assertIn("not available for local use", str(context.exception))

    @patch("sources.llm_provider.OpenAI")
    def test_default_base_url_is_the_gateway(self, mock_openai):
        mock_openai.return_value.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="ok"))]
        )
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        provider.atlascloud_fn([{"role": "user", "content": "hi"}])

        self.assertEqual(
            mock_openai.call_args[1]["base_url"], "https://api.atlascloud.ai/v1"
        )
        self.assertEqual(mock_openai.call_args[1]["api_key"], "apikey-test")

    @patch("sources.llm_provider.OpenAI")
    def test_base_url_override_is_honoured(self, mock_openai):
        os.environ["ATLASCLOUD_BASE_URL"] = "https://gateway.internal/v1"
        mock_openai.return_value.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="ok"))]
        )
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        provider.atlascloud_fn([{"role": "user", "content": "hi"}])

        self.assertEqual(
            mock_openai.call_args[1]["base_url"], "https://gateway.internal/v1"
        )

    @patch("sources.llm_provider.OpenAI")
    def test_model_and_history_are_forwarded_unchanged(self, mock_openai):
        """The gateway's model ids are 'vendor/model'; they must pass through as-is."""
        create = mock_openai.return_value.chat.completions.create
        create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="42"))]
        )
        history = [
            {"role": "system", "content": "You are terse."},
            {"role": "user", "content": "What is 2+2?"},
        ]
        provider = Provider("atlascloud", "deepseek-ai/deepseek-v3.2", is_local=False)
        result = provider.atlascloud_fn(history)

        self.assertEqual(result, "42")
        self.assertEqual(create.call_args[1]["model"], "deepseek-ai/deepseek-v3.2")
        self.assertEqual(create.call_args[1]["messages"], history)

    @patch("sources.llm_provider.OpenAI")
    def test_empty_content_raises(self, mock_openai):
        """An empty completion must fail loudly, not be returned as a valid answer."""
        mock_openai.return_value.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=""))]
        )
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        with self.assertRaises(Exception) as context:
            provider.atlascloud_fn([{"role": "user", "content": "hi"}])
        self.assertIn("empty", str(context.exception).lower())

    @patch("sources.llm_provider.OpenAI")
    def test_api_error_is_wrapped_with_the_provider_name(self, mock_openai):
        mock_openai.return_value.chat.completions.create.side_effect = Exception("401")
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        with self.assertRaises(Exception) as context:
            provider.atlascloud_fn([{"role": "user", "content": "hi"}])
        self.assertIn("Atlas Cloud API error", str(context.exception))

    @patch("sources.llm_provider.OpenAI")
    def test_respond_dispatches_to_atlascloud(self, mock_openai):
        """respond() must route the provider name to atlascloud_fn."""
        mock_openai.return_value.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="routed"))]
        )
        provider = Provider("atlascloud", "openai/gpt-4.1-mini", is_local=False)
        self.assertEqual(
            provider.respond([{"role": "user", "content": "hi"}], verbose=False),
            "routed",
        )


if __name__ == "__main__":
    unittest.main()
