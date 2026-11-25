# Architecture

[VERIFIED] The current FastAPI foundation exposes GET /health and validates configuration. [ASSUMED] The diagrams specify the proposed target architecture. Implementation and validation gates are in TASKS.md.

## System

```mermaid
flowchart LR
    B["React client: mic, transcript, playback"] <-->|Audio and events| G["FastAPI session gateway"]
    G --> S["Endpointing and STT"]
    S --> T["Turn coordinator"]
    T <--> R["RAG and cited chunks"]
    T --> L["LLM adapter: Gemini A, Gemini B, mock"]
    L --> Y["Sentence buffer and TTS"]
    Y --> G
    T --> K["Availability, booking, CRM"]
    K --> D[("SQLite")]
    T --> Q["Background work queue"]
    Q --> W["Analysis and post-call workers"]
    W --> D
    D --> I["CRM and insights API"]
    I --> B
```

## Per-turn sequence

```mermaid
sequenceDiagram
    participant B as Browser
    participant G as Gateway
    participant T as Turn coordinator
    participant M as Memory and retrieval
    participant L as Gemini chain
    participant A as Analysis worker
    participant K as Booking store
    B->>G: Audio frames and turn ID
    G->>T: Endpoint and final transcript
    T->>M: Read committed profile, recent turns and evidence
    T--)A: Enqueue extraction, scoring and sentiment
    T->>L: Bounded prompt and cited evidence
    opt Explicitly confirmed booking
        L-->>T: Proposed tool arguments
        T->>K: Validate and commit with idempotency key
        K-->>T: Committed receipt or slot conflict
    end
    L-->>T: Text deltas
    T-->>G: Speakable phrase or validated tool outcome
    G-->>B: Audio chunks tagged with turn ID
    A-->>M: Versioned profile and analysis update
    opt Barge-in
        B->>G: Interrupt and advance turn ID
        G-->>T: Cancel prior generation and synthesis
    end
```

## Data flow

```mermaid
flowchart TD
    AUDIO["Mic frames"] --> STT["Ephemeral audio buffer and STT"]
    STT --> TURN["Turn text and session ID"]
    KB["Approved bilingual company documents"] --> IDX["Chunks, source IDs and embeddings"]
    IDX --> PROMPT["Bounded prompt with citations"]
    TURN --> PROMPT
    PROMPT --> REPLY["Grounded reply or abstention"]
    TURN --> ANALYSIS["Background analysis"]
    ANALYSIS --> PROFILE["Versioned lead profile"]
    REPLY --> PLAYER["TTS and browser playback"]
    CONF["Explicit slot confirmation"] --> TX["Transactional booking and CRM upsert"]
    TX --> SUMMARY["Post-call summary and aggregates"]
    PROFILE --> SUMMARY
```

| Component | Responsibility and technology | Failure handling | Scaling direction |
|---|---|---|---|
| Browser and gateway | React/Vite, FastAPI WebSocket, IDs and bounded buffers | Drop late audio, cancel by turn, expose reconnect status | Stateless gateways with sticky active streams |
| STT and TTS | Compare Gemini and local faster-whisper for STT; Gemini and edge-tts for TTS | Configured mock, browser speech fallback, visible degraded mode | Pool warm workers and bound admission |
| Turn and memory | Read sliding window, rolling summary and structured fields | Proceed using latest committed state; order updates by turn sequence | Redis session state, durable Postgres records |
| Retrieval | Local multilingual embeddings and vector plus lexical search | Below threshold return abstention; retain source version | Independent retrieval workers and managed index |
| LLM | Stream deltas; local caching, token and time budgets | Gemini A → Gemini B → deterministic mock; shared quota cooldown where applicable | Limit by project, model and tenant |
| Booking and CRM | Validate tool args, timezone and consent; SQLite transaction | Unique slot constraint and request replay; webhook outbox | Postgres plus idempotent delivery workers |
| Background analysis | Lead score, sentiment, profile extraction, rolling summary and post-call jobs | Bound queue; retry with deduplication; preserve pending status | Durable queue and independently scaled consumers |
| Telemetry and dashboard | Per-stage timings, aggregates, provider status | Count errors and missing measurements explicitly | Structured metrics and tenant-filtered queries |

OpenAI is optional after a successful bounded credit probe and explicit fallback configuration. With current credit exhausted the standard chain is A → B → mock. Tool proposals and retrieved documents are untrusted inputs. The server owns booking authorization and generates the spoken confirmation from committed state.
