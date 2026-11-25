# ShelfPilot · FORTIVEX AI sales voice agent

An inbound sales agent for a fictional retail inventory vendor. The planned demo takes a multilingual product inquiry through a grounded answer, qualification, a confirmed appointment and a CRM update. **P0 currently exposes a keyless health API and the verification suite.** The first interactive text demo is the P1 checkpoint.

## Start on Windows

From the repository root, use Python 3.13. On the original demo laptop PowerShell can locate it even when the launcher is missing from PATH.

```powershell
$python = Join-Path $env:USERPROFILE 'AppData\Local\Programs\Python\Python313\python.exe'
& $python scripts/tasks.py setup
& .\.venv\Scripts\python.exe scripts/tasks.py verify
& .\.venv\Scripts\python.exe scripts/tasks.py run
```

In a second terminal, run `Invoke-RestMethod http://127.0.0.1:8000/health`. Visit [interactive API docs](http://127.0.0.1:8000/docs) to inspect the response. Stop the server with Ctrl+C. A standard Python installation can use `python scripts/tasks.py setup` instead.

| Make command | Windows equivalent from the repository root |
|---|---|
| make setup | `& $python scripts/tasks.py setup` |
| make verify | `& .\.venv\Scripts\python.exe scripts/tasks.py verify` |
| make scan | `& .\.venv\Scripts\python.exe scripts/tasks.py scan` |
| make run PORT=8001 | `& .\.venv\Scripts\python.exe scripts/tasks.py run --port 8001` |

Make setup accepts a BOOTSTRAP override for a nonstandard Python path. On Linux use Python 3.13, Git, and GNU Make. Setup needs network access for the locked packages. Once installed, the foundation's verification and HTTP server run offline. The optional pre-commit hook environment is initialized on first use.

## Credentials

Mock mode is the default. Copy .env.example to .env only for a new configuration. Never replace a populated file. The server reads the local file at startup. Keep its real values out of chat, Git, cloud sync, client bundles and screenshots. This project's OneDrive location requires checking your local sync settings. See SECURITY.md for the scope of the scanner.

## Read the evidence

- [Product requirements](docs/PRD.md) and [ordered delivery gates](docs/TASKS.md)
- [Architecture and failure modes](docs/ARCHITECTURE.md), [data model](docs/DATA_MODEL.md) and [current API contract](docs/API_SPEC.yaml)
- [Provider verification](docs/reports/STEP-000.md) and [Windows foundation verification](docs/reports/STEP-001.md)
- [Directory guide](docs/DIRECTORY_GUIDE.md), [learning log](docs/LEARNING_LOG.md) and [deployment](docs/DEPLOYMENT.md)
