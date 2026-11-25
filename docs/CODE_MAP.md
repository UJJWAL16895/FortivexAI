# Code map · one turn

## Voice turn

| Order | When this happens | Open this function |
|---:|---|---|
| 1 | Click Record, then Stop or wait for the cap | frontend/src/main.jsx · toggleMic |
| 2 | Finish PCM WAV at 16 kHz and estimate trailing silence | frontend/src/voice.js · toWav |
| 3 | POST WAV with selected language, return a timed transcript | frontend/src/voice.js · transcribe → src/api/voice.py · transcribe_audio |
| 4 | Transcribe with the selected engine or the backup | src/voice/local.py · recognize → _recognize, or src/voice/gemini.py · transcribe |
| 5 | Send the transcript through the same socket used for a typed turn | frontend/src/main.jsx · send, then the text path below |
| 6 | Play each approved sentence in order | frontend/src/voice.js · createPlayback → play; src/api/voice.py · speak_sentence for a remote clip |

## Text turn

| Order | When this happens | Open this function |
|---:|---|---|
| 1 | Submit the typed message | frontend/src/main.jsx · send |
| 2 | Validate the frame and select the reply path | src/api/text_session.py · text_session |
| 3 | Handle unsupported claims, or try Gemini A → B → mock | src/llm/reply.py · ReplyPath.stream and _live; src/llm/claims.py · follow_up |
| 4 | Read provider SSE and split the draft | src/llm/gemini.py · stream_gemini; src/llm/sentences.py · SentenceBuffer.push |
| 5 | Display approved sentences and final provenance | frontend/src/main.jsx · client.onmessage inside App |
