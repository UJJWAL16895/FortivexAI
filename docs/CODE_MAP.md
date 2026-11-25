# Code map · one turn

## Voice turn

| Order | When this happens | Open this function |
|---:|---|---|
| 1 | Click Record, then Stop or wait for the cap | frontend/src/main.jsx · toggleMic |
| 2 | Finish PCM WAV at 16 kHz and estimate trailing silence | frontend/src/voice.js · toWav |
| 3 | POST WAV with selected language, return a timed transcript | frontend/src/voice.js · transcribe → src/api/voice.py · transcribe_audio |
| 4 | Transcribe with the selected engine or the backup | src/voice/local.py · recognize → _recognize, or src/voice/gemini.py · transcribe |
| 4a | Load cached Base and Small when live local mode starts | src/api/app.py · lifespan → src/voice/local.py · warm |
| 5 | Send the transcript through the same socket used for a typed turn | frontend/src/main.jsx · send, then the text path below |
| 6 | Play each approved sentence in order | frontend/src/voice.js · createPlayback → play; src/api/voice.py · speak_sentence for a remote clip |

## Text turn

| Order | When this happens | Open this function |
|---:|---|---|
| 1 | Submit the typed message | frontend/src/main.jsx · send |
| 2 | Validate the frame and check the current lead session | src/api/text_session.py · text_session → src/memory/session.py · LeadSession.handle |
| 2a | Parse count/date, ask for confirmation or recall existing details | src/memory/details.py · store_count and target_date; src/memory/session.py · ConfirmableDetails.spoken |
| 2b | Find a reviewed product card, cite it or abstain | src/rag/index.py · Knowledge.load and Knowledge.lookup; frontend/src/main.jsx renders citation |
| 3 | Handle unsupported claims, or try Gemini A → B → mock with recent turns | src/llm/reply.py · ReplyPath.stream and _live; src/llm/claims.py · follow_up |
| 4 | Read provider SSE and split the draft | src/llm/gemini.py · stream_gemini; src/llm/sentences.py · SentenceBuffer.push |
| 5 | Display approved sentences and final provenance | frontend/src/main.jsx · client.onmessage inside App |
| 6 | Save the completed pair, publish the profile and pending values | src/memory/session.py · LeadSession.remember; src/api/text_session.py · text_session |
| Booking | Enter a contact, request a demo time, explicitly confirm or return later | src/crm/conversation.py · BookingSession.handle → src/crm/store.py · save, offer, book |
| CRM view | Load persisted demo leads and booking receipts | src/api/app.py · crm_view → src/crm/store.py · snapshot |
