"""Only release a reviewed passage plus a fact-free conversational sentence."""

import re

from src.llm.claims import HINDI

HOW = re.compile(r"\bhow (?:does|do|can|to)\b|कैसे|\bkaise\b", re.I)
FOLLOW_UP = (
    "Would you like to talk through your setup?",
    "Would you like to explore that in a demo?",
)
FOLLOW_UP_HI = ("क्या आप अपने सेटअप के बारे में बात करना चाहेंगे?", "क्या आप इसे डेमो में देखना चाहेंगे?")


def grounded_options(passage: str) -> tuple[str, ...]:
    questions = FOLLOW_UP_HI if HINDI.search(passage) else FOLLOW_UP
    return tuple(f"{passage} {question}" for question in questions)


def grounded_reply(draft: str, passage: str) -> str | None:
    clean = " ".join(draft.split())
    return clean if clean in grounded_options(passage) else None
