# Delivery gates

Only advance after the current acceptance checks, report, learning log and commit. Freeze the commit of each tagged checkpoint and record its SHA, tag, setup commands and demo evidence in the corresponding report. Tags are release actions at the named checkpoints.

| Gate | Deliverable and acceptance evidence |
|---|---|
| P0 · Foundation | Read STEP-001 for Windows Make/Python parity, keyless liveness, staged secret scanning, type checks, schema validation, architecture and limitations. |
| P1 · Offline text checkpoint | React/Vite → WebSocket → deterministic LLM mock → transcript. Implement make demo and Python equivalent with the same scripted turns. Test fresh checkout without API keys, start UI, run demo, verify, tag **demo-p1-text**. |
| P2 · Live reply path | Select 2–3 authenticated catalog Flash/Lite IDs. Verify model-specific minimal thinking and record actual request settings. Run matched, interleaved synthetic English/Hindi/Hinglish prompts with warmups, timing first non-empty visible text, first speakable phrase, total, errors and quota. Report per-model n, median and p95, sample limitations and token usage. Select A and B using quality and latency. Exercise failures A → B → mock, bounded retries/jitter, token bucket, project daily cap, cache and visible provider status. Shared project exhaustion goes straight to mock. Optional OpenAI requires usable credit and explicit enablement. |
| P3 · Memory | Maintain sliding context and last committed profile immediately; enqueue extraction, rolling summary and scoring off-path. Prove cross-session recall and out-of-order worker safety. |
| P4 · RAG | Chunk versioned bilingual fictional documents. Evaluate source hit rate, abstention, citations and prompt injection. Calibrate threshold on held-out questions. |
| Early hero · Text + booking | Pull minimal P7 forward immediately after grounding. Text inquiry → cited reply → offer → explicit confirmation → UTC slot transaction → idempotent SQLite CRM update → visible receipt. Add replay and conflicting-slot tests. Run the scripted hero before starting voice. |
| P5 · Voice + CRM checkpoint | Add endpointing, sentence TTS streaming and interruption. Run the early hero by voice over the same booking and CRM code. Mock/offline mode includes deterministic audio fixtures. Exercise browser mic and playback separately. Verify booking/CRM records, run full gates, tag **demo-voice-booking-crm**. |
| P6 · Languages | Test Hindi, English and Hinglish turn switches, native and Roman scripts, configured voice, contact and number handling. |
| P7 · Tool depth | Extend the released booking flow with reschedule, cancel, timezone transitions, concurrent requests and an opt-in webhook adapter with delivery deduplication. |
| P8 · Analysis | Enqueue sentiment, BANT and profile extraction by turn ID. Schema-validate, retry once on invalid output, apply safe unknown defaults. Test updates arriving late and natural escalation. |
| P9 · Post-call | Durable, idempotent post-call work. Render summary and proposed follow-up. Verify dashboard denominators against fixture calls. |
| P10 · Full hero | Extend the early hero with qualification, sentiment change, follow-up and insights. Automated end-to-end test plus consented or synthetic recorded run. |
| P11 · Reliability and polish | UI polish and animations after usability; reduced-motion support. Exercise cancellation, slow providers, disconnection, redaction and overload. |
| P12 · Operational case | Finish load test, deployment, SECURITY, COSTS, SCALABILITY and BUSINESS_CASE reports. Distinguish 100,000 registered users from concurrent sessions and show capacity math, measured bottleneck, sourced prices, retention and migration. |
| P13 · Interview | Verify every code-navigation and live-edit recipe; rehearse demo and fallback, 60-second pitch and 40 project-specific Q&As. |

## Voice comparison gate

[ASSUMED] Use the same consented or synthetic English and Hindi clips and human-checked transcripts for Gemini transcription vs local faster-whisper. Report corpus size, duration, WER, Hindi character error rate, numbers and names, hardware, warm/cold latency and actual errors. Compare Gemini TTS vs edge-tts with identical scripts including prices, calendar dates and store names. Record first playable byte, playback start, total synthesis time and intelligibility/pronunciation rubric per language. Human ratings require a listener and documented sample count. Mark missing measurements [UNKNOWN].

Capture dated official free-tier terms for each cloud candidate and check actual project access. Local STT has hardware costs. edge-tts is an **unofficial demo-only dependency** that connects to the Edge online service. Treat its availability and production terms as unverified. Test optional Gemini Live for free-tier eligibility and end-to-end latency using the same scripts. Adopt only with measured advantage. [edge-tts source](https://github.com/rany2/edge-tts) · [faster-whisper source](https://github.com/SYSTRAN/faster-whisper)
