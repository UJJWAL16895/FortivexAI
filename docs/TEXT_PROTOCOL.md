# P1 text WebSocket

Connect to /ws/text on the same origin as the console. Local scripts may omit the Origin header. The server emits `{"type":"ready","provider":"mock"}` on connection.

Send one turn as `{"text":"Can I manage three stores?"}`. The server trims whitespace and accepts 1–500 characters. Each valid turn emits one event with type reply, text and latency_ms. Latency measures provider compute on the server and excludes the socket, rendering and any future audio.

Malformed JSON, oversized application text and unsupported frames receive type error with a short text message. The next valid request on the same connection can still succeed. The native and container server configs bound WebSocket messages at 16 KiB. The console keeps transcript text in React state for the current page. The P1 provider is a deterministic mock independent of cloud credentials.
