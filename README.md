# ShelfPilot · FORTIVEX AI sales voice agent

ShelfPilot is an inbound sales agent for a fictional retail inventory vendor. Try text or click **Record**, say a short question, then click **Stop**. Use Chrome or Edge on localhost and allow microphone access. The keyless voice demo uses a scripted transcript and bundled mock audio. Live mode transcribes your recording, streams the reply and plays it sentence by sentence.

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

Open [the Sales Console](http://127.0.0.1:8000), wait for Connected and choose a suggested question or type your own. Stop the server with Ctrl+C. To run the scripted lead recall demo on an available port, use `& .\.venv\Scripts\python.exe scripts/tasks.py demo --port 0`. On macOS/Linux, use `python3.13 scripts/tasks.py setup` and the equivalent `.venv/bin/python` commands.

| Make command | Windows equivalent from the repository root |
|---|---|
| make setup | `& $python scripts/tasks.py setup` |
| make verify | `& .\.venv\Scripts\python.exe scripts/tasks.py verify` |
| make scan | `& .\.venv\Scripts\python.exe scripts/tasks.py scan` |
| make run PORT=8001 | `& .\.venv\Scripts\python.exe scripts/tasks.py run --port 8001` |
| make demo PORT=0 | `& .\.venv\Scripts\python.exe scripts/tasks.py demo --port 0` |

Make setup accepts a BOOTSTRAP override for a nonstandard Python path. Setup needs network access to install locked Python and npm packages. The console, scripted demo and verification afterwards run offline. The optional pre-commit hook environment is initialized on first use.

## Credentials

To use Gemini, set AGENT_MODE=live in the local .env and configure both model IDs from the benchmark report. Restart the API. Each reply is labelled LIVE or MOCK. To demonstrate failover without a key, set `$env:ALLOW_FALLBACK_DEMO='true'` before launch, then choose **Simulate Gemini failures**. The provider trace shows both simulated failures and the mock response. Remove the environment setting after the demo.

For optional local CPU transcription, add `--voice-models` to the setup command and set VOICE_STT=local in the local .env. The Make equivalent is `make setup VOICE_MODELS=1`. This downloads Base and Small. Local mode preloads both and uses Small for English and Hindi. Choose a language in the console. A missing local model falls back to Gemini. Core-only setup defaults to Gemini for live speech. Common English sentences use bundled speech. Other live speech can use unofficial, demo-only edge-tts, Gemini or the browser. [Deployment and model setup](docs/DEPLOYMENT.md)

Try “My name is Asha. I work at Cedar Retail. We have three stores.” The assistant reads back the count. Reply “yes,” then ask “What do you remember?” The profile and the last four turns belong to the open conversation. [P3-lite report](docs/reports/STEP-006.md)

Ask “How much does Growth cost?” for a cited fictional price, or ask for an undocumented discount to see abstention. The offline quickstart includes the reviewed knowledge cards. For multilingual semantic matching, use setup --knowledge-model (Make equivalent `make setup KNOWLEDGE_MODEL=1`) and set KNOWLEDGE_EMBEDDINGS=true before restart. [Retrieval evidence](docs/reports/STEP-007.md)

For the text hero, ask about Growth, then type “My email is hero@example.test.” Say or type “Book a demo” and “Confirm booking.” Open **View demo CRM**. Refresh and enter the same contact to see returning-lead recognition. Use fictional contacts only. The default file is `data/runtime/crm.sqlite3`, and Compose stores it on a named volume. [Text hero evidence](docs/reports/STEP-008.md)

For the voice hero, record the price question and both booking commands in live local voice mode. Enter the fictional contact with the keyboard. Select **End conversation**, then **View insights** for the completed call. Insights use simple language heuristics and retain recent reports until the app restarts. [Voice evidence](docs/reports/STEP-009.md)

Mock mode is the default. Copy .env.example to .env only for a new configuration. Never replace a populated file. The server reads the local file at startup. Keep its real values out of chat, Git, cloud sync, client bundles and screenshots. This project's OneDrive location requires checking your local sync settings. See SECURITY.md for the scope of the scanner.

## Read the evidence

- [Product requirements](docs/PRD.md) and [ordered delivery gates](docs/TASKS.md)
- [Architecture and failure modes](docs/ARCHITECTURE.md), [data model](docs/DATA_MODEL.md) and [current API contract](docs/API_SPEC.yaml)
- [Provider verification](docs/reports/STEP-000.md) and [Windows foundation verification](docs/reports/STEP-001.md)
- [Directory guide](docs/DIRECTORY_GUIDE.md), [learning log](docs/LEARNING_LOG.md) and [deployment](docs/DEPLOYMENT.md)
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md) and [P1 verification](docs/reports/STEP-002.md)
- [P2 model benchmark](docs/reports/STEP-003.md) and [voice checkpoint](docs/reports/STEP-004.md)
- [Explain the project](docs/EXPLAINED_SIMPLY.md) and [code map](docs/CODE_MAP.md)
