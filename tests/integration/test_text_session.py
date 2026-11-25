from fastapi.testclient import TestClient

from src.api.app import create_app


def test_mock_text_turn_and_recovery(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()).websocket_connect("/ws/text") as socket:
        assert socket.receive_json()["mode"] == "mock"
        socket.send_text("{")
        assert socket.receive_json()["type"] == "error"
        socket.send_json({"text": "  "})
        assert socket.receive_json()["type"] == "error"
        socket.send_json({"text": "How do I manage multiple stores?"})
        events = []
        while (reply := socket.receive_json())["type"] not in {"reply", "error"}:
            events.append(reply["type"])
        assert "delta" in events and "sentence" in events
        assert reply["type"] == "reply"
        assert "locations" in reply["text"]
        assert reply["latency_ms"] >= 0
        socket.send_json({"text": "What does it cost?"})
        while (reply := socket.receive_json())["type"] not in {"reply", "error"}:
            pass
        assert "human follow-up" in reply["text"]


def test_socket_keeps_confirmation_and_recall_local_to_one_connection(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    client = TestClient(create_app())

    def exchange(socket, text):
        socket.send_json({"text": text})
        while (reply := socket.receive_json())["type"] != "reply":
            pass
        profile = socket.receive_json()
        assert profile["type"] == "profile"
        return reply["text"], profile

    with client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        reply, event = exchange(
            socket, "My name is Asha. I work at Cedar Retail. We have three stores."
        )
        assert "3 stores" in reply and event["pending"] == {"store_count": 3}
        assert "store_count" not in event["profile"]
        _, event = exchange(socket, "yes")
        assert event["profile"]["store_count"] == 3 and event["pending"] is None
        reply, _ = exchange(socket, "What do you remember?")
        assert "Asha" in reply and "Cedar Retail" in reply and "3 stores" in reply
    with client.websocket_connect("/ws/text") as new_socket:
        new_socket.receive_json()
        reply, event = exchange(new_socket, "What do you remember?")
        assert "Asha" not in reply and "store_count" not in event["profile"]


def test_foreign_browser_origin_is_rejected():
    import pytest
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect):
        with TestClient(create_app()).websocket_connect(
            "/ws/text", headers={"origin": "https://foreign.example"}
        ):
            pass
