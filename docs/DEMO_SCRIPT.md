# Demo script · Thin voice checkpoint

1. Use the README quickstart and open http://127.0.0.1:8000.
2. Select the multi-store prompt, type a pricing question, and request a demo. Show the transcript, connection status and reply compute time.
3. Run `make demo PORT=0` or the documented Python equivalent for the same flow on a separate socket.
4. Trace one message through React, the text session and the deterministic mock. Explain where later voice and booking enter the design.
5. Click Record, speak a short synthetic sales question, and click Stop. Show the transcription provider, transcript and playback timing. In MOCK the spoken answer is scripted. In LIVE use a fictional query and point out any provider fallback.
6. With ALLOW_FALLBACK_DEMO enabled, click Simulate Gemini failures to display A → B → mock.

The P1 checkpoint is offline after dependencies are installed. If the browser is unavailable, use the scripted demo and show the protocol. The final rehearsal and pitch belong to P13.
