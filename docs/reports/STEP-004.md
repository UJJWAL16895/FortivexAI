# STEP-004 · Thin voice checkpoint

## Objective and plan

Verify browser microphone capture → transcription → streamed reply → sentence playback. Keep a runnable keyless path, compare a tiny English/Hindi speech set, and publish demo-voice-thin before P3. Start with an HTTP acceptance test, then verify Chrome using a synthetic WAV as its capture device.

## Evidence · 26 November 2026

| Engine | Observed timing | Errors and quick quality | Free-tier status and decision |
|---|---|---|---|
| Gemini 3.5 Transcribe | English 6181 ms, Hindi 6210 ms on successful requests | Two exact transcripts on the first pass. Two 503-class failures on a repeat pass. | [VERIFIED] Standard audio input and text output are eligible on Google's free tier. **Selected for live STT** based on Hindi quality. If unavailable, the console offers typed input. |
| faster-whisper Tiny, CPU int8 | 560 ms English, 2184 ms Hindi for the same Edge-synthesized clips. Cached model startup 883 ms. | Exact English, badly garbled Hindi with auto-detection. The installed PyAV rejected the package's file-open keyword, so the bench supplied decoded PCM arrays. Both clips then completed. | [VERIFIED] Runs locally after model download. No cloud STT fee. **Comparison only** at this checkpoint. |
| edge-tts 7.3.1 | English first encoded chunk 850–1028 ms, total 1344–1457 ms. Hindi first chunk 939–1130 ms, total 1264–1434 ms. | Four MP3 responses decoded to WAV. Successful Gemini transcription reproduced both fixture scripts exactly. | [VERIFIED] Requests succeeded without an API key. [UNKNOWN] Service terms, availability and any published free allowance. **Selected for the demo. Unofficial and demo-only.** |
| Gemini 3.8 Flash TTS, Kore | English full clip 5142–6739 ms, Hindi 4693–5609 ms. Buffered WAV response. | Four playable WAV outputs. English matched in a faster-whisper round trip. Hindi words were partly recognizable by that comparator, which also struggled with the Edge Hindi clip. | [VERIFIED] Google lists free-tier input and output for this model. Select with VOICE_TTS=gemini. Browser synthesis remains available. |

The corpus contains one short English phrase and one short Hindi phrase about three stores and Friday. The recordings are synthetic, clean and narrow. TTS checks used decode and STT round-trip quality rather than a listener study. Edge first chunk and Gemini complete WAV represent different transfer points. The app awaits a full sentence clip before playback. The timings include transport for cloud engines. A 503-class failure can be an upstream response or a transport failure mapped by the adapter. Account quota and billed amount remain [UNKNOWN]. [Google pricing](https://aistudio.google.com/docs/pricing) · [Transcription API](https://aistudio.google.com/docs/transcribe) · [Gemini TTS](https://aistudio.google.com/docs/speech-generation) · [edge-tts source](https://github.com/rany2/edge-tts) · [faster-whisper source](https://github.com/SYSTRAN/faster-whisper)

## Verification and self-review

- [VERIFIED] Before implementation the voice endpoint test returned `404 == 422`. The implemented API validates origin and WAV shape, enforces size and passes the integration test. The HTTP spec matches the app.
- [VERIFIED] After fixing a narrow-screen overflow, Chrome at 390 px reported `MOCK`, `34 ms · Mock audio`, `overflow:false`, and `pageErrors:0`. The microphone API supplied a synthetic fixture and Web Audio started bundled phrase playback. The two fixture MP3s were generated locally with FFmpeg's Flite filter.
- [VERIFIED] Chrome live returned `gemini-3.5-transcribe · 8747 ms`, Gemini first text `1237.62 ms`, `11818 ms · edge-tts` stop to playback, `LIVE`, and no page errors or horizontal overflow. Another live run reached playback at 12591 ms and exposed the mobile overflow corrected above.
- [VERIFIED] Windows `make verify` reported `20 passed in 3.72s`, clean lint, mypy and secret scan, and Vite built the UI with both audio assets. `make demo PORT=0` reported `Demo passed: 3 replies over WebSocket (mock).` Mermaid rendered five charts. Review covered recording lifecycle, same-origin POSTs, provider labels, bounded upload, lack of disk retention and the keyless path.
- [VERIFIED] Docker Compose reported `healthy running`. Chrome exercised the same microphone fixture and reported `29 ms · Mock audio`, `overflow:false`, `pageErrors:0`.
- [VERIFIED] P2 GitHub Actions passed on fresh Windows and Ubuntu runners. [P2 CI](https://github.com/UJJWAL16895/FortivexAI/actions/runs/45688981865)

To reproduce, install the locked app and optional evaluation requirements, run `python -m scripts.benchmark_speech` from the venv, and use the README quickstart. The browser smoke script takes URL, a synthetic capture WAV, Chrome executable path and expected mock/live mode. Install the existing docs tool lock with npm ci --prefix tools/diagrams first. The smoke script exercises browser capture APIs and the Web Audio start event. Speakers, ambient noise and microphone hardware remain [UNKNOWN].

## Scope and next gate

[ASSUMED] The first-audio budget remains p50 ≤ 2.0 s and p95 ≤ 3.5 s from the final voiced sample. The thin checkpoint uses the recorder stop event and observed both live samples well above the target. P5 will instrument the actual voiced endpoint, evaluate streaming voice input, and add barge-in and playback cancellation. P3 is the next phase after the release tag.
