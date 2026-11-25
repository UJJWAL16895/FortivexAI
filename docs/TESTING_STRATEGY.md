# Testing strategy

P0 exercises mock defaults, startup validation, secret masking, real/copied/staged credential detection, and HTTP contract consistency. Git fixtures build disposable repositories. The health integration runs an ASGI request and the manual gate starts an actual TCP listener. CI runs the same Python verification command in Windows and Linux jobs.

Subsequent gates add deterministic provider fixtures, database race and replay checks, retrieval expected-source and abstention sets, and a browser hero run. Keep network benchmarks separate from offline CI. Record model/version, language, dataset, hardware, sample count, clocks, failure count, and warm/cold state. Compare identical inputs and report both successful timings and failed requests.

Use only synthetic examples in Git. For every booking test inspect committed database state, not just assistant text. For fallback tests inject 429, 503, invalid output, early stream close, late audio after cancellation and a shared project cooldown.

To reproduce the architecture syntax check, install the docs-only lock with `npm ci --prefix tools/diagrams`. Use an installed Chrome executable via a local Puppeteer JSON file containing executablePath. Create a temporary output directory and run the tool below. P1 renders four diagrams, including the current text path. The project keeps the Mermaid sources in Markdown.

```powershell
& tools/diagrams/node_modules/.bin/mmdc.cmd -i docs/ARCHITECTURE.md -o "$env:TEMP/architecture.md" -p $browserConfigPath
```
