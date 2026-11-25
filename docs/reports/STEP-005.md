# STEP-005 · Voice latency and claims guardrail

## Objective and plan

Measure the existing microphone-to-playback wait, compare four STT paths on identical English/Hindi fixtures, and keep the repository runnable on Windows and Docker. Run a failing discount regression before touching the reply path. Release a tag only after a measurable improvement. P3 remains the next gate.

## Per-stage browser timings · 26 November 2026

| Run | Endpoint tail estimate / PCM encode | Transfer overhead | STT | First model text | First approved sentence | TTS first output | Stop to playback |
|---|---:|---:|---:|---:|---:|---:|---:|
| Thin historic English, same synthetic browser fixture | NOT MEASURED | NOT MEASURED | 8747 ms, Gemini | 1238 ms | NOT MEASURED | NOT MEASURED | **11818 ms**, edge-tts |
| Final English 1 | 0 / 12 ms | 6 ms | 1213 ms, Base | 3991 ms | 3995 ms | 4 ms, bundle | **5237 ms** |
| Final English 2 | 0 / 8 ms | 4 ms | 545 ms, Base | 1071 ms | 1074 ms | 4 ms, bundle | **1640 ms** |
| Final English 3 | 0 / 8 ms | 4 ms | 576 ms, Base | 1005 ms | 1008 ms | 5 ms, bundle | **1605 ms** |
| Final Hindi, different fixture | 0 / 12 ms | 7 ms | 2718 ms, Small | 1347 ms | 5305 ms | 811 ms, edge-tts | **9238 ms** |
| Final direct discount-policy turn | 0 / 21 ms | 7 ms | 1272 ms, Base | No model call | 2 ms | 5 ms, bundle | **1318 ms** |

[VERIFIED] The three matched English browser runs have a **1.64 s median**, compared with a single **11.82 s** earlier run. We measured the same synthetic input and stop protocol at different times. The model run at 5.24 s and the Hindi sample show that **2.0 s is not established across languages or conditions**. The simple median of three English and one Hindi non-policy samples is about 3.44 s, an unbalanced sample. The old cloud STT dominated the original sample. First model text dominated the slow matched run. Hindi lost time in sentence completion and remote synthesis.

The endpoint is explicit Stop. Tail is a 20 ms window energy estimate on the recorded PCM; zero here means the fixture contained energy near the capture end. It does not establish zero VAD latency. Transfer is browser fetch wall time minus API processing wall time; it includes round-trip and response overhead. One-way network upload and hardware speaker lag were **NOT MEASURED**. First approved sentence is measured from WebSocket send. Edge first output is the first provider audio bytes; bundle first output is the local clip response headers. Playback means Web Audio starts the decoded source. These intervals have different clocks and boundaries, so they should not be summed indiscriminately.

## STT comparison on the same two English/Hindi clips

| Candidate | English | Hindi | Decision |
|---|---|---|---|
| Browser Web Speech, en-IN / hi-IN, interim enabled | Chrome ended without a final result; no interim | Same result; no interim | Exposed in Chrome, unsuccessful on this setup. Edge headless failed to launch. Neither timing is established. |
| faster-whisper Base, CPU int8 | 1012 ms; correct meaning | 806 ms; Urdu script from Hindi input | **English primary** on this laptop. The browser's separate fixture transcribed “three stores” as “free stores,” so speed does not imply accuracy. |
| faster-whisper Small, CPU int8 | 1850 ms; exact sentence | 2407 ms; meaning preserved in Devanagari, minor spelling differences | **Hindi primary** on this laptop. Cached load was about 1.94 s; the app warms both models at startup. |
| Gemini 3.5 Transcribe | 6181 ms and exact in first pass; 503-class failure in repeat | 6210 ms and exact in first pass; 503-class failure in repeat | **Fallback** for the warm laptop. It is the default on core-only installs. Either engine can receive the same validated WAV after the other fails. |
| Gemini 3.8 Live, free-tier eligible | 1445 ms endpoint to first audio bytes; 3379 ms from connection start | 1561 ms endpoint to first audio bytes; 2534 ms from connection start | Both input transcripts matched. This raw probe used explicit end-of-activity plus synthetic PCM. First audio bytes exclude decode and playback. The full guarded browser path was **NOT MEASURED**. Keep it experimental because direct audio bypasses the text claims check. |

