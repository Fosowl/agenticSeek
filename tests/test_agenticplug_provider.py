import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.llm_provider import Provider


class TestAgenticPlugProvider(unittest.TestCase):
    """Tests for the AgenticPlug (OpenAI-compatible) provider."""

    def _make_provider(self, server_address="127.0.0.1:8080"):
        # is_local=True keeps the provider out of the unsafe-provider path so it
        # does not try to load an API key during __init__.
        return Provider(
            "agenticplug",
            "hermes",
            server_address=server_address,
            is_local=True,
        )

    def test_agenticplug_registered(self):
        provider = self._make_provider()
        self.assertIn("agenticplug", provider.available_providers)

    def test_agenticplug_not_in_unsafe_providers(self):
        """AgenticPlug runs against a local/self-hosted gateway, so it must not
        be treated as a cloud provider that auto-loads a *_API_KEY env var."""
        provider = self._make_provider()
        self.assertNotIn("agenticplug", provider.unsafe_providers)
        self.assertIsNone(provider.api_key)

    @patch.dict(os.environ, {}, clear=False)
    @patch('sources.llm_provider.OpenAI')
    def test_defaults_to_local_server_address(self, mock_openai_class):
        for var in ("AGENTICPLUG_BASE_URL", "AGENTICPLUG_API_KEY",
                    "AGENTICPLUG_MODEL", "AGENTICPLUG_ROUTE_HEADER"):
            os.environ.pop(var, None)

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="ok"))]
        )

        provider = self._make_provider(server_address="127.0.0.1:8080")
        provider.agenticplug_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_openai_class.call_args.kwargs
        self.assertEqual(call_kwargs["base_url"], "http://127.0.0.1:8080/v1")
        self.assertEqual(call_kwargs["api_key"], "not-required")
        self.assertNotIn("default_headers", call_kwargs)

    @patch.dict(os.environ, {
        "AGENTICPLUG_BASE_URL": "http://127.0.0.1:9000/v1",
        "AGENTICPLUG_API_KEY": "dev-placeholder",
        "AGENTICPLUG_MODEL": "hermes-large",
        "AGENTICPLUG_ROUTE_HEADER": "hermes",
    })
    @patch('sources.llm_provider.OpenAI')
    def test_env_overrides_apply(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="ok"))]
        )

        provider = self._make_provider()
        provider.agenticplug_fn([{"role": "user", "content": "hi"}])

        call_kwargs = mock_openai_class.call_args.kwargs
        self.assertEqual(call_kwargs["base_url"], "http://127.0.0.1:9000/v1")
        self.assertEqual(call_kwargs["api_key"], "dev-placeholder")
        self.assertEqual(
            call_kwargs["default_headers"],
            {"X-AgenticPlug-Route": "hermes"},
        )

        create_kwargs = mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs["model"], "hermes-large")

    @patch.dict(os.environ, {}, clear=False)
    @patch('sources.llm_provider.OpenAI')
    def test_returns_response_content(self, mock_openai_class):
        for var in ("AGENTICPLUG_BASE_URL", "AGENTICPLUG_API_KEY",
                    "AGENTICPLUG_MODEL", "AGENTICPLUG_ROUTE_HEADER"):
            os.environ.pop(var, None)

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="hello world"))]
        )

        provider = self._make_provider()
        result = provider.agenticplug_fn([{"role": "user", "content": "hi"}])
        self.assertEqual(result, "hello world")

    @patch.dict(os.environ, {}, clear=False)
    @patch('sources.llm_provider.OpenAI')
    def test_handles_api_error(self, mock_openai_class):
        for var in ("AGENTICPLUG_BASE_URL", "AGENTICPLUG_API_KEY",
                    "AGENTICPLUG_MODEL", "AGENTICPLUG_ROUTE_HEADER"):
            os.environ.pop(var, None)

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("upstream down")

        provider = self._make_provider()
        with self.assertRaises(Exception) as ctx:
            provider.agenticplug_fn([{"role": "user", "content": "hi"}])
        self.assertIn("AgenticPlug API error", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
