# STEP-002 · P1 keyless text checkpoint

## Objective and plan

Prove a complete interactive text turn before introducing live providers. Write socket acceptance tests, wire the deterministic mock and console, replay three prompts over a real socket, and verify the README flow in a keyless checkout. Close the phase with a Conventional Commit and the demo-p1-text tag.

## Implemented and reviewed

[VERIFIED] React sends one JSON turn, FastAPI validates it, and a deterministic mock replies. The browser shows connection status, a transcript, example prompts and backend compute time. The same origin hosts the UI and socket. Native setup and the multi-stage image compile the locked frontend. The HTTP contract remains valid. Reviewed the staged diff for credential exposure, origin enforcement, data retention, portable commands and scope.

## Verification

| Evidence for FR-001 and NFR-001/003 | Output |
|---|---|
| Test first | The original application returned WebSocketDisconnect in the mock-turn test. `1 failed, 1 passed`. |
| Windows Make | `14 passed, 1 warning in 10.59s`. Ruff clean, mypy 7 source files clean, Vite 8.3.8 built 15 modules. |
| Fresh Windows checkout, no .env | Python setup installed the locks and built the console. Python verify returned `14 passed, 1 warning in 3.23s` and `✓ built in 472ms`. |
| Both scripted entry points | `Demo passed: 3 replies over WebSocket (mock).` Prompts covered stores, pricing and a demo request. |
| Chrome, README server in fresh checkout | `agentMessages:4, buyerMessages:3, mobileOverflow:false, compute:"0.017 ms", pageErrors:0`. Tested suggested prompts and a typed submission, then checked at 390 px. Agent count includes greeting. |
| Docker Compose | `healthy running`. The same Chrome script found three buyer turns and no page errors. |
| Architecture | Mermaid rendered `Found 4 mermaid charts in Markdown input`. |
| Secrets | `Secret scan: clean (Git index and non-ignored working tree).` Pre-commit runs the same check. |

## Decisions, risks and next gate

[VERIFIED] React/Vite built assets and the WebSocket come from one FastAPI process. That avoids a second server in the release quickstart. Messages stay in the current browser tab. The latency readout measures mock compute. Starlette emits a test-client deprecation warning for its existing HTTPX transport. The test suite and actual socket exercise both completed.

[ASSUMED] The proposed capacity, business and cost inputs remain scenarios. [UNKNOWN] Provider benchmarks, real audio latency and quality, account-level quota and end-to-end booking outcomes.

Next is the short P2 model comparison and A/B chain. Then release the thin voice path under demo-voice-thin before P3. The grounded text booking and CRM hero follows P4, with deeper voice in P5. See LEARNING_LOG.md for the five P1 questions and answers, and SUBMISSION_CHECKLIST.md for remaining evidence.
