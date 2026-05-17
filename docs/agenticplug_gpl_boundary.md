# AgenticPlug GPL-Compliant Integration Boundary

This document describes the licensing boundary between the **AgenticSeek fork**
and the **AgenticPlug** external service. It is intended to help contributors and
downstream users understand how the two projects co-exist without creating
licensing ambiguity under GPL-3.0.

## AgenticSeek Fork License

The AgenticSeek fork remains **GPL-3.0 licensed** in its entirety. All code
within this repository — including the AgenticPlug client adapter — is
distributed under the same GPL-3.0 terms as the upstream project.

## AgenticPlug External Service Boundary

**AgenticPlug is an external, separately-maintained service.** It is not part of
the AgenticSeek codebase and is not distributed with or linked into AgenticSeek.
The two projects interact only over documented network protocols:

- **REST API** (OpenAI-compatible Chat Completions endpoint)
- **MCP** (Model Context Protocol, between the gateway and backends)
- **OpenAI-compatible wire format** used by the client adapter in AgenticSeek

This architecture establishes a clean **API boundary** — the same design pattern
used by any client application that talks to OpenAI, Anthropic, or any other
self-hosted or SaaS LLM backend. The AgenticSeek adapter does not import, embed,
call, or link against any AgenticPlug library or binary. It constructs standard
HTTP requests against a configurable base URL.

## Code Separation Rules

To preserve the GPL boundary:

- **Do not copy** AgenticPlug proprietary, internal, or broker-side code into
  the AgenticSeek repository.
- **Do not inline** AgenticPlug gateway logic, routing rules, or authentication
  implementations into AgenticSeek source files.
- **Keep the adapter generic.** The AgenticPlug adapter in AgenticSeek is an
  OpenAI-compatible HTTP client. It intentionally does not contain
  AgenticPlug-specific business logic, backend selection algorithms, or
  authentication flows beyond standard bearer-token forwarding.

If AgenticPlug ever ships a client SDK, the AgenticSeek adapter **must not
import or link it** unless that SDK is itself released under GPL-3.0 or a
GPL-compatible license.

## Secrets and Credentials

All secrets, credentials, and authentication material belong in the
**AgenticPlug connector/broker** — never in the AgenticSeek repository:

- **API keys, tokens, JWTs, and signing keys** are stored and managed by
  AgenticPlug or its deployment tooling.
- The AgenticSeek adapter reads only the environment variables documented in
  [agenticplug_provider.md](agenticplug_provider.md). These hold user-supplied
  values (base URL, dev-only placeholder key, optional route hint); they are
  never committed to the AgenticSeek source tree.
- The `.env.example` file in this repository shows only placeholder values and
  documents that the `AGENTICPLUG_API_KEY` is a dev-only placeholder.

See the [main AgenticPlug provider documentation](agenticplug_provider.md) for
configuration details.

## Protocol Compatibility

The AgenticSeek client adapter communicates with AgenticPlug exclusively through
standard, publicly-documented protocols:

| Protocol | Usage |
|---|---|
| OpenAI Chat Completions (REST) | Primary LLM interaction; `POST /v1/chat/completions` |
| Custom HTTP headers | Optional routing (`X-AgenticPlug-Route`), standard `Authorization: Bearer` |
| Future: MCP | Model Context Protocol for tool/resource exchange between AgenticPlug-managed backends |

No custom wire format, binary protocol, or undocumented API is used between the
two projects. Any future protocol additions will be documented here before
implementation.

## Relationship to Upstream AgenticSeek

This fork does not alter the upstream AgenticSeek license. The addition of the
AgenticPlug provider adapter does not change the license of any pre-existing
AgenticSeek code. The adapter itself is a new, original GPL-3.0 contribution.

## When to Re-evaluate

Review this boundary if any of the following changes:

- AgenticPlug ships a client-side library or SDK.
- AgenticSeek starts importing code from an AgenticPlug repository.
- A protocol richer than OpenAI-compatible REST/MCP is introduced between the
  two projects.
- The AgenticPlug connector/broker is included, vendored, or submoduled into
  the AgenticSeek tree.

## Disclaimer

**This document is not legal advice.** The authors are not lawyers, and nothing
in this document should be interpreted as a formal legal opinion about the scope
or requirements of GPL-3.0. The analysis above reflects the project's intent and
architectural choices; it is provided for transparency and contributor guidance
only.

Before commercializing, redistributing, or modifying the integration, obtain a
**formal legal review** from qualified counsel who can evaluate your specific
facts, jurisdiction, and planned use. GPL compliance depends on how software is
combined and distributed, and only a lawyer familiar with your situation can
advise on those details.

[agenticplug_provider.md]: agenticplug_provider.md
