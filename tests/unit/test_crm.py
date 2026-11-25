from concurrent.futures import ThreadPoolExecutor

from src.crm.store import CRM, normalize_contact


def test_unique_slot_idempotent_confirmation_and_reopen(tmp_path):
    path = tmp_path / "crm.sqlite3"
    store = CRM(path)
    a = normalize_contact("Asha@EXAMPLE.COM")
    b = normalize_contact("+91 98765 43210")
    assert a == "asha@example.com" and b == "+919876543210"
    assert store.save(a, {"name": "Asha"}) is False
    assert store.save(a, {"store_count": 3}) is True
    slot = store.offer()
    assert slot
    with ThreadPoolExecutor(2) as pool:
        receipts = list(pool.map(lambda contact: store.book(contact, slot), [a, b]))
    assert sum(receipts) == 1
    winner = a if receipts[0] else b
    assert CRM(path).book(winner, slot)
    assert len(CRM(path).snapshot()["bookings"]) == 1
    assert CRM(path).load(a) == {"name": "Asha", "store_count": 3}
