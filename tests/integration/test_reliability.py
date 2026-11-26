import asyncio
import logging
import threading

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.core.logging import RedactContacts
from src.core.settings import Settings
from src.llm.reply import ReplyPath


def test_disconnect_cancels_mid_turn(monkeypatch, tmp_path):
    monkeypatch.setenv("CRM_PATH", str(tmp_path / "disconnect.sqlite3"))
    stopped = threading.Event()

    class SlowReply:
        async def stream(self, *_args, **_kwargs):
            yield {"type": "delta", "text": "first fragment"}
            try:
                await asyncio.sleep(30)
            finally:
                stopped.set()

    app = create_app()
    with TestClient(app) as client:
        app.state.replies = SlowReply()
        with client.websocket_connect("/ws/text") as socket:
            socket.receive_json()
            socket.send_json({"text": "I want inventory help."})
            assert socket.receive_json()["type"] == "delta"
            socket.close()
            assert stopped.wait(1)


@pytest.mark.asyncio
async def test_slow_provider_has_a_bounded_timeout_and_mock_fallback(monkeypatch):
    async def hanging(*args):
        await asyncio.sleep(30)
        yield ""

    monkeypatch.setattr("src.llm.reply.stream_gemini", hanging)
    monkeypatch.setattr("src.llm.reply.REPLY_TIMEOUT", 0.02)
    import httpx

    settings = Settings(
        _env_file=None, agent_mode="live", gemini_api_key="synthetic-token", gemini_model="fixture"
    )
    async with httpx.AsyncClient() as client:
        path = ReplyPath(settings, client)
        async with asyncio.timeout(1):
            events = [event async for event in path.stream("Hello")]
    assert any(event.get("code") == 504 for event in events)
    assert events[-1]["mode"] == "mock"


def test_contact_redaction_removes_values_from_logs(caplog):
    logger = logging.getLogger("uvicorn.error")
    shield = RedactContacts()
    logger.addFilter(shield)
    try:
        with caplog.at_level(logging.WARNING, logger=logger.name):
            logger.warning(
                "Fixture %s called from %s and %s",
                "hero@example.test",
                "+91 98765 43210",
                "+९१ ९८७६५ ४३२१०",
            )
    finally:
        logger.removeFilter(shield)
    assert "[email]" in caplog.text and caplog.text.count("[phone]") == 2
    assert all(value not in caplog.text for value in ("hero@", "98765", "९८७६५"))
