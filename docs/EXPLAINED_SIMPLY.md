# Explain ShelfPilot without notes

The home page introduces the journey and plays a local scripted sample. The working console lives at /console and runs the actual backend. A local fixture never spends provider quota.

Use the [40 project-specific questions](INTERVIEW_QA.md) for the full rehearsal.

## The project in three sentences

ShelfPilot is a prototype inbound voice agent for a fictional retail inventory software vendor. It helps a buyer ask an early sales question while saving a rep from repeating the same intake conversation. Today it listens, creates a transcript and speaks a short guarded reply, with a fully local scripted demo and a live provider path.

## Follow one voice turn

| Step | Input → output | Where to look | What can fail |
|---|---|---|---|
| Capture | Microphone sound → recording chunks | frontend/src/Console.jsx, toggleMic | The browser can deny permission or lack a mic. |
| End the turn | Stop click or timer → finished recording | toggleMic and frontend/src/voice.js, toWav | The buyer can stop early or leave a long silence. An energy check estimates the tail after speech. |
| Transcribe | Mono 16 kHz WAV → text | src/api/voice.py, transcribe_audio; src/voice/local.py, recognize; src/voice/gemini.py, transcribe | A model can mishear a number. A local model may be missing or a cloud request can fail. |
| Reply | Text → a readback, recalled detail, or checked model reply | src/api/text_session.py, text_session; src/memory/session.py, LeadSession.handle; src/llm/reply.py, ReplyPath.stream | A provider can fail. An unclear number requires confirmation. |
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
| Idempotency | Repeating the same action leaves the same result. Pressing a lift button twice requests one lift. Confirming the offered slot twice returns one booking. |
| Hallucination | A model confidently gives a made-up detail. It is like a draft writer guessing a price. |
| Guardrail | Code controls what can leave the system. It acts like a checklist at the door. The current door accepts only reviewed sentences. |

## Choices and trade-offs

| Choice | Why and trade-off |
|---|---|
| Gemini Flash-Lite | A completed both ten-prompt passes and streams short replies. Its delay varies and B has failed several times. |
| Local faster-whisper plus Gemini fallback | Warm CPU transcription reduces network wait. Both languages default to Small after Base misheard “three stores.” Small costs more CPU time. |
| edge-tts | Quick English/Hindi synthesis in the demo. It calls an unofficial online service with uncertain availability. Bundled approved phrases avoid repeated synthesis. |
| FastAPI | The same Python server can validate data, handle WebSockets and serve the UI. It requires a host that keeps the server running. |
| WebSocket for replies | Multiple text and sentence events arrive on one open connection. It adds connection state and reconnect handling. The audio upload and clip downloads use HTTP. |
| One server for UI and backend | One URL and one start command. A public release must protect that entry point. |
| Mock mode | Predictable rehearsal without credentials. Its transcript and replies are scripted. |
| Sentence-level TTS | The first approved sentence can play while more text arrives. We wait for safe sentence boundaries and queue clips in order. |
| Strict claims check | It prevents made-up claims from reaching either screen or speaker. This limits open-ended replies. Product answers use the reviewed cards. |

## Built and still to build

| Built | Still to build |
|---|---|
| Typed and push-to-talk turns, keyless voice, live text, English/Hindi microphone setting | Automatic turn detection, full barge-in and robust multilingual conversation |
| Warm local/cloud STT fallback, first-output stage timing, guarded model output | Larger speech quality dataset, latency target under normal load and a broader knowledge corpus |
| Four-turn memory, persistent fictional CRM leads, spoken confirmation, exact safe phrase playback and optional live TTS | Verified customer identity, production retention and durable analytics jobs |
| Cited document answers, confirmed booking and recent call insights | Broader corpus evaluation, human follow-up delivery and production analysis validation |
| Verification, Docker and HTTPS deployment guidance | Verified public deployment and production scale |

## Numbers you can defend

Measured on 26 November 2026 using Chrome with synthetic microphone input on the demo laptop. The warmed previous build had medians of 6.18 s in English and 8.69 s in Hindi over three runs per language. The P3-lite confirmation path reached median playback in 1.67 s in English and 3.98 s in Hindi over three runs each. The same inputs now produce a local readback, so these are timings for different reply paths. Physical microphone-to-speaker lag, performance under load and conversion lift are **NOT MEASURED**. See STEP-006 for individual timings.

## Say the weak points honestly

- “Cloud transcription was the biggest delay in the original browser run. I moved it to my laptop and measured the same fixture again. The reply model was the largest remaining wait in those three English runs.”
- “Base heard ‘free stores’ in three trials. Small heard ‘three stores’ in all three. I also added voice readback and an affirmative confirmation before saving a count.”
- “Gemini Live returned audio quickly in a probe. It would speak before our text guard could check its claims, so I kept it out of the shipped turn.”
- “I can offer a human follow-up in the demo. Sending a message is a later integration. The short dialogue lasts for one connection. Confirmed CRM details can be recalled by contact.”

## 60-second pitch

Retail software reps spend time answering similar first questions. ShelfPilot handles the early conversation. The browser records a short turn and the server transcribes it. The agent shows the reviewed source of each product answer, or offers to check with a specialist. It books an explicitly confirmed time and records the fictional lead in SQLite. When the call ends, the operator can read a summary and a follow-up draft in Insights. The same console has a keyless text demo.

