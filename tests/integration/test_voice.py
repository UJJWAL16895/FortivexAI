import io
import wave

from fastapi.testclient import TestClient

from src.api.app import create_app


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
                headers={"Content-Type": "audio/wav", "Origin": "https://unrelated.example"},
            ).status_code
            == 403
        )
