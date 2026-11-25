# Learning log

## P0 · Configuration and trust boundaries

A credential can authenticate a model listing while generation still fails. STEP-000 demonstrates that distinction with a successful OpenAI listing followed by exhausted generation credit. This makes a real completion probe essential for choosing a live provider.

Read src/core/settings.py first. Configuration is validated before FastAPI accepts requests. src/api/app.py exposes only status and mode, so inspecting health does not reveal the underlying settings. Read scripts/secret_scan.py next. Git stores a staged snapshot and a working copy separately. Cleaning the working file does not remove leaked bytes already staged for commit.

Common mistakes include treating a catalog listing as proof of available credit, putting secrets in URLs, and timing only text generation when a user waits for audio. The architecture starts analysis in the background so it can finish after the spoken response.

Exercise: in a disposable checkout run the settings and staged-leak tests individually. Change the health response model locally and observe the contract test fail. Explain what a live HTTP 200 proves and which provider checks still need real network evidence.
