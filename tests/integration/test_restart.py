from fastapi.testclient import TestClient

from src.api.app import create_app


def test_dashboard_counts_survive_restart(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MODE", "mock")
    monkeypatch.setenv("CRM_PATH", str(tmp_path / "restart.sqlite3"))

    def call(client, turns):
        with client.websocket_connect("/ws/text") as socket:
            socket.receive_json()
            for text in turns:
                socket.send_json({"text": text})
                while socket.receive_json()["type"] != "profile":
                    pass

    with TestClient(create_app()) as client:
        call(client, [])
        call(client, ["I am the owner. We need stock reports."])
        call(client, ["contact lead@example.test", "Book a demo", "Confirm booking", "Thank you."])
    with TestClient(create_app()) as client:
        report = client.get("/api/insights").json()
        assert report["totals"] == {"calls": 2, "booked_calls": 1, "booking_rate": 0.5}
        assert [record["booked"] for record in report["calls"]] == [True, False]
        assert report["calls"][0]["sentiment"][-1] == "Positive"
        assert report["calls"][1]["score"] == 50
        assert report["calls"][1]["summary"]
