import pytest

from src.llm.sentences import SentenceBuffer


def test_sentence_available_before_stream_end_without_cutting_a_decimal():
    buffer = SentenceBuffer()
    assert buffer.push("It costs 12.") == []
    assert buffer.push("50. Do you") == ["It costs 12.50."]
    assert buffer.push(" need it? ") == ["Do you need it?"]
    assert buffer.finish() == []


def test_hindi_and_final_fragment():
    buffer = SentenceBuffer()
    assert buffer.push("बताइए। और") == ["बताइए।"]
    assert buffer.finish() == ["और"]


@pytest.mark.asyncio
async def test_simulated_chain_reports_both_failures_before_mock(monkeypatch):
    from src.core.settings import Settings
    from src.llm.reply import ReplyPath

    monkeypatch.setenv("AGENT_MODE", "mock")
    result = [
        event async for event in ReplyPath(Settings(_env_file=None)).stream("cost", simulate=True)
    ]
    assert [
        (event["provider"], event["status"])
        for event in result
        if event["type"] == "provider" and event["status"] != "trying"
    ] == [("Gemini A", "failed"), ("Gemini B", "failed"), ("mock", "active")]
    assert result[-1]["provider"] == "mock"
    assert "human follow-up" in result[-1]["text"]
