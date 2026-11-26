from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from src.crm.live_booking import LiveBooking
from src.crm.store import CRM
from src.llm.conversation import BookingUnderstanding
from src.memory.session import IST


def proposed_time():
    return (datetime.now(IST) + timedelta(days=1)).replace(
        hour=17, minute=0, second=0, microsecond=0
    )


def test_time_first_and_decline_then_contact_first(tmp_path):
    crm = CRM(tmp_path / "a.sqlite3")
    booking = LiveBooking(crm)
    assert "time" in booking.advance(BookingUnderstanding(intent="affirm"), {})
    assert not crm.snapshot()["bookings"]
    booking.advance(BookingUnderstanding(preferred_datetime=proposed_time()), {})
    assert booking.state == "need_contact"
    booking.advance(BookingUnderstanding(intent="decline"), {})
    assert booking.state == "idle" and not booking.slots
    booking.advance(BookingUnderstanding(contact="demo@example.test"), {"name": "Demo"})
    assert booking.state == "need_time"
    booking.advance(BookingUnderstanding(preferred_datetime=proposed_time()), {})
    assert booking.state == "awaiting_confirmation"
    assert len(crm.snapshot()["leads"]) == 1 and not crm.snapshot()["bookings"]
    first = booking.advance(BookingUnderstanding(intent="affirm"), {})
    assert first == booking.advance(BookingUnderstanding(intent="affirm"), {})
    assert len(crm.snapshot()["bookings"]) == 1


def test_parallel_confirmation_and_two_nearest_alternatives(tmp_path):
    crm = CRM(tmp_path / "race.sqlite3")
    a, b = LiveBooking(crm), LiveBooking(crm)
    for booking, contact in [(a, "a@example.test"), (b, "b@example.test")]:
        booking.advance(
            BookingUnderstanding(
                intent="book", contact=contact, preferred_datetime=proposed_time()
            ),
            {},
        )
        assert booking.state == "awaiting_confirmation"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda b: b.advance(BookingUnderstanding(intent="affirm"), {}), [a, b])
        )
    assert sum(result.startswith("Demo booked") for result in results) == 1
    assert len(crm.snapshot()["bookings"]) == 1
    loser = a if a.state == "offered_slot" else b
    assert loser.state == "offered_slot" and len(loser.slots) == 2
    assert {datetime.fromisoformat(slot).strftime("%H:%M") for slot in loser.slots} == {
        "16:30",
        "17:30",
    }
    chosen = datetime.fromisoformat(loser.slots[0])
    loser.advance(BookingUnderstanding(preferred_datetime=chosen), {})
    assert loser.state == "awaiting_confirmation"
    assert "Demo booked" in loser.advance(BookingUnderstanding(intent="affirm"), {})
    assert len(crm.snapshot()["bookings"]) == 2
