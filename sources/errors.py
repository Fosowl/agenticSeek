"""
User-facing errors.

An AgenticSeekError carries what went wrong, why it plausibly happened and how
to fix it, so it can be shown as a readable panel (sources.logger.report_error)
instead of a raw traceback. diagnose_provider_error() turns the exceptions raised
by LLM SDKs and HTTP clients into such errors.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Sequence, Tuple

from dotenv import find_dotenv

ISSUES_URL = "https://github.com/Fosowl/agenticSeek/issues"


class AgenticSeekError(Exception):
    """An error meant for the user: a short title, the error itself, plausible causes and fixes."""

    def __init__(self, title: str, message: str, causes: Sequence[str] = (),
                 fixes: Sequence[str] = (), context: str = ""):
        super().__init__(f"{title}: {message}")
        self.title = title
        self.message = message
        self.causes = list(causes)
        self.fixes = list(fixes)
        self.context = context

    def summary(self) -> str:
        """Plain-text rendering for places without a terminal (web UI, logs)."""
        lines = [f"{self.title}: {self.message}"]
        if self.causes:
            lines.append("Why this might happen:")
            lines += [f"- {cause}" for cause in self.causes]
        if self.fixes:
            lines.append("How to fix it:")
            lines += [f"- {fix}" for fix in self.fixes]
        return "\n".join(lines)

    @classmethod
    def unexpected(cls, exc: BaseException, while_doing: str) -> "AgenticSeekError":
        """Wrap an exception nobody anticipated (most likely a bug)."""
        return cls(
            title="Unexpected error",
            message=f"{type(exc).__name__} while {while_doing}: {_shorten(str(exc)) or 'no details'}",
            causes=["This is most likely a bug in agenticSeek rather than a problem with your setup."],
            fixes=["Try again. If it keeps happening, open an issue at "
                   f"{ISSUES_URL} and attach the log file below."],
        )


class ProviderError(AgenticSeekError):
    """An LLM provider failed. `kind` names the failure class (auth, rate_limit, connection, ...)."""

    def __init__(self, kind: str, title: str, message: str, causes: Sequence[str] = (),
                 fixes: Sequence[str] = (), context: str = "", status_code: Optional[int] = None):
        super().__init__(title, message, causes, fixes, context)
        self.kind = kind
        self.status_code = status_code


PROVIDER_LABELS = {
    "ollama": "Ollama",
    "server": "the agenticSeek LLM server",
    "openai": "OpenAI",
    "lm-studio": "LM Studio",
    "huggingface": "Hugging Face",
    "google": "Google Gemini",
    "deepseek": "DeepSeek",
    "together": "Together AI",
    "dsk_deepseek": "DeepSeek (dsk)",
    "openrouter": "OpenRouter",
    "anthropic": "Anthropic",
    "minimax": "MiniMax",
    "litellm": "LiteLLM",
}

# Where users create API keys; only providers with a stable, well-known page.
KEY_PAGES = {
    "openrouter": "https://openrouter.ai/settings/keys",
    "openai": "https://platform.openai.com/api-keys",
    "anthropic": "https://console.anthropic.com/settings/keys",
    "google": "https://aistudio.google.com/apikey",
    "deepseek": "https://platform.deepseek.com/api_keys",
    "together": "https://api.together.ai/settings/api-keys",
    "huggingface": "https://huggingface.co/settings/tokens",
}

# Every key issued by these providers starts with this prefix.
KEY_PREFIXES = {
    "openrouter": "sk-or-",
    "anthropic": "sk-ant-",
    "openai": "sk-",
    "deepseek": "sk-",
    "huggingface": "hf_",
    "google": "AIza",
}

LOCAL_PROVIDERS = {"ollama", "lm-studio", "server"}

_TIMEOUT_NAMES = {"TimeoutError", "Timeout", "TimeoutException", "APITimeoutError",
                  "ReadTimeout", "ConnectTimeout", "WriteTimeout", "PoolTimeout"}
_CONNECTION_NAMES = {"ConnectionError", "ConnectError", "APIConnectionError", "NetworkError",
                     "NewConnectionError", "MaxRetryError", "gaierror"}
_CONNECTION_TEXT = re.compile(r"refused|failed to connect|name or service not known|"
                              r"nodename nor servname|getaddrinfo failed|no route to host")
_MODEL_MISSING_TEXT = re.compile(r"model[^.\n]{0,80}(?:not found|does not exist|is invalid|unknown)|"
                                 r"(?:no such|unknown|invalid) model|not a valid model")
_STATUS_TEXT = re.compile(r"\b(?:error code|status(?: code)?|http)[:\s]+(\d{3})\b", re.IGNORECASE)
_STATUS_PREFIX = re.compile(r"^Error code: \d{3} - ")
_OS_ERROR_TEXT = re.compile(r"\[Errno -?\d+\] [^'\"()\[\]]+")


@dataclass(frozen=True)
class ProviderContext:
    """What the diagnosis needs to know about the configured provider."""
    provider: str
    model: str
    server_address: str = ""
    is_local: bool = False
    api_key: Optional[str] = field(default=None, repr=False)  # only its prefix is checked, never shown

    @property
    def label(self) -> str:
        return PROVIDER_LABELS.get(self.provider, self.provider)

    @property
    def key_var(self) -> str:
        return f"{self.provider.upper()}_API_KEY"

    @property
    def runs_locally(self) -> bool:
        return self.provider in LOCAL_PROVIDERS or self.is_local

    @property
    def header(self) -> str:
        return " · ".join(part for part in (self.provider, self.model) if part)


def provider_error(kind: str, ctx: ProviderContext, detail: str = "",
                   status_code: Optional[int] = None) -> ProviderError:
    """Build the user-facing error for a known failure kind."""
    title, message, causes, fixes = _explain(kind, ctx, detail, status_code)
    return ProviderError(kind, title, message, causes, fixes, context=ctx.header, status_code=status_code)


def diagnose_provider_error(exc: BaseException, ctx: ProviderContext) -> ProviderError:
    """Classify a raw provider exception and explain it."""
    if isinstance(exc, ProviderError):
        return exc
    chain = list(_exception_chain(exc))
    names = {cls.__name__ for err in chain for cls in type(err).__mro__}
    # timeouts are judged on the raised exception only: urllib3 makes every
    # NewConnectionError (refused, DNS, ...) a subclass of ConnectTimeoutError
    outer_names = {cls.__name__ for cls in type(exc).__mro__}
    raw_text = " ".join(str(err) for err in chain)
    text = raw_text.lower()
    status = _status_code(chain)
    detail = _detail(chain)
    missing_module = next((err for err in chain if isinstance(err, ImportError)), None)

    if missing_module is not None:
        kind, detail = "missing_dependency", missing_module.name or str(missing_module)
    elif outer_names & _TIMEOUT_NAMES or "timed out" in text:
        kind = "timeout"
    elif status == 401 or "AuthenticationError" in names:
        kind = "auth"
    elif status == 403 or "PermissionDeniedError" in names:
        kind = "forbidden"
    elif status == 402:
        kind = "payment"
    elif status == 429 or "RateLimitError" in names or "rate limit" in text or "too many requests" in text:
        kind = "rate_limit"
    elif status == 404 or "NotFoundError" in names or _MODEL_MISSING_TEXT.search(text):
        kind = "model_not_found"
    elif status in (400, 413, 422) or names & {"BadRequestError", "UnprocessableEntityError"}:
        kind = "bad_request"
    elif (status is not None and status >= 500) or "InternalServerError" in names \
            or "overloaded" in text or "try again later" in text:
        kind = "unavailable"
    elif names & _CONNECTION_NAMES or _CONNECTION_TEXT.search(text):
        kind = "connection"
        detail = connection_detail(exc) or detail
    elif "JSONDecodeError" in names or isinstance(exc, (KeyError, IndexError, TypeError, AttributeError)):
        kind, detail = "bad_response", f"{type(exc).__name__}: {detail}"
    else:
        kind = "unknown"
    return provider_error(kind, ctx, detail, status)


def connection_detail(exc: BaseException) -> str:
    """The OS-level reason of a connection failure ("[Errno 61] Connection refused"), or ""."""
    raw_text = " ".join(str(err) for err in _exception_chain(exc))
    os_error = _OS_ERROR_TEXT.search(raw_text)  # beats urllib3's wall of text
    return os_error.group(0).strip() if os_error else ""


def env_file_path() -> str:
    """The .env file agenticSeek reads, relative to the working directory when possible."""
    path = os.path.abspath(find_dotenv(usecwd=True) or ".env")
    relative = os.path.relpath(path)
    return path if relative.startswith("..") else relative


def _explain(kind: str, ctx: ProviderContext, detail: str,
             status: Optional[int]) -> Tuple[str, str, List[str], List[str]]:
    label, model, addr = ctx.label, ctx.model, ctx.server_address
    http = f" (HTTP {status})" if status else ""
    said = f": {detail}" if detail else "."
    env = env_file_path()
    key_page = KEY_PAGES.get(ctx.provider)

    if kind == "missing_key":
        fixes = [f"Create a key at {key_page}."] if key_page else []
        fixes += [f"Add {ctx.key_var}=<your key> to {env}, then restart agenticSeek.",
                  "Or run a model locally: set provider_name = ollama and is_local = True in config.ini."]
        return ("Missing API key",
                f"{label} needs an API key, but {ctx.key_var} is not set.",
                [f"{ctx.key_var} is missing, empty or misspelled in {env}."],
                fixes)

    if kind == "local_unsupported":
        return ("Cloud-only provider",
                f"{label} is not available for local use, but config.ini sets is_local = True.",
                [f"is_local = True means the model runs on your machine; {label} only runs in the cloud."],
                [f"Set is_local = False in config.ini to use the {label} API.",
                 "Or switch to a local provider: provider_name = ollama, lm-studio or server."])

    if kind == "empty_response":
        return ("Empty response",
                f"{label} answered, but the response is empty{said}",
                ["The model hit a content filter or its output limit.",
                 "The provider had a transient failure."],
                ["Send the request again.", "If it keeps happening, try another provider_model in config.ini."])

    if kind == "server_error":
        return ("LLM server error",
                f"The agenticSeek LLM server at {addr} reported{said}",
                ["The server was started without a working backend, or the model failed to load.",
                 "Another generation is still running on the server."],
                ["Check the console of the machine running llm_server.", "Restart the server, then retry."])

    if kind == "missing_dependency":
        package = detail.split(".")[0] or detail
        return ("Missing Python package",
                f"The {ctx.provider} provider needs the '{package}' package, which is not installed.",
                ["Some providers rely on optional packages.",
                 "agenticSeek is running outside its virtual environment."],
                [f"Install it in the agenticSeek environment: pip install {package}",
                 "Or reinstall all dependencies: pip install -r requirements.txt"])

    if kind == "timeout":
        if ctx.runs_locally:
            causes = ["The model is too large for your hardware, or still loading into memory.",
                      f"The server at {addr} is busy with another request."]
            fixes = ["Wait until the model has loaded, then retry.", "Use a smaller model in provider_model."]
        else:
            causes = ["Slow or unstable network connection.", f"{label} is overloaded."]
            fixes = ["Retry in a moment.", "Check your network, VPN or proxy."]
        return ("Request timed out", f"{label} did not answer in time{said}", causes, fixes)

    if kind == "auth":
        causes = [f"{ctx.key_var} in {env} is wrong, expired or revoked."]
        prefix = KEY_PREFIXES.get(ctx.provider)
        if ctx.api_key and prefix and not ctx.api_key.startswith(prefix):
            causes.insert(0, f"{ctx.key_var} does not start with '{prefix}' like every {label} key does: "
                             "it is probably a key for another service or a placeholder.")
        fixes = [f"Check or create a key at {key_page}."] if key_page else []
        fixes.append(f"Put it in {env} as {ctx.key_var}=<your key> (no quotes or spaces), "
                     "then restart agenticSeek.")
        return ("Authentication failed", f"{label} rejected the API key{http}{said}", causes, fixes)

    if kind == "forbidden":
        return ("Access denied",
                f"{label} refused access{http}{said}",
                [f"Your key works but has no access to '{model}' (plan, region or organisation restriction)."],
                [f"Check that your {label} account may use '{model}'.", "Or pick another provider_model in config.ini."])

    if kind == "payment":
        return ("Out of credits",
                f"{label} requires payment{http}{said}",
                [f"Your {label} account has no credits left, or billing is not set up."],
                [f"Add credits or a payment method to your {label} account.",
                 "Or switch to a free model or a local provider."])

    if kind == "model_not_found":
        causes = [f"provider_model = {model} in config.ini is misspelled or not offered by {label}."]
        if ctx.provider == "ollama":
            causes.append("The model is not downloaded in Ollama.")
            fixes = [f"Download it: ollama pull {model}", "List installed models: ollama list"]
        elif ctx.provider == "lm-studio":
            fixes = ["Load the model in LM Studio and copy its exact identifier into provider_model."]
        elif ctx.provider == "server":
            causes.append(f"provider_server_address = {addr} does not point to an agenticSeek LLM server.")
            fixes = ["Check provider_server_address and the model the server was started with."]
        elif ctx.provider == "openrouter":
            fixes = ["Copy the exact model id (vendor/model-name) from https://openrouter.ai/models."]
        else:
            fixes = [f"Use a model id exactly as listed in the {label} documentation."]
        return ("Model not found", f"{label} has no model '{model}'{http}{said}", causes, fixes)

    if kind == "rate_limit":
        return ("Rate limited",
                f"{label} is throttling requests{http}{said}",
                ["Too many requests in a short time.", "Your plan's quota or free-tier limit is used up."],
                ["Wait a minute, then retry.", f"Check usage and limits in your {label} account.",
                 "Or switch provider_model to a less busy model."])

    if kind == "bad_request":
        return ("Request rejected",
                f"{label} rejected the request{http}{said}",
                ["The conversation is longer than the model's context window.",
                 f"'{model}' does not support part of the request (system prompt, parameter, ...)."],
                ["Start a fresh session: set recover_last_session = False in config.ini and restart.",
                 "Or try another provider_model."])

    if kind == "unavailable":
        if ctx.runs_locally:
            causes = [f"The {label} server crashed or ran out of memory while generating."]
            fixes = ["Check the server's console output, then restart it.", "Use a smaller model."]
        else:
            causes = [f"{label} is overloaded or having an outage; your configuration is likely fine."]
            fixes = ["Retry in a few minutes.", "Or try another provider_model."]
        return ("Provider unavailable", f"{label} failed on its side{http}{said}", causes, fixes)

    if kind == "connection":
        causes, fixes = _connection_help(ctx)
        target = addr if ctx.runs_locally else f"the {label} API"
        return (f"Cannot reach {label}", f"Could not connect to {target}{said}", causes, fixes)

    if kind == "bad_response":
        return ("Unexpected response",
                f"{label}'s reply is not in the expected format{said}",
                ["The provider returned an error inside a normal-looking reply "
                 "(common when a model is unavailable or filtered).",
                 "The provider changed its API format."],
                ["Retry.", "Or try another provider_model.",
                 f"If it keeps happening, open an issue at {ISSUES_URL} with the log file."])

    return ("Provider error",
            f"{label} request failed{http}{said}",
            ["Unrecognised error; the full traceback in the log file has the details."],
            ["Retry.", f"If it keeps happening, open an issue at {ISSUES_URL} with the log file."])


def _connection_help(ctx: ProviderContext) -> Tuple[List[str], List[str]]:
    addr = ctx.server_address
    fix_address = "Fix provider_server_address in config.ini."
    if ctx.provider == "ollama":
        causes = ["Ollama is not running.",
                  f"provider_server_address = {addr} is not where Ollama listens (default 127.0.0.1:11434)."]
        fixes = ["Start it: ollama serve", fix_address]
    elif ctx.provider == "lm-studio":
        causes = ["The LM Studio local server is not started.",
                  f"provider_server_address = {addr} does not match its port (default 1234)."]
        fixes = ["In LM Studio, open the Developer tab and start the server.", fix_address]
    elif ctx.provider == "server":
        causes = ["The agenticSeek LLM server is not running on the remote machine.",
                  f"provider_server_address = {addr} is wrong, or a firewall blocks the port."]
        fixes = ["Start llm_server on the remote machine.", fix_address]
    elif ctx.runs_locally:
        causes = [f"No OpenAI-compatible server is running at {addr}."]
        fixes = ["Start your local server (vLLM, llama.cpp, ...).", fix_address]
    else:
        return ([f"No internet connection, or a VPN, proxy or firewall blocks the {ctx.label} API.",
                 f"{ctx.label} is having an outage."],
                ["Check your connection and retry.", "Disable the VPN or proxy, or allow the API host."])
    docker_url = os.getenv("DOCKER_INTERNAL_URL")
    if docker_url:
        causes.append(f"Inside Docker the host is reached through {docker_url}: the server must listen "
                      "on 0.0.0.0, not only on 127.0.0.1.")
    return causes, fixes


def _exception_chain(exc: Optional[BaseException]) -> Iterator[BaseException]:
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        yield exc
        exc = exc.__cause__ or exc.__context__


def _attr(obj, name: str):
    """getattr that tolerates properties raising (httpx exceptions do)."""
    try:
        return getattr(obj, name, None)
    except Exception:
        return None


def _status_code(chain: List[BaseException]) -> Optional[int]:
    for err in chain:
        for candidate in (_attr(err, "status_code"), _attr(_attr(err, "response"), "status_code")):
            if isinstance(candidate, int) and 100 <= candidate < 600:
                return candidate
        match = _STATUS_TEXT.search(str(err))
        if match:
            return int(match.group(1))
    return None


def _detail(chain: List[BaseException]) -> str:
    """The most specific human message: API error bodies first, exception text last."""
    for err in chain:
        message = _payload_message(_attr(err, "body"))
        if message:
            return _shorten(message)
        response = _attr(err, "response")
        if response is not None:
            message = _response_message(response)
            if message:
                return _shorten(message)
        ollama_error = _attr(err, "error")
        if isinstance(ollama_error, str) and ollama_error:
            return _shorten(ollama_error)
    first = chain[0]
    return _shorten(_STATUS_PREFIX.sub("", str(first))) or type(first).__name__


def _payload_message(payload) -> str:
    if isinstance(payload, str):
        return payload.strip()
    if not isinstance(payload, dict):
        return ""
    for key in ("message", "detail", "error_description"):
        if isinstance(payload.get(key), str) and payload[key].strip():
            return payload[key].strip()
    return _payload_message(payload.get("error"))


def _response_message(response) -> str:
    try:
        message = _payload_message(response.json())
        if message:
            return message
    except Exception:
        pass
    text = _attr(response, "text")
    return text.strip() if isinstance(text, str) else ""


def _shorten(text: str, limit: int = 400) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 1] + "…"
