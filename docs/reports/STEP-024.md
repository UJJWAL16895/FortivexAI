# STEP-024 · LIVE booking, sentiment, guardrail and sales fixes

The rollback is pre-booking-fix at 4f11dfe. Changes are on booking-sentiment-fix. Main remains on the prior checkpoint because the bounded real LIVE smoke did not finish Transcript B.

## Reproduction before application edits

| Bug | Fault location and reason | Observed red replay |
|---|---|---|
| Booking | src/api/conversation.py, live_turn dispatched writes only when the model labeled the message booking. The legacy BookingSession.handle did not parse a preferred date/time. A generated acknowledgment could escape without a row. | Model said it saved the phone, asked for email and then said the time was noted. SQLite held zero bookings. The first replay also reached its local burst limit at confirmation. Subsequent fixture runs replenish only the test bucket. |
| Sentiment | src/analytics/core.py, analyze_turn defaulted unmatched text to Neutral. src/analytics/worker.py used it on LIVE and MOCK. | Transcript B showed Neutral then Neutral. |
| Duplicate follow-up | src/api/conversation.py, live_turn joined the output of check_line for each sentence. Each unsupported sentence independently became the same fallback. | A synthetic 40% annual discount question with two invented claims returned the fallback twice. Refusal was correct for that replay because the reviewed offer supports 10% on annual prepayment, not 40%. The original user's triggering message is unavailable. Existing logs omit raw turns. |
| Sales flow | src/llm/conversation.py, LiveDraft and src/api/conversation.py, live_turn had no structured sales signal or policy step. | Transcript B returned the cited fact and a generic acknowledgment but no demo offer. The decline got no gentle question. |

The first targeted run reported 4 failed. The implementation replaces rejected replies once before speech. Gemini emits booking understanding, BANT, sentiment and buying signal with the existing conversation draft. A validation error gets one correction attempt within the existing provider budget. The async worker publishes and persists the validated result after replying. This avoids a second Gemini call per normal turn. The legacy MOCK rules are visibly labeled.

## Real LIVE smoke

[VERIFIED] One isolated server and database, with a hard cap of 12 provider requests. Transcript B was resumed once on a new connection within the same process after the first quota result. Final budget counter was **8/12**. The synthetic phone is a reserved fictional number. The status, label, score and confidence below are the values delivered to the badge.

| Buyer | Observed reply | First model text | Analysis |
|---|---|---:|---|
| book a demo | What phone number or email should I use for the demo? | 2741.27 ms | Positive, 0.8, confidence 0.9 |
| Fictional phone | What date and time would suit you for the demo in IST? | 4214.97 ms | Positive, 0.8, confidence 0.9 |
| tomorrow 5 PM | I can offer 27 November 2026 at 17:00 IST (UTC+05:30). Would you like me to reserve it? | 3242.87 ms | Positive, 0.8, confidence 0.95 |
| Confirm booking | Demo booked for 27 November 2026 at 17:00 IST (UTC+05:30). | 1585.14 ms | Positive, 0.9, confidence 0.95 |
| i dont want to buy | Live quota reached, using mock | — | Not analyzed |
| i dont want to buy, bounded recovery | Live model unavailable, switching to mock. A returned application timeout code 504 and B returned 503. | — | Not analyzed |
| ok i change my mind and i am too happy to buy with the 10 percent discount | NOT MEASURED with Gemini. The turn was omitted after the socket reverted to mock. | — | Not analyzed |

CRM returned one lead for the fictional phone, need “demo”. Bookings returned the same contact with slot `2026-11-27T17:00:00+05:30`. The sales replay is verified offline only. The assistant did not request a second contact in Transcript A. Timing is first model text, not end-to-end audio. Four successful booking turns do not establish typical latency or classification accuracy.

## Remaining limits

- Live intent and sentiment depend on the provider. Confidence is model-reported and calibration is NOT MEASURED. The state machine and output guard keep transaction acknowledgments server-owned, but arbitrary multilingual claim detection is NOT MEASURED.
- Availability comes from the demo SQLite calendar and a local IST schedule. There is no external calendar or notification delivery. Session state survives while that call is open. Saved leads, bookings and reports persist in SQLite.
- The real smoke used synthetic text inputs over the cockpit's WebSocket protocol. Physical mic and live browser playback are NOT MEASURED in this phase.

## Regression evidence

- [VERIFIED] The project verification passed with `68 passed`, clean secret scan and type checks, and a successful production build.
- [VERIFIED] Chrome with a fake provider observed the Pending booking card progress from contact to time to confirmation, then a committed receipt and one booking row. It rendered Negative then Positive badges for Transcript B and a cited demo offer. Browser exceptions were zero.
- [VERIFIED] Existing Chrome cockpit checks passed at 1440, 1280, 768 and 390 px. The synthetic microphone and Markdown export checks also passed.

Files that carry the behavioral changes are src/crm/live_booking.py, src/crm/store.py, src/api/conversation.py, src/api/text_session.py, src/llm/conversation.py, src/llm/reply.py and src/analytics/{core,worker}.py. The cockpit renders the additional payload in Console.jsx, CockpitPanels.jsx and CockpitRecords.jsx and includes provenance in reportExport.js. Integration replay and state-machine race coverage are in tests/integration/test_live_booking_sales.py and tests/unit/test_live_booking.py.
