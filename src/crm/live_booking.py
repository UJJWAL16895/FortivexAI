"""Connection-local booking state. Only this class describes LIVE booking outcomes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from src.crm.store import CRM, label_slot, normalize_contact
from src.llm.conversation import BookingUnderstanding
from src.memory.session import IST

BookingState = Literal[
    "idle", "need_contact", "need_time", "offered_slot", "awaiting_confirmation", "booked"
]


@dataclass
class LiveBooking:
    store: CRM
    state: BookingState = "idle"
    contact: str | None = None
    preferred: datetime | None = None
    slots: list[str] = field(default_factory=list)
    receipt: str | None = None

    def snapshot(self) -> dict[str, object]:
        return {
            "state": self.state,
            "has_contact": self.contact is not None,
            "slots": [label_slot(slot) for slot in self.slots],
            "receipt": label_slot(self.receipt) if self.receipt else None,
        }

    def advance(self, proposal: BookingUnderstanding, profile: dict[str, object]) -> str | None:
        intent = proposal.intent
        if intent == "decline":
            if self.state not in {"idle", "booked"}:
                self.state = "booked" if self.receipt else "idle"
                self.preferred, self.slots = None, []
                return (
                    "No problem. I’ll keep your existing appointment."
                    if self.receipt
                    else "No problem. I won’t reserve a time."
                )
            return None
        if self.state == "booked" and intent == "affirm" and not proposal.preferred_datetime:
            return self.confirmation()
        if (
            self.state == "booked"
            and intent not in {"book", "change"}
            and proposal.preferred_datetime is None
        ):
            return None

        if proposal.contact:
            contact = normalize_contact(proposal.contact)
            if contact is None:
                return "Please provide a valid phone number or email address."
            if self.contact and contact != self.contact:
                return "Start a new call before changing the booking contact."
            if not self.contact:
                self.store.save(contact, profile)
                self.contact = contact

        if proposal.preferred_datetime is not None:
            preferred = proposal.preferred_datetime
            if preferred.tzinfo is None or preferred.utcoffset() != IST.utcoffset(None):
                return "Please give the appointment date and time in IST."
            preferred = preferred.replace(second=0, microsecond=0)
            if preferred <= datetime.now(IST):
                return "Please give me a future date and time in IST."
            self.preferred = preferred
            self.slots = []

        if self.state == "idle" and not (
            proposal.contact
            or proposal.preferred_datetime
            or intent in {"book", "affirm", "change"}
        ):
            return None
        if self.state == "booked" and intent == "book" and proposal.preferred_datetime is None:
            return self.confirmation()
        if (
            self.state == "awaiting_confirmation"
            and intent == "affirm"
            and not proposal.preferred_datetime
        ):
            assert self.contact and len(self.slots) == 1
            slot = self.slots[0]
            committed = (
                self.store.move(self.contact, self.receipt, slot)
                if self.receipt
                else self.store.book(self.contact, slot)
            )
            if committed:
                self.receipt, self.state, self.slots = slot, "booked", []
                return self.confirmation()
            self.slots = []
        if not self.contact:
            self.state = "need_contact"
            return (
                "What phone number or email should I use for the demo?"
                if intent != "affirm" or self.preferred
                else "What date and time would suit you in IST? I’ll also need a phone number or email."
            )
        if not self.preferred:
            self.state = "need_time"
            return "What date and time would suit you for the demo in IST?"
        if self.slots and not proposal.preferred_datetime:
            if self.state == "offered_slot":
                return "Which of the offered times would suit you?"
            return None

        preferred_slot = self.preferred.isoformat()
        self.slots = self.store.available_near(self.preferred)
        if not self.slots:
            self.state = "need_time"
            return "I couldn’t find an open slot near that time. What other date works for you?"
        if self.slots != [preferred_slot]:
            self.state = "offered_slot"
            alternatives = " or ".join(label_slot(slot) for slot in self.slots)
            return f"That time is unavailable. I can offer {alternatives}. Which time would you prefer?"
        self.state = "awaiting_confirmation"
        return f"I can offer {label_slot(preferred_slot)}. Would you like me to reserve it?"

    def confirmation(self) -> str:
        assert self.receipt is not None
        return f"Demo booked for {label_slot(self.receipt)}."
