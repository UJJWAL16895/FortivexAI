# Explain ShelfPilot without notes

## The project in three sentences

ShelfPilot is a prototype inbound voice agent for a fictional retail inventory software vendor. It helps a buyer ask an early sales question while saving a rep from repeating the same intake conversation. Today it listens, creates a transcript and speaks a short guarded reply, with a fully local scripted demo and a live provider path.

## Follow one voice turn

| Step | Input → output | Where to look | What can fail |
|---|---|---|---|
| Capture | Microphone sound → recording chunks | frontend/src/main.jsx, toggleMic | The browser can deny permission or lack a mic. |
| End the turn | Stop click or timer → finished recording | toggleMic and frontend/src/voice.js, toWav | The buyer can stop early or leave a long silence. An energy check estimates the tail after speech. |
| Transcribe | Mono 16 kHz WAV → text | src/api/voice.py, transcribe_audio; src/voice/local.py, recognize; src/voice/gemini.py, transcribe | A model can mishear a number. A local model may be missing or a cloud request can fail. |
| Reply | Text → candidate sentences or a policy reply | src/api/text_session.py, text_session; src/llm/reply.py, ReplyPath.stream | A provider can run out of quota or invent an answer. |
| Split and check | Text chunks → approved sentences | src/llm/sentences.py, SentenceBuffer; src/llm/claims.py, APPROVED and follow_up | A chunk may end mid-word. Unknown wording is blocked. |
| Synthesize | Approved sentence → audio | frontend/src/voice.js, createPlayback; src/api/voice.py, speak_sentence | The clip can be unavailable or the speech service can fail. The browser can try its own voice. |
| Play | Audio clip → speaker output and timestamp | createPlayback, play | Autoplay policy can block audio. The transcript stays readable. |

```text
MIC → STOP → WAV → STT → TEXT → MODEL / POLICY → SAFE SENTENCE → SPEECH → SPEAKER
                                  |
                                  +---- unverified claim → offer human follow-up
```

```text
Browser -- audio upload --> FastAPI -- optional fallback --> Gemini Transcribe
Browser <== text socket ==> FastAPI -- streamed reply -----> Gemini A or B
Browser -- safe sentence -> FastAPI -- optional synthesis -> edge-tts / Gemini TTS
Browser <-- audio clip ---- FastAPI     (bundled clips play locally)
```

## Words to know

| Word | Plain meaning and analogy |
|---|---|
| STT | Speech to text. It acts like a note taker who writes what they heard. |
| TTS | Text to speech. It acts like a reader saying the note aloud. |
| LLM | A language model predicts what to say next. Think of a fast draft writer. |
| Token | A small piece of text the model processes. Think of a puzzle piece, sometimes part of a word. |
| Streaming | Pieces arrive as they are made. It is like a tap filling a cup while it is running. |
| WebSocket | An open two-way connection. It is like keeping a phone call open through several exchanges. |
| VAD and endpointing | VAD spots likely speech. Endpointing decides that the buyer has finished. It is like noticing a pause versus deciding whose turn it is. Stop is the current endpoint. |
| Latency | Waiting time between two named points. Think of ordering food and writing down when it arrives. |
| RAG | Search trusted material and give the answer writer relevant excerpts. It is like answering an open-book question. |
| Embeddings | Numbers that help compare meaning. Think of coordinates for where ideas sit on a map. |
| Vector store | A searchable index of those coordinates and their source text. It is like a library catalog organized by meaning. |
| Mock and live | A mock gives predictable rehearsal behavior. A live provider actually runs the model. Think of a practice switch versus the connected machine. |
| Fallback chain | An ordered list of backups. If one ride is cancelled, try the next available ride. |
| Rate limiting | A cap on work over time. It is like a ticket dispenser issuing a limited number per minute. |
| Caching | Reuse an earlier answer for the same safe input. Think of keeping a copy instead of going back to the printer. |
| Idempotency | Repeating the same action leaves the same result. Pressing a lift button twice requests one lift. Booking still needs this. |
| Hallucination | A model confidently gives a made-up detail. It is like a draft writer guessing a price. |
| Guardrail | Code controls what can leave the system. It acts like a checklist at the door. The current door accepts only reviewed sentences. |

## Choices and trade-offs

| Choice | Why and trade-off |
|---|---|
| Gemini Flash-Lite | A completed both ten-prompt passes and streams short replies. Its delay varies and B has failed several times. |
| Local faster-whisper plus Gemini fallback | Warm CPU transcription reduces network wait. English uses Base and Hindi uses Small. Installation, CPU cost and misheard words are real trade-offs. |
| edge-tts | Quick English/Hindi synthesis in the demo. It calls an unofficial online service with uncertain availability. Bundled approved phrases avoid repeated synthesis. |
| FastAPI | The same Python server can validate data, handle WebSockets and serve the UI. It requires a host that keeps the server running. |
| WebSocket for replies | Multiple text and sentence events arrive on one open connection. It adds connection state and reconnect handling. The audio upload and clip downloads use HTTP. |
| One server for UI and backend | One URL and one start command. A public release must protect that entry point. |
| Mock mode | Predictable rehearsal without credentials. Its transcript and replies are scripted. |
| Sentence-level TTS | The first approved sentence can play while more text arrives. We wait for safe sentence boundaries and queue clips in order. |
| Strict claims check | It prevents made-up claims from reaching either screen or speaker. The assistant has fewer possible replies until retrieval lands. |

