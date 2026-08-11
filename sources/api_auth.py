"""Shared-secret bearer token guard for sensitive AgenticSeek API routes.

Off by default: if AGENTICSEEK_API_TOKEN is unset, every request passes,
matching the existing local-only UX. Set AGENTICSEEK_API_TOKEN to require a
matching `Authorization: Bearer <token>` header on routes that depend on
require_api_token.
"""

import hmac
import os

from fastapi import Header, HTTPException


async def require_api_token(authorization: str | None = Header(default=None)) -> None:
    expected_token = os.getenv("AGENTICSEEK_API_TOKEN")
    if not expected_token:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or malformed Authorization header",
        )

    provided_token = authorization[len("Bearer "):]
    if not hmac.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=401, detail="Invalid API token")
