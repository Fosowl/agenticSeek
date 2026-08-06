import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from sources.api_auth import require_api_token


def _build_protected_app():
    app = FastAPI()

    @app.post("/protected", dependencies=[Depends(require_api_token)])
    async def protected():
        return {"ok": True}

    return app


class TestApiAuth(unittest.TestCase):
    """Regression tests for the AGENTICSEEK_API_TOKEN guard (#520)."""

    def setUp(self):
        self._previous_token = os.environ.pop("AGENTICSEEK_API_TOKEN", None)
        self.client = TestClient(_build_protected_app())

    def tearDown(self):
        if self._previous_token is not None:
            os.environ["AGENTICSEEK_API_TOKEN"] = self._previous_token
        else:
            os.environ.pop("AGENTICSEEK_API_TOKEN", None)

    def test_no_token_configured_allows_request(self):
        response = self.client.post("/protected")
        self.assertEqual(response.status_code, 200)

    def test_token_configured_rejects_missing_header(self):
        os.environ["AGENTICSEEK_API_TOKEN"] = "s3cret"
        response = self.client.post("/protected")
        self.assertEqual(response.status_code, 401)

    def test_token_configured_rejects_malformed_header(self):
        os.environ["AGENTICSEEK_API_TOKEN"] = "s3cret"
        response = self.client.post("/protected", headers={"Authorization": "s3cret"})
        self.assertEqual(response.status_code, 401)

    def test_token_configured_rejects_wrong_token(self):
        os.environ["AGENTICSEEK_API_TOKEN"] = "s3cret"
        response = self.client.post(
            "/protected", headers={"Authorization": "Bearer wrong"}
        )
        self.assertEqual(response.status_code, 401)

    def test_token_configured_accepts_correct_token(self):
        os.environ["AGENTICSEEK_API_TOKEN"] = "s3cret"
        response = self.client.post(
            "/protected", headers={"Authorization": "Bearer s3cret"}
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
