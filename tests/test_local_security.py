import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from sources.local_security import (
    DEFAULT_BACKEND_HOST,
    DEFAULT_CORS_ORIGINS,
    LOCAL_TOKEN_HEADER,
    TOKEN_EXEMPT_PATHS,
    LocalTokenMiddleware,
    is_loopback_host,
    parse_cors_origins,
    resolve_backend_host,
)


class TestParseCorsOrigins(unittest.TestCase):
    def test_default_yields_two_localhost_origins(self):
        self.assertEqual(
            parse_cors_origins(DEFAULT_CORS_ORIGINS),
            ["http://localhost:3000", "http://127.0.0.1:3000"],
        )

    def test_strips_whitespace_and_drops_empties(self):
        self.assertEqual(
            parse_cors_origins(" http://a.test , , http://b.test ,"),
            ["http://a.test", "http://b.test"],
        )

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(parse_cors_origins(""), [])

    def test_wildcard_preserved_for_opt_in_loosening(self):
        self.assertEqual(parse_cors_origins("*"), ["*"])

    def test_none_returns_empty_list(self):
        self.assertEqual(parse_cors_origins(None), [])


class TestResolveBackendHost(unittest.TestCase):
    def test_defaults_to_loopback_on_host(self):
        self.assertEqual(resolve_backend_host(None, in_docker=False), "127.0.0.1")
        self.assertEqual(DEFAULT_BACKEND_HOST, "127.0.0.1")

    def test_defaults_to_zero_in_docker(self):
        self.assertEqual(resolve_backend_host(None, in_docker=True), "0.0.0.0")

    def test_explicit_env_host_wins_in_either_environment(self):
        self.assertEqual(
            resolve_backend_host("192.168.1.10", in_docker=False),
            "192.168.1.10",
        )
        self.assertEqual(
            resolve_backend_host("127.0.0.1", in_docker=True),
            "127.0.0.1",
        )

    def test_empty_env_host_falls_through_to_default(self):
        self.assertEqual(resolve_backend_host("", in_docker=False), "127.0.0.1")


class TestIsLoopbackHost(unittest.TestCase):
    def test_loopback_addresses(self):
        for h in ("127.0.0.1", "localhost", "::1"):
            self.assertTrue(is_loopback_host(h), h)

    def test_non_loopback_addresses(self):
        for h in ("0.0.0.0", "192.168.1.10", "10.0.0.1", ""):
            self.assertFalse(is_loopback_host(h), h)


def _build_app(token: str) -> FastAPI:
    app = FastAPI()
    if token:
        app.add_middleware(LocalTokenMiddleware, token=token)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/is_active")
    def is_active():
        return {"is_active": False}

    @app.get("/latest_answer")
    def latest_answer():
        return {"answer": ""}

    @app.get("/screenshot")
    def screenshot():
        return {"screenshot": None}

    @app.post("/query")
    def query():
        return {"ok": True}

    @app.get("/screenshots/foo.png")
    def screenshots_static():
        return {"png": True}

    return app


class TestLocalTokenMiddleware(unittest.TestCase):
    def test_empty_token_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            LocalTokenMiddleware(app=FastAPI(), token="")

    def test_query_requires_token_when_enabled(self):
        client = TestClient(_build_app(token="sekret"))
        resp = client.post("/query")
        self.assertEqual(resp.status_code, 401)
        self.assertIn(LOCAL_TOKEN_HEADER, resp.json()["error"])

    def test_query_accepts_matching_token(self):
        client = TestClient(_build_app(token="sekret"))
        resp = client.post("/query", headers={LOCAL_TOKEN_HEADER: "sekret"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"ok": True})

    def test_query_rejects_wrong_token(self):
        client = TestClient(_build_app(token="sekret"))
        resp = client.post("/query", headers={LOCAL_TOKEN_HEADER: "nope"})
        self.assertEqual(resp.status_code, 401)

    def test_exempt_paths_skip_token_check(self):
        client = TestClient(_build_app(token="sekret"))
        for path in TOKEN_EXEMPT_PATHS:
            resp = client.get(path)
            self.assertEqual(resp.status_code, 200, path)

    def test_screenshots_prefix_is_exempt(self):
        client = TestClient(_build_app(token="sekret"))
        resp = client.get("/screenshots/foo.png")
        self.assertEqual(resp.status_code, 200)

    def test_no_middleware_when_token_unset_preserves_backcompat(self):
        client = TestClient(_build_app(token=""))
        # No header, no problem — same as today's behavior.
        self.assertEqual(client.post("/query").status_code, 200)


class TestCorsDefaultIsRestrictive(unittest.TestCase):
    """Belt-and-braces: the default origin list should NOT include '*'."""

    def test_no_wildcard_by_default(self):
        origins = parse_cors_origins(DEFAULT_CORS_ORIGINS)
        self.assertNotIn("*", origins)
        self.assertTrue(all(o.startswith("http://") for o in origins))

    def test_cors_middleware_blocks_disallowed_origin(self):
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=parse_cors_origins(DEFAULT_CORS_ORIGINS),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/health")
        def health():
            return {"ok": True}

        client = TestClient(app)
        # Preflight from a disallowed origin should not echo back the origin.
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://evil.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertNotEqual(
            resp.headers.get("access-control-allow-origin"),
            "http://evil.example",
        )

    def test_cors_middleware_allows_listed_origin(self):
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=parse_cors_origins(DEFAULT_CORS_ORIGINS),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/health")
        def health():
            return {"ok": True}

        client = TestClient(app)
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(
            resp.headers.get("access-control-allow-origin"),
            "http://localhost:3000",
        )


if __name__ == "__main__":
    unittest.main()
