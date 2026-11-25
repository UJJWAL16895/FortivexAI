# STEP-006 · P3-lite and warmed voice recheck

## Objective and scope

Re-run warmed speech on the demo laptop, verify the recognition error and missing-model recovery, then ship a bounded lead profile and sliding dialogue. Keep provider and guardrail behavior reproducible. P3-lite uses connection memory and no background jobs. RAG, storage across sessions and booking remain open.

## Measured voice timing · 26 November 2026

Chrome used the same synthetic English and Hindi microphone files as the previous latency step. Ran three turns per language before P3 and three afterward, alternating languages. Times run from the manual recorder Stop event to browser playback. The target based on final voiced audio is still unverified. The energy-tail estimate was zero on these captures, which repeat the synthetic source.

| Path | English stop to playback | Hindi stop to playback | Measured stage medians |
|---|---|---|---|
| Warm demo-voice-fast rerun | 7.147, 6.180, 1.752 s; median **6.180 s** | 9.641, 5.045, 8.688 s; median **8.688 s** | EN Base STT 789 ms and first Gemini text 5217 ms. HI Small STT 2744 ms, first Gemini text 4538 ms, Edge first audio bytes 891 ms. |
| P3-lite readback, models preloaded | 1.858, 1.645, 1.669 s; median **1.669 s** | 5.153, 3.978, 3.497 s; median **3.978 s** | EN Small STT 1645 ms, first approved sentence 2 ms, bundled response 4 ms. HI Small STT 2099 ms, first approved sentence 18 ms, Edge first bytes 1164 ms. No model call for readbacks. |

[VERIFIED] Both CTranslate2 models finished loading before Uvicorn announced startup complete. App logs showed `Whisper base loaded before serving in 792 ms.` and `Whisper small loaded before serving in 1063 ms.` These are one startup on this laptop. The earlier 9.238 s Hindi run already preloaded both weights. Its 2.718 s STT was CPU inference and transcription work. The separate delay before the first approved sentence was also substantial. First raw model text was 1.347 s and the first approved sentence was 5.305 s on the reply clock. A distinct re-run still showed warmed Hindi turns near nine seconds, so cold weight loading cannot explain the result. P3 confirmation uses a local response instead of waiting for model text; Hindi still waits for a remote audio clip. The results compare changed reply paths on the same input, and do not generalize to open questions.

## English count recognition

| CPU int8 model | Problem fixture, three runs | Second English clip, three runs | Choice |
|---|---|---|---|
| Base | “free stores” 3/3, 688–765 ms | Preserved 3 stores and Friday 3/3, 679–708 ms | Available via WHISPER_EN_MODEL=base |
| Small | “three stores” 3/3, 2168–2331 ms | Preserved three stores and Friday 3/3, 2144–2363 ms | Default for English, as well as the existing Hindi choice |

[VERIFIED] Measurements used decoded PCM arrays, Ryzen 7 5800H CPU, four threads, beam size one, and an explicit English hint. The six final browser runs used Small. English read “I heard 3 stores. Is that correct?” Hindi read both 3 stores and 27 November 2026. The profile showed pending until the affirmative test turn. The earlier “free stores” transcript triggers a clarification and never sets a number. Small is slower here and the samples cover two clean synthetic clips.

## Setup, fallback and verification

- [VERIFIED] The first test-first run failed with `ModuleNotFoundError: No module named 'src.memory.session'`. The resulting tests cover numeric and date readback, standalone correction after a misheard count, history rollover, Hindi affirmation and socket isolation. The adapter test checks that prior completed turns use user/model roles in the Gemini request.
- [VERIFIED] Windows `make setup VOICE_MODELS=1` installed the optional lock and reported `Whisper base weights available.` and `Whisper small weights available.` The machine already cached both models. Ordinary setup prints the optional command, and never requires the model downloads for a mock demo.
- [VERIFIED] A live process started with an empty Hugging Face cache and offline mode. Both preload attempts warned and the API started. POSTing the same English WAV returned HTTP 200 on the first attempt, provider `gemini-3.5-transcribe`, transcript “Can I manage three stores?” and STT path time 7965 ms. This simulation left the normal model cache untouched. Integration tests inject a missing local model and exercise the reverse cloud-failure path.
- [VERIFIED] Python verification reported `28 passed in 5.12s`. Windows `make verify` reported `28 passed in 4.98s`, clean secret scan, Ruff, strict mypy and a successful Vite build. `make demo PORT=0` reported `Demo passed: 5 replies over WebSocket (mock), including lead recall.`
- [VERIFIED] Six live browser turns confirmed 3 stores, with no page errors or horizontal overflow. Docker Compose reported `healthy running`. Its browser smoke read back 3 stores in mock mode, recorded `35 ms · Bundled speech`, and committed the count after affirmation. A two-turn live socket returned both replies through Gemini A and the claims guardrail, including the turn with prior dialogue.

## Decisions and next gate

Keep up to four prior completed turns on one socket. Extract names, company and need with small explicit patterns. Only store counts and requested dates are numeric extraction fields. Keep those fields pending until affirmative confirmation. Supported dates include ISO, day and English month name, tomorrow, and weekday names, using the demo's India timezone. Corrections read back the new value, and rejection preserves earlier confirmed values. The server drops this state on disconnect. Retrieval, cross-session identity, full profile extraction and long-term storage require later work.

RAG comes next. It must cite evidence for price, discount and product claims and test the insufficient-evidence response. Build booking and CRM after retrieval, tag the verified text journey as demo-text-hero, then run it by voice before sentiment, lead score and summary. Gemini Live stays outside the main demo.
