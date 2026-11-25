# STEP-008 · Text sales hero

The sequence is a cited Growth price, fictional email, time offer, explicit “Confirm booking,” and the resulting SQLite lead and booking. A reconnect using the same normalized contact recognizes the lead. The demo tests a bare “yes” and confirms that it produces no booking.

- [VERIFIED] Windows verification reported `34 passed in 4.62s` with clean Ruff, formatting, mypy and secret scan.
- [VERIFIED] Chrome printed `Text hero: citation, timezone, one booking, one CRM lead, returning caller verified.`
- [VERIFIED] Two concurrent SQLite claims for one slot left one owner. Confirmation replay by that owner returned the same receipt with one persisted booking. Reopening the SQLite file preserved the lead.
- One demo CRM database stores fictional contact keys. Appointment offers use India time (IST, UTC+05:30). The console reads the demo CRM over HTTP. This endpoint requires an authenticated deployment perimeter and synthetic data. A contact key does not establish identity.

Next verify the same flow through microphone capture and audible replies. The isolated voice test will use a synthetic microphone and a fictional contact entered in the UI.
