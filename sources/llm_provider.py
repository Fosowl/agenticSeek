import os
import platform
import socket
import subprocess
import time
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from ollama import Client as OllamaClient
from openai import OpenAI

from sources.errors import AgenticSeekError, ProviderContext, diagnose_provider_error, provider_error
from sources.logger import Logger, install_excepthook
from sources.utility import pretty_print, animate_thinking

class Provider:
    def __init__(self, provider_name, model, server_address="127.0.0.1:5000", is_local=False):
        install_excepthook()  # the provider is built first at startup: show later setup errors as panels
        self.provider_name = provider_name.lower()
        # Normalize provider name aliases (e.g. README documents 'togetherAI' but canonical key is 'together')
        _aliases = {"togetherai": "together"}
        self.provider_name = _aliases.get(self.provider_name, self.provider_name)
        self.model = model
        self.is_local = is_local
        self.server_ip = server_address
        self.server_address = server_address
        self.available_providers = {
            "ollama": self.ollama_fn,
            "server": self.server_fn,
            "openai": self.openai_fn,
            "lm-studio": self.lm_studio_fn,
            "huggingface": self.huggingface_fn,
            "google": self.google_fn,
            "deepseek": self.deepseek_fn,
            "together": self.together_fn,
            "dsk_deepseek": self.dsk_deepseek,
            "openrouter": self.openrouter_fn,
            "anthropic": self.anthropic_fn,
            "minimax": self.minimax_fn,
            "litellm": self.litellm_fn,
            "test": self.test_fn
        }
        self.logger = Logger("provider.log")
        self.api_key = None
        self.internal_url, self.in_docker = self.get_internal_url()
        self.unsafe_providers = ["openai", "deepseek", "dsk_deepseek", "together", "google", "openrouter", "anthropic", "minimax"]
        if self.provider_name not in self.available_providers:
            raise AgenticSeekError(
                "Unknown provider",
                f"provider_name = {provider_name} in config.ini is not a supported provider.",
                fixes=[f"Use one of: {', '.join(name for name in self.available_providers if name != 'test')}."])
        if self.provider_name in self.unsafe_providers and self.is_local == False:
            pretty_print("Warning: you are using an API provider. You data will be sent to the cloud.", color="warning")
            self.api_key = self.get_api_key(self.provider_name)
        elif self.provider_name != "ollama":
            pretty_print(f"Provider: {provider_name} initialized at {self.server_ip}", color="success")

    def get_model_name(self) -> str:
        return self.model

    def get_api_key(self, provider):
        load_dotenv()
        api_key = os.getenv(f"{provider.upper()}_API_KEY")
        if not api_key:
            raise provider_error("missing_key", ProviderContext(provider, self.model))
        return api_key

    def error_context(self) -> ProviderContext:
        return ProviderContext(self.provider_name, self.model, self.server_ip, self.is_local, self.api_key)

    def get_internal_url(self):
        load_dotenv()
        url = os.getenv("DOCKER_INTERNAL_URL")
        if not url: # running on host
            return "http://localhost", False
        return url, True

    def respond(self, history, verbose=True):
        """
        Use the choosen provider to generate text.
        Raises:
            AgenticSeekError: the request failed; the error explains why and how to fix it.
        """
        llm = self.available_providers[self.provider_name]
        self.logger.info(f"Using provider: {self.provider_name} at {self.server_ip}")
        try:
            return llm(history, verbose)
        except KeyboardInterrupt:
            self.logger.warning("User interrupted the operation with Ctrl+C")
            return "Operation interrupted by user. REQUEST_EXIT"
        except AgenticSeekError:
            raise
        except Exception as e:
            self.logger.error(f"Provider {self.provider_name} failed: {e!r}")
            raise diagnose_provider_error(e, self.error_context()) from e

    def is_ip_online(self, address: str, timeout: int = 10) -> bool:
        """
        Check if an address is online by sending a ping request.
        """
        if not address:
            return False
        parsed = urlparse(address if address.startswith(('http://', 'https://')) else f'http://{address}')

        hostname = parsed.hostname or address
        if "127.0.0.1" in address or "localhost" in address:
            return True
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            self.logger.error(f"Cannot resolve: {hostname}")
            return False
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip_address]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return False

    def server_fn(self, history, verbose=False):
        """
        Use a remote server with LLM to generate text.
        """
        thought = ""
        route_setup = f"{self.server_ip}/setup"
        route_gen = f"{self.server_ip}/generate"

        if not self.is_ip_online(self.server_ip):
            pretty_print(f"Server is offline at {self.server_ip}", color="failure")

        requests.post(route_setup, json={"model": self.model})
        requests.post(route_gen, json={"messages": history})
        is_complete = False
        while not is_complete:
            status = requests.get(f"{self.server_ip}/get_updated_sentence").json()
            if "error" in status:
                raise provider_error("server_error", self.error_context(), str(status["error"]))
            thought = status["sentence"]
            is_complete = bool(status["is_complete"])
            time.sleep(2)
        return thought

    def ollama_fn(self, history, verbose=False):
        """
        Use local or remote Ollama server to generate text.
        """
        thought = ""
        if self.is_local:
            server_port = self.server_address.split(":")[-1] if ":" in str(self.server_address) else "11434"
            host = f"{self.internal_url}:{server_port}"
        else:
            host = f"http://{self.server_address}"
        client = OllamaClient(host=host)

        try:
            stream = client.chat(
                model=self.model,
                messages=history,
                stream=True,
            )
            for chunk in stream:
                if verbose:
                    print(chunk["message"]["content"], end="", flush=True)
                thought += chunk["message"]["content"]
        except Exception as e:
            if getattr(e, "status_code", None) == 404:
                animate_thinking(f"Downloading {self.model}...")
                client.pull(self.model)
                return self.ollama_fn(history, verbose)
            raise

        return thought

    def huggingface_fn(self, history, verbose=False):
        """
        Use huggingface to generate text.
        """
        from huggingface_hub import InferenceClient
        client = InferenceClient(
            api_key=self.get_api_key("huggingface")
        )
        completion = client.chat.completions.create(
            model=self.model,
            messages=history,
            max_tokens=1024,
        )
        thought = completion.choices[0].message
        return thought.content

    def openai_fn(self, history, verbose=False):
        """
        Use openai to generate text.
        """
        base_url = self.server_ip
        if self.is_local and self.in_docker:
            try:
                host, port = base_url.split(':')
            except Exception as e:
                port = "8000"
            client = OpenAI(api_key=self.api_key, base_url=f"{self.internal_url}:{port}")
        elif self.is_local:
            client = OpenAI(api_key=self.api_key, base_url=f"http://{base_url}")
        else:
            client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=history,
        )
        if response is None:
            raise provider_error("empty_response", self.error_context())
        thought = response.choices[0].message.content
        if verbose:
            print(thought)
        return thought

    def anthropic_fn(self, history, verbose=False):
        """
        Use Anthropic to generate text.
        """
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)
        system_message = None
        messages = []
        for message in history:
            clean_message = {'role': message['role'], 'content': message['content']}
            if message['role'] == 'system':
                system_message = message['content']
            else:
                messages.append(clean_message)

        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=messages,
            system=system_message
        )
        if response is None:
            raise provider_error("empty_response", self.error_context())
        thought = response.content[0].text
        if verbose:
            print(thought)
        return thought

    def google_fn(self, history, verbose=False):
        """
        Use google gemini to generate text.
        """
        if self.is_local:
            raise provider_error("local_unsupported", self.error_context())

        client = OpenAI(api_key=self.api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
        )
        if response is None:
            raise provider_error("empty_response", self.error_context())
        thought = response.choices[0].message.content
        if verbose:
            print(thought)
        return thought

    def together_fn(self, history, verbose=False):
        """
        Use together AI for completion
        """
        from together import Together
        if self.is_local:
            raise provider_error("local_unsupported", self.error_context())
        client = Together(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
        )
        if response is None:
            raise provider_error("empty_response", self.error_context())
        thought = response.choices[0].message.content
        if verbose:
            print(thought)
        return thought

    def deepseek_fn(self, history, verbose=False):
        """
        Use deepseek api to generate text.
        """
        if self.is_local:
            raise provider_error("local_unsupported", self.error_context())
        client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
            stream=False
        )
        thought = response.choices[0].message.content
        if verbose:
            print(thought)
        return thought

    def lm_studio_fn(self, history, verbose=False):
        """
        Use local lm-studio server to generate text.
        """
        if self.in_docker:
            # Extract scheme, host, and port from server_address
            port = "1234"  # default
            addr = self.server_address
            if "://" not in addr:
                addr = f"http://{addr}"
            parsed_addr = urlparse(addr)
            if parsed_addr.port:
                port = str(parsed_addr.port)
            hostname = parsed_addr.hostname or "localhost"
            scheme = parsed_addr.scheme or "http"
            # For localhost/127.0.0.1, redirect to Docker internal URL so containers
            # can reach the host machine; for all other hosts use the configured address
            if hostname in ("localhost", "127.0.0.1"):
                url = f"{self.internal_url}:{port}"
            else:
                url = f"{scheme}://{hostname}:{port}"
        else:
            # Normalize the address to ensure it has a scheme prefix
            addr = self.server_ip
            if "://" not in addr:
                addr = f"http://{addr}"
            url = addr
        route_start = f"{url}/v1/chat/completions"
        payload = {
            "messages": history,
            "temperature": 0.7,
            "max_tokens": 4096,
            "model": self.model
        }

        response = requests.post(route_start, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if verbose:
            print("Response from LM Studio:", result)
        choices = result.get("choices") or [{}]
        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise provider_error("empty_response", self.error_context(), str(result)[:200])
        return content

    def openrouter_fn(self, history, verbose=False):
        """
        Use OpenRouter API to generate text.
        """
        if self.is_local:
            raise provider_error("local_unsupported", self.error_context())
        client = OpenAI(api_key=self.api_key, base_url="https://openrouter.ai/api/v1")
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
        )
        if response is None:
            raise provider_error("empty_response", self.error_context())
        thought = response.choices[0].message.content
        if verbose:
            print(thought)
        return thought

    def minimax_fn(self, history, verbose=False):
        """
        Use MiniMax API through its OpenAI- or Anthropic-compatible interface.

        Supported models:
        - MiniMax-M3: Latest flagship model with enhanced reasoning and coding (default)
        - MiniMax-M2.7: Previous flagship, kept for compatibility
        - MiniMax-M2.7-highspeed: High-speed version of M2.7 for low-latency scenarios

        Note: temperature must be in range (0.0, 1.0], default is 1.0
        """
        load_dotenv()
        base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")

        if self.is_local:
            raise provider_error("local_unsupported", self.error_context())
        if base_url.rstrip("/").endswith("/anthropic"):
            system_message = None
            messages = []
            for message in history:
                if message["role"] == "system":
                    system_message = message["content"]
                else:
                    messages.append(message)
            payload = {
                "model": self.model,
                "max_tokens": 1024,
                "messages": messages,
                "temperature": 1.0,
            }
            if system_message is not None:
                payload["system"] = system_message
            response = requests.post(
                f"{base_url.rstrip('/')}/v1/messages",
                headers={"Content-Type": "application/json", "X-Api-Key": self.api_key},
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            content = response.json().get("content", [])
            thought = "".join(
                block.get("text", "") for block in content if block.get("type") == "text"
            )
        else:
            client = OpenAI(api_key=self.api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=self.model,
                messages=history,
                temperature=1.0,
            )
            thought = response.choices[0].message.content if response is not None else None
        if not thought:
            raise provider_error("empty_response", self.error_context())
        if verbose:
            print(thought)
        return thought

    def dsk_deepseek(self, history, verbose=False):
        """
        Use: xtekky/deepseek4free
        For free api. Api key should be set to DSK_DEEPSEEK_API_KEY
        This is an unofficial provider, you'll have to find how to set it up yourself.
        """
        from dsk.api import DeepSeekAPI
        thought = ""
        message = '\n---\n'.join([f"{msg['role']}: {msg['content']}" for msg in history])

        api = DeepSeekAPI(self.api_key)
        chat_id = api.create_chat_session()
        for chunk in api.chat_completion(chat_id, message):
            if chunk['type'] == 'text':
                thought += chunk['content']
        return thought

    def litellm_fn(self, history, verbose=False):
        """
        Use LiteLLM AI gateway for completion.
        Routes to 100+ providers (OpenAI, Anthropic, Azure, Bedrock,
        Vertex AI, Groq, Together, Ollama, etc.) based on model prefix.
        See https://docs.litellm.ai/docs/providers
        """
        import litellm

        if self.is_local:
            raise provider_error("local_unsupported", self.error_context())

        api_key = os.getenv("LITELLM_API_KEY", None)

        call_kwargs = {
            "model": self.model,
            "messages": history,
            "drop_params": True,
        }
        if api_key:
            call_kwargs["api_key"] = api_key
        response = litellm.completion(**call_kwargs)
        if response is None:
            raise provider_error("empty_response", self.error_context())
        thought = response.choices[0].message.content
        if verbose:
            print(thought)
        return thought

    def test_fn(self, history, verbose=True):
        """
        This function is used to conduct tests.
        """
        thought = """
\n\n```json\n{\n  \"plan\": [\n    {\n      \"agent\": \"Web\",\n      \"id\": \"1\",\n      \"need\": null,\n      \"task\": \"Conduct a comprehensive web search to identify at least five AI startups located in Osaka. Use reliable sources and websites such as Crunchbase, TechCrunch, or local Japanese business directories. Capture the company names, their websites, areas of expertise, and any other relevant details.\"\n    },\n    {\n      \"agent\": \"Web\",\n      \"id\": \"2\",\n      \"need\": null,\n      \"task\": \"Perform a similar search to find at least five AI startups in Tokyo. Again, use trusted sources like Crunchbase, TechCrunch, or Japanese business news websites. Gather the same details as for Osaka: company names, websites, areas of focus, and additional information.\"\n    },\n    {\n      \"agent\": \"File\",\n      \"id\": \"3\",\n      \"need\": [\"1\", \"2\"],\n      \"task\": \"Create a new text file named research_japan.txt in the user's home directory. Organize the data collected from both searches into this file, ensuring it is well-structured and formatted for readability. Include headers for Osaka and Tokyo sections, followed by the details of each startup found.\"\n    }\n  ]\n}\n```
        """
        return thought


if __name__ == "__main__":
    provider = Provider("server", "deepseek-r1:32b", " x.x.x.x:8080")
    res = provider.respond(["user", "Hello, how are you?"])
    print("Response:", res)
