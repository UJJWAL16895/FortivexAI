"""P3-lite state scoped to an open WebSocket."""

import re
from collections import deque
from datetime import date, datetime, timedelta, timezone

from pydantic import BaseModel

from src.llm.claims import HINDI
from src.memory.details import MISHEARD_STORES, store_count, target_date

IST = timezone(timedelta(hours=5, minutes=30))
AFFIRM = {
    "yes",
    "yes correct",
    "correct",
    "that's right",
    "confirm",
    "हाँ",
    "हां",
    "सही है",
    "haan",
    "han",
    "sahi hai",
}
REJECT = {"no", "wrong", "incorrect", "नहीं", "गलत"}
RECALL = re.compile(r"\b(?:remember|what did i say|what did i tell)\b|याद", re.I)


class ConfirmableDetails(BaseModel):
    store_count: int | None = None
    target_date: date | None = None

    def spoken(self, hindi: bool) -> str:
        parts = []
        if self.store_count is not None:
            parts.append(f"{self.store_count} दुकानें" if hindi else f"{self.store_count} stores")
        if self.target_date is not None:
            if hindi:
                months = "जनवरी फ़रवरी मार्च अप्रैल मई जून जुलाई अगस्त सितंबर अक्टूबर नवंबर दिसंबर".split()
                parts.append(
                    f"{self.target_date.day} {months[self.target_date.month - 1]} {self.target_date.year}"
                )
            else:
                parts.append(f"{self.target_date.day} {self.target_date:%B %Y}")
        return (" और " if hindi else " and ").join(parts)


class LeadProfile(ConfirmableDetails):
    name: str | None = None
    company: str | None = None
    need: str | None = None
    language: str = "en"


class LeadSession:
    def __init__(self) -> None:
        self.profile = LeadProfile()
        self.pending: ConfirmableDetails | None = None
        self.awaiting_store_count = False
        self.history: deque[tuple[str, str]] = deque(maxlen=4)

    def remember(self, user: str, reply: str) -> None:
        self.history.append((user[:500], reply[:500]))

    def handle(self, text: str, *, today: date | None = None) -> str | None:
        hindi = bool(HINDI.search(text))
        current_date = today or datetime.now(IST).date()
        token = " ".join(text.strip().casefold().strip(".!?,।").replace(",", " ").split())
        if token in AFFIRM | REJECT and self.pending is not None:
            pending, self.pending = self.pending, None
            if token in AFFIRM:
                for key, value in pending.model_dump(exclude_none=True).items():
                    setattr(self.profile, key, value)
                self.awaiting_store_count = False
                return (
                    "धन्यवाद, मैंने ये बातें दर्ज कर ली हैं।"
                    if hindi
                    else "Thanks, I’ve confirmed those details."
                )
            self.awaiting_store_count = pending.store_count is not None
            return "कृपया सही जानकारी बताइए।" if hindi else "Please tell me the correct details."

        self.profile.language = "hi" if hindi else "en"
        if RECALL.search(text):
            recalled = ", ".join(
                filter(
                    None,
                    (
                        self.profile.name,
                        self.profile.company,
                        self.profile.need,
                        self.profile.spoken(hindi),
                    ),
                )
            )
            if hindi:
                return (
                    f"आपने बताया था: {recalled}।" if recalled else "अभी कोई पक्की जानकारी दर्ज नहीं है।"
                )
            return (
                f"You told me: {recalled}."
                if recalled
                else "I don’t have any confirmed details yet."
            )

        for field, pattern in (
            ("name", r"\bmy name is\s+([^.!?,;]{1,50})"),
            ("company", r"\b(?:i work at|company is|i'm from)\s+([^.!?,;]{1,60})"),
            ("need", r"\b(?:i need|we need|we want)\s+([^.!?,;]{1,80})"),
        ):
            if match := re.search(pattern, text, re.I):
                value = re.split(r"\s+and\s+", match[1].strip(), maxsplit=1, flags=re.I)[0]
                if field != "need" and value:
                    setattr(self.profile, field, value)
                elif (
                    field == "need"
                    and value
                    and not re.search(r"\d", value)
                    and store_count(value) is None
                    and target_date(value, current_date) is None
                ):
                    self.profile.need = value

        if MISHEARD_STORES.search(text):
            self.pending = None
            self.awaiting_store_count = True
            return (
                "दुकानों की संख्या साफ़ नहीं सुनाई दी। कितनी दुकानें हैं?"
                if hindi
                else ("I may have misheard the store count. How many stores did you mean?")
            )
        count = store_count(text)
        if count is None and (
            self.awaiting_store_count or (self.pending and self.pending.store_count)
        ):
            bare = re.sub(r"^(?:no|नहीं) ", "", token)
            if re.fullmatch(r"[^\s]{1,10}", bare):
                count = store_count(bare + " stores")
        details = ConfirmableDetails(
            store_count=count,
            target_date=target_date(text, current_date),
        )
        if value := details.spoken(hindi):
            if self.pending is not None:
                details = self.pending.model_copy(update=details.model_dump(exclude_none=True))
                value = details.spoken(hindi)
            self.pending = details
            self.awaiting_store_count = False
            return (
                f"मैंने सुना {value}। क्या यह सही है?"
                if hindi
                else (f"I heard {value}. Is that correct?")
            )
        if self.pending is not None:
            value = self.pending.spoken(hindi)
            return f"क्या {value} सही है?" if hindi else f"Can you confirm {value}?"
        return None
