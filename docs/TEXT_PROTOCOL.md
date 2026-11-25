# Streaming text WebSocket

Connect to /ws/text on the same origin as the console. The ready event contains mode and allow_fallback_demo.

Send one turn as `{"text":"Can I manage three stores?"}`. The server trims whitespace and accepts 1–500 characters. Provider events report attempts and outcomes. Delta events append visible text. Sentence events carry speakable text as boundaries arrive. Reply events seal the transcript with text, provider, mode and latency_ms, measured from chain start to its first visible text. An error ends the turn. Once any text has streamed, an interrupted turn ends instead of mixing text from another provider.

Malformed JSON, oversized application text and unsupported frames receive an error. Frame size is capped at 16 KiB in the launch commands. The console holds transcript text in React state. With ALLOW_FALLBACK_DEMO enabled, the optional simulate_failure field injects a 503 for both Gemini slots before any network request.
