"""Validated, explainable demo analysis. Raw customer wording is not retained here."""

import re
from typing import Literal

from pydantic import BaseModel, Field

Sentiment = Literal["Positive", "Neutral", "Negative"]

SIGNALS = {
    "budget": (r"\b(?:my|our) budget\b|हमारा बजट|मेरा बजट", "Buyer mentioned a budget."),
    "authority": (
        r"\b(?:i am|i'm) (?:the )?(?:owner|decision maker|founder)\b|मैं मालिक",
        "Buyer identified a decision-making role.",
    ),
    "need": (r"\b(?:i|we) (?:need|want)\b|चाहिए|ज़रूरत", "Buyer stated a need."),
    "timeline": (
        r"\b(?:this month|next week|tomorrow|by friday|next month)\b|इस महीने|अगले हफ्ते",
        "Buyer mentioned a timeline.",
    ),
}
NEGATIVE = re.compile(r"\b(?:frustrated|angry|too expensive|terrible|upset)\b|परेशान|महंगा", re.I)
POSITIVE = re.compile(r"\b(?:great|thanks|thank you|sounds good|excited)\b|धन्यवाद|बढ़िया", re.I)


class TurnAnalysis(BaseModel):
    sentiment: Sentiment
    signals: list[Literal["budget", "authority", "need", "timeline"]]


class CallAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    rating: Literal["Hot", "Warm", "Cold"]
    reasons: list[str]
    sentiment: list[Sentiment]
    booked: bool
    summary: str
    next_action: str
    follow_up_draft: str


def analyze_turn(text: str) -> TurnAnalysis:
    sentiment = (
        "Negative" if NEGATIVE.search(text) else "Positive" if POSITIVE.search(text) else "Neutral"
    )
    return TurnAnalysis.model_validate(
        {
            "sentiment": sentiment,
            "signals": [
                key for key, (pattern, _) in SIGNALS.items() if re.search(pattern, text, re.I)
            ],
        }
    )


def summarize_call(turns: list[TurnAnalysis], *, booked: bool) -> CallAnalysis:
    found = {signal for turn in turns for signal in turn.signals}
    reasons = [description for key, (_, description) in SIGNALS.items() if key in found]
    score = 25 * len(reasons)
    sentiment = [turn.sentiment for turn in turns]
    if booked:
        action = "Send the recorded demo details after human review."
    elif "Negative" in sentiment:
        action = "Ask a specialist to review the concern before following up."
    else:
        missing = next((key for key in SIGNALS if key not in found), None)
        action = f"Ask the buyer about {missing}." if missing else "Offer a demo time."
    summary = "Demo booked. " if booked else "No demo booked. "
    summary += " ".join(reasons) if reasons else "No explicit BANT signal was recorded."
    draft = "Thanks for speaking with ShelfPilot. "
    draft += (
        "A specialist can confirm your demo details."
        if booked
        else "Would you like a specialist to follow up?"
    )
    return CallAnalysis(
        score=score,
        rating="Hot" if score >= 75 else "Warm" if score >= 50 else "Cold",
        reasons=reasons,
        sentiment=sentiment,
        booked=booked,
        summary=summary,
        next_action=action,
        follow_up_draft=draft,
    )
