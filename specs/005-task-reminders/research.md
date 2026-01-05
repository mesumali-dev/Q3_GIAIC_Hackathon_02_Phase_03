# Research: Task Reminders & Notifications

**Feature**: 005-task-reminders
**Date**: 2026-01-02
**Purpose**: Document technical decisions, patterns, and best practices for implementing reminder system

## Key Technical Decisions

### 1. On-Demand Reminder Evaluation (No Background Workers)

**Decision**: Evaluate reminders synchronously during API requests (login, page load, refresh) rather than using background workers or cron jobs.

**Rationale**:
- Constraint from spec: "No background workers or cron jobs"
- Simplifies deployment (no additional processes to manage)
- Aligns with serverless architecture (Neon PostgreSQL)
- Acceptable latency for user-initiated actions

**Implementation Pattern**:
```python
# In API endpoint or middleware
def get_due_reminders(user_id: str, db: Session) -> List[Reminder]:
    """
    Query reminders where:
    - remind_at <= current_server_time
    - user_id matches authenticated user
    - is_active = True
    """
    now = datetime.utcnow()
    return db.exec(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.remind_at <= now)
        .where(Reminder.is_active == True)
    ).all()
```

**Tradeoffs**:
- Pro: Simple, stateless, no infrastructure complexity
- Con: Reminders only trigger when user interacts with app (not true real-time)
- Con: User must be online to receive notifications

**Alternatives Considered**:
- Background worker with task queue (rejected: violates constraint, adds complexity)
- Database triggers (rejected: violates stateless backend principle)
- Scheduled cron job (rejected: violates constraint)

---

### 2. Repeat Reminder Logic (Server-Side Calculation)

**Decision**: Calculate next reminder time server-side by incrementing `triggered_count` and updating `remind_at` when repeat interval exists.

**Rationale**:
- Ensures consistent time calculations (server time is authoritative)
- Prevents client-side manipulation of repeat schedules
- Atomic updates prevent duplicate notifications

**Implementation Pattern**:
```python
def process_due_reminder(reminder: Reminder, db: Session) -> None:
    """
    Process a single due reminder:
    1. Increment triggered_count
    2. If triggered_count < repeat_count, calculate next remind_at
    3. If repeat exhausted, deactivate reminder
    """
    reminder.triggered_count += 1

    if reminder.repeat_interval_minutes and reminder.triggered_count < reminder.repeat_count:
        # Schedule next repeat
        reminder.remind_at += timedelta(minutes=reminder.repeat_interval_minutes)
    else:
        # No more repeats, deactivate
        reminder.is_active = False

    db.add(reminder)
    db.commit()
```

**Tradeoffs**:
- Pro: Accurate, secure, prevents race conditions
- Con: Requires database update on every reminder trigger
- Mitigation: Use database transaction to ensure atomicity

**Alternatives Considered**:
- Client-side calculation (rejected: security risk, inconsistent times)
- Pre-generate all repeat instances (rejected: storage overhead, inflexible)

---

### 3. Notification Model vs. Ephemeral Response

**Decision**: Return due reminders as API response data rather than persisting separate Notification entities.

**Rationale**:
- Spec's "Notification" entity represents UI state, not database persistence
- Simplifies data model (one table instead of two)
- Reminder deletion immediately stops notifications (no orphaned notification records)
- Frontend manages notification display state

**Implementation Pattern**:
```python
# Backend API
@router.get("/{user_id}/reminders/due")
async def get_due_reminders(user_id: str, db: Session = Depends(get_db)):
    """
    Return all due reminders for user.
    Frontend displays these as notifications.
    """
    reminders = get_due_reminders(user_id, db)
    # Process each reminder (update triggered_count, calculate next)
    for reminder in reminders:
        process_due_reminder(reminder, db)
    return reminders
```

```typescript
// Frontend state
const [notifications, setNotifications] = useState<Reminder[]>([]);

useEffect(() => {
  fetchDueReminders().then(setNotifications);
}, []);
```

