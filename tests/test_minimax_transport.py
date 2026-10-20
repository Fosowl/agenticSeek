"""Exercise serialized MiniMax requests through the public provider entry point."""

import copy
import json
import os
import unittest
from unittest.mock import patch

import httpx
import requests
from openai import OpenAI

from sources.llm_provider import Provider


class TestMiniMaxTransport(unittest.TestCase):
    def test_model_selection_at_transport_boundary(self):
        models = (None, "", "MiniMax-M3.1-Flash", "MiniMax-M3", "MiniMax-M2.7",
                  "MiniMax-M2.7-highspeed", "custom-model")
        for host in ("api.minimax.io", "api.minimaxi.com"):
            for protocol in ("v1", "anthropic"):
                for model in models:
                    with self.subTest(host=host, protocol=protocol, model=model):
                        self.check_request(host, protocol, model)

    def check_request(self, host, protocol, model):
        base_url = f"https://{host}/{protocol}"
        # Preserve protocol-specific structured content and conversation history.
        image = (
            {"type": "image", "source": {"type": "url", "url": "https://example.com/image.png"}}
            if protocol == "anthropic" else
            {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}
        )
        history = [
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": [{"type": "text", "text": "Hello"}, image]},
        ]
        original = copy.deepcopy(history)
        captured = []

        def openai_transport(request):
            captured.append((str(request.url), json.loads(request.content)))
            return httpx.Response(200, json={
                "id": "test-completion", "object": "chat.completion", "created": 0,
                "model": model or "MiniMax-M3.1-Flash",
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": "Hello!"}}],
            })

        def anthropic_transport(session, request, **kwargs):
            captured.append((request.url, json.loads(request.body)))
            response = requests.Response()
            response.status_code = 200
            response._content = json.dumps({"content": [
                {"type": "thinking", "thinking": "Reasoning"},
                {"type": "text", "text": "Hello!"},
            ]}).encode()
            return response

        with httpx.Client(transport=httpx.MockTransport(openai_transport)) as http_client:
            client = OpenAI(api_key="test-key", base_url=base_url, http_client=http_client)
            with patch.dict(os.environ, {"MINIMAX_BASE_URL": base_url}), \
                    patch("sources.llm_provider.load_dotenv"), \
                    patch.object(Provider, "get_api_key", return_value="test-key"), \
                    patch("sources.llm_provider.OpenAI", return_value=client), \
                    patch.object(requests.Session, "send", new=anthropic_transport):
                provider = Provider("MiniMax", model, is_local=False)
                self.assertEqual(provider.respond(history, verbose=False), "Hello!")
                self.assertEqual(provider.get_model_name(), model or "MiniMax-M3.1-Flash")

        self.assertEqual(history, original)
        self.assertEqual(len(captured), 1)
        url, payload = captured[0]
        expected = {"model": model or "MiniMax-M3.1-Flash", "temperature": 1.0}
        if protocol == "anthropic":
            self.assertEqual(url, f"{base_url}/v1/messages")
            expected.update(max_tokens=1024, system="Be helpful.", messages=history[1:])
        else:
            self.assertEqual(url, f"{base_url}/chat/completions")
            expected["messages"] = history
        # No unsupported thinking, effort, or service-tier overrides are introduced.
        self.assertEqual(payload, expected)

    def test_other_provider_model_is_unchanged(self):
        for model in (None, "", "saved-model"):
            with self.subTest(model=model):
                self.assertEqual(Provider("test", model).get_model_name(), model)


if __name__ == "__main__":
    unittest.main()
