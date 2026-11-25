from fastapi.testclient import TestClient

from src.api.app import create_app


def test_mock_text_turn_and_recovery(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()).websocket_connect("/ws/text") as socket:
        assert socket.receive_json() == {"type": "ready", "provider": "mock"}
        socket.send_text("{")
        assert socket.receive_json()["type"] == "error"
        socket.send_json({"text": "  "})
        assert socket.receive_json()["type"] == "error"
        socket.send_json({"text": "Can I manage three stores?"})
        reply = socket.receive_json()
        assert reply["type"] == "reply"
        assert "locations" in reply["text"]
        assert reply["latency_ms"] >= 0
        socket.send_json({"text": "What does it cost?"})
        assert "pricing" in socket.receive_json()["text"]


def test_foreign_browser_origin_is_rejected():
    import pytest
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect):
        with TestClient(create_app()).websocket_connect(
            "/ws/text", headers={"origin": "https://foreign.example"}
        ):
            pass
