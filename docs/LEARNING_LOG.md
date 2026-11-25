# Learning log

## Multilingual quiz

1. **Is Roman Hindi detected as a complete language?** The demo recognizes a small set of patterns and uses English wording for the tested Roman query.
2. **Can a session switch scripts?** Yes. The test keeps one socket open and checks all three styles.
3. **How do two phone scripts match?** Unicode decimal digits are normalized to ASCII before storage.
4. **What happens on “kal”?** No date is guessed.
5. **What still needs a manual change in voice mode?** Set the microphone language hint when switching.

## Persistence quiz

1. **Where is a report stored?** In SQLite, in the call_reports table.
2. **What is saved for each turn?** Its derived sentiment label in the report, with the raw text left out.
3. **What is the booking rate?** Booked analyzed calls divided by all successfully saved analyzed calls.
4. **Does opening an empty socket count?** No. It produces no analyzed turn.
5. **Does the 50-report panel cap limit the denominator?** No. The SQL count queries all saved reports.

## Core analysis quiz

1. **When is analysis submitted?** After the reply. A queue lets the socket hand off work immediately.
2. **What is a BANT signal?** A buyer statement that gives evidence about budget, authority, need or timeline.
3. **What checks the data shape?** Pydantic schemas validate each turn and the completed call.
4. **When does the report appear?** When the socket ends and the worker reaches its finalization job.
5. **What happens to a draft follow-up?** The console displays it for a person to review. The app sends nothing.

The voice checkpoint reuses the text path after transcription. Its five-question quiz and run details are in STEP-009.

## Text hero quiz

1. **What gives a returning demo lead the same record?** The normalized phone or email is its SQLite key.
2. **What reserves a time?** The exact confirmation after an offer. A general yes does not reserve it.
3. **What prevents double-booking?** SQLite allows one row per time slot.
4. **What if a confirmation is repeated?** The existing owner receives the same receipt.
5. **What does the CRM panel read?** A snapshot of saved fictional leads and bookings from the backend.

## P4 quiz

1. **What is a chunk?** One short, reviewed answer card with an ID, a topic and bilingual wording.
2. **Where do prices come from?** The selected pricing card. Gemini does not write the price answer.
3. **How does the optional local model help?** It compares meaning when the question uses different words.
4. **What happens on a weak match?** The app offers specialist follow-up without citing a card.
5. **What happens if a document changes?** The digest no longer matches, so the app skips that file until review.

## P0 · Configuration and trust boundaries

A credential can authenticate a model listing while generation still fails. STEP-000 demonstrates that distinction with a successful OpenAI listing followed by exhausted generation credit. This makes a real completion probe essential for choosing a live provider.

Read src/core/settings.py first. Configuration is validated before FastAPI accepts requests. src/api/app.py exposes only status and mode, so inspecting health does not reveal the underlying settings. Read scripts/secret_scan.py next. Git stores a staged snapshot and a working copy separately. Cleaning the working file does not remove leaked bytes already staged for commit.

Common mistakes include treating a catalog listing as proof of available credit, putting secrets in URLs, and timing only text generation when a user waits for audio. The architecture starts analysis in the background so it can finish after the spoken response.

Exercise: in a disposable checkout run the settings and staged-leak tests individually. Change the health response model locally and observe the contract test fail. Explain what a live HTTP 200 proves and which provider checks still need real network evidence.

## P0 quiz

1. **What starts the API?** Uvicorn calls create_app, which validates settings and registers routes.
2. **Why use SecretStr?** Common representations mask the value and the adapter can explicitly unwrap it when needed.
3. **Why scan the Git index?** It contains the bytes that go into the commit, even after the working file has changed.
4. **Why test the OpenAPI document?** It catches drift between the published HTTP contract and the running route definition.
5. **What does a green health response prove?** The local process can answer requests and expose its configured mode.

## P1 · A browser conversation over one connection

Read frontend/src/main.jsx, src/api/text_session.py and src/llm/mock.py in that order. The input becomes JSON, FastAPI validates it, and the mock replies with predictable text. The browser keeps a transcript and displays the reply compute time it receives from the server. A WebSocket stays open across messages, so the three-turn demo can use one connection.

Serving the built assets and the socket from FastAPI makes the URL and origin easy to explain. Vite compiles the UI during setup and verification. A common mistake is to call the compute time a user's waiting time. The timer covers the mock function and excludes travel and display. Try adding one fictional mock branch and one scripted question proving that branch.

### P1 quiz

