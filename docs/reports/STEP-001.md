# STEP-001 · P0 foundation and Windows verification

## Objective and plan

Build the smallest executable foundation for ShelfPilot. Start with failing acceptance tests, validate configuration, serve a keyless health route, lock the installed dependencies, add index-aware secret scanning, verify Windows entry points, render the architecture, and smoke-test the container before the first commit.

## What shipped

[VERIFIED] FastAPI factory and typed health response, validated settings, a published OpenAPI contract with drift test, fully pinned Python environment, a docs-only npm lock, local pre-commit hook, Windows and Linux CI jobs, a non-root container and one verification implementation shared by Make and Python. The project contains the requested documentation categories with stage-specific content. Release criteria and evidence collection are in TASKS.md. Later feature modules are created as directories by setup; their behavior is implemented at their respective gates.

## Verification evidence

| Check | Observed output |
|---|---|
| Test first, before implementing src | `ModuleNotFoundError: No module named 'src'` and `1 error during collection` |
| Windows toolchain | `Python 3.13.2`, `GNU Make 4.4.1`. Installed the WinGet ezwinports.make user package. Docker Desktop engine subsequently returned `Server 29.6.2`. |
| Both setup entry points | `make setup` and Python 3.13 `scripts/tasks.py setup` each exited 0 and printed `pre-commit installed at .git\hooks\pre-commit`. |
| Both scan entry points | `make scan` and the venv Python `scripts/tasks.py scan` printed `Secret scan: clean (Git index and non-ignored working tree).` |
| Make verification | `No broken requirements found.`, `All checks passed!`, `Success: no issues found in 5 source files`, `12 passed in 3.32s` |
| Python verification | `No broken requirements found.`, `All checks passed!`, `Success: no issues found in 5 source files`, `12 passed in 2.85s` |
| Both run entry points, separate ephemeral TCP ports | `make GET /health 200 {"status":"ok","mode":"mock"}` and `python GET /health 200 {"status":"ok","mode":"mock"}` |
| Ignore and index checks | `git status --short --ignored -- .env` returned `!! .env`. `git ls-files -- .env` returned no paths. check-ignore matched .env, sample .key, recording, .db and .sqlite3-wal paths. |
| Staged pre-commit hook | `Scan staged and working files for secrets................................Passed` |
| Architecture render | Mermaid CLI reported `Found 3 mermaid charts in Markdown input`. Rendered system (213193 bytes), sequence (202582 bytes), and data-flow (207341 bytes) SVGs into a temporary directory. |
| Container | `Image fortivex-p0-api Built`, `uid= 65532 env-file-absent=True`; pinned-base Compose smoke returned `healthy running` and `Compose GET /health 200 {"status":"ok","mode":"mock"}`. Test stack removed. |
| API contract | Integration suite parsed docs/API_SPEC.yaml, validated OpenAPI 3.1 and compared the entire document with create_app().openapi(). |
| Pre-commit review | `git diff --cached --check` exited 0. Reviewed the staged file list, credential exclusions, Docker context, tests and the documented stage boundaries. |

## Decisions and issues resolved

- Read STEP-000 for authenticated model results and exact catalog output. Gemini 3.5 Flash-Lite stays provisional for P2. The normal fallback is Gemini A → Gemini B → mock. OpenAI requires evidence of credit and explicit activation.
- [ASSUMED] Set first audible reply targets of p50 ≤ 2.0 s and p95 ≤ 3.5 s. NON_FUNCTIONAL.md defines the clock boundaries and stage budgets. Move profile extraction, sentiment and scoring off the reply path.
- The scanner flagged a credential-shaped test assignment. Reused the test sentinel via a variable and kept the detection rule. Regression fixtures cover staged contents after the working copy is cleaned, a forced .env add and copies of the local value.
- The Docker executable was installed outside the shell PATH. Added its existing resources/bin directory to the **test process** PATH so Docker could invoke its credential helper. Started Docker Desktop, resolved the base image digest and validated the resulting container.
- An inherited Codex Git environment with empty config values caused a pre-commit subprocess to report `missing config value GIT_CONFIG_VALUE_0`. For the local hook check the process used GIT_CONFIG_COUNT=0. No persistent Git configuration was changed. The hook executed.
- Pulled the thin text hero forward to the first grounded booking transaction. Require tags demo-p1-text and demo-voice-booking-crm only after their respective demos pass.

## Limitations and next gate

[UNKNOWN] First-audio performance, English/Hindi speech quality, the winning Gemini pair, account-level quota, final throughput and commercial outcomes. P0 proves liveness and verification. P2 must record 2–3 model benchmarks. P5 must publish paired transcription and synthesis measurements, documented eligibility and Live audio evidence. edge-tts is unofficial and demo-only.

Next gate: P1 React/Vite text turn, deterministic mock, scripted demo, fresh-checkout verification and first demo tag. See LEARNING_LOG.md for the P0 exercise.
