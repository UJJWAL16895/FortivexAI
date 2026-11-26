# STEP-020 · Live Call Cockpit

Scope was the console presentation. Server, API and WebSocket contract, historical measurements and existing browser assertions were kept. The branch began at the pushed pre-console-ui rollback tag on be7aaf6.

## Verification

| Check | Evidence |
|---|---|
| Windows make verify | [VERIFIED] Secret scan clean. No broken requirements. Ruff passed, mypy found no issues in 25 source files, 46 pytest tests passed, and Vite built the production client. |
| Chrome cockpit | [VERIFIED] At 1440 and 390 px the check printed: connected, guide, source drawer, abstention, booking, CRM, saved analysis, reset, fallback, presenter and keyboard passed; zero errors and overflow. The 768 px check verified two columns, connection, the keyboard skip link, no errors and no overflow. External HTTP requests were blocked for these responsive journeys. |
| Existing Chrome text hero | [VERIFIED] Citation, timezone, one booking, one CRM lead and returning caller verified. Insights panel also verified completed bookings, report and follow-up draft. |
| Chrome synthetic mic | [VERIFIED] The existing mock fixture confirmed three stores. The cockpit-specific check confirmed that microphone amplitude changed the orb scale, playback emitted Speaking and the actual timing measurement populated. Physical microphone performance remains unmeasured. |
| Showcase and export | [VERIFIED] Three overview widths passed, plus the blocked-external scripted player and console connection. Markdown export fixture passed. |
| Lighthouse | [VERIFIED] Lighthouse 13.6.0 mobile profile on Windows Chrome against localhost /console returned Performance 97, Accessibility 100 and color contrast pass. One lab run. |
| Bundle scan | [VERIFIED] The release scanner found zero credential candidates in 13 build files. The page uses system fonts and ships no external tracking. |

The pre-console UI built a console chunk of 17.45 kB raw and 6.05 kB gzip. The cockpit console chunk was 30.65 kB raw and 10.60 kB gzip, a gain of 13.20 kB raw and 4.55 kB gzip. The additional route-only CSS was 17.93 kB raw and 4.74 kB gzip. The CRM/Insights record module loads on demand and was 3.30 kB raw and 1.22 kB gzip. Shared JS rose from 222.05 to 222.28 kB raw and from 69.68 to 69.76 kB gzip.

## Reproduce

Start an isolated mock server with ALLOW_FALLBACK_DEMO=true and a temporary CRM_PATH, then run:

```powershell
$chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
$fixture = Join-Path $env:TEMP 'fortivex-mic-input.wav'
node tests/e2e/cockpit_browser.mjs http://127.0.0.1:8004 $chrome docs/diagrams/ui $fixture
node tests/e2e/voice_browser.mjs http://127.0.0.1:8004 $fixture $chrome mock en 2500 confirm
```

The optional WAV argument uses the same synthetic microphone fixture as the existing voice check. The console never generates a mock conversation automatically. Sentiment and BANT appear after a saved report. The API exposes workspace reports without a session ID, so the cards identify the latest saved report. The API exposes the confirmed time and timezone but no separate receipt ID. Text language tags are limited to observable script and explicit voice hints. No latency or business metric was inferred from missing data.

## Screenshots

| State | Desktop | Mobile |
|---|---|---|
| Empty | [Desktop](../diagrams/ui/cockpit-desktop-empty.png) | [Mobile](../diagrams/ui/cockpit-mobile-empty.png) |
| Mid-conversation | [Desktop](../diagrams/ui/cockpit-desktop-conversation.png) | [Mobile](../diagrams/ui/cockpit-mobile-conversation.png) |
| Booking | [Desktop](../diagrams/ui/cockpit-desktop-receipt.png) | [Mobile](../diagrams/ui/cockpit-mobile-receipt.png) |
| Insights | [Desktop](../diagrams/ui/cockpit-desktop-insights.png) | [Mobile](../diagrams/ui/cockpit-mobile-insights.png) |

Screenshots show synthetic contacts and actual fixture outcomes.
