import json

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.crm.conversation import BookingSession
from src.llm.gemini import ProviderError
from src.memory.session import LeadSession
from src.rag.index import Knowledge


def setup(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "live")
    monkeypatch.setenv("VOICE_STT", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-conversation-token")
    monkeypatch.setenv("GEMINI_MODEL", "fixture")
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "")
    monkeypatch.setenv("GEMINI_RPM", "1000")
    monkeypatch.setenv("GEMINI_TPM", "100000")


def turn(socket, prompt):
    socket.send_json({"text": prompt})
    events = []
    while (event := socket.receive_json())["type"] != "profile":
        events.append(event)
    return events


def test_all_live_utterances_reach_provider_without_legacy_routing(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    calls = []
    retrievals = []
    retrieve = Knowledge.retrieve

    def fetch(self, text):
        retrievals.append(text)
        return retrieve(self, text)

    def forbidden(*_args):
        raise AssertionError("Legacy phrase routing ran for a live conversation turn")

    monkeypatch.setattr(Knowledge, "lookup", forbidden)
    monkeypatch.setattr(Knowledge, "retrieve", fetch)
    monkeypatch.setattr(LeadSession, "handle", forbidden)
    monkeypatch.setattr(BookingSession, "handle", forbidden)

    async def provider(_client, _key, _model, _thinking, text, history, system, _schema):
        calls.append(text)
        context = json.loads(system.split("Session data: ", 1)[1])
        assert "lead" in context and "passages" in context
        if text == "no":
            assert history[-1][1] == "Would you like me to follow up?"
        if text == "yes":
            assert history[-1][1] == "Would you like to book a demo?"
        if text == "How does the multi-store dashboard work?":
            assert any(item["id"] == "multi-store" for item in context["passages"])
        responses = {
            "Ask about following up": "Would you like me to follow up?",
            "Ask me about booking": "Would you like to book a demo?",
            "no": "No problem!",
            "yes": "Please say Confirm booking to reserve the time.",
        }
        yield json.dumps(
            {
                "action": "none",
                "lines": [
                    {
                        "text": responses.get(text, "How do you track stock today?"),
                        "kind": "conversation",
                    }
                ],
            }
        )

    monkeypatch.setattr("src.llm.reply.stream_gemini", provider)
    prompts = (
        "hii",
        "hiiiii",
        "helo",
        "namaste",
        "kaise ho",
        "hello how are you",
        "thanks",
        "ok",
        "Ask about following up",
        "no",
        "Ask me about booking",
        "yes",
        "zxqv",
        "How does the multi-store dashboard work?",
    )
    # This fixture accelerates only the local bucket, so no network or quota is used.
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        for prompt in prompts:
            client.app.state.replies.budget.tokens = 3
            events = turn(socket, prompt)
            reply = next(event for event in events if event["type"] == "reply")
            assert reply["origin"] == "gemini"
            assert "check with our team" not in reply["text"]
    assert calls == retrievals == list(prompts)


def test_checked_output_keeps_safe_line_and_cites_hindi_price(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)

    async def provider(_client, _key, _model, _thinking, text, _history, system, _schema):
        evidence = json.loads(system.split("Session data: ", 1)[1])["passages"]
        if text.startswith("ग्रोथ"):
            lines = [
                {
                    "kind": "fact",
                    "source": "growth",
                    "text": next(item["text"] for item in evidence if item["id"] == "growth"),
                }
            ]
        else:
            lines = [
                {"kind": "conversation", "text": "Happy to help!"},
                {"kind": "conversation", "text": "ShelfPilot offers a 40% discount and a $1 plan."},
            ]
        yield json.dumps({"action": "none", "lines": lines})

    monkeypatch.setattr("src.llm.reply.stream_gemini", provider)
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        events = turn(socket, "Is the Enterprise price $1?")
        reply = next(event for event in events if event["type"] == "reply")
        assert reply["text"].startswith("Happy to help!")
        assert reply["approved_follow_up"]
        assert not any(
            "40%" in event.get("text", "") or "$1" in event.get("text", "") for event in events
        )
        events = turn(socket, "ग्रोथ की कीमत क्या है?")
        reply = next(event for event in events if event["type"] == "reply")
        assert "₹2,499" in reply["text"]
        assert reply["origin"] == "knowledge" and reply["citation"]["id"] == "growth"


def test_exhausted_provider_switches_to_mock_without_specialist(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)

    async def provider(*_args):
        raise ProviderError(403)
        yield ""

    monkeypatch.setattr("src.llm.reply.stream_gemini", provider)
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        socket.receive_json()
        events = turn(socket, "hii")
        assert any(event.get("phase") == "unavailable" for event in events)
        assert any(
            event.get("text") == "Live model unavailable, switching to mock." for event in events
        )