## Built and still to build

| Built | Still to build |
|---|---|
| Typed and push-to-talk turns, keyless voice, live text, English/Hindi microphone setting | Automatic turn detection, full barge-in and robust multilingual conversation |
| Local/cloud STT fallback, first-output stage timing, guarded model output | Larger speech quality dataset, latency target under normal load and useful grounded facts |
| Exact safe phrase playback, optional live TTS, visible provider trace | Persistent memory, document retrieval, booking, CRM and post-call insights |
| Verification, Docker and HTTPS deployment guidance | Verified public deployment and production scale |

## Numbers you can defend

Measured on 26 November 2026. The first release recorded 11.82 s to playback for one live browser fixture. The final latency build gave 5.24, 1.64 and 1.61 s for three runs using the same English fixture. One final Hindi browser run gave 9.24 s. These used Chrome with a synthetic capture device on the demo laptop. Physical microphone-to-speaker lag, performance under load and conversion lift are **NOT MEASURED**. See STEP-005 for provider runs, exact clocks and sample limits.

## Say the weak points honestly

- “Cloud transcription was the biggest delay in the original browser run. I moved it to my laptop and measured the same fixture again. The reply model was the largest remaining wait in those three English runs.”
- “Faster recognition can still hear the wrong word. Base heard ‘free stores’ on a fixture that said ‘three stores.’ I kept the text visible so we can spot this.”
- “Gemini Live returned audio quickly in a probe. It would speak before our text guard could check its claims, so I kept it out of the shipped turn.”
- “The demo can offer a human follow-up. It does not send a message to a human today.”

## 60-second pitch

Retail software reps spend time answering similar first questions. ShelfPilot explores how to handle that first conversation with a buyer. The browser records a short turn and sends it to a local or cloud transcriber. FastAPI streams the reply. The server checks sentences before the browser displays or speaks them. Without evidence, the agent offers to check with a person. The same console runs with a deterministic mock, so the demo can run without provider credentials. Moving transcription onto the laptop reduced the waiting time in the test fixture. The next steps are a persistent lead profile, retrieved product knowledge and transactional booking.

## 3-minute walkthrough

1. Open the console and point out mode, provider and language. Record one short question. Show the transcript and mention that this laptop can run the first transcription locally.
2. Open CODE_MAP.md. Trace the mic button to WAV encoding, then to transcribe_audio. Show the two-provider loop and how both engines receive the same WAV.
3. Follow the transcript into text_session and ReplyPath.stream. Explain the A/B retry budget, the MOCK fallback, and why the text from a model is just a draft.
4. Open claims.py and the invented-discount test. Show that the unsafe stub never reaches the transcript or audio. Point to the phrase splitter and playback queue.
5. Show the benchmark and define the timing markers. Mention that synthetic quiet input and a few samples do not predict production throughput. Finish by describing the next memory and retrieval gates.

## 15 interview questions

1. **Who buys this?** A vendor with repeated inbound sales questions. The first demo targets a fictional inventory vendor.
2. **What is the complete flow today?** Record, transcribe, stream a guarded reply and play it back.
3. **Why two reply models?** A can fail before it outputs any visible sentence. B offers a second chance.
4. **What happens when both reply models fail?** The same socket switches to a named deterministic mock if nothing has been delivered.
5. **How do you protect prices?** Unknown queries get a fixed check-and-follow-up response. Raw model claims do not pass the reviewed sentence list.
6. **Did you call a rep?** No. The prototype offers a human follow-up.
7. **Why use HTTP for the upload?** Push-to-talk produces one bounded WAV. A simple POST is enough for that stage.
8. **Why use WebSocket for the reply?** It carries partial results and a final event on the open connection.
9. **How do you know the first sentence was ready?** The sentence buffer sees a punctuation boundary and the claim check approves the sentence.
10. **What was slowest?** Cloud STT dominated the original sample. The largest wait in the new matched English runs was the reply model.
11. **Why is Gemini Live absent from the app?** Its direct speech bypasses the current text check. The raw probe is documented.
12. **Can this run offline?** After setup the keyless scripted mode can. Live replies need provider access.
13. **What is the risk of storing a transcript?** It can contain personal information. The browser session currently keeps it in memory.
14. **How would you scale?** Measure active sockets, queue delay and provider quota first, then isolate workers and use durable data services.
15. **What can you change live?** Edit one reviewed sentence or mock branch, update its expectation and run verification.
