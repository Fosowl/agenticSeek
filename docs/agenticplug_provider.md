# AgenticPlug Provider

AgenticSeek can run as a local client of an [AgenticPlug](https://github.com/)
gateway, an OpenAI-compatible router that fronts one or more backend models.
This keeps the agent-agnostic gateway separate from AgenticSeek itself: the
client only speaks the OpenAI Chat Completions wire format and adds optional
routing/auth headers.

## Scope

This provider only implements client-side configuration. It does not:

- start, stop, or restart any backend (e.g. OpenClaw remains live regardless),
- implement remote shell or other privileged tools,
- expose AgenticSeek beyond localhost,
- require any secret to be pasted into a chat session.

All configuration is read from environment variables; defaults route to
`127.0.0.1` so the change is fully backward-compatible.

## Authentication

Production AgenticPlug deployments authenticate with a **GitHub App / JWT**
flow handled on the server side. The bearer value accepted by this client via
`AGENTICPLUG_API_KEY` is a **dev-only placeholder** for local testing against a
gateway that does not require auth, or for short-lived tokens minted by other
tooling. It is sent as `Authorization: Bearer <value>` by the OpenAI SDK; do
not commit real secrets to `.env`.

## Configuration

In `config.ini`:

```ini
[MAIN]
is_local = True
provider_name = agenticplug
provider_model = hermes
provider_server_address = 127.0.0.1:8080
```

In `.env` (all optional):

```bash
# Full base URL of the gateway. Falls back to provider_server_address + /v1.
AGENTICPLUG_BASE_URL=http://127.0.0.1:8080/v1

# Optional model override. Falls back to provider_model.
AGENTICPLUG_MODEL=hermes

# Dev-only placeholder. Production auth is GitHub App / JWT.
AGENTICPLUG_API_KEY=dev-placeholder

# Optional route hint for the gateway (sent as X-AgenticPlug-Route header).
AGENTICPLUG_ROUTE_HEADER=hermes
```

## Backend routing

`AGENTICPLUG_ROUTE_HEADER` is forwarded as the `X-AgenticPlug-Route` header so
the gateway can pick a specific backend. For example, setting it to `hermes`
routes to the Hermes backend on the AgenticPlug server. The header is only
sent when the variable is set, so omitting it preserves the gateway's default
routing.

## See also

- [AgenticPlug GPL-Compatible Integration Boundary](agenticplug_gpl_boundary.md)
  — documents the licensing boundary between the AgenticSeek fork and the
  AgenticPlug external service.
