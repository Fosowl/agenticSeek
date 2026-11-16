import httpx
import pytest
from ollama import Client

from sources import llm_provider


@pytest.mark.parametrize(
    ("address", "expected_url"),
    [
        ("ollama.example:11434", "http://ollama.example:11434/api/chat"),
        ("https://ollama.example/llm", "https://ollama.example/llm/api/chat"),
    ],
)
def test_remote_ollama_uses_configured_endpoint(
    address, expected_url, monkeypatch, tmp_path
):
    monkeypatch.setenv("AGENT_RUNTIME_DIR", str(tmp_path))
    requested_urls = []

    def respond(request):
        requested_urls.append(str(request.url))
        return httpx.Response(
            200, json={"message": {"role": "assistant", "content": "ok"}, "done": True}
        )

    def mock_client(host):
        return Client(host=host, transport=httpx.MockTransport(respond))

    monkeypatch.setattr(llm_provider, "OllamaClient", mock_client)
    provider = llm_provider.Provider("ollama", "test-model", address, is_local=False)

    assert provider.respond([], verbose=False) == "ok"
    assert requested_urls == [expected_url]
