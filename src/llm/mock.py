"""Deterministic replies for a fictional inventory sales conversation."""

from collections.abc import AsyncGenerator


class MockLLM:
    name = "mock"

    async def stream(self, message: str) -> AsyncGenerator[str]:
        yield await self.reply(message)

    async def reply(self, message: str) -> str:
        text = message.casefold()
        if any(word in text for word in ("price", "pricing", "cost", "budget")):
            return "I’ll check that with our team. Would you like a human follow-up?"
        if any(word in text for word in ("store", "location", "inventory", "stock")):
            return "How many locations do you manage today?"
        if "demo" in text:
            return "What would you like to see in a demo?"
        return "What would you like to improve about how you track inventory today?"
