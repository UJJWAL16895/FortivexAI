from src.crm.conversation import BookingSession
from src.crm.store import CRM
from src.memory.session import LeadSession


def test_cancel_replay_and_taken_reschedule_keep_database_consistent(tmp_path):
    crm = CRM(tmp_path / "depth.db")
    session = BookingSession(crm)
    lead = LeadSession()
    session.handle("a@example.test", lead)
    session.handle("book a demo", lead)
    assert "booked" in session.handle("confirm booking", lead)
    old = session.reservation
    session.handle("reschedule booking", lead)
    contested = session.slot
    assert old and contested and old != contested
    crm.save("b@example.test", {})
    assert crm.book("b@example.test", contested)
    assert "original booking" in session.handle("confirm reschedule", lead)
    assert any(row["slot"] == old for row in crm.snapshot()["bookings"])
    session.handle("reschedule booking", lead)
    assert "Demo moved" in session.handle("confirm reschedule", lead)
    assert all(row["slot"] != old for row in crm.snapshot()["bookings"])
    session.handle("cancel booking", lead)
    assert "cancelled" in session.handle("confirm cancellation", lead)
    assert "cancelled" in session.handle("confirm cancellation", lead)
    assert [row["contact"] for row in crm.snapshot()["bookings"]] == ["b@example.test"]
