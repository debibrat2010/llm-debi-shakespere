from unittest.mock import patch

from fastapi.testclient import TestClient

from shakespeare_app.web import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index():
    r = client.get("/")
    assert r.status_code == 200
    assert "Bard" in r.text
    assert "/api/translate" in r.text


def test_api_translate_empty():
    r = client.post("/api/translate", json={"text": "   "})
    assert r.status_code == 200
    assert r.json() == {"translation": ""}


def test_api_translate_success():
    with patch("shakespeare_app.web.to_shakespeare", return_value="Hark!"):
        r = client.post("/api/translate", json={"text": "Listen!"})
    assert r.status_code == 200
    assert r.json() == {"translation": "Hark!"}


def test_api_translate_upstream_error():
    with patch("shakespeare_app.web.to_shakespeare", side_effect=RuntimeError("no key")):
        r = client.post("/api/translate", json={"text": "Hello"})
    assert r.status_code == 502
    assert "no key" in r.json()["detail"]


def test_api_translate_authentication_error():
    import httpx
    from openai import AuthenticationError

    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    resp = httpx.Response(401, request=req)
    err = AuthenticationError("Incorrect API key provided", response=resp, body=None)

    with patch("shakespeare_app.web.to_shakespeare", side_effect=err):
        r = client.post("/api/translate", json={"text": "Hello"})
    assert r.status_code == 401
    assert "OPENAI_API_KEY" in r.json()["detail"]


def test_api_translate_insufficient_quota():
    import httpx
    from openai import RateLimitError

    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    resp = httpx.Response(429, request=req)
    body = {
        "error": {
            "message": "You exceeded your current quota",
            "type": "insufficient_quota",
            "code": "insufficient_quota",
        }
    }
    err = RateLimitError("You exceeded your current quota", response=resp, body=body)

    with patch("shakespeare_app.web.to_shakespeare", side_effect=err):
        r = client.post("/api/translate", json={"text": "Hello"})
    assert r.status_code == 429
    assert "billing" in r.json()["detail"].lower()


def test_api_translate_rate_limit_generic():
    import httpx
    from openai import RateLimitError

    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    resp = httpx.Response(429, request=req)
    err = RateLimitError("Too many requests", response=resp, body={"error": {"code": "rate_limit_exceeded"}})

    with patch("shakespeare_app.web.to_shakespeare", side_effect=err):
        r = client.post("/api/translate", json={"text": "Hello"})
    assert r.status_code == 429
    assert "limit" in r.json()["detail"].lower()