One clean synthetic clip per language, explicit language hints for local engines, Windows Ryzen 7 5800H. The cloud transcribe timings use the same fixture data and the earlier two passes documented in STEP-004. Browser language-specific recognition is not a shipped fallback. If both configured STT providers fail the console preserves typed input and never invents a live transcript. Google lists free-tier audio eligibility for both cloud engines. Account billing remains [UNKNOWN]. [Pricing](https://aistudio.google.com/docs/pricing) · [Live WebSocket API](https://aistudio.google.com/docs/live-api/get-started-websocket) · [Browser recognition API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)

## Repeated Gemini A/B benchmark

| Model | Original P2 · ~01:14 IST | Controlled replay of original request | Current shorter safety prompt · ~02:26 IST |
|---|---|---|---|
| A · 3.5 Flash-Lite | 10/10, median 3919 ms | 9/10, median 2179 ms, 953–4791 ms | 10/10, median 1454 ms, 1073–2889 ms |
| B · 3.1 Flash-Lite | 2/10, median 4640 ms | 9/10, median 1014 ms, 743–7551 ms | 6/10, median 1227 ms, 1023–1997 ms |

Same ten English/Hindi/Hinglish prompts per model. The replay used the original system prompt, minimal thinking, maxOutputTokens=192 and the streaming endpoint. Medians include only completed samples. **3.9 s was not stable**, even under matched settings. Keep A first for completion consistency across runs. B remains the backup. Reproduce the controlled run with `python -m scripts.benchmark_replies --p2-prompt`. The bench calls the provider adapter directly. Its raw draft output is synthetic benchmark evidence and never enters the app's transcript.

## Verification and trade-offs

- [VERIFIED] The discount test initially failed because the output included `40%`. The new gate checks sentence text before either display or speech. Common pricing and product questions get a safe check-and-human-follow-up reply. The first unsupported model sentence stops generation and triggers the safe alternative. Human contact itself is still unimplemented.
- [VERIFIED] Both STT fallback directions receive the same WAV in integration tests. Windows Python verification reported `23 passed in 4.65s`, clean secret scan, Ruff and strict mypy, and a successful Vite build.
- [VERIFIED] Windows `make verify` reported `23 passed in 5.40s` and the script reported three replies. Compose reported `healthy running`, and the mock browser path started bundled speech in 31 ms. Port 8000 was occupied on the demo machine. The Compose port override enabled the rerun without stopping the existing listener.
- [VERIFIED] The English and Hindi browser runs above reached Web Audio playback with no page errors or horizontal overflow. Approved English clips come from local Flite-generated assets.
- Considered a spoken acknowledgement while waiting. Kept the existing visible status instead so acknowledgement audio cannot be mistaken for an answer or inflate the time-to-answer result.
- [UNKNOWN] Production traffic, physical-device delay, wider accents and public hosting. HTTPS/access-code options are documented in DEPLOYMENT.md.

## Reproduce

Use scripts/benchmark_speech.py to generate the synthetic WAV fixture directory. Run scripts/benchmark_local_stt.py and scripts/benchmark_live.py as Python modules with that directory. Run scripts/benchmark_browser_stt.mjs with the console URL, fixture directory and browser executable. The timed browser round trip is tests/e2e/voice_browser.mjs. EXPLAINED_SIMPLY.md and CODE_MAP.md describe the shipped paths.

The measured matched improvement qualifies for demo-voice-fast after the release checks. P3 comes next. Keep the original target and quantify misses rather than resetting the budget.
