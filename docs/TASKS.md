# Delivery gates

Only advance after the current acceptance checks, report, learning log and commit. Freeze the commit of each tagged checkpoint and record its SHA, tag, setup commands and demo evidence in the corresponding report. Tags are release actions at the named checkpoints.

At every phase boundary keep main runnable from a fresh checkout. Exercise README quickstart and align docs/SUBMISSION_CHECKLIST.md with current evidence. Map each acceptance test to a numbered PRD requirement and add five phase questions with answers to the learning log.

Core brief checkpoints are recorded in STEP-007 through STEP-010. Park further voice-latency tuning after the accepted Hindi median from STEP-006. Protect the complete journey before adding webhook adapters, rescheduling or polish.

| Gate | Deliverable and acceptance evidence |
|---|---|
| P0 · Foundation | Read STEP-001 for Windows Make/Python parity, keyless liveness, staged secret scanning, type checks, schema validation, architecture and limitations. |
| P1 · Offline text checkpoint | React/Vite → WebSocket → deterministic LLM mock → transcript. Implement make demo and Python equivalent with the same scripted turns. Test fresh checkout without API keys, start UI, run demo, verify, tag **demo-p1-text**. |
| P2 · Live reply path | Compare 2–3 catalog Flash/Lite models with about 10 matched English, Hindi and Hinglish prompts per model. Verify minimal thinking settings. Put first-text latency, quick quality checks, errors and limitations in one table; choose A and B. Exercise A → B → mock, bounded retries/jitter, token bucket, project cap, cache and UI status. Use mock on shared quota exhaustion. OpenAI requires usable credit and explicit enablement. |
| Thin voice · After P2 | Browser mic → STT → LLM → TTS → playback. STEP-004 records English/Hindi samples, measured delay, errors, quick quality and free-tier status. Verify the thin flow and tag **demo-voice-thin** before P3. |
| Voice latency · Before P3 | Time endpoint, transfer, STT, first model text, synthesis and playback. Compare identical English/Hindi clips, exercise both STT failover directions, block unsupported claims and compare against the thin checkpoint. Record STEP-005 and refresh interview docs. |
| P3-lite · Session memory | Four-turn sliding window and structured lead profile on one socket. Read back extracted counts and dates before committing. Validate correction, recall, session isolation, both Whisper startup loads and missing-model Gemini fallback. See STEP-006. |
| P4 · RAG | Chunk versioned bilingual fictional documents. Cite evidence, say “I don't have that information” on weak retrieval and offer human follow-up. Test supported and unsupported pricing, discounts and product claims as well as citation integrity and prompt injection. |
| Early hero · Text booking and CRM | After grounding, run text inquiry → cited reply → explicit booking → persisted SQLite CRM update. Verify idempotency and conflicts, then tag **demo-text-hero**. Run the same journey over voice before prioritizing sentiment, lead score and summary. |
| Early hero · Voice booking and CRM | Run the tagged text business journey through the existing push-to-talk path, with number/date readback and a persisted booking and CRM record. Keep a deterministic fixture. Tag **demo-voice-booking-crm** after this journey passes. |
| P8–P9 · Core analysis after hero | Add schema-checked sentiment, lead score and call summary. Keep extraction and analysis off the spoken reply path. Verify escalation and post-call output against fixtures. |
| P5 · Voice depth | Add endpointing, sentence TTS streaming and interruption. Exercise physical browser mic and playback separately and re-measure the first-audio budget. |
| P6 · Languages | Test Hindi, English and Hinglish turn switches, native and Roman scripts, configured voice, contact and number handling. |
| P7 · Tool depth | Extend the released booking flow with reschedule, cancel, timezone transitions, concurrent requests and an opt-in webhook adapter with delivery deduplication. |
| P8–P9 · Analysis depth | Measure richer BANT, sentiment trend and post-call insights. Verify schema recovery, deduplication, late updates, draft follow-up and dashboard aggregates. Add durable jobs only when needed. |
| P10 · Full hero | Extend the early hero with qualification, sentiment change, follow-up and insights. Automated end-to-end test plus consented or synthetic recorded run. |
| P11 · Reliability and polish | UI polish and animations after usability; reduced-motion support. Exercise cancellation, slow providers, disconnection, redaction and overload. |
| P12 · Operational case | Finish load test, deployment, SECURITY, COSTS, SCALABILITY and BUSINESS_CASE reports. Distinguish 100,000 registered users from concurrent sessions and show capacity math, measured bottleneck, sourced prices, retention and migration. |
| P13 · Interview | Verify every code-navigation and live-edit recipe; rehearse demo and fallback, 60-second pitch and 40 project-specific Q&As. |

## Voice comparison gate

[ASSUMED] Use identical consented or synthetic English and Hindi inputs for both STT engines and identical TTS scripts for both synthesizers. Include a price, date and store name. Summarize latency, actual errors, quick transcript or pronunciation checks and sample limits in one table. P5 adds streaming, barge-in and browser-measured first audio. Mark missing measurements [UNKNOWN].

Capture dated official free-tier terms for each cloud candidate and check actual project access. Local STT has hardware costs. edge-tts is an **unofficial demo-only dependency** that connects to the Edge online service. Treat its availability and production terms as unverified. Keep Gemini Live outside the main demo path. [edge-tts source](https://github.com/rany2/edge-tts) · [faster-whisper source](https://github.com/SYSTRAN/faster-whisper)
