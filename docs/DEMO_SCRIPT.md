# FORTIVEX Round 3 demo

## 60-second pitch

Retail software reps spend time repeating first-call answers and arranging demos. ShelfPilot is a bilingual browser sales agent that replies from approved product cards, books an explicitly confirmed time and records a returning demo lead. The operator can see what the caller said in the current transcript and review the saved sentiment, BANT reasons and draft follow-up. I will show both the successful path and an unsupported discount. The repo has a keyless demo, tested SQLite booking behavior and measured local limits.

## Rehearsal and fallback

Follow the exact click and speech sequence in [Hero acceptance](RELEASE_HERO.md). Say “The contact is fictional. The time says IST. I can reopen this lead and the database still has the confirmation.” Keep a keyless local tab ready. If the mic or network fails, type the same questions and commands. If the computer fails, play the backup recording.

To record the backup, start with a fresh local database and close private tabs and notifications. Use Windows Snipping Tool screen recording or another recorder available on the device. Capture only the browser, demonstrate the six steps, stop recording and play the file back to check sound and readability. Save the recording outside Git and share it only with the intended evaluator.

## Known limits to say out loud

Physical microphone performance remains unmeasured. Hindi readback measured 3.98 seconds median on three synthetic turns. The retrieval evaluation has twenty authored questions. The demo uses rule-based sentiment and BANT, and the draft requires a person to send it. Contact-key recall is a demonstration shortcut without verified identity. The SQLite and local CPU setup are for a single-instance demo. The 100,000-user projection is a scenario.
