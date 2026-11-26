from fastapi.testclient import TestClient

from src.api.app import create_app


def test_replies_and_speech_use_the_same_reviewed_passage(monkeypatch):
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()).websocket_connect("/ws/text") as socket:
        socket.receive_json()
        for query, source, expected in (
            ("Growth ka price kya hai?", "growth", "₹2,499"),
            ("सालाना भुगतान पर छूट कितनी है?", "annual", "10%"),
            ("Is there a 40% annual discount?", None, "Discounts are handled"),
            ("How much is Enterprise?", None, "specialist follow up"),
        ):
            socket.send_json({"text": query})
            events = []
            while (reply := socket.receive_json())["type"] != "reply":
                events.append(reply)
            assert expected in reply["text"]
            assert [event["text"] for event in events if event["type"] == "sentence"] == [
                reply["text"]
            ]
            if source:
                assert reply["citation"]["id"] == source
            else:
                assert reply["citation"] is None
            assert socket.receive_json()["type"] == "profile"
