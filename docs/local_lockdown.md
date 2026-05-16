# Local Lockdown (Secure-by-Default Networking)

AgenticSeek is a **local laptop client**. It has no built-in authentication,
authorization, audit log, or rate limiting. Until [agenticplug][agenticplug]
(GitHub App-authenticated, JWT-fronted) is in place as the security boundary,
**exposing the AgenticSeek API beyond `localhost` is unsupported.**

This document covers the secure-by-default settings shipped in `api.py` and
how to (intentionally) loosen them when you understand the trade-offs.

## What changed

| Concern         | Before               | Default now                                  |
|-----------------|----------------------|----------------------------------------------|
| Bind host       | `0.0.0.0`            | `127.0.0.1` on host, `0.0.0.0` only in Docker |
| CORS origins    | `*` (wildcard)       | `http://localhost:3000,http://127.0.0.1:3000` |
| Local token     | n/a                  | Off by default; opt-in via `BACKEND_LOCAL_TOKEN` |
| `safe_mode`     | Implicit `False`     | Still `False` — documented, not changed       |

Behavior is **backward-compatible** for users who run the bundled React UI on
`localhost:3000` and talk to the backend on `127.0.0.1:7777` — the common
local-laptop path that this project targets.

## Environment variables

All three are read from the process environment (or `.env` via
`python-dotenv`). See `.env.example` for the canonical commented block.

### `BACKEND_HOST`

The interface uvicorn binds to. If unset:

- On the host: `127.0.0.1` (loopback only).
- Inside a Docker container (detected via `/.dockerenv` or cgroup): `0.0.0.0`,
  so the published `docker-compose` port mapping continues to work.

If you set this to anything other than `127.0.0.1` / `localhost` on the host,
`api.py` prints a warning on startup reminding you the surface is unauthenticated.

### `BACKEND_CORS_ORIGINS`

Comma-separated allowlist passed straight to FastAPI's `CORSMiddleware`.
Whitespace around entries is stripped. Defaults to the two localhost origins
used by the bundled React frontend. You can:

- Add another origin: `BACKEND_CORS_ORIGINS="http://localhost:3000,http://my-dev-box.lan:3000"`
- Restore the legacy wildcard (not advised): `BACKEND_CORS_ORIGINS="*"`

### `BACKEND_LOCAL_TOKEN`

Optional shared secret. When **set**, `api.py` installs a middleware that
rejects any request without a matching `X-Local-Token: <value>` header with
HTTP 401. When **unset** (default), no token is required.

Exempt paths (no token needed, so the browser UI can poll without one):

- `GET /health`
- `GET /is_active`
- `GET /latest_answer`
- `GET /screenshot`
- Anything under `/screenshots/`

This is a **tripwire**, not real authentication: a single shared secret on a
host that you control. It exists to make accidental LAN exposure (e.g. someone
flipping `BACKEND_HOST=0.0.0.0` to debug) noisy rather than silent. Real
auth — GitHub App / JWT — will live in agenticplug, not here.

Example, on the client side:

```bash
curl -H "X-Local-Token: $BACKEND_LOCAL_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query":"hello"}' \
     http://127.0.0.1:7777/query
```

## `safe_mode`

`sources/tools/tools.py` defines `self.safe_mode = False` on the base `Tools`
class. This stays the default for now to preserve existing behavior; the
attribute is consumed by `BashInterpreter` to block known-unsafe commands when
enabled. This PR **does not** change the default — it only documents it so
the surface is explicit before any remote tools land.

When the remote RPC/HPC tool path is added (post agenticplug), `safe_mode`
should be forced `True` for any non-local tool invocation. That work is out
of scope here.

## Roadmap context

This PR is a prerequisite for the later remote RPC/HPC tools track:

1. **(this PR)** Lock the local API down by default.
2. agenticplug provider already lands as an OpenAI-compatible LLM client
   (PR #3) — LLM traffic only, no tool execution.
3. agenticplug grows GitHub App / JWT auth and becomes the security boundary.
4. *Only then* does AgenticSeek expose remote tools, and only via the
   agenticplug gateway — never directly on its own port.

OpenClaw and the existing Hermes backend on `reumanlab` are untouched by
this change.

[agenticplug]: https://github.com/
