import io
import wave

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.voice import gemini, local
from src.llm.gemini import ProviderError


def test_keyless_voice_fixture_and_bad_audio(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        writer.writeframes(bytes(3200))
    with TestClient(create_app()) as client:
        url = "/api/voice/transcribe"
        assert (
            client.post(url, content=b"invalid", headers={"Content-Type": "audio/wav"}).status_code
            == 422
        )
        response = client.post(
            url, content=stream.getvalue(), headers={"Content-Type": "audio/wav"}
        )
        assert response.status_code == 200
        assert response.json()["provider"] == "mock"
        assert "stores" in response.json()["text"]
        assert client.post("/api/voice/speak", json={"text": "Say this"}).status_code == 204
        assert (
            client.post(
                url,
                content=stream.getvalue(),
                headers={
                    "Content-Type": "audio/wav",
                    "Origin": "https://unrelated.example",
                },
            ).status_code
            == 403
        )


@pytest.mark.parametrize("primary", ["local", "gemini"])
def test_one_stt_failure_keeps_the_same_audio_for_fallback(monkeypatch, tmp_path, primary):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "live")
    monkeypatch.setenv("VOICE_STT", primary)
    monkeypatch.setenv("GEMINI_MODEL", "fixture-model")
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-stt-key")
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        writer.writeframes(bytes(3200))
    audio = stream.getvalue()
    calls = []

    async def local_stt(recording, language):
        assert recording == audio and language == "hi"
        calls.append("local")
        if primary == "local":
            raise RuntimeError
        return "नमस्ते"

    async def gemini_stt(client, key, model_name, recording):
        assert recording == audio
        calls.append("gemini")
        if primary == "gemini":
            raise ProviderError(503)
        return "नमस्ते"

    async def skip_warm():
        return None

    monkeypatch.setattr("src.api.app.warm", skip_warm)
    monkeypatch.setattr(local, "recognize", local_stt)
    monkeypatch.setattr(gemini, "transcribe", gemini_stt)
    with TestClient(create_app()) as client:
        result = client.post(
            "/api/voice/transcribe?language=hi",
            content=audio,
            headers={"Content-Type": "audio/wav"},
        )
    assert result.json()["text"] == "नमस्ते"
    assert calls == [primary, "gemini" if primary == "local" else "local"]
