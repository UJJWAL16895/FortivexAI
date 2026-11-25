from datetime import date

from src.memory.session import LeadSession


def test_numbers_and_dates_require_explicit_confirmation():
    session = LeadSession()
    reply = session.handle(
        "We have three stores and need a demo on 2026-12-04.", today=date(2026, 11, 26)
    )
    assert "3 stores" in reply and "4 December 2026" in reply
    assert session.profile.store_count is None and session.profile.target_date is None
    assert session.handle("yes") == "Thanks, I’ve confirmed those details."
    assert session.profile.store_count == 3
    assert session.profile.target_date == date(2026, 12, 4)


def test_misheard_free_stores_and_correction_do_not_pollute_profile():
    session = LeadSession()
    assert "misheard" in session.handle("Can I manage free stores?")
    assert session.profile.store_count is None
    assert "3 stores" in session.handle("three")
    assert "4 stores" in session.handle("No, four.")
    assert session.profile.store_count is None
    session.handle("yes")
    assert session.profile.store_count == 4
    session.handle("We have 9 stores.")
    session.handle("no")
    assert session.profile.store_count == 4


def test_history_rolls_off_while_confirmed_profile_stays():
    session = LeadSession()
    session.handle("My name is Asha. I work at Cedar Retail. We have three stores.")
    session.handle("yes")
    for turn in range(8):
        session.remember(f"buyer {turn}", f"agent {turn}")
    assert len(session.history) == 4
    assert session.history[0] == ("buyer 4", "agent 4")
    assert session.profile.name == "Asha"
    assert session.profile.company == "Cedar Retail"
    assert "3 stores" in session.handle("What do you remember about my stores?")


def test_hindi_store_confirmation():
    session = LeadSession()
    assert "3 दुकानें" in session.handle("मेरी तीन दुकानें हैं।")
    assert session.profile.store_count is None
    session.handle("हाँ")
    assert session.profile.store_count == 3
