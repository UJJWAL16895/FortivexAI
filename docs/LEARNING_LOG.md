# Learning log

## P0 · Configuration and trust boundaries

A credential can authenticate a model listing while generation still fails. STEP-000 demonstrates that distinction with a successful OpenAI listing followed by exhausted generation credit. This makes a real completion probe essential for choosing a live provider.

Read src/core/settings.py first. Configuration is validated before FastAPI accepts requests. src/api/app.py exposes only status and mode, so inspecting health does not reveal the underlying settings. Read scripts/secret_scan.py next. Git stores a staged snapshot and a working copy separately. Cleaning the working file does not remove leaked bytes already staged for commit.

Common mistakes include treating a catalog listing as proof of available credit, putting secrets in URLs, and timing only text generation when a user waits for audio. The architecture starts analysis in the background so it can finish after the spoken response.

Exercise: in a disposable checkout run the settings and staged-leak tests individually. Change the health response model locally and observe the contract test fail. Explain what a live HTTP 200 proves and which provider checks still need real network evidence.

## P0 quiz

1. **What starts the API?** Uvicorn calls create_app, which validates settings and registers routes.
2. **Why use SecretStr?** Common representations mask the value and the adapter can explicitly unwrap it when needed.
3. **Why scan the Git index?** It contains the bytes that go into the commit, even after the working file has changed.
4. **Why test the OpenAPI document?** It catches drift between the published HTTP contract and the running route definition.
5. **What does a green health response prove?** The local process can answer requests and expose its configured mode.

## P1 · A browser conversation over one connection

Read frontend/src/main.jsx, src/api/text_session.py and src/llm/mock.py in that order. The input becomes JSON, FastAPI validates it, and the mock replies with predictable text. The browser keeps a transcript and displays the reply compute time it receives from the server. A WebSocket stays open across messages, so the three-turn demo can use one connection.

Serving the built assets and the socket from FastAPI makes the URL and origin easy to explain. Vite compiles the UI during setup and verification. A common mistake is to call the compute time a user's waiting time. The timer covers the mock function and excludes travel and display. Try adding one fictional mock branch and one scripted question proving that branch.

### P1 quiz

1. **What makes Send available?** The socket sent ready, there is nonblank input, and a prior reply is not pending.
2. **Where are the length and shape validated?** TextTurn in src/api/text_session.py validates the JSON after the frame is decoded.
3. **What happens after malformed JSON?** The handler sends an error and continues reading on the same socket.
4. **Which file makes a reply deterministic?** src/llm/mock.py selects a fixed response from the text.
5. **What is shared by the browser and CLI demo?** Both connect to /ws/text and use the same ready, turn and reply protocol. The demo checks expected words in three replies.
