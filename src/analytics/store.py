"""Persist completed, validated reports without recording raw speech or contact keys."""

import sqlite3
from contextlib import closing
from pathlib import Path

from pydantic import BaseModel

from src.analytics.core import CallAnalysis


class Totals(BaseModel):
    calls: int
    booked_calls: int
    booking_rate: float


class Dashboard(BaseModel):
    calls: list[CallAnalysis]
    totals: Totals
    dropped_jobs: int


class ReportStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        with closing(sqlite3.connect(path, timeout=4)) as db, db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS call_reports (
                    id INTEGER PRIMARY KEY,
                    booked INTEGER NOT NULL CHECK (booked IN (0, 1)),
                    report TEXT NOT NULL
                )
            """)

    def save(self, report: CallAnalysis) -> None:
        with closing(sqlite3.connect(self.path, timeout=4)) as db, db:
            db.execute(
                "INSERT INTO call_reports (booked, report) VALUES (?, ?)",
                (report.booked, report.model_dump_json()),
            )

    def dashboard(self, dropped: int) -> Dashboard:
        with closing(sqlite3.connect(self.path, timeout=4)) as db, db:
            db.execute("BEGIN")
            calls, booked = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(booked), 0) FROM call_reports"
            ).fetchone()
            reports = db.execute("SELECT report FROM call_reports ORDER BY id DESC LIMIT 50")
            return Dashboard(
                calls=[CallAnalysis.model_validate_json(report) for (report,) in reports],
                totals=Totals(
                    calls=calls, booked_calls=booked, booking_rate=booked / calls if calls else 0
                ),
                dropped_jobs=dropped,
            )
