import re

from src.crm.store import CRM, label_slot, normalize_contact
from src.memory.session import LeadProfile, LeadSession

BOOK = re.compile(r"\b(?:book(?: me)? (?:a |the )?demo|schedule (?:a |the )?demo)\b|डेमो बुक", re.I)
CONFIRM = re.compile(r"\b(?:confirm(?: the)? booking|confirm(?: the)? demo)\b|बुकिंग पक्की", re.I)


class BookingSession:
    def __init__(self, crm: CRM) -> None:
        self.crm = crm
        self.contact: str | None = None
        self.slot: str | None = None

    def handle(self, text: str, lead: LeadSession) -> str | None:
        raw = re.sub(r"^(?:my (?:email|phone) is|contact)\s+", "", text.strip(), flags=re.I)
        contact = normalize_contact(raw)
        if contact:
            if self.contact and self.contact != contact:
                return "Start a new conversation before choosing a different demo contact."
            previous = self.crm.load(contact)
            fields = lead.profile.model_dump(mode="json", exclude_none=True, exclude={"language"})
            seen = self.crm.save(contact, fields)
            self.contact, self.slot = contact, None
            lead.profile = LeadProfile.model_validate(
                {**previous, **fields, "language": lead.profile.language}
            )
            name = lead.profile.name
            if seen:
                return f"Welcome back, {name}." if name else "Welcome back. I found your demo lead."
            return "I saved the demo contact. Say book a demo to see an available time."

        if CONFIRM.fullmatch(text.strip().rstrip(".!?।")):
            if not self.contact or not self.slot:
                return "There is no pending demo time. Say book a demo first."
            if self.crm.book(self.contact, self.slot):
                return f"Demo booked for {label_slot(self.slot)}."
            self.slot = None
            return "That time is no longer available. Say book a demo for another time."

        if BOOK.search(text):
            if not self.contact:
                return "Enter a fictional email or phone number first so I can save the demo lead."
            self.slot = self.slot or self.crm.offer()
            if self.slot:
                return f"I can offer {label_slot(self.slot)}. Say confirm booking to reserve it."
            return "There are no demo times available."
        return None
