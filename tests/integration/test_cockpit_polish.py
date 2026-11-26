from fastapi.testclient import TestClient

from src.api.app import create_app


def reply_for(socket, text):
    socket.send_json({"text": text})
    while (reply := socket.receive_json())["type"] != "reply":
        pass
    return reply


def test_live_analysis_follows_reply_and_preserves_confirmations(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        for index, text in enumerate(
            ("I am the owner. We need inventory tools.", "Thanks! We have three stores.", "yes"), 1
        ):
            socket.send_json({"text": text, "turn_id": index})
            while socket.receive_json()["type"] != "reply":
                pass
            profile = socket.receive_json()
            assert profile["type"] == "profile"
            live = socket.receive_json()
            assert live["type"] == "analysis" and live["turn_id"] == index
            assert live["score"] == 50 and live["rating"] == "Warm"
            if index == 2:
                assert live["sentiment"] == "Positive"
                assert profile["pending"] == {"store_count": 3}
            if index == 3:
                assert profile["profile"]["store_count"] == 3
        assert client.get("/api/insights").json()["totals"]["calls"] == 0


def test_refund_abstains_without_citing_a_policy(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        reply = reply_for(socket, "Do you offer refunds?")
        assert reply["citation"] is None and reply["mode"] == "knowledge"
        assert "Refund questions are handled by our sales team." in reply["text"]
