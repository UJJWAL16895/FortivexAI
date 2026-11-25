# Deployment

For a local evaluation use the Windows commands in README.md. A fresh clone needs Git, Python 3.13, network for initial dependency installation, and optionally GNU Make. Use localhost and mock mode for the foundation smoke test. Run verification on both the original machine and a fresh checkout for release checkpoints.

Docker Compose uses infra/docker-compose.yml and an explicit mock environment. From the root run `docker compose -f infra/docker-compose.yml up --build -d`, inspect `docker compose -f infra/docker-compose.yml ps`, request the loopback health URL and use `docker compose -f infra/docker-compose.yml down` to stop that stack. The image uses the foundation dependency lock, including development checks, for reproducible evaluation. Split runtime/development image dependencies and verify updated base image security before production distribution.

[UNKNOWN] Managed deployment footprint, TLS termination, resource limits, failover configuration and production capacity. Record actual container and CI results in the step report. Extend this runbook as deployment targets are verified.
