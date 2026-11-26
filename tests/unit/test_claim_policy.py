import json
from dataclasses import asdict

import httpx
import pytest

from src.core.settings import Settings
from src.llm.reply import ReplyPath


@pytest.mark.asyncio
async def test_invented_discount_never_leaks_to_text_or_speech(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    key = "synthetic-provider-test-token"
    settings = Settings(agent_mode="live", gemini_api_key=key, gemini_model="fixture")
    fake_reply = "Great news, all customers automatically get a 40% launch discount."
    data = {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "action": "none",
                                    "lines": [{"text": fake_reply, "kind": "conversation"}],
                                }
                            )
                        }
                    ]
                },
            }
        ]
    }
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text="data: " + json.dumps(data) + "\n\n")
        )
    ) as client:
        path = ReplyPath(settings, client)
        for prompt in ("Tell me something exciting.", "Do you offer a discount?"):
            events = [event async for event in path.converse(prompt, (), {}, ())]
            text_events = [asdict(line)["text"] for line in events[-1]["lines"]]
            assert all("40%" not in item for item in text_events)
            assert any("check" in item.casefold() for item in text_events)
            assert any("human follow-up" in item.casefold() for item in text_events)
