import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field

from src.analytics.core import CallAnalysis, TurnAnalysis, analyze_turn, summarize_call


@dataclass
class Call:
    turns: deque[TurnAnalysis] = field(default_factory=lambda: deque(maxlen=100))
    booked: bool = False
    incomplete: bool = False


class Insights:
    def __init__(self) -> None:
        self.jobs: asyncio.Queue[tuple[Call, str | None]] = asyncio.Queue(maxsize=128)
        self.recent: deque[CallAnalysis] = deque(maxlen=50)
        self.dropped = 0

    def submit(self, call: Call, text: str | None) -> None:
        try:
            self.jobs.put_nowait((call, text))
        except asyncio.QueueFull:
            call.incomplete = True
            self.dropped += 1

    async def work(self) -> None:
        while True:
            call, text = await self.jobs.get()
            try:
                if text is None:
                    if call.turns and not call.incomplete:
                        self.recent.appendleft(summarize_call(list(call.turns), booked=call.booked))
                else:
                    call.turns.append(analyze_turn(text))
            except Exception:
                call.incomplete = True
                self.dropped += 1
                logging.getLogger("uvicorn.error").warning("A demo analysis job was skipped.")
            finally:
                self.jobs.task_done()
            await asyncio.sleep(0)
