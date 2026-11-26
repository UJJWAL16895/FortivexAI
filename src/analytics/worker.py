import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from src.analytics.core import TurnAnalysis, analyze_turn, summarize_call
from src.analytics.store import ReportStore


@dataclass
class Call:
    turns: deque[TurnAnalysis] = field(default_factory=lambda: deque(maxlen=100))
    booked: bool = False
    incomplete: bool = False


class Insights:
    def __init__(self, store: ReportStore) -> None:
        self.store = store
        self.jobs: asyncio.Queue[tuple[Call, str | None, asyncio.Future[dict[str, Any]] | None]] = (
            asyncio.Queue(maxsize=128)
        )
        self.dropped = 0

    def submit(
        self, call: Call, text: str | None, result: asyncio.Future[dict[str, Any]] | None = None
    ) -> None:
        try:
            self.jobs.put_nowait((call, text, result))
        except asyncio.QueueFull:
            call.incomplete = True
            self.dropped += 1
            if result and not result.done():
                result.set_result({"status": "unavailable"})

    async def work(self) -> None:
        while True:
            call, text, result = await self.jobs.get()
            try:
                if text is None:
                    if call.turns and not call.incomplete:
                        report = summarize_call(list(call.turns), booked=call.booked)
                        await asyncio.to_thread(self.store.save, report)
                else:
                    turn = analyze_turn(text)
                    call.turns.append(turn)
                    if result and not result.done():
                        report = summarize_call(list(call.turns), booked=call.booked)
                        result.set_result(
                            {
                                "status": "ready",
                                "sentiment": turn.sentiment,
                                "score": report.score,
                                "rating": report.rating,
                                "reasons": report.reasons,
                            }
                        )
            except Exception:
                call.incomplete = True
                self.dropped += 1
                if result and not result.done():
                    result.set_result({"status": "unavailable"})
                logging.getLogger("uvicorn.error").warning("A demo analysis job was skipped.")
            finally:
                self.jobs.task_done()
            await asyncio.sleep(0)