1. **What makes Send available?** The socket sent ready, there is nonblank input, and a prior reply is not pending.
2. **Where are the length and shape validated?** TextTurn in src/api/text_session.py validates the JSON after the frame is decoded.
3. **What happens after malformed JSON?** The handler sends an error and continues reading on the same socket.
4. **Which file makes a reply deterministic?** src/llm/mock.py selects a fixed response from the text.
5. **What is shared by the browser and CLI demo?** Both connect to /ws/text and use the same ready, turn and reply protocol. The demo checks expected words in three replies.

## P2 · Stream a reply and switch providers safely

Read src/llm/gemini.py, src/llm/reply.py and src/llm/sentences.py. Gemini yields text as it arrives. A small buffer emits complete speakable sentences and keeps an unfinished fragment until later chunks arrive. The next provider can take over before visible output. An interrupted partial turn ends with an error because replaying it can duplicate words that were already spoken.

A token bucket refills at a fixed rate. Each outbound request spends one credit. The rolling counters also cap attempted requests and estimated prompt volume. These counters are process-local limits, not readings from Google. Try changing a simulated error or splitting 12.50 across three chunks in a test.

### P2 quiz

1. **What marks Gemini's first visible text?** The first nonblank candidate text part without the thought flag.
2. **Why keep incomplete sentences?** Splitting at every chunk can cut words or decimals and make speech sound unnatural.
3. **When can B take over?** After A fails before visible text, provided the shared request budget allows B.
4. **How does the UI distinguish a fallback?** Provider events show outcomes, and each completed transcript message retains its LIVE or MOCK label.
5. **What does the failure button send to Gemini?** Nothing. It injects failures before the HTTP adapter.

## Thin voice · Turn a recording into a spoken reply

Read frontend/src/voice.js, src/api/voice.py and src/voice/gemini.py. Record ends at a clear button press. The browser resamples to mono 16 kHz PCM so both the API and tests have a predictable format. The text returned by STT goes through the same WebSocket path as typed input. Each sentence is queued for playback as it arrives. Ordering keeps the second sentence from interrupting the first. Try changing one bundled mock sentence and testing its audio mapping.

### Thin voice quiz

1. **What stops capture?** The Stop button or the 12-second timer, followed by release of the input tracks.
2. **What does the server validate?** MIME type, bounded byte count, WAV header, mono format, 16-bit depth, 16 kHz rate and complete frames.
3. **When can synthesis begin?** When a complete sentence event arrives, while the final reply may still be streaming.
4. **What is audible without credentials?** Bundled synthetic mock clips corresponding to the fixed mock transcript and reply.
5. **What starts the thin latency clock?** The recorder's stop event. Final-voiced-sample timing and barge-in arrive in P5.

## Voice latency · Move the expensive stage closer

Cloud transcription took most of one earlier turn. The warm laptop can now read the WAV first. If one transcriber fails, the next gets the same bytes. Read src/api/voice.py and src/voice/local.py. The server checks every candidate sentence against a reviewed list while retrieval is being built. Read src/llm/claims.py and the invented-discount regression test. A short bundled clip can be faster than asking a remote synthesizer to read the same sentence again. Read frontend/src/voice.js.

Try switching the local language to Hindi, then simulate the primary STT failure in the integration test. Keep model first-text timing separate from the first approved sentence and from actual playback.

### Five questions on P2 and voice

1. **What happened to the original bottleneck?** The original sample spent 8.75 s on cloud STT. Warm local English STT took 0.55–1.21 s in three final browser runs.
2. **How can a single STT failure keep the same turn alive?** The server already has the bounded WAV and sends those same bytes to the backup engine.
3. **Which text reaches TTS?** Only reviewed sentences or the fixed offer to check with a human. Raw model text cannot reach the player.
4. **Why can first model text and audio start differ?** The first model chunk may be incomplete or unsafe. The browser waits for a checked sentence and playable audio.
5. **Why keep Gemini Live out for now?** Its raw audio was faster in the probe, but it would speak before our current claims gate could check the words.

## P3-lite · Remember a little and confirm what matters

Read src/memory/session.py and src/memory/details.py. History is like a small desk tray that holds the last four exchanges. The lead profile is a separate note with confirmed facts. A number or date goes on a scratch pad first. The user hears it and confirms it before it goes into the profile. Both structures belong to one open socket. Try a count correction and then ask the agent to read back the profile.

### P3-lite quiz

1. **What happens to older turns?** A four-entry deque drops the oldest completed pair. Confirmed profile fields remain on the same socket.
2. **What if STT hears “free stores”?** The agent asks the caller for the count and stores no guessed value.
3. **When does a date become part of the profile?** After the agent reads back a calendar date and the caller affirms. A correction is read back again.
4. **Why use Small for English?** It recognized “three stores” in all three runs of the problem fixture. Base misheard it in all three. Small used more CPU time.
5. **What happens with no local weights?** Startup says which weights are unavailable, and the same recording can go to Gemini Transcribe.
