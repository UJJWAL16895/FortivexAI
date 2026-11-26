import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.llm.gemini import ProviderError
from src.llm.grounded import grounded_options


def reply_for(socket, text):
    socket.send_json({"text": text})
    while (reply := socket.receive_json())["type"] != "reply":
        pass
    return reply


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello!", "Nice to meet you"),
        ("How are you?", "Doing well"),
        ("Thanks!", "You’re welcome"),
        ("नमस्ते!", "एक दुकान"),
        ("kaise ho?", "Doing well"),
        ("ठीक है", "स्टॉक"),
    ],
)
def test_pleasantry_uses_approved_words(monkeypatch, tmp_path, text, expected):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        reply = reply_for(socket, text)
        assert expected in reply["text"]
        assert reply["origin"] == "approved" and reply["mode"] == "session"


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


@pytest.mark.parametrize("outcome", ["unsupported", "approved", "unavailable"])
def test_grounded_elaboration_accepts_exact_supported_answer_only(monkeypatch, tmp_path, outcome):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "live")
    monkeypatch.setenv("VOICE_STT", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fictional-fixture-secret")
    monkeypatch.setenv("GEMINI_MODEL", "fixture")
    passage = "ShelfPilot shows stock from multiple stores in one dashboard."

    async def draft(_client, _key, _model, _thinking, prompt):
        assert passage in prompt
        assert "how does" not in prompt.lower()
        if outcome == "unavailable":
            raise ProviderError(503)
        yield (
            (passage + " It syncs every second and comes with a 40% discount.")
            if outcome == "unsupported"
            else grounded_options(passage)[0]
        )

    monkeypatch.setattr("src.llm.reply.stream_gemini", draft)
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        reply = reply_for(socket, "How does the multi-store dashboard work?")
        assert reply["citation"]["id"] == "multi-store"
        if outcome != "approved":
            assert reply["origin"] == "knowledge" and reply["text"] == passage
        else:
            assert reply["origin"] == "gemini" and reply["provider"] == "fixture"
            assert reply["text"] == grounded_options(passage)[0]
            assert reply["passage"] == passage


def test_refund_abstains_without_citing_a_policy(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        reply = reply_for(socket, "Do you offer refunds?")
        assert reply["citation"] is None and reply["mode"] == "knowledge"
        assert "Refund questions are handled by our sales team." in reply["text"]
