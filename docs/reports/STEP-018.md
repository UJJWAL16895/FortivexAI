# STEP-018 · Public preview preparation

The local demo now has an optional hosted mode. Public mode defaults to mock even when AGENT_MODE is live. Explicit live mode needs both flags, a provider configuration and an evaluator code. The app checks that code before allowing API and WebSocket work. One process counts accepted API requests and incoming application messages against rolling limits. The image omits local model weights.

| Check | Evidence |
|---|---|
| HTTP and WebSocket safeguards | [VERIFIED] Four focused pytest tests passed. They checked mock default, Secure/HttpOnly cookie, denied unauthenticated HTTP and socket, and rolling per-peer and shared caps. |
| Docker | [VERIFIED] Built the image and started it on a supplied PORT of 8107. Log: Public startup self-check passed. Mode=mock; reviewed knowledge and SQLite ready. /health returned status ok and mode mock. /api/public-status returned public true, mode mock and locked false. Chrome loaded the public MOCK banner and connected to the WebSocket. |
| Hosted deployment | [UNKNOWN] Account setup, managed TLS/proxy behavior and shared runner limits await the owner-led deploy. See DEPLOY_STEPS.md. |

### Quiz with answers

1. What must be enabled for public live? **Both live flags, provider settings and a strong evaluator code.**
2. Does the browser get a Gemini key? **No. It gets a signed, temporary cookie after unlock.**
3. What counts against the limits? **Protected API calls, unlock attempts and received WebSocket messages.**
4. What happens to the counters after a restart? **They reset because they live in the current process.**
5. Why does the public image skip Whisper? **It keeps the image and runtime lighter. Mock uses scripted transcription and intentional live uses Gemini.**
