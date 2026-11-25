# Interview questions

1. **How do you launch locally?** Use README setup and run, then open localhost:8000.
2. **What does the mock guarantee?** Predictable, keyless demo turns.
3. **Why one app?** One origin serves React, HTTP and WebSockets.
4. **What moves over WebSocket?** Text frames, provider state, sentences and profile updates.
5. **What moves over HTTP?** Audio uploads, synthesis and operator snapshots.
6. **What is the voice endpoint?** Manual Stop or the recording duration cap.
7. **What files are uploaded?** Bounded mono 16 kHz PCM WAV.
8. **Why use Small?** It recognized three stores on the tested clip.
9. **Which STT comes next?** Gemini if local transcription fails and vice versa.
10. **Why exclude Gemini Live?** Native audio bypasses the current text approval path.
11. **What did Hindi measure?** 3.98 seconds median on three readback trials.
12. **What does LIVE mean?** Live configuration, with actual provider shown separately.
13. **What do sentence events do?** They let playback begin ahead of a complete response.
14. **What ends a slow model request?** A deadline and bounded fallback.
15. **What happens if the browser closes?** The receiver cancels the turn and closes the generator.
16. **How long does dialogue memory last?** One socket with four completed pairs.
17. **What persists across sockets?** Confirmed CRM profile, bookings and completed reports.
18. **What is the source of a product fact?** An approved bilingual knowledge card.
19. **What do local embeddings do?** Compare semantic distance when aliases miss.
20. **What is a citation?** The source file and card ID shown beside the reply.
21. **What happens on weak retrieval?** The app offers specialist follow-up.
22. **How did retrieval score?** 14/15 hybrid source hits and five correct abstentions.
23. **How are source files reviewed?** A manifest digest must match.
24. **What stops an invented discount?** Prices and discounts come from cards or abstention.
25. **What does the agent do with numbers?** Read them back before saving confirmed details.
26. **What happens on kal?** It stays ambiguous and is not stored as a date.
27. **How are contact digits normalized?** Unicode decimal digits are converted to ASCII.
28. **What is CRM identity?** A normalized synthetic key with no identity verification.
29. **How is a time committed?** Explicit confirmation triggers a unique slot insert.
30. **What does the booking rate count?** Booked reports divided by all saved analyzed call reports.
31. **What stops analytics blocking speech?** The socket queues work after the reply.
32. **What is BANT?** Budget, authority, need and timeline.
33. **How is the analysis validated?** Pydantic checks the report shape and score bounds.
34. **Do drafts get sent?** They stay available for manual review.
35. **Which logs mask contact values?** Selected server loggers use pattern filtering.
36. **What survives a restart?** SQLite reports, leads and bookings on persistent storage.
37. **What was the load measurement?** Local mock cited turns, not fleet voice throughput.
38. **What changes for 100,000 registrations?** Move socket state, durable jobs and database work to separate services.
39. **What is the commercial claim?** A labeled scenario. Pilot outcomes are unmeasured.
40. **How do you recover a working demo?** Use a verified rollback tag and a separate fictional database.

## Hard questions and honest answers

- **What is weakest?** Physical mic and multilingual breadth. Demonstrate the measured fixtures and say where they stop.
- **What is mocked?** Keyless STT, preset audio and unsupported general replies. Booking, SQLite and approved retrieval execute in the demo.
- **What is unmeasured?** Real conversion, production voice capacity and held-out corpus accuracy.
- **What would you improve?** Validate streaming STT, tenant identity and durable job recovery before live customer data.
