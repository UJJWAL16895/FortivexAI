# Architecture

[VERIFIED] These diagrams describe the shipped application. [System SVG](diagrams/system.svg) · [Sequence SVG](diagrams/sequence.svg) · [One-page PDF](diagrams/architecture.pdf)

## System

```mermaid
flowchart LR
    B["React browser: console and scripted showcase"] <-->|"Text turns and sentence events over WebSocket"| S["FastAPI text session"]
    B -->|"Bounded WAV over HTTP"| V["FastAPI speech routes"]
    V --> STT["Whisper Small or Gemini, scripted in mock"]
    S --> M["Four-turn window and confirmed profile"]
    S --> K["Reviewed bilingual cards and optional MiniLM"]
    S --> L["Guarded Gemini A → B → mock"]
    S --> C["Explicit booking and contact recall"]
    S --> Q["Bounded analysis queue"]
    C --> DB[("SQLite")]
    Q --> DB
    B -->|"CRM and Insights HTTP reads"| API["FastAPI snapshots"]
    API --> DB
    B -->|"Approved sentences"| T["Bundled audio or speech synthesis"]
```

## Per-turn sequence

```mermaid
sequenceDiagram
    participant B as Browser
    participant V as Voice HTTP
    participant S as Text WebSocket
    participant K as Reviewed cards
    participant D as SQLite
    participant Q as Analysis queue
    opt Push to talk
      B->>V: WAV and language after Stop
      V-->>B: Transcript or typed recovery request
    end
    B->>S: Transcript or typed text
    alt Product question
      S->>K: Find a reviewed answer
      K-->>S: Exact answer and citation, or abstention
    else Explicit booking confirmation
      S->>D: Claim unique slot
      D-->>S: Committed receipt or conflict
    else General turn
      Note over S: Read back details or stream checked Gemini/mock sentences
    end
    S-->>B: Approved sentence and final data
    opt Speech
      B->>V: Request synthesis if no bundled clip
      V-->>B: Clip or browser fallback
    end
    S--)Q: Submit analysis after reply
    Q->>D: Persist validated report on call end
```

## Data flow

```mermaid
flowchart TD
    WAV["Transient audio"] --> TXT["Transcript"]
    TXT --> TURN["Turn text and socket profile"]
    CARDS["Reviewed bilingual files"] --> MATCH["Aliases and optional semantic matches"]
    TURN --> MATCH
    MATCH --> OUT["Exact answer with citation or abstention"]
    TURN --> GUARD["General model output checked before delivery"]
    OUT --> UI["Browser transcript and playback"]
    GUARD --> UI
    TURN --> CRM["Confirmed slot and contact → SQLite"]
    TURN --> ANALYSIS["Derived sentiment and BANT → SQLite on call end"]
```

| Component | Responsibility and technology | Failure handling | Scaling approach [ASSUMED] |
|---|---|---|---|
| Browser and gateway | React/Vite, FastAPI WebSocket and HTTP audio uploads | Cancel active generation on disconnect. Text stays available if mic fails. | Keep affinity on active sockets and move reconnectable state to Redis. |
| STT and TTS | Push-to-talk WAV, optional local faster-whisper, Gemini, bundled speech, edge-tts and browser playback | Try configured STT backup, type on failure, keep transcript if audio fails. | Warm GPU or managed streaming STT and capacity-limited synthesis. |
| Turn and memory | Four pairs in a socket and readback before committing numbers and dates | Ambiguous details remain pending. Contact recall is a separate SQLite operation. | Redis with expiry and tenant-scoped profile storage. |
| Retrieval and LLM | Digest-reviewed bilingual cards, aliases, optional local similarity. Gemini A → B → mock for general replies. | Weak retrieval abstains. Time and provider budget limits plus checked sentences constrain output. | Managed tenant-filtered index, quota-aware routing and safe caching. |
| Booking and CRM | Explicit confirmation, unique slot constraint, SQLite upsert | Conflict preserves the existing booking. Typed and recognized commands share the same path. | Authoritative Postgres writer, replicas for views. |
| Analysis | Bounded post-reply queue and validated derived reports | Queue saturation may drop jobs. Completed reports persist in SQLite. | Durable jobs keyed by call ID and bounded workers. |
| Public perimeter | Single-process optional HTTP and socket access code gate and quotas | Public default mock. Counters reset with the process. | Trusted proxy and distributed durable quotas before broad live traffic. |

See [Code map](CODE_MAP.md), [Scaling](SCALABILITY.md) and [Public deployment](DEPLOY_STEPS.md). OpenAI remains outside the active chain. Gemini Live is a documented probe. Browser audio is uploaded over HTTP after Stop or the recording cap.
