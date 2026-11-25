# STEP-019 · Release audit

26 November 2026. Prepared the release handoff, checked claims against code and recorded output, and ran fresh-clone regressions. The original PRD gates that are still partial are listed in PRD.md. No application features were added during this audit.

## Fresh-clone verification

Application snapshot c28f478 from the public remote. Installed Python 3.13.2 and Node 24.11.1 on Windows. The initial setup used package caches and network-capable install commands. The demo had no credentials or existing database.

```powershell
git clone https://github.com/UJJWAL16895/FortivexAI.git fortivex-audit
Set-Location fortivex-audit
$python = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python313/python.exe'
& $python scripts/tasks.py setup
& .\.venv\Scripts\python.exe scripts/tasks.py verify
& .\.venv\Scripts\python.exe scripts/tasks.py demo --port 0
```

```text
pre-commit installed at .git\hooks\pre-commit
added 18 packages in 2s
Secret scan: clean (Git index and non-ignored working tree).
No broken requirements found.
All checks passed!
Success: no issues found in 25 source files
46 passed in 15.86s
Demo passed: mock recall, cited price, confirmed booking, saved CRM and insights.
```

## Chrome and live verification

Installed the pinned browser utilities with `PUPPETEER_SKIP_DOWNLOAD=true` in PowerShell and `npm ci --prefix tools/diagrams --no-audit --no-fund`. Used an isolated CRM_PATH for each server. The mock server ran with `scripts/tasks.py run --port 8108`. Chrome was the system installation. Set CHECK_HERO_INSIGHTS=1.

| Check | Command and observed output |
|---|---|
| Text | `node tests/e2e/hero_browser.mjs http://127.0.0.1:8108 $chrome` → Text hero: citation, timezone, one booking, one CRM lead, returning caller verified. |
| Showcase | `node tests/e2e/showcase_browser.mjs http://127.0.0.1:8108 $chrome` → 390, 768 and 1440 px anchors valid, no overflow. Offline blocked-external showcase, scripted player and console connection passed. |
| Mock mic | `node tests/e2e/voice_browser.mjs http://127.0.0.1:8108 $wav $chrome mock en 2500 confirm` → Confirmed 3 stores in the lead profile. Chrome showed zero page errors. |
| Export | `node tests/e2e/report_export.mjs` → Derived Markdown export passed. |
| Live-mode voice | `node tests/e2e/hero_browser.mjs http://127.0.0.1:8109 $chrome $voiceFolder` → Voice hero: citation, timezone, one booking, one CRM lead, returning caller verified. |
| Insights in both journeys | Insights panel: completed booking count, report and follow-up draft verified. |
| Separate live Gemini smoke | Three short synthetic general turns reached Gemini A active. The filter returned policy mode on all three because the returned text did not pass the reviewed-phrase check. The browser hero uses reviewed cards and booking code for those business turns. |

For the live test the clean clone installed `requirements-speech-eval.lock` via pip, reused the laptop's downloaded Base and Small weights, and ran Uvicorn with `src.api.app:create_app --factory --host 127.0.0.1 --port 8109 --ws websockets-sansio --no-access-log`. The launcher read the ignored original .env into the child process without copying or printing keys, set AGENT_MODE=live, PUBLIC_DEMO=false, VOICE_STT=local and VOICE_TTS=edge, and used a dedicated database. The three WAV inputs were synthesized for the price, booking and confirmation phrases. Chrome exercised actual capture, transcription and playback events with those files. Physical capture and speech quality remain unmeasured.

GitHub Actions ran application snapshot c28f478 on Ubuntu and Windows. [Both jobs passed](https://github.com/UJJWAL16895/FortivexAI/actions/runs/45714608072). Tagging also requires both jobs on the final audit commit.

## Security evidence

```powershell
git fetch --all --tags
& .\.venv\Scripts\python.exe scripts/audit_release.py
git check-ignore -- .env
git ls-files -- .env
```

[VERIFIED] All scanned scopes had zero credential and prohibited-path hits. The compiled bundle had 11 files and zero contact candidates. Git reported .env ignored and no tracked path. Candidate fixture addresses and SVG coordinate matches were reviewed. See CLAIMS_AUDIT.md for scope and limitations.

## Quiz with answers

1. **What did the fresh clone check?** Installation, build, static checks, automated tests and the mock business workflow without secrets.
2. **Does the voice hero need Gemini to invent a pricing answer?** No. Reviewed cards supply known facts and booking code confirms real SQLite state.
3. **What happened in the model smoke?** Gemini A returned data. The strict speech policy selected its reviewed response when generated text missed the allowlist.
4. **What carries over when the server restarts?** Completed reports, bookings and CRM entries in the persisted database. Public quota counters reset.
5. **What tag is the fallback before the showcase?** demo-final. It keeps the verified local application with the core sales journey.
