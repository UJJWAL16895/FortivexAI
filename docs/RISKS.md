# Risk register

| Exposure | Detection | Mitigation and gate |
|---|---|---|
| Catalog access without generation quota | Real generation status; STEP-000 includes a 503 and exhausted credit | Gemini A/B circuit breakers, project cooldown, offline scripted demo |
| Analytics or long model reasoning stalls speech | Compare reply timings with artificially delayed analysis | Queue analysis and profile updates; benchmark minimal thinking at P2 |
| False affirmative booking | Concurrent confirmation or retry of stale slot | Server transaction, idempotency key, committed receipt before speech |
| Background profile regresses | Deliver turn N after N+1 in tests | Sequence-aware writes and immutable turn events |
| Secret or caller data reaches logs/build context | Canary tests, staged scan, Docker allowlist | Keep credentials local, suppress raw request/error bodies, use synthetic fixtures |
| Demo host loses an unofficial speech service | Run a failure-injected voice demo | Local/browsable fallbacks and explicit provider labels |
| Registration estimate mistaken for throughput | Compare reported active streams with measured saturation | Show workload assumptions, bottleneck and exclusions in scalability report |
| Starlette test transport deprecation | Pytest escalates Starlette deprecation warnings to errors | Pin Starlette, httpx2 and its transport in requirements.lock. P2 installs httpx2 so TestClient uses the supported transport. Recheck warnings and both CI platforms on upgrades. |
| Live voice waits on cloud transcription | Record stop-to-playback and STT delay in the browser | Preserve the keyless audio fixture and text entry. P5 tests streaming STT and endpointing against the first-audio target. |
