# STEP-011 · Persistent insights

Before this change a restart cleared analysis. Now the worker writes one validated report per analyzed call to the same SQLite file as CRM. Reports include the ordered sentiment labels, score, reasons, summary and draft. The dashboard calculates booked calls divided by all saved analyzed calls. The newest 50 reports are displayed separately from the counts. Empty conversations and incomplete queue jobs do not enter the denominator. Pre-upgrade in-memory reports cannot be recovered.

[VERIFIED] The restart fixture failed first with `KeyError: 'totals'`. It now exercises two app lifespans against one database. An empty connection, an unbooked call and a booked call produce 2 analyzed calls, 1 booking, and a 50% rate. Saved scores and sentiments are checked.
