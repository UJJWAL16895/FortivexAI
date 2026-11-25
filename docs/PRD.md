# Product requirements

[ASSUMED] The demo brand, ShelfPilot, sells inventory software to Indian retailers. A buyer comparing systems needs a trustworthy answer and a convenient next appointment. An SDR needs the buyer’s context and a follow-up task. All source material and prices for this brand will be fictional.

## Acceptance journey

1. A buyer starts an inbound call in English, Hindi or Hinglish. Show recording consent before retaining audio.
2. The buyer asks about multi-store inventory. Retrieve a passage and expose its citation in the transcript. Abstain below the calibrated threshold.
3. Remember the store count. Ask one missing qualification question. A pricing objection should affect the next conversational response and appear in the rep’s notes.
4. Offer a timezone-labelled slot. Ask for explicit confirmation. Only announce success after a transaction commits.
5. Open the CRM and see one lead with the appointment. After hang-up, review the summary, objections, score, sentiment trend and follow-up draft. The dashboard reflects the completed call once.

## Release boundaries

P0 supplies the executable foundation and contract. P1 supplies the offline text console. After P2 adds live replies, release a thin voice round trip. The early text hero adds grounded answers, booking and a local CRM. The next tagged checkpoint runs that business journey over voice with deeper streaming and interruption support.

[UNKNOWN] Buyer willingness to pay, measured conversion lift and production legal obligations. Treat commercial projections as scenarios until validated. Initial delivery targets a single-user inbound browser demo.

## Numbered acceptance criteria

Each criterion is pass/fail. Planned test names below are evidence commitments, tracked by gate in TASKS.md.

| ID | Company requirement | Pass criterion | Test or evidence |
|---|---|---|---|
| FR-001 | Functional prototype and technical walkthrough | Keyless React text reaches the deterministic provider over WebSocket and renders three expected replies. | P1 test_mock_text_turn_and_recovery, make demo, browser smoke |
| FR-002 | Real-time STT and TTS | A microphone utterance produces audible playback and barge-in stops the prior turn. | Thin voice demo and P5 voice round-trip/interruption tests |
| FR-003 | Contextual memory | A reconnected authorized contact recalls the correct prior profile after window rollover. | P3 recall and profile version tests |
| FR-004 | Multilingual communication | English, Hindi and Hinglish fixture turns match the expected reply language after a switch. | P6 code-switch fixtures |
| FR-005 | Lead qualification and sentiment | A known fixture yields the expected BANT score and sentiment trend, including a handoff on escalation. | P8 scoring, validation and escalation tests |
| FR-006 | RAG knowledge retrieval | The expected chunk is cited for answerable questions and unrelated inputs receive the no-information response. | P4 labeled source and abstention tests |
| FR-007 | Booking and CRM | Exactly one conflicting confirmation succeeds, repeat delivery leaves one lead, and cancellation or reschedule updates persisted state. | Early hero race/replay and P7 mutation tests |
| FR-008 | Summarization and insights | A completed fixture creates one accurate summary and dashboard counts match persisted fixtures. | P9 summary and aggregate tests |
| FR-009 | Complete business workflow | A recorded inbound voice run shows a cited reply, booked slot, CRM lead and post-call insights. | P10 recorded run and automated hero |
| NFR-001 | Individual source, runnable MVP and architecture | Public source, documented system/sequence/data flow and fresh-checkout quickstart pass at every phase boundary. | Submission checklist, CI and release smoke |
| NFR-002 | Real-time responsiveness | Report p50 and p95 from last voiced sample to first audio against 2.0 s and 3.5 s targets; delayed analytics do not delay the reply. | P2 time-boxed model probe and P5 timing/isolation tests |
| NFR-003 | Security and resilience | Verify ignores and scans credentials, cross-origin browser sockets fail, and injected Gemini failures reach the mock path. | P0 staged scan tests, P1 origin test, P2 failure injection |
| NFR-004 | 1,00,000-user scalability and infrastructure | Document demand math, runnable deployment and a load run with a measured bottleneck. | P12 load and deployment report |
| NFR-005 | Commercial feasibility and operational cost | Present cost inputs with sources or explicit assumptions and a buyer ROI sensitivity model. | P12 business and cost review |
| NFR-006 | Live coding and debugging | Rehearse a documented code change, repair a representative failure, run verification and answer phase quizzes. | Phase learning logs and P13 rehearsal |
