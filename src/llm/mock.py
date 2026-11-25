"""Deterministic replies for a fictional inventory sales conversation."""


class MockLLM:
    name = "mock"

    async def reply(self, message: str) -> str:
        text = message.casefold()
        if any(word in text for word in ("price", "pricing", "cost", "budget")):
            return "I can help narrow down pricing. How many locations would use ShelfPilot?"
        if any(word in text for word in ("store", "location", "inventory", "stock")):
            return (
                "ShelfPilot brings inventory across locations into one view. "
                "How many locations do you manage today?"
            )
        if "demo" in text:
            return "What would you most like to see in a ShelfPilot demo?"
        return "What would you like to improve about how you track inventory today?"
