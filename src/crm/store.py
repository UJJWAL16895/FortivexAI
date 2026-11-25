"""SQLite is the authority for lead identity and the demo slot claim."""

import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

from src.memory.session import IST

EMAIL = re.compile(r"[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", re.ASCII)


def normalize_contact(raw: str) -> str | None:
    value = raw.strip().casefold()
    if len(value) <= 160 and EMAIL.fullmatch(value):
        return value
    if re.fullmatch(r"\+?[0-9() -]+", value):
        phone = re.sub(r"\D", "", value)
        if 10 <= len(phone) <= 15:
            return "+" + (("91" + phone) if len(phone) == 10 else phone)
    return None


def label_slot(slot: str) -> str:
    return datetime.fromisoformat(slot).strftime("%d %B %Y at %H:%M IST (UTC+05:30)")


class CRM:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS leads (
                    contact TEXT PRIMARY KEY, profile TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bookings (
                    slot TEXT PRIMARY KEY,
                    contact TEXT NOT NULL REFERENCES leads(contact)
                );
            """)

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=4)
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def save(self, contact: str, profile: dict[str, object]) -> bool:
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute(
                "SELECT profile FROM leads WHERE contact=?", (contact,)
            ).fetchone()
            fields = json.loads(previous[0]) if previous else {}
            fields.update(profile)
            db.execute(
                "INSERT INTO leads VALUES (?, ?) ON CONFLICT(contact) DO UPDATE SET profile=excluded.profile",
                (contact, json.dumps(fields, ensure_ascii=False)),
            )
            return previous is not None

    def load(self, contact: str) -> dict[str, object]:
        with closing(self.connect()) as db:
            row = db.execute("SELECT profile FROM leads WHERE contact=?", (contact,)).fetchone()
            return dict(json.loads(row[0])) if row else {}

    def offer(self) -> str | None:
        now = datetime.now(IST)
        with closing(self.connect()) as db:
            occupied = {
                row[0]
                for row in db.execute("SELECT slot FROM bookings WHERE slot>=?", (now.isoformat(),))
            }
        for offset in range(1, 8):
            day = (now + timedelta(days=offset)).replace(minute=0, second=0, microsecond=0)
            for hour in (11, 15):
                slot = day.replace(hour=hour).isoformat()
                if slot not in occupied:
                    return slot
        return None

    def book(self, contact: str, slot: str) -> bool:
        if datetime.fromisoformat(slot) <= datetime.now(IST):
            return False
        with closing(self.connect()) as db, db:
            db.execute(
                "INSERT INTO bookings SELECT ?, contact FROM leads WHERE contact=? "
                "ON CONFLICT(slot) DO NOTHING",
                (slot, contact),
            )
            owner = db.execute("SELECT contact FROM bookings WHERE slot=?", (slot,)).fetchone()
            return bool(owner and owner[0] == contact)

    def snapshot(self) -> dict[str, list[dict[str, object]]]:
        with closing(self.connect()) as db:
            leads = [
                {"contact": key, **json.loads(profile)}
                for key, profile in db.execute(
                    "SELECT contact, profile FROM leads ORDER BY contact"
                )
            ]
            bookings = [
                {"contact": key, "slot": slot, "label": label_slot(slot)}
                for slot, key in db.execute("SELECT slot, contact FROM bookings ORDER BY slot")
            ]
        return {"leads": leads, "bookings": bookings}
