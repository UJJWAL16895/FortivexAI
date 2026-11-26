import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.llm.claims import CHECK_SHORT_EN
from src.memory.session import IST


def draft(text, *, action="none", booking=None, analysis=None, buying_signal="none", lines=None):
    return {
        "action": action,
        "lines": lines or [{"text": text, "kind": "conversation"}],
        "booking": booking,
        "analysis": analysis,
        "buying_signal": buying_signal,
    }


A = {
    "book a demo": draft("What is your contact?", action="booking", booking={"intent": "book"}),
    "+12025550142": draft(
        "I saved your phone. What is your email?",
        booking={"contact": "+12025550142", "intent": "other"},
    ),
    "tomorrow 5 PM": draft(
        "Noted. Please say Confirm booking.",
        booking={
            "preferred_datetime": (datetime.now(IST) + timedelta(days=1))
            .replace(hour=17, minute=0, second=0, microsecond=0)
            .isoformat(),
            "intent": "other",
        },
    ),
    "Confirm booking": draft(
        "Your demo is confirmed.", action="booking", booking={"intent": "affirm"}
    ),
}
B = {
    "i dont want to buy": draft(
        "I understand completely. Let me know if you change your mind!",
        buying_signal="declining",
        analysis={"sentiment": "Negative", "score": -0.55, "confidence": 0.9},
    ),
    "ok i change my mind and i am too happy to buy with the 10 percent discount": draft(
        "",
        buying_signal="ready_to_buy",
        analysis={"sentiment": "Positive", "score": 0.85, "confidence": 0.95},
        lines=[
            {
                "text": "Annual prepayment gives a 10% discount on Starter or Growth.",
                "kind": "fact",
                "source": "annual",
            },
            {"text": "That's wonderful to hear!", "kind": "conversation"},
        ],
    ),
}
C = "Can I get a 40% annual discount?"
C_REPLY = draft(
    "",
    lines=[
        {"text": "Annual prepayment gives a 40% discount.", "kind": "fact"},
        {"text": "Growth is $1 per month.", "kind": "fact"},
    ],
)
EXTRA = {
    "kal shaam 5 baje": A["tomorrow 5 PM"],
    "yes": A["Confirm booking"],
    "I am furious": draft(
        "I hear you.", analysis={"sentiment": "Negative", "score": -0.9, "confidence": 0.9}
    ),
    "I am still furious": draft(
        "I hear you.", analysis={"sentiment": "Negative", "score": -0.8, "confidence": 0.9}
    ),
    "What is your name?": draft(
        "I’m ShelfPilot.", analysis={"sentiment": "Neutral", "score": 0, "confidence": 0.9}
    ),
    "asdkfj": draft("Could you repeat that?"),
    "fake status": draft("Your demo is confirmed."),
}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key, value in {
        "AGENT_MODE": "live",
        "VOICE_STT": "gemini",
        "GEMINI_API_KEY": "synthetic-booking-test",
        "GEMINI_MODEL": "fixture",
        "GEMINI_FALLBACK_MODEL": "",
        "GEMINI_RPM": "1000",
        "GEMINI_TPM": "100000",
    }.items():
        monkeypatch.setenv(key, value)

    async def fake(_client, _key, _model, _thinking, text, _history, _system, schema):
        if text == "timeout":
            raise TimeoutError
        if text == "invalid":
            yield json.dumps(
                draft(
                    "This should not be emitted.",
                    analysis={"sentiment": "Happy", "score": 2, "confidence": 1},
                )
            )
            return
        response = {**A, **B, **EXTRA, C: C_REPLY}[text]
        # Replay the same model output against the previous schema for the diagnosis.
        fields = schema["properties"]
        yield json.dumps(
            {key: value for key, value in response.items() if key in fields and value is not None}
        )

    monkeypatch.setattr("src.llm.reply.stream_gemini", fake)
    with TestClient(create_app()) as test_client:
        budget = test_client.app.state.replies.budget
        reserve = budget.reserve

        def replenish(cost):
            budget.tokens = 3
            reserve(cost)

        budget.reserve = replenish
        yield test_client


def turn(ws, text, number):
    ws.send_json({"text": text, "turn_id": number})
    events = {}
    while (event := ws.receive_json())["type"] != "analysis":
        events[event["type"]] = event
    return events["reply"], event


def test_transcript_a(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        replies = [turn(ws, text, n)[0]["text"] for n, text in enumerate(A, 1)]
        print("A:", replies)
        result = client.get("/api/crm").json()
        assert len(result["bookings"]) == len(result["leads"]) == 1
        assert "17:00 IST" in replies[-1]
        assert "email" not in replies[1].lower()


def test_transcript_b_sentiment(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        outcomes = [turn(ws, text, n)[1]["sentiment"] for n, text in enumerate(B, 1)]
        print("B sentiment:", outcomes)
        assert outcomes == ["Negative", "Positive"]


def test_transcript_b_sales(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        decline, buy = [turn(ws, text, n)[0]["text"] for n, text in enumerate(B, 1)]
        print("B replies:", decline, buy)
        assert decline.count("?") == 1
        assert "demo" in buy.lower() and "10%" in buy


def test_transcript_c(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        reply, _ = turn(ws, C, 1)
        print("C reproduction:", reply["text"])
        assert reply["text"] == CHECK_SHORT_EN


def test_roman_hindi_time_and_plain_yes(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        assert turn(ws, "kal shaam 5 baje", 1)[0]["booking"]["state"] == "need_contact"
        reply, _ = turn(ws, "+12025550142", 2)
        assert reply["booking"]["state"] == "awaiting_confirmation"
        assert "17:00 IST" in reply["text"]
        assert turn(ws, "yes", 3)[0]["booking"]["state"] == "booked"


def test_live_analysis_states_and_escalation(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        assert turn(ws, "I am furious", 1)[1]["sentiment_score"] == -0.9
        reply, result = turn(ws, "I am still furious", 2)
        assert "sorry" in reply["text"] and "someone" in reply["text"]
        assert result["status"] == "analyzed" and result["confidence"] == 0.9
        assert turn(ws, "What is your name?", 3)[1]["sentiment"] == "Neutral"
        analysis = turn(ws, "asdkfj", 4)[1]
        assert analysis["status"] == "not_analyzed" and analysis["sentiment"] is None


def test_generated_booking_success_cannot_create_receipt(client):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        reply, _ = turn(ws, "fake status", 1)
        assert reply["text"] == CHECK_SHORT_EN
        assert reply["booking"]["receipt"] is None
        assert not client.get("/api/crm").json()["bookings"]


@pytest.mark.parametrize(("prompt", "attempts"), [("timeout", 1), ("invalid", 2)])
def test_failed_live_analysis_never_synthesizes_neutral(client, prompt, attempts):
    with client.websocket_connect("/ws/text") as ws:
        ws.receive_json()
        reply, result = turn(ws, prompt, 1)
        assert reply["mode"] == "mock"
        assert result["status"] == "not_analyzed" and result["sentiment"] is None
        assert len(client.app.state.replies.budget.calls) == attempts
