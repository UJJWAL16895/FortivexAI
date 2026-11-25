"""Measure concurrent mock WebSocket turns. Start a local mock server first."""

import argparse
import asyncio
import json
from time import perf_counter

from websockets.asyncio.client import connect


async def measure(url: str, sessions: int, turns: int) -> dict[str, object]:
    samples = []
    errors = 0
    go = asyncio.Event()

    async def session() -> None:
        nonlocal errors
        await go.wait()
        try:
            async with asyncio.timeout(40), connect(url) as socket:
                ready = json.loads(await socket.recv())
                if ready.get("mode") != "mock":
                    raise ValueError("Expected a mock server")
                for _ in range(turns):
                    sent = perf_counter()
                    await socket.send(json.dumps({"text": "How much does Growth cost?"}))
                    while (event := json.loads(await socket.recv()))["type"] != "profile":
                        if (
                            event["type"] == "reply"
                            and event.get("citation", {}).get("id") != "growth"
                        ):
                            raise ValueError("Unexpected response")
                    samples.append((perf_counter() - sent) * 1000)
        except Exception:
            errors += 1

    tasks = [asyncio.create_task(session()) for _ in range(sessions)]
    started = perf_counter()
    go.set()
    await asyncio.gather(*tasks)
    elapsed = perf_counter() - started
    samples.sort()
    return {
        "sessions": sessions,
        "complete_turns": len(samples),
        "session_errors": errors,
        "turns_per_second": round(len(samples) / elapsed, 1),
        "p50_ms": round(samples[len(samples) // 2], 1) if samples else None,
        "p95_ms": round(samples[(len(samples) - 1) * 95 // 100], 1) if samples else None,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="ws://127.0.0.1:8000/ws/text")
    parser.add_argument("--sessions", nargs="+", type=int, default=[10, 50, 125, 250])
    parser.add_argument("--turns", type=int, default=5)
    args = parser.parse_args()
    for sessions in args.sessions:
        print(json.dumps(await measure(args.url, sessions, args.turns)), flush=True)
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
