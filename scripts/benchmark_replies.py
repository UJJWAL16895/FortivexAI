"""Run matched synthetic English, Hindi and Hinglish prompts using the local key."""

import argparse
import asyncio
import json
import statistics
from time import perf_counter

import httpx
from dotenv import dotenv_values

from src.llm.gemini import ProviderError, stream_gemini

MODELS = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite")
PROMPTS = (
    "How would I get started if I manage three stores?",
    "What does ShelfPilot cost for two locations?",
    "Can you book a demo for me tomorrow?",
    "Our stock counts differ between locations. Can you help?",
    "मेरी तीन दुकानें हैं। मैं शुरुआत कैसे करूँ?",
    "दो दुकानों के लिए कीमत क्या है?",
    "क्या आप कल का डेमो बुक कर सकते हैं?",
    "Meri 3 stores hain, kaise start karun?",
    "Price thoda high hai, koi discount hai kya?",
    "Stock mismatch aa raha hai, demo mil sakta hai?",
)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="*", default=MODELS)
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()
    models = args.models
    key = dotenv_values(".env").get("GEMINI_API_KEY")
    if not key or key.startswith("replace_with_"):
        raise SystemExit("Enter GEMINI_API_KEY in the local .env first.")
    stats: dict[str, list[float]] = {model: [] for model in models}
    async with httpx.AsyncClient(timeout=14, trust_env=False) as client:
        for index, prompt in enumerate(PROMPTS[: args.count]):
            for model in models[:: 1 if index % 2 == 0 else -1]:
                started = perf_counter()
                first = None
                parts = []
                try:
                    async with asyncio.timeout(18):
                        thinking = "off" if model == "gemini-2.5-flash-lite" else "minimal"
                        async for delta in stream_gemini(client, key, model, thinking, prompt):
                            if first is None and delta.strip():
                                first = (perf_counter() - started) * 1000
                            parts.append(delta)
                    if first is not None:
                        stats[model].append(first)
                    print(
                        json.dumps(
                            {
                                "prompt": index + 1,
                                "model": model,
                                "first_ms": round(first or 0),
                                "reply": "".join(parts),
                            },
                            ensure_ascii=True,
                        ),
                        flush=True,
                    )
                except (ProviderError, TimeoutError) as error:
                    print(
                        model, index + 1, "failed", getattr(error, "status", "timeout"), flush=True
                    )
                await asyncio.sleep(2)
    for model, values in stats.items():
        print(
            model,
            "completed",
            len(values),
            "median",
            round(statistics.median(values)) if values else None,
            "range",
            tuple(round(v) for v in (min(values), max(values))) if values else None,
        )


if __name__ == "__main__":
    asyncio.run(main())
