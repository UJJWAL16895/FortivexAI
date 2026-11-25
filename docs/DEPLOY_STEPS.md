# Deploy the public preview

Host comparison checked 26 November 2026.

| Option | HTTPS WebSockets and idle behavior | Free limit and data |
|---|---|---|
| Render Free Web Service | Supports inbound WebSockets and managed TLS. Spins down after 15 idle minutes. Docs estimate about one minute to wake. | 750 free instance-hours/workspace/month. The free filesystem is ephemeral across sleep/restart/redeploy. [Render Free](https://render.com/docs/free) · [WebSockets](https://render.com/docs/websocket) |
| Google Cloud Run | Supports WebSockets with request timeouts up to 60 minutes. With zero minimum instances, the next request can encounter a cold start. An open socket keeps the instance active. | Request-based free allowance uses tier-1 benchmarks of 180,000 vCPU-s, 360,000 GiB-s and 2 million requests/month. Billing mode and region matter. SQLite on the instance filesystem is ephemeral. [Pricing](https://cloud.google.com/run/pricing) · [WebSockets](https://docs.cloud.google.com/run/docs/triggering/websockets) |

Choose Render Free for an optional mock preview. Use local Docker or a host with a persistent volume for showing the restart guarantee. Do not deploy this Python backend to Vercel serverless. Cloud startup, quotas and private data durability on a hosted service are unverified.

## Render steps

1. Create or sign in to your Render account. In Account Settings → Git Deployment Credentials add and authorize the GitHub connection. The account owner does these steps.
2. Select New → Web Service → Git Provider and select FortivexAI. Choose the verified submission commit or a branch pointing to it. Set Language to Docker, leave root directory blank, set Dockerfile Path to infra/Dockerfile and use the repository root as the build context. Choose a region near the evaluator and Free for this mock preview.
3. In Advanced, set Health Check Path to /health. Apply the environment settings below in Render Environment. Deploy, then inspect startup logs for the self-check.
4. Open the provided HTTPS URL. Play the scripted call, open /console, confirm the public/mock banner, and verify the socket, cited price and a synthetic booking. Refresh and inspect CRM and Insights. Restart or sleep on Free can erase the database. Check again after waking the app.
5. Keep live disabled for the public link. If you intentionally enable it, use a long unique evaluator code, share it only with the intended evaluator, and verify a fresh private window cannot access protected HTTP or sockets. Check that unlocking grants console access and rate caps respond. Restore mock after the evaluation.

| Environment variable | Hosting value |
|---|---|
| PORT | Set 8000, or leave the platform-provided value if its build confirms routing. |
| PUBLIC_DEMO | true |
| AGENT_MODE | mock |
| PUBLIC_LIVE_ENABLED | false |
| PUBLIC_REQUESTS_PER_MINUTE | 20 (rolling per trusted peer) |
| PUBLIC_DAILY_REQUEST_CAP | 250 (rolling single-process total) |
| CRM_PATH | /app/data/runtime/crm.sqlite3 |
| KNOWLEDGE_EMBEDDINGS | false |
| VOICE_STT | gemini, forced in public mode to skip local downloads |
| VOICE_TTS | browser for public mock; choose an approved live TTS only if needed |
| PUBLIC_ACCESS_CODE | Leave unset for the unauthenticated synthetic mock. Required, minimum 16 characters, to turn on public live. Set a random unique secret through Render. |
| GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FALLBACK_MODEL | Leave API key unset for mock. For intentional live set the key through Render and models to the IDs verified in STEP-003. |
| FORWARDED_ALLOW_IPS | Set only to proxy peers you have verified with the platform. Without a trusted forwarded client identity, limits safely apply to the apparent peer and may be shared. |

The access-code gate issues a Secure, HttpOnly browser cookie for the current UTC day. The per-IP and daily counters are in one process and reset on restart. Provider budgets add a second process-local limit. Use one worker for this demo. A production quota budget needs shared durable counters. The protected live routes still need HTTPS and careful handling of synthetic contacts. Verified locally with HTTP and socket tests and a Docker smoke check. Account setup, proxy IP handling and hosted HTTPS are unverified until you deploy. [Render first deployment](https://render.com/docs/your-first-deploy) · [Docker settings](https://render.com/docs/docker)
