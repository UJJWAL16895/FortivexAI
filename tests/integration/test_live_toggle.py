import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.api.app import create_app
from src.llm.gemini import ProviderError

KEY = "fictional-toggle-fixture-secret"
CODE = "fictional-evaluator-access-code"


@pytest.fixture(autouse=True)
def configure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key, value in {
        "AGENT_MODE": "mock",
        "PUBLIC_DEMO": "false",
        "GEMINI_API_KEY": KEY,
        "GEMINI_MODEL": "fixture",
        "VOICE_STT": "local",
        "CRM_PATH": str(tmp_path / "test.sqlite3"),
    }.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def fake_provider(monkeypatch):
    async def probe(*_args):
        return None

    async def warm():
        return True

    async def stream(*_args):
        yield "How many locations do you manage today?"

    monkeypatch.setattr("src.api.live_mode.probe_gemini", probe)
    monkeypatch.setattr("src.api.live_mode.warm", warm)
    monkeypatch.setattr("src.llm.reply.stream_gemini", stream)


def receive(socket):
    event = socket.receive_json()
    assert KEY not in repr(event)
    return event


def switch(socket, mode):
    socket.send_json({"mode": mode})
    while True:
        event = receive(socket)
        if event["type"] == "mode_status" and event.get("phase") not in {"checking", "warming"}:
            return event


def turn(socket, text):
    socket.send_json({"text": text})
    events = []
    while (event := receive(socket))["type"] != "profile":
        events.append(event)
    return events


def test_switch_keeps_memory_and_is_private_to_socket(fake_provider):
    with (
        TestClient(create_app()) as client,
        client.websocket_connect("/ws/text") as a,
        client.websocket_connect("/ws/text") as b,
    ):
        ready = receive(a)
        assert ready["mode"] == receive(b)["mode"] == "mock"
        assert ready["voice_session"]
        turn(a, "My name is Asha.")
        assert switch(a, "live")["mode"] == "live"
        assert any("Asha" in e.get("text", "") for e in turn(a, "What do you remember?"))
        assert any(e.get("mode") == "live" for e in turn(a, "I want inventory help."))
        assert any(e.get("mode") == "mock" for e in turn(b, "I want inventory help."))
        assert switch(a, "mock")["mode"] == "mock"


def test_missing_key_stays_mock(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        receive(socket)
        result = switch(socket, "live")
        assert result["mode"] == "mock"
        assert result["message"] == "No API key configured on the server"


def test_invalid_key_is_sanitized(monkeypatch):
    async def invalid(*_args):
        raise ProviderError(401)

    monkeypatch.setattr("src.api.live_mode.probe_gemini", invalid)
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        receive(socket)
        result = switch(socket, "live")
        assert result["mode"] == "mock"
        assert "invalid" in result["message"].lower()


def test_public_requires_access_and_explicit_enablement(monkeypatch, fake_provider):
    monkeypatch.setenv("PUBLIC_DEMO", "true")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        assert not receive(socket)["live_allowed"]
        assert switch(socket, "live")["mode"] == "mock"
    monkeypatch.setenv("PUBLIC_LIVE_ENABLED", "true")
    monkeypatch.setenv("PUBLIC_ACCESS_CODE", CODE)
    with TestClient(create_app(), base_url="https://testserver") as client:
        with (
            pytest.raises(WebSocketDisconnect),
            client.websocket_connect("wss://testserver/ws/text"),
        ):
            pass
        assert (
            client.post(
                "/api/unlock", content=CODE, headers={"Origin": "https://testserver"}
            ).status_code
            == 204
        )
        with client.websocket_connect("wss://testserver/ws/text") as socket:
            receive(socket)
            assert switch(socket, "live")["mode"] == "live"


def test_daily_cap_reverts_live_connection(monkeypatch, fake_provider):
    monkeypatch.setenv("GEMINI_DAILY", "1")
    with TestClient(create_app()) as client, client.websocket_connect("/ws/text") as socket:
        receive(socket)
        assert switch(socket, "live")["mode"] == "live"
        events = turn(socket, "I want inventory help.")
        assert any(e.get("phase") == "quota" and e.get("mode") == "mock" for e in events)
        assert any(e.get("mode") == "mock" for e in events)
        assert switch(socket, "live")["mode"] == "mock"


def test_missing_whisper_routes_only_the_switched_tab_to_cloud(monkeypatch, fake_provider):
    import io
    import wave

    async def unavailable():
        return False

    async def transcribe(*_args):
        return "Cloud fixture"

    monkeypatch.setattr("src.api.live_mode.warm", unavailable)
    monkeypatch.setattr("src.api.voice.gemini.transcribe", transcribe)
    audio = io.BytesIO()
    with wave.open(audio, "wb") as clip:
        clip.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        clip.writeframes(b"\0" * 64)
    with (
        TestClient(create_app()) as client,
        client.websocket_connect("/ws/text") as a,
        client.websocket_connect("/ws/text") as b,
    ):
        handles = [receive(a)["voice_session"], receive(b)["voice_session"]]
        result = switch(a, "live")
        assert "Whisper unavailable" in result["message"]
        for handle, expected_text in zip(
            handles, ["Cloud fixture", "Can I manage three stores?"], strict=True
        ):
            reply = client.post(
                "/api/voice/transcribe",
                content=audio.getvalue(),
                headers={"Content-Type": "audio/wav", "X-Voice-Session": handle},
            )
            assert KEY not in reply.text
            assert reply.json()["text"] == expected_text
        assert switch(a, "mock")["quota"]["used"] == 2
