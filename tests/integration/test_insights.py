from time import monotonic, sleep

from fastapi.testclient import TestClient

from src.api.app import create_app


def test_completed_socket_publishes_validated_insights(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MODE", "mock")
    monkeypatch.setenv("CRM_PATH", str(tmp_path / "insights.sqlite3"))
    with TestClient(create_app()) as client:
        with client.websocket_connect("/ws/text") as socket:
            socket.receive_json()
            for prompt in (
                "I am the owner. We need inventory help.",
                "I am frustrated. Our budget is 3000 rupees and we need it this month.",
            ):
                socket.send_json({"text": prompt})
                while socket.receive_json()["type"] != "profile":
                    pass
            assert client.get("/api/insights").json()["calls"] == []
            socket.send_json({"text": "End conversation", "end_call": True})
            assert "ended" in socket.receive_json()["text"]
        deadline = monotonic() + 2
        while monotonic() < deadline:
            response = client.get("/api/insights").json()
            if response["calls"]:
                break
            sleep(0.01)
        assert len(response["calls"]) == 1
        call = response["calls"][0]
        assert call["rating"] == "Hot" and call["score"] == 100
        assert call["sentiment"] == ["Neutral", "Negative"]
        assert "specialist" in call["next_action"]
        assert "3000" not in str(call)
