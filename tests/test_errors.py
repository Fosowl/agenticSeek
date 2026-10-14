import os
import sys
import unittest

import httpx
import openai
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.errors import ProviderContext, diagnose_provider_error

REQUEST = httpx.Request("POST", "https://api.example.com/v1/chat/completions")


def openai_status_error(cls, status, body):
    return cls(f"Error code: {status} - {body}", response=httpx.Response(status, request=REQUEST), body=body)


def requests_http_error(status, content):
    response = requests.Response()
    response.status_code = status
    response._content = content
    return requests.HTTPError(f"{status} Error", response=response)


class TestDiagnoseProviderError(unittest.TestCase):

    def test_openrouter_401_shows_api_message_and_flags_foreign_key(self):
        exc = openai_status_error(openai.AuthenticationError, 401,
                                  {"message": "Missing Authentication header", "code": 401})
        ctx = ProviderContext("openrouter", "openai/gpt-oss-120b", api_key="bit-not-an-openrouter-key")
        err = diagnose_provider_error(exc, ctx)
        self.assertEqual((err.kind, err.status_code), ("auth", 401))
        self.assertIn("Missing Authentication header", err.message)
        self.assertTrue(any("sk-or-" in cause for cause in err.causes))
        self.assertNotIn("bit-not-an-openrouter-key", err.summary())

    def test_well_formed_key_is_not_flagged(self):
        exc = openai_status_error(openai.AuthenticationError, 401, {"message": "User not found."})
        err = diagnose_provider_error(exc, ProviderContext("openrouter", "m", api_key="sk-or-v1-abc"))
        self.assertFalse(any("sk-or-" in cause for cause in err.causes))

    def test_timeout_wins_over_connection(self):
        # APITimeoutError subclasses APIConnectionError
        err = diagnose_provider_error(openai.APITimeoutError(request=REQUEST), ProviderContext("openai", "gpt-4o"))
        self.assertEqual(err.kind, "timeout")

    def test_ollama_refused_connection_points_to_ollama_serve(self):
        exc = httpx.ConnectError("[Errno 61] Connection refused")
        err = diagnose_provider_error(exc, ProviderContext("ollama", "llama3", "127.0.0.1:11434", is_local=True))
        self.assertEqual(err.kind, "connection")
        self.assertTrue(any("ollama serve" in fix for fix in err.fixes))

    def test_refused_requests_connection_is_not_a_timeout(self):
        # urllib3's NewConnectionError subclasses ConnectTimeoutError
        try:
            requests.post("http://127.0.0.1:1/v1/chat/completions", timeout=5)
        except requests.ConnectionError as exc:
            err = diagnose_provider_error(exc, ProviderContext("lm-studio", "llama3", "127.0.0.1:1"))
        self.assertEqual(err.kind, "connection")

    def test_http_429_uses_json_error_message(self):
        exc = requests_http_error(429, b'{"error": {"message": "slow down"}}')
        err = diagnose_provider_error(exc, ProviderContext("minimax", "MiniMax-M3"))
        self.assertEqual((err.kind, err.status_code), ("rate_limit", 429))
        self.assertIn("slow down", err.message)

    def test_invalid_model_id_beats_generic_bad_request(self):
        exc = openai_status_error(openai.BadRequestError, 400,
                                  {"message": "openai/gpt-oss-12b is not a valid model ID", "code": 400})
        err = diagnose_provider_error(exc, ProviderContext("openrouter", "openai/gpt-oss-12b"))
        self.assertEqual(err.kind, "model_not_found")

    def test_missing_module_suggests_pip_install(self):
        exc = ModuleNotFoundError("No module named 'litellm'", name="litellm")
        err = diagnose_provider_error(exc, ProviderContext("litellm", "gpt-4o-mini"))
        self.assertEqual(err.kind, "missing_dependency")
        self.assertTrue(any("pip install litellm" in fix for fix in err.fixes))


if __name__ == '__main__':
    unittest.main()
