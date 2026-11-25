# STEP-016 · Booking changes

Before, a reserved demo could only be confirmed again. Ask “cancel booking” or “reschedule booking” in its current session, then speak the explicit confirmation requested. Cancellation is repeat-safe in that session. One SQLite UPDATE moves an owned slot only when the new slot is free. A taken slot leaves the original reservation intact.

## Quiz

1. **What does reschedule modify?** One owned appointment row.
2. **Can it steal a taken slot?** The unique key rejects the move.
3. **Can a generic yes cancel?** The explicit cancellation phrase is required.
4. **What does duplicate cancellation do?** It returns the same result.
5. **Which calls can edit an appointment today?** The session that reserved it.
