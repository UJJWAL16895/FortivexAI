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
        self.booked = False
        self.reservation: str | None = None
        self.pending_change: str | None = None

    def handle(self, text: str, lead: LeadSession) -> str | None:
        raw = re.sub(
            r"^(?:my (?:email|phone) is|contact|मेरा (?:फ़ोन|फोन|नंबर)|mera (?:phone|number))\s+",
            "",
            text.strip(),
            flags=re.I,
        )
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

        command = text.strip().casefold().rstrip(".!?।")
        if command == "cancel booking" and self.reservation:
            self.pending_change = "cancel"
            return "Say confirm cancellation to release your booked time."
        if command == "confirm cancellation" and self.pending_change == "cancel" and self.contact:
            if self.reservation:
                self.crm.cancel(self.contact, self.reservation)
                self.reservation = self.slot = None
                self.booked = False
            return "The booking is cancelled."
        if command == "reschedule booking" and self.reservation:
            self.slot = self.crm.offer(skip=self.reservation)
            self.pending_change = "move" if self.slot else None
            return (
                f"I can offer {label_slot(self.slot)}. Say confirm reschedule to move your booking."
                if self.slot
                else "There are no other demo times available."
            )
        if command == "confirm reschedule" and self.pending_change == "move":
            if (
                self.contact
                and self.slot
                and self.reservation
                and self.crm.move(self.contact, self.reservation, self.slot)
            ):
                self.reservation = self.slot
                self.pending_change = None
                return f"Demo moved to {label_slot(self.slot)}."
            self.slot = self.pending_change = None
            return "That time is unavailable. Your original booking stays reserved."
        if CONFIRM.fullmatch(command):
            if self.pending_change == "move":
                return "Say confirm reschedule to move your booking."
            if not self.contact or not self.slot:
                return "There is no pending demo time. Say book a demo first."
            if self.crm.book(self.contact, self.slot):
                self.booked = True
                self.reservation = self.slot
                self.pending_change = None
                return f"Demo booked for {label_slot(self.slot)}."
            self.slot = None
            return "That time is no longer available. Say book a demo for another time."

        if BOOK.search(text):
            if self.reservation:
                return f"Your demo is booked for {label_slot(self.reservation)}."
            if not self.contact:
                return "Enter a fictional email or phone number first so I can save the demo lead."
            self.slot = self.slot or self.crm.offer()
            if self.slot:
                return f"I can offer {label_slot(self.slot)}. Say confirm booking to reserve it."
            return "There are no demo times available."
        return None
