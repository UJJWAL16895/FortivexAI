# ShelfPilot · FORTIVEX AI sales voice agent

ShelfPilot is an inbound sales agent for a fictional retail inventory vendor. **P1 runs a keyless browser text demo.** Try questions about multiple stores, price and a demo. The current replies are deterministic mock responses. Voice, citations and booking follow in later checkpoints.

## Start on Windows

From a fresh clone, install Git, Python 3.13 and Node 24 with npm. In PowerShell, enter the repository and run:

```powershell
$python = 'python'
# If Python is missing from PATH on the demo laptop, set $python to:
# Join-Path $env:USERPROFILE 'AppData\Local\Programs\Python\Python313\python.exe'
& $python scripts/tasks.py setup
& .\.venv\Scripts\python.exe scripts/tasks.py verify
& .\.venv\Scripts\python.exe scripts/tasks.py run
```

Open [the Sales Console](http://127.0.0.1:8000), wait for Connected and choose a suggested question or type your own. Stop the server with Ctrl+C. To run the three-turn script in a separate terminal without a port conflict, use `& .\.venv\Scripts\python.exe scripts/tasks.py demo --port 0`. On macOS/Linux, use `python3.13 scripts/tasks.py setup` and the equivalent `.venv/bin/python` commands.

| Make command | Windows equivalent from the repository root |
|---|---|
| make setup | `& $python scripts/tasks.py setup` |
| make verify | `& .\.venv\Scripts\python.exe scripts/tasks.py verify` |
| make scan | `& .\.venv\Scripts\python.exe scripts/tasks.py scan` |
| make run PORT=8001 | `& .\.venv\Scripts\python.exe scripts/tasks.py run --port 8001` |
| make demo PORT=0 | `& .\.venv\Scripts\python.exe scripts/tasks.py demo --port 0` |

Make setup accepts a BOOTSTRAP override for a nonstandard Python path. Setup needs network access to install locked Python and npm packages. The console, scripted demo and verification afterwards run offline. The optional pre-commit hook environment is initialized on first use.

## Credentials

Mock mode is the default. Copy .env.example to .env only for a new configuration. Never replace a populated file. The server reads the local file at startup. Keep its real values out of chat, Git, cloud sync, client bundles and screenshots. This project's OneDrive location requires checking your local sync settings. See SECURITY.md for the scope of the scanner.

## Read the evidence

- [Product requirements](docs/PRD.md) and [ordered delivery gates](docs/TASKS.md)
- [Architecture and failure modes](docs/ARCHITECTURE.md), [data model](docs/DATA_MODEL.md) and [current API contract](docs/API_SPEC.yaml)
- [Provider verification](docs/reports/STEP-000.md) and [Windows foundation verification](docs/reports/STEP-001.md)
- [Directory guide](docs/DIRECTORY_GUIDE.md), [learning log](docs/LEARNING_LOG.md) and [deployment](docs/DEPLOYMENT.md)
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md) and [P1 verification](docs/reports/STEP-002.md)
