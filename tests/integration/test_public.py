import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.api.app import create_app

CODE = "fictional-demo-access-phrase"
TOKEN = "synthetic-fixture-token"


def test_public_startup_is_mock_without_an_explicit_live_switch(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PUBLIC_DEMO", "true")
    monkeypatch.setenv("AGENT_MODE", "live")
    with TestClient(create_app()) as client:
        assert client.get("/health").json()["mode"] == "mock"
        assert client.get("/api/public-status").json()["public"] is True


def test_live_gate_checks_http_and_socket_with_secure_cookie(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name, value in {
        "PUBLIC_DEMO": "true",
        "PUBLIC_LIVE_ENABLED": "true",
        "AGENT_MODE": "live",
        "PUBLIC_ACCESS_CODE": CODE,
        "GEMINI_API_KEY": TOKEN,
        "GEMINI_MODEL": "fixture",
        "VOICE_STT": "local",
    }.items():
        monkeypatch.setenv(name, value)
    with TestClient(create_app(), base_url="https://testserver") as client:
        assert client.app.state.settings.voice_stt == "gemini"
        assert client.get("/api/crm").status_code == 401
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("wss://testserver/ws/text"):
                pass
        assert client.post("/api/unlock", content=CODE).status_code == 403
        reply = client.post("/api/unlock", content=CODE, headers={"Origin": "https://testserver"})
        assert reply.status_code == 204
        assert "Secure" in reply.headers["set-cookie"] and "HttpOnly" in reply.headers["set-cookie"]
        assert client.get("/api/crm").status_code == 200
        with client.websocket_connect("wss://testserver/ws/text") as socket:
            assert socket.receive_json()["mode"] == "live"


def test_public_caps_http_and_websocket_work(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PUBLIC_DEMO", "true")
    monkeypatch.setenv("PUBLIC_REQUESTS_PER_MINUTE", "3")
    monkeypatch.setenv("PUBLIC_DAILY_REQUEST_CAP", "2")
    with TestClient(create_app()) as client:
        assert client.get("/api/crm").status_code == 200
        with client.websocket_connect("/ws/text") as socket:
            assert socket.receive_json()["type"] == "ready"
            socket.send_json({"text": ""})
            assert socket.receive_json()["type"] == "error"
            socket.send_json({"text": "Book a demo"})
            with pytest.raises(WebSocketDisconnect):
                socket.receive_json()
        assert client.get("/api/insights").status_code == 429
        assert client.get("/health").status_code == 200


def test_public_limits_each_peer_separately():
    from src.core.public import PublicGuard

    guard = PublicGuard(create_app(), "", 1, 2)
    assert guard.reserve("192.0.2.1")
    assert not guard.reserve("192.0.2.1")
    assert guard.reserve("192.0.2.2")
    assert not guard.reserve("192.0.2.3")
