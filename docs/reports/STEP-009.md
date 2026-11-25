# STEP-009 · Voice sales hero

[VERIFIED] After tagging demo-text-hero, Chrome returned “Voice hero: citation, timezone, one booking, one CRM lead, returning caller verified.” The test used three Flite-generated synthetic microphone clips for the price question, booking request and explicit confirmation. The browser recorded through MediaRecorder and the warmed local Whisper Small transcribed the uploads. Playback started for each of the three spoken turns. The tester entered the fictional name and email by keyboard. This run tested the application voice path on synthetic input, and physical capture remains unmeasured.

Code path: the microphone transcript reaches the same text socket and shared booking state. The cited answer, offer and receipt reach the browser speech queue as sentences. Gemini Live remains outside the main demo. No further latency tuning was performed.

## Voice hero quiz

1. **Where does voice join text?** After transcription, the browser submits the same text socket frame.
2. **Which phrases were spoken?** The Growth price question, “Book a demo” and “Confirm booking.”
3. **What did the tester type?** The name and fictional email.
4. **What plays the offer?** The normal sentence playback queue.
5. **How do we know it booked?** The test queries the saved CRM data and confirms one booking after reconnecting.
