# ADR 003 · The database authorizes booking

Accepted for design. Parallel callers and retried confirmations can collide. Use UTC slots, explicit user confirmation, unique active slot constraints, idempotent request keys and a single transaction for appointment and outbox. The assistant may propose arguments. Use committed receipts for confirmation. SQLite keeps the first demo local. PostgreSQL migration must preserve these invariants under load.