## 3-minute walkthrough

1. Open the console and point out mode, provider and language. Record one short question. Show the transcript and mention that this laptop can run the first transcription locally.
2. Open CODE_MAP.md. Trace the mic button to WAV encoding, then to transcribe_audio. Show the two-provider loop and how both engines receive the same WAV.
3. Follow the transcript into text_session. Show the pending value, confirm it, and ask what the agent remembers. Open LeadSession and show the four-turn deque. Then trace an ordinary turn through ReplyPath.stream and the A/B fallback.
4. Open claims.py and the invented-discount test. Show that the unsafe stub never reaches the transcript or audio. Point to the phrase splitter and playback queue.
5. Ask for a Growth price, open the citation, explicitly confirm a booking and open the CRM view. End the call and open Insights. Name the limits of the small speech and retrieval samples.

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
10. **What was slowest?** Cloud STT dominated the original sample. With warmed local models, CPU transcription and remote reply or synthesis still take time. Readback can skip the model.
11. **Why is Gemini Live absent from the app?** Its direct speech bypasses the current text check. The raw probe is documented.
12. **Can this run offline?** After setup the keyless scripted mode can. Live replies need provider access.
13. **Where does memory live?** Four completed pairs and the lead profile live on one server socket. Counts and dates are pending until yes. The browser shows the profile.
14. **How would you scale?** Measure active sockets, queue delay and provider quota first, then isolate workers and use durable data services.
15. **What can you change live?** Edit one reviewed sentence or mock branch, update its expectation and run verification.

## P4 update · The answer can show its source

The text hero now adds a mailbox and a shared calendar. The mailbox key is a normalized fictional phone or email. The calendar offers a time in IST and reserves it only after “Confirm booking.” SQLite accepts a single owner per slot, like a ticket counter with one seat left. The CRM panel reads the saved lead and booking.

The voice hero ran the same journey with three synthetic microphone inputs on 26 November 2026. The tester typed the fictional contact. The browser recorded the spoken question and the two booking commands. Each turn reached playback and one booking survived reconnecting. Physical microphone performance for the hero is **NOT MEASURED**.

Think of a short stack of reviewed index cards. Each has a topic, two answers in English and Hindi, and a source label. The app looks for a clear topic match first. With the optional local multilingual model, it can also compare the meaning of a question with each card. It reads the selected answer directly and shows the citation. If the match is weak, it offers a specialist follow-up. A reviewer-approved digest prevents an edited file from entering this path.

On 26 November 2026 the authored twenty-question evaluation found 14/15 expected sources with embeddings and 12/15 with aliases alone. Both correctly abstained on 5/5 unsupported questions. Larger held-out accuracy is **NOT MEASURED**.

## Core analysis update

The operator can download the visible report as Markdown. The browser copies the derived report fields into a file.

A booking can be cancelled or moved within the session that reserved it. The server waits for an explicit confirmation. A contested move leaves the old appointment in place.

After the reply is sent, the backend drops the buyer turn on a small work queue. A worker checks simple sentiment words and explicit BANT signals. BANT means budget, authority, need and timeline. Think of four boxes a sales rep can tick when the buyer gives evidence. When the call ends, the worker creates a checked report with the score, reasons, sentiment by turn, next action and a draft. The insights panel shows completed calls. The report is a demo heuristic, and population accuracy is **NOT MEASURED**. SQLite keeps completed reports across restarts. The follow-up is a draft for a person to review.

**Public preview.** The default hosted setup uses scripted answers and no provider quota. Optional real replies require an evaluator code. A single server keeps a short request tally. It starts fresh on restart.

## Final rehearsal

The clean Windows copy passed 46 tests. Its live-mode browser run booked and saved a fictional lead with synthetic microphone audio. Three separate general prompts reached Gemini A. The reviewed-phrase filter used the policy reply for each of those prompts. Be clear about which path generated a given reply. The audit report has the command output.

## Live Call Cockpit

Think of the console as three desks. On the left, you record or choose a scenario. The orb moves with your mic level while recording, and the label says what the app is doing. In the middle, you read the conversation. A source chip opens the reviewed answer, and the booking receipt shows the confirmed time. On the right, the profile and timing change as their events arrive. End the call to see its report in Insights. The sentiment and score cards read the latest saved report. Reset starts a fresh screen and opens a new connection.

## One-click live mode

Think of the switch as a setting on your own call. When you click LIVE, the server checks its key, sends Gemini one tiny request and prepares speech recognition. The same call keeps its history and lead profile. It shows a divider once the change is confirmed. If the quota runs out, the connection moves to mock. Other tabs keep their own modes. The counter shows how many requests this server has reserved over the last 24 hours.

## Why each reply has a source label

A greeting, readback or handoff offer uses words prepared in advance and shows Scripted/approved phrase. A product or price question usually reads the reviewed Knowledge card. For a supported “how does it work” question in LIVE mode, Gemini can pick a two-sentence version. The first sentence is the approved fact and the second is a friendly question. The server checks both before speaking. If Gemini returns something different or is unavailable, ShelfPilot reads the card. General LIVE replies still go through the guardrail, and deterministic model fallback shows Mock.

The browser adds an Analyzing marker to each buyer message. When the background worker finishes, the marker becomes a sentiment label. The right column uses those actual results for its trend and cumulative BANT score. The confirmed profile still comes from the current session, and Insights holds the saved reports.
