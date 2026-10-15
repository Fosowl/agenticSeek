import os
import shutil
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from sources.api_auth import (
    ALLOWED_HOSTS_ENV,
    TOKEN_ENV,
    HostAllowlistMiddleware,
    allowed_hosts,
    ensure_api_token,
    require_api_token,
)

_GUARDED_ENV = (TOKEN_ENV, ALLOWED_HOSTS_ENV, "AGENT_RUNTIME_DIR")


def _build_protected_app():
    app = FastAPI()
    app.add_middleware(HostAllowlistMiddleware, hosts=allowed_hosts())

    @app.post("/protected", dependencies=[Depends(require_api_token)])
    async def protected():
        return {"ok": True}

    return app


class _EnvIsolation(unittest.TestCase):
    def setUp(self):
        self._saved_env = {name: os.environ.pop(name, None) for name in _GUARDED_ENV}
        self._runtime_dir = tempfile.mkdtemp()
        os.environ["AGENT_RUNTIME_DIR"] = self._runtime_dir

    def tearDown(self):
        for name, value in self._saved_env.items():
            os.environ.pop(name, None)
            if value is not None:
                os.environ[name] = value
        shutil.rmtree(self._runtime_dir, ignore_errors=True)


class TestRequireApiToken(_EnvIsolation):
    """The API runs agent shell commands, so the guard must fail closed (#520)."""

    def _post(self, headers=None, host="localhost:7777"):
        client = TestClient(_build_protected_app(), base_url=f"http://{host}")
        return client.post("/protected", headers=headers or {})

    def test_no_token_configured_rejects_request(self):
        self.assertEqual(self._post().status_code, 503)

    def test_token_configured_rejects_missing_header(self):
        os.environ[TOKEN_ENV] = "s3cret"
        self.assertEqual(self._post().status_code, 401)

    def test_token_configured_rejects_malformed_header(self):
        os.environ[TOKEN_ENV] = "s3cret"
        self.assertEqual(self._post({"Authorization": "s3cret"}).status_code, 401)

    def test_token_configured_rejects_wrong_token(self):
        os.environ[TOKEN_ENV] = "s3cret"
        self.assertEqual(self._post({"Authorization": "Bearer wrong"}).status_code, 401)

    def test_non_ascii_token_is_rejected_not_crashing(self):
        os.environ[TOKEN_ENV] = "s3cret"
        response = self._post({"Authorization": "Bearer s3crét".encode("utf-8")})
        self.assertEqual(response.status_code, 401)

    def test_token_configured_accepts_correct_token(self):
        os.environ[TOKEN_ENV] = "s3cret"
        self.assertEqual(self._post({"Authorization": "Bearer s3cret"}).status_code, 200)

    def test_rebinding_host_is_rejected_even_with_token(self):
        os.environ[TOKEN_ENV] = "s3cret"
        response = self._post({"Authorization": "Bearer s3cret"}, host="evil.example.com:7777")
        self.assertEqual(response.status_code, 400)

    def test_extra_allowed_host_is_accepted(self):
        os.environ[TOKEN_ENV] = "s3cret"
        os.environ[ALLOWED_HOSTS_ENV] = " 192.168.1.100 , "
        response = self._post({"Authorization": "Bearer s3cret"}, host="192.168.1.100:7777")
        self.assertEqual(response.status_code, 200)

    def test_ipv6_loopback_host_is_accepted(self):
        os.environ[TOKEN_ENV] = "s3cret"
        response = self._post({"Authorization": "Bearer s3cret", "Host": "[::1]:7777"})
        self.assertEqual(response.status_code, 200)

    def test_lookalike_loopback_hosts_are_rejected(self):
        os.environ[TOKEN_ENV] = "s3cret"
        for host in ("localhost.evil.example.com", "127.0.0.1.nip.io", "evil.example.com@localhost"):
            with self.subTest(host=host):
                response = self._post({"Authorization": "Bearer s3cret", "Host": host})
                self.assertEqual(response.status_code, 400)


class TestEnsureApiToken(_EnvIsolation):
    """Without AGENTICSEEK_API_TOKEN the backend must still require a token."""

    def test_generates_and_persists_owner_only_token(self):
        token, path = ensure_api_token()
        self.assertGreaterEqual(len(token), 32)
        self.assertEqual(os.environ[TOKEN_ENV], token)
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)

    def test_reuses_stored_token_across_restarts(self):
        first_token, _ = ensure_api_token()
        os.environ.pop(TOKEN_ENV)
        second_token, _ = ensure_api_token()
        self.assertEqual(first_token, second_token)

    def test_regenerates_when_stored_file_is_empty(self):
        open(os.path.join(self._runtime_dir, "api_token"), "w").close()
        token, _ = ensure_api_token()
        self.assertTrue(token)

    def test_env_token_wins_and_writes_no_file(self):
        os.environ[TOKEN_ENV] = "chosen-by-user"
        self.assertEqual(ensure_api_token(), ("chosen-by-user", None))
        self.assertEqual(os.listdir(self._runtime_dir), [])


if __name__ == "__main__":
    unittest.main()
