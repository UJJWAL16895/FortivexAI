# User stories and acceptance examples

| User and task | An observable acceptance check | Gate |
|---|---|---|
| Evaluator starts the app without cloud credentials | Browser can send and receive a deterministic mock turn, and the provider label names the mock | P1 |
| Owner switches from Hindi to English halfway through a question | The agent tracks store count and matches the latest language, including Roman Hindi fixtures | P3/P6 |
| Buyer asks about an undocumented discount | Transcript shows the abstention and no invented figure | P4 |
| Buyer interrupts a long explanation | Stop playback, cancel in-flight generation, discard stale chunks by turn ID | P5 |
| Two buyers confirm the same slot | One durable appointment, one new offer, both responses match the database | Early hero/P7 |
| Rep opens a returning lead | Authorized contact lookup recalls the correct profile and avoids duplicates | P3/P7 |
| Rep sees an angry buyer | Offer a human handoff and record an event once | P8 |
| Manager reviews yesterday’s calls | Dashboard measures correspond to unique calls, timestamps and documented denominators | P9 |