**Tradeoffs**:
- Pro: Simpler data model, no data synchronization issues
- Con: No persistent notification history (acceptable per spec's "Out of Scope")
- Con: Dismissed notifications reappear on next fetch (mitigated by deactivating reminder)

**Alternatives Considered**:
- Separate Notification table (rejected: unnecessary complexity for ephemeral UI state)
- Mark reminders as "viewed" (rejected: spec requires deletion, not viewing)

---

### 4. Reminder Deletion Strategy (Hard Delete)

**Decision**: Hard delete reminders from database when user deletes a notification.

**Rationale**:
- Spec requirement: "deleted reminders never reappear"
- Simplifies queries (no need to filter soft-deleted records)
- No audit trail required (per spec's "Out of Scope": reminder history)

**Implementation Pattern**:
```python
@router.delete("/{user_id}/reminders/{reminder_id}")
async def delete_reminder(
    user_id: str,
    reminder_id: int,
    db: Session = Depends(get_db)
):
    reminder = db.get(Reminder, reminder_id)
    if not reminder or reminder.user_id != user_id:
        raise HTTPException(status_code=404)

    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}
```

**Tradeoffs**:
- Pro: Simple, guaranteed no reappearance
- Con: Permanent data loss (acceptable per spec)
- Mitigation: Frontend confirms deletion before API call

**Alternatives Considered**:
- Soft delete with `deleted_at` timestamp (rejected: adds complexity, no requirement for history)
- Archive to separate table (rejected: out of scope)

---

### 5. Timezone Handling (Server UTC, Client Local Display)

**Decision**: Store all reminder times in UTC on the server; convert to user's local timezone for display only.

**Rationale**:
- Database best practice for timestamp fields
- Handles daylight saving time transitions
- Supports future multi-timezone user base

**Implementation Pattern**:
```python
# Backend model
class Reminder(SQLModel, table=True):
    remind_at: datetime  # Stored in UTC

# Backend API
reminder.remind_at = datetime.fromisoformat(request.remind_at).astimezone(timezone.utc)
```

```typescript
// Frontend form submission
const reminderTime = new Date(formData.date + 'T' + formData.time);
const isoString = reminderTime.toISOString();  // Converts to UTC
await createReminder({ remind_at: isoString });

// Frontend display
const localTime = new Date(reminder.remind_at).toLocaleString();
```

**Tradeoffs**:
- Pro: Portable, handles timezone changes correctly
- Con: Requires frontend/backend time conversion
- Mitigation: Use ISO 8601 format for all API communication

**Alternatives Considered**:
- Store timezone with each reminder (rejected: unnecessary for single-user MVP)
- Use user's local timezone (rejected: fragile, breaks on travel/DST)

---

### 6. Task Deletion with Active Reminders (Cascade Delete)

**Decision**: When a task is deleted, cascade delete all associated reminders.

**Rationale**:
- Prevents orphaned reminders referencing non-existent tasks
- Simplifies UI (no need to handle "task deleted" error state)
- Aligns with user expectation (deleting task removes all related data)

**Implementation Pattern**:
```python
# In Task model
class Task(SQLModel, table=True):
    # ... existing fields

# In Reminder model
class Reminder(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", ondelete="CASCADE")
```

**Tradeoffs**:
- Pro: Referential integrity maintained automatically
- Con: Deleting task silently removes reminders (acceptable per spec)
- Mitigation: Could add frontend warning "This will delete X reminders" (future enhancement)

**Alternatives Considered**:
- Prevent task deletion with active reminders (rejected: poor UX, spec doesn't require)
- Orphan reminders with null task_id (rejected: violates data integrity)

---

## Best Practices Findings

### SQLModel with PostgreSQL

**Pattern**: Use SQLModel's `Field` with `foreign_key` and `index=True` for optimal query performance.

```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class Reminder(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    task_id: int = Field(foreign_key="task.id", ondelete="CASCADE")
    remind_at: datetime = Field(index=True)  # Index for fast due-reminder queries
    repeat_interval_minutes: int | None = None
    repeat_count: int | None = None
    triggered_count: int = Field(default=0)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes Rationale**:
- `user_id`: Queries always filter by user (user-scoped data)
- `remind_at`: Range queries for due reminders (`remind_at <= now`)
- `is_active`: Filter out deactivated reminders

**Source**: SQLModel docs, PostgreSQL index best practices

---

### FastAPI Dependency Injection for Auth

**Pattern**: Reuse existing JWT validation middleware as dependency for reminder endpoints.

```python
from fastapi import Depends, HTTPException
from src.middleware.auth import verify_jwt

@router.post("/{user_id}/reminders")
async def create_reminder(
    user_id: str,
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    jwt_user_id: str = Depends(verify_jwt)
):
    if user_id != jwt_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # ... create reminder
```

**Source**: Existing task API implementation, FastAPI security docs

---

### Next.js 16 App Router with Client Components

**Pattern**: Use client components for interactive reminder UI with `"use client"` directive.

```typescript
// src/components/reminders/ReminderForm.tsx
"use client";

import { useState } from "react";

export function ReminderForm({ taskId }: { taskId: number }) {
  const [reminderTime, setReminderTime] = useState("");
  const [repeatInterval, setRepeatInterval] = useState<number | null>(null);

  // Form submission logic
}
```

**Rationale**:
- Interactive forms require client-side state
- Date/time pickers need browser APIs
- Real-time notification badge updates

**Source**: Next.js 16 App Router docs, existing frontend patterns

---

### Tailwind CSS for Responsive Notification UI

**Pattern**: Use Tailwind utility classes for responsive notification badge and dropdown.

```typescript
// Notification badge
<button className="relative p-2 hover:bg-gray-100 rounded-full">
  <BellIcon className="h-6 w-6" />
  {count > 0 && (
    <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
      {count}
    </span>
  )}
</button>
```

**Source**: Tailwind CSS docs, existing UI component patterns

---

## Research Summary

All technical unknowns from the Technical Context section have been resolved:

1. ✅ **Reminder evaluation strategy**: On-demand during API requests
2. ✅ **Repeat logic implementation**: Server-side calculation with atomic updates
3. ✅ **Notification persistence**: Ephemeral (API response, not database table)
4. ✅ **Deletion strategy**: Hard delete from database
5. ✅ **Timezone handling**: UTC storage, local display
6. ✅ **Task deletion behavior**: Cascade delete reminders

**No blockers identified.** Implementation can proceed to Phase 1 (Data Model & Contracts).
