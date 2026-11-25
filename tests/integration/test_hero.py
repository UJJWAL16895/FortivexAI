from fastapi.testclient import TestClient

from src.api.app import create_app


def test_cited_answer_then_confirmed_booking_and_returning_lead(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MODE", "mock")
    monkeypatch.setenv("CRM_PATH", str(tmp_path / "hero.sqlite3"))
    with TestClient(create_app()) as client:

        def exchange(socket, text):
            socket.send_json({"text": text})
            while (answer := socket.receive_json())["type"] != "reply":
                pass
            socket.receive_json()
            return answer

        with client.websocket_connect("/ws/text") as socket:
            socket.receive_json()
            assert exchange(socket, "How much does Growth cost?")["citation"]["id"] == "growth"
            exchange(socket, "My name is Asha.")
            exchange(socket, "My email is hero@example.com")
            assert "IST (UTC+05:30)" in exchange(socket, "Book a demo")["text"]
            exchange(socket, "yes")
            assert client.get("/api/crm").json()["bookings"] == []
            first = exchange(socket, "Confirm booking")
            assert "Demo booked" in first["text"]
            assert exchange(socket, "Confirm booking")["text"] == first["text"]

        with client.websocket_connect("/ws/text") as socket:
            socket.receive_json()
            assert "Welcome back, Asha" in exchange(socket, "hero@EXAMPLE.COM")["text"]
        crm = client.get("/api/crm").json()
        assert len(crm["leads"]) == len(crm["bookings"]) == 1
