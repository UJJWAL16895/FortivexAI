# Deployment

For a local evaluation use the Windows commands in README.md. A fresh clone needs Git, Python 3.13, Node 24 with npm, network for initial installation and optionally GNU Make. Setup installs locked dependencies and builds the console. FastAPI serves the built assets and WebSocket on port 8000. Run verification on the demo machine and a fresh checkout for each release.

Docker Compose builds the frontend in a Node stage and copies the resulting assets into the non-root Python image. From the root run `docker compose -f infra/docker-compose.yml up --build --wait`, open http://127.0.0.1:8000 and try a message, then stop the stack with `docker compose -f infra/docker-compose.yml down`. For local triage check container state, then /health, then the browser socket. To roll back, check out the last verified demo tag and rebuild. The prototype has no persistent call data in P1.

[UNKNOWN] Managed deployment footprint, TLS termination, resource limits, failover configuration and production capacity. Record actual container and CI results in the step report. Extend this runbook as deployment targets are verified.
