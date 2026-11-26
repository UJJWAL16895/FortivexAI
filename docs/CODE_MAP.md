# Code map · one turn

## Five-minute tour

1. Open frontend/src/Console.jsx and voice.js for console and microphone events. main.jsx chooses the route. Showcase.jsx renders the overview.
2. Open src/api/text_session.py for turn routing and disconnect cancellation.
3. Open src/rag/index.py and src/llm/reply.py for citations and provider fallback.
4. Open src/crm/conversation.py and store.py for contact recall and slot claims.
5. Open src/analytics/worker.py and store.py for saved insights and denominators.

## Voice turn

| Order | When this happens | Open this function |
|---:|---|---|
| 1 | Click Record, then Stop or wait for the cap | frontend/src/Console.jsx · toggleMic |
| 2 | Finish PCM WAV at 16 kHz and estimate trailing silence | frontend/src/voice.js · toWav |
| 3 | POST WAV with selected language, return a timed transcript | frontend/src/voice.js · transcribe → src/api/voice.py · transcribe_audio |
| 4 | Transcribe with the selected engine or the backup | src/voice/local.py · recognize → _recognize, or src/voice/gemini.py · transcribe |
| 4a | Load cached Base and Small when live local mode starts | src/api/app.py · lifespan → src/voice/local.py · warm |
| 5 | Send the transcript through the same socket used for a typed turn | frontend/src/Console.jsx · send, then the text path below |
| 6 | Play each approved sentence in order | frontend/src/voice.js · createPlayback → play; src/api/voice.py · speak_sentence for a remote clip |
| Voice hero | A recognized price question or booking command follows the same text steps below | tests/e2e/hero_browser.mjs exercises capture, transcription and playback |

## Text turn

| Order | When this happens | Open this function |
|---:|---|---|
| 1 | Submit the typed message | frontend/src/Console.jsx · send |
| 2 | Validate the frame and check the current lead session | src/api/text_session.py · text_session → run_turns → src/memory/session.py · LeadSession.handle |
| 2a | Parse count/date, ask for confirmation or recall existing details | src/memory/details.py · store_count and target_date; src/memory/session.py · ConfirmableDetails.spoken |
| 2b | Find a reviewed product card, cite it or abstain | src/rag/index.py · Knowledge.load and Knowledge.lookup; frontend/src/Console.jsx renders citation |
| 3 | Handle unsupported claims, or try Gemini A → B → mock with recent turns | src/llm/reply.py · ReplyPath.stream and _live; src/llm/claims.py · follow_up |
| 4 | Read provider SSE and split the draft | src/llm/gemini.py · stream_gemini; src/llm/sentences.py · SentenceBuffer.push |
| 5 | Display approved sentences and final provenance | frontend/src/Console.jsx · client.onmessage inside App |
| 6 | Save the completed pair, publish the profile and pending values | src/memory/session.py · LeadSession.remember; src/api/text_session.py · text_session |
| Booking | Enter a contact, request a demo time, explicitly confirm or return later | src/crm/conversation.py · BookingSession.handle → src/crm/store.py · save, offer, book |
| CRM view | Load persisted demo leads and booking receipts | src/api/app.py · crm_view → src/crm/store.py · snapshot |
| Change booking | Explicit cancellation or reschedule in the booking session | src/crm/conversation.py · BookingSession.handle → src/crm/store.py · cancel and move |
| After reply | Enqueue the turn with no wait for analysis | src/api/text_session.py · text_session → src/analytics/worker.py · Insights.submit |
| End conversation | Close the socket and enqueue finalization | src/api/text_session.py · text_session → src/analytics/worker.py · Insights.work |
| View insights | Read completed validated reports | src/api/app.py · insights_view → src/analytics/store.py · ReportStore.dashboard |
| Export call report | Create a Markdown file from the saved derived fields | frontend/src/reportExport.js · reportMarkdown and downloadReport |

**Public preview** · src/core/settings.py validates startup, src/core/public.py checks access and capacity, and the Console.jsx banner shows mode and the optional unlock form.

## Cockpit UI

- Open /console → frontend/src/Console.jsx mounts the navigation, session start, timers, drawers and controls.
- Record or Stop → toggleMic reads the analyser and updates CallPanel. voice.js → createPlayback signals when audio actually starts or ends.
- Display a turn → CockpitPanels.jsx → Conversation and ChatMessage. A citation opens the exact approved reply excerpt. A confirmed booking reply renders the receipt.
- End the call → Console.jsx → endCall sends the existing end frame and reads the existing Insights endpoint for a new saved report. The intelligence cards display the latest persisted report.
- Open workspace records → Console.jsx → openRecords fetches CRM or Insights and lazy-loads CockpitRecords.jsx.

## Connection mode

Console.jsx → chooseMode → WebSocket mode frame → text_session.py → live_mode.py / switch_mode. The handler reserves a provider request, probes Gemini in llm/gemini.py, then warms cached Whisper in voice/local.py. The resulting state belongs to the socket. The voice HTTP routes resolve X-Voice-Session to that state. ReplyPath.stream accepts the connection's mode and keeps the process-wide budget.

## Live analysis and grounded replies

text_session.py attaches the optional turn ID to the worker result after sending the reply and profile. analytics/worker.py computes the existing sentiment and BANT rules and returns a snapshot. Console.jsx applies the event to the matching buyer bubble, then CockpitPanels.jsx renders the badge, trend and score.

For product explanations, rag/index.py retrieves the card and llm/reply.py tries a short grounded selection in live mode. llm/grounded.py checks the complete output before it can reach text or speech. The citation opens the original passage.
