"""Local lockdown helpers for the AgenticSeek API.

AgenticSeek is a local laptop client with no built-in authentication.
Until agenticplug (GitHub App / JWT) fronts the API, these helpers keep
the surface area small and explicit so accidental exposure is loud, not
silent. See docs/local_lockdown.md for the full rationale.

Kept in its own module so tests can exercise it without importing the
full FastAPI app (which pulls in browser, agents, celery, redis, etc).
"""

from __future__ import annotations

import os
from typing import Iterable, List, Sequence

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


DEFAULT_BACKEND_HOST = "127.0.0.1"
DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
LOCAL_TOKEN_HEADER = "X-Local-Token"
TOKEN_EXEMPT_PATHS = frozenset({
    "/health",
    "/is_active",
    "/latest_answer",
    "/screenshot",
})


def parse_cors_origins(raw: str) -> List[str]:
    """Split a comma-separated CORS env var into a clean list.

    Empty entries are dropped and whitespace is stripped. A single "*"
    is preserved so operators can opt back into the legacy wildcard.
    """
    return [o.strip() for o in (raw or "").split(",") if o.strip()]


def resolve_backend_host(
    env_host: str | None,
    in_docker: bool,
    default_host: str = DEFAULT_BACKEND_HOST,
) -> str:
    """Pick the uvicorn bind host.

    Explicit `BACKEND_HOST` always wins. Otherwise default to
    `127.0.0.1` on the host and `0.0.0.0` inside Docker (so the
    published port mapping keeps working).
    """
    if env_host:
        return env_host
    if in_docker:
        return "0.0.0.0"
    return default_host


def is_loopback_host(host: str) -> bool:
    """True iff `host` is a literal loopback address we consider safe."""
    return host in {"127.0.0.1", "localhost", "::1"}


class LocalTokenMiddleware(BaseHTTPMiddleware):
    """Optional shared-secret gate for non-browser local API calls.

    Disabled unless `BACKEND_LOCAL_TOKEN` is set, so behavior stays
    backward-compatible for existing local users. When enabled,
    requests to non-exempt paths must carry a matching `X-Local-Token`
    header. This is *not* a substitute for real auth — it is a
    tripwire against accidental exposure on a LAN until agenticplug
    auth is wired up.
    """

    def __init__(
        self,
        app,
        token: str,
        exempt_paths: Iterable[str] = TOKEN_EXEMPT_PATHS,
        exempt_prefixes: Sequence[str] = ("/screenshots/",),
    ) -> None:
        super().__init__(app)
        if not token:
            raise ValueError("LocalTokenMiddleware requires a non-empty token")
        self._token = token
        self._exempt_paths = set(exempt_paths)
        self._exempt_prefixes = tuple(exempt_prefixes)

    def _is_exempt(self, path: str) -> bool:
        if path in self._exempt_paths:
            return True
        return any(path.startswith(p) for p in self._exempt_prefixes)

    async def dispatch(self, request: Request, call_next):
        if self._is_exempt(request.url.path):
            return await call_next(request)
        provided = request.headers.get(LOCAL_TOKEN_HEADER)
        if provided != self._token:
            return JSONResponse(
                status_code=401,
                content={"error": f"missing or invalid {LOCAL_TOKEN_HEADER}"},
            )
        return await call_next(request)


def env_local_token() -> str:
    """Read and trim the optional local token from the environment."""
    return os.getenv("BACKEND_LOCAL_TOKEN", "").strip()
