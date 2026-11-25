# STEP-010 · Core call analysis

## Behavior

After the socket sends a reply, it enqueues a buyer turn without waiting. A worker extracts rule-based sentiment and explicit budget, authority, need and timeline signals. Pydantic validates turn and call schemas. End conversation or disconnect queues finalization. Insights shows the ordered sentiments, BANT score and reasons, booking outcome, summary, next action and a draft for manual review. The recent-call dashboard counts calls and booked calls. It depends on neither Gemini nor an external worker service.

## Evidence

- [VERIFIED] The first unit test could not import the analysis module. The implemented test verifies Hot and Cold scoring, reasons, negative sentiment and an action after booking.
- [VERIFIED] The integration test confirms that a report appears only after the socket ends, gets Hot/100 for all four explicit signals, preserves the two-turn sentiment order, and omits the fixture's raw budget number.
- [VERIFIED] Windows Python verification reported `36 passed in 4.96s` with clean secret scan, Ruff and mypy. The five-reply mock demonstration passed.
- [VERIFIED] Docker Compose returned `healthy running`. Chrome printed `Insights panel: completed booking count, report and follow-up draft verified.` The same run also checked citation, booking and returning lead.
- [VERIFIED] The first voice-tag Ubuntu run uncovered a fixture race: the second test competitor had not been added to CRM. Main now registers both competitors and separately asserts that an unknown contact cannot book. The schema still enforces one owner per slot.

## Limits

Rules recognize a small set of phrases and never verify buyer claims. Treat ratings as conversation signals for an operator. Population accuracy is NOT MEASURED. The process keeps at most 50 recent completed reports, up to 100 analyzed turns per call and a bounded queue. A report with skipped jobs is omitted, and the view reports the skipped-job count. Derived insights are in memory. CRM records and bookings persist separately. Drafts require a person to send them. The deployment uses fictional contacts and requires an access-controlled perimeter if hosted.
