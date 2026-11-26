# Streaming text WebSocket

Connect to /ws/text on the same origin as the console. The ready event contains mode and allow_fallback_demo.

Send one turn as `{"text":"Can I manage three stores?"}`. The server trims whitespace and accepts 1–500 characters. Provider events report attempts and outcomes. Delta events append visible text. Sentence events carry speakable text as boundaries arrive. Reply events seal the transcript with text, provider, mode and latency_ms, measured from chain start to its first visible text. An error ends the turn. Once any text has streamed, an interrupted turn ends instead of mixing text from another provider.

Malformed JSON, oversized application text and unsupported frames receive an error. Frame size is capped at 16 KiB in the launch commands. The console holds transcript text in React state. With ALLOW_FALLBACK_DEMO enabled, the optional simulate_failure field injects a 503 for both Gemini slots before any network request.

The server emits first_text when the provider produces its first nonblank text. Deltas contain only approved sentence text. Unsupported pricing queries can use the fixed policy without a model call. A policy reply reports mode policy and latency_ms null when the model was bypassed. Policy output can be spoken without calling a remote TTS for bundled phrases.

Each socket owns one LeadSession. After a valid turn the server sends a profile event with profile and pending fields. Extracted count and date appear in pending until an explicit affirmative reply. Rejection or correction leaves the previous confirmed profile intact. Confirmations and recall are mode session, with null model latency, and use the same sentence events as other replies. The server discards the session when the socket closes.

## Optional mode control

A client can send a frame containing only a mode field, either live or mock. mode_status events carry a phase, effective mode, sanitized message, optional probe timing and model, and a quota snapshot. The ready event also includes live_allowed, quota and an ephemeral voice_session handle. The browser passes that handle as X-Voice-Session on existing voice requests. It expires with the socket. Existing text turn frames and reply events are unchanged. An optional quota event refreshes the rolling process counter.

A buyer text frame may include turn_id. The background worker's analysis event echoes it and carries a status, sentiment, cumulative score, rating and scoring reasons when available. Without turn_id the event is omitted. Replies can include an origin, the original passage for a grounded elaboration and an approved_follow_up marker for mixed provenance.
