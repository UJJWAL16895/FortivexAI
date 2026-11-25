# Deployment

For a local evaluation use the Windows commands in README.md. A fresh clone needs Git, Python 3.13, Node 24 with npm, network for initial installation and optionally GNU Make. Setup installs locked dependencies and builds the console. FastAPI serves the built assets and WebSocket on port 8000. Run verification on the demo machine and a fresh checkout for each release.

Docker Compose builds the frontend in a Node stage and copies the resulting assets into the non-root Python image. From the root run `docker compose -f infra/docker-compose.yml up --build --wait`, open http://127.0.0.1:8000 and try a message, then stop the stack with `docker compose -f infra/docker-compose.yml down`. For local triage check container state, then /health, then the browser socket. To roll back, check out the last verified demo tag and rebuild. The prototype has no persistent call data in P1.

The supplied Compose profile runs the mock voice demo. For a live demo use the native app on loopback and a populated local .env. For remote browsers plan HTTPS and an explicit microphone permission test. Check /api/voice/transcribe separately from the reply socket when diagnosing recording errors.

If port 8000 is occupied, set SHELFPILOT_HOST_PORT to an unused local port before starting Compose. Use that port in the browser URL.

[UNKNOWN] Managed deployment footprint, TLS termination, resource limits, failover configuration and production capacity. Record actual container and CI results in the step report. Extend this runbook as deployment targets are verified.

## Local Windows setup (primary)

Use the README quickstart. The keyless demo needs only the core lock. For faster live microphone turns on the demo laptop, run the commands below from the repository root after setup. The last command downloads the public CPU model weights once. Set VOICE_STT=local in the local .env and restart before the session. Leave VOICE_STT=gemini for a machine without the optional CPU packages. The server tries both configured engines when one fails.

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements-speech-eval.lock
& .\.venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; [WhisperModel(n, device='cpu', compute_type='int8', cpu_threads=4) for n in ('base', 'small')]"
```

## Docker and an HTTPS WebSocket host

Build from the repo root with `docker build -f infra/Dockerfile -t shelfpilot-demo .`. The supplied Compose profile binds port 8000 to loopback for mock demos. For remote access, run the image as a long-lived service on a WebSocket-capable host, such as Render's Docker or image service, or a small VM with a reverse proxy. Keep the UI, audio POSTs and WebSocket on one HTTPS origin, route the WebSocket upgrade, and check that the platform timeout allows demo sessions. Set live credentials in the host's secret settings and keep them out of the image. Test the microphone and reconnect over HTTPS. Vercel's traditional serverless deployment is unsuitable for this repository's always-running Python WebSocket backend. Vercel also advertises a WebSocket public beta for supported runtimes, which this project has not verified. [Render WebSockets](https://render.com/docs/websocket) · [Vercel limits](https://vercel.com/docs/limits) · [Vercel beta announcement](https://vercel.com/changelog/websocket-support-is-now-in-public-beta)

Require a shared evaluator access code at the HTTPS entry point before exposing a demo. One option on a VM is Caddy Basic Auth with username evaluator. Run `caddy hash-password` interactively, save the hash as DEMO_PASSWORD_HASH in the proxy environment, and use this site block. Publish only the proxy ports. Keep Uvicorn on loopback or an isolated private network. Configure Uvicorn to trust forwarded scheme headers only from the actual proxy. Verify unauthenticated GET and WebSocket upgrade fail, then authenticate in the browser and verify the socket connects. This shared credential is for a private demo audience. [Caddy Basic Auth](https://caddyserver.com/docs/caddyfile/directives/basic_auth)

```caddyfile
demo.example.com {
    basic_auth {
        evaluator {env.DEMO_PASSWORD_HASH}
    }
    reverse_proxy 127.0.0.1:8000
}
```

[UNKNOWN] Public hosting and proxy authentication have not been deployed in this phase. Both Windows local and Docker remain the supported evaluation paths.
