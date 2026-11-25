import json

import httpx
import pytest

from src.core.settings import Settings
from src.llm.reply import ReplyPath

TEST_KEY = "synthetic-test-key"


@pytest.mark.asyncio
@pytest.mark.parametrize("partial", [False, True])
async def test_real_adapter_falls_back_only_before_visible_text(monkeypatch, tmp_path, partial):
    monkeypatch.chdir(tmp_path)
    settings = Settings(
        agent_mode="live",
        gemini_api_key=TEST_KEY,
        gemini_model="fixture-a",
        gemini_fallback_model="fixture-b",
    )
    calls = []

    def response(request):
        model = request.url.path.split("/")[-1].split(":")[0]
        calls.append(model)
        assert request.headers["x-goog-api-key"] == TEST_KEY
        body = json.loads(request.content)
        assert body["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "minimal"}
        if model == "fixture-a" and not partial:
            return httpx.Response(503)
        data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "How many locations do you manage today? What would you like to see in a demo?"
                            }
                        ]
                    }
                }
            ]
        }
        if not partial:
            data["candidates"][0]["finishReason"] = "STOP"
        return httpx.Response(200, text="data: " + json.dumps(data) + "\n\n")

    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
        events = [event async for event in ReplyPath(settings, client).stream("Hello there")]
    if partial:
        assert calls == ["fixture-a"]
        assert events[-1]["type"] == "error"
    else:
        assert calls == ["fixture-a", "fixture-a", "fixture-b"]
        assert events[-1]["provider"] == "fixture-b"
        assert events[-1]["mode"] == "live"
        assert [event["text"] for event in events if event["type"] == "sentence"] == [
            "How many locations do you manage today?",
            "What would you like to see in a demo?",
        ]
