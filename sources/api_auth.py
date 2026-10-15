"""Bearer-token and Host-header guards for the AgenticSeek HTTP API.

The API drives agents that run shell commands, so it fails closed: every
protected route needs `Authorization: Bearer <token>`. The token comes from
AGENTICSEEK_API_TOKEN, or it is generated once and stored in the runtime
directory, so users paste it into the web UI only one time.
"""

from __future__ import annotations

import hmac
import os
import secrets
from urllib.parse import urlsplit

from fastapi import Header, HTTPException
from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse

from sources.workspace import ensure_runtime_dir

TOKEN_ENV = "AGENTICSEEK_API_TOKEN"
ALLOWED_HOSTS_ENV = "AGENTICSEEK_ALLOWED_HOSTS"
TOKEN_FILE_NAME = "api_token"
TOKEN_ENTROPY_BYTES = 32
TOKEN_FILE_MODE = 0o600
DEFAULT_ALLOWED_HOSTS = ("localhost", "127.0.0.1", "::1")
INVALID_HOST_STATUS = 400
NON_HOST_CHARS = "@/?#\\"
BEARER_PREFIX = "Bearer "


def _read_token_file(path: str) -> str | None:
    """Read a stored API token.

    ensure_api_token calls this at backend start with the token file path.
    It returns the stripped file content, or None when there is no usable token.

    Args:
        path (str): Absolute path of the token file in the runtime directory.

    Returns:
        str | None: The stored token, or None if the file is missing or empty.
    """
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        token = handle.read().strip()
    return token or None


def _write_new_token_file(path: str) -> str:
    """Generate a new API token and store it with owner-only permissions.

    ensure_api_token calls this when no token is configured or stored.
    It writes a random URL-safe token to the file and makes the file mode 0600.

    Args:
        path (str): Absolute path of the token file in the runtime directory.

    Returns:
        str: The new token.
    """
    token = secrets.token_urlsafe(TOKEN_ENTROPY_BYTES)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, TOKEN_FILE_MODE)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(token + "\n")
    os.chmod(path, TOKEN_FILE_MODE)
    return token


def ensure_api_token() -> tuple[str, str | None]:
    """Make sure the backend has an API token before it serves requests.

    api.py calls this one time at import, before uvicorn starts.
    It keeps AGENTICSEEK_API_TOKEN when set; otherwise it loads or creates the
    token file in the runtime directory and puts the token in the process env.

    Returns:
        tuple[str, str | None]: The token, and the token file path when the
            token comes from the file (None when it comes from the env).
    """
    configured = os.getenv(TOKEN_ENV)
    if configured:
        return configured, None
    path = os.path.join(ensure_runtime_dir(), TOKEN_FILE_NAME)
    token = _read_token_file(path) or _write_new_token_file(path)
    os.environ[TOKEN_ENV] = token
    return token, path


def allowed_hosts() -> list[str]:
    """List the host names the API accepts in the Host header.

    api.py calls this to configure HostAllowlistMiddleware against DNS rebinding.
    It returns the loopback names plus the comma-separated AGENTICSEEK_ALLOWED_HOSTS.

    Returns:
        list[str]: Lower-case host names (no port, no IPv6 brackets).
    """
    extra = os.getenv(ALLOWED_HOSTS_ENV, "").split(",")
    hosts = list(DEFAULT_ALLOWED_HOSTS) + [host.strip() for host in extra if host.strip()]
    return [host.lower().strip("[]") for host in hosts]


def host_name(host_header: str) -> str:
    """Extract the host name from a Host header value.

    HostAllowlistMiddleware calls this for every request. Unlike Starlette's
    TrustedHostMiddleware it handles IPv6 literals such as `[::1]:7777`.

    Args:
        host_header (str): Raw Host header, with optional port.

    Returns:
        str: Lower-case host name, or "" when the header is not a plain
            `host[:port]` (userinfo, paths and spaces are refused).
    """
    if any(char in NON_HOST_CHARS or char.isspace() for char in host_header):
        return ""
    try:
        return urlsplit(f"//{host_header}").hostname or ""
    except ValueError:
        return ""


class HostAllowlistMiddleware:
    """ASGI middleware that rejects requests whose Host is not allowlisted.

    api.py installs it so DNS-rebinding pages, which send their own domain in
    the Host header, cannot reach the loopback API.
    """

    def __init__(self, app, hosts: list[str]):
        """Store the wrapped app and the allowed host names.

        Args:
            app: The ASGI app that FastAPI wraps with this middleware.
            hosts (list[str]): Host names from allowed_hosts().
        """
        self.app = app
        self.hosts = frozenset(hosts)

    async def __call__(self, scope, receive, send):
        """Pass allowed requests on, answer 400 to the others.

        Args:
            scope (dict): ASGI connection scope.
            receive (callable): ASGI receive channel.
            send (callable): ASGI send channel.
        """
        if scope["type"] in ("http", "websocket"):
            if host_name(Headers(scope=scope).get("host", "")) not in self.hosts:
                response = PlainTextResponse("Invalid host header", status_code=INVALID_HOST_STATUS)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


async def require_api_token(authorization: str | None = Header(default=None)) -> None:
    """Reject requests that do not carry the API token.

    FastAPI runs this dependency for every protected route, with the
    Authorization header of the request. It fails closed when no token exists.

    Args:
        authorization (str | None): Raw Authorization header from the request.

    Raises:
        HTTPException: 503 when the server has no token, 401 when the header
            is missing, malformed, or holds the wrong token.
    """
    expected_token = os.getenv(TOKEN_ENV)
    if not expected_token:
        raise HTTPException(status_code=503, detail="API token not configured on the server")
    if not authorization or not authorization.startswith(BEARER_PREFIX):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    provided_token = authorization[len(BEARER_PREFIX):]
    if not hmac.compare_digest(provided_token.encode(), expected_token.encode()):
        raise HTTPException(status_code=401, detail="Invalid API token")


if __name__ == "__main__":
    import tempfile

    os.environ.pop(TOKEN_ENV, None)
    os.environ["AGENT_RUNTIME_DIR"] = tempfile.mkdtemp()
    first_token, stored_path = ensure_api_token()
    os.environ.pop(TOKEN_ENV)
    assert ensure_api_token() == (first_token, stored_path), "token must be reused"
    assert oct(os.stat(stored_path).st_mode & 0o777) == oct(TOKEN_FILE_MODE)
    print(f"ok: token persisted at {stored_path}; hosts={allowed_hosts()}")
