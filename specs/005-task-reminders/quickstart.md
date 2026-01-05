# Quickstart: Task Reminders & Notifications

**Feature**: 005-task-reminders
**Date**: 2026-01-02
**For**: Developers implementing the reminder system

## Overview

This guide provides a step-by-step walkthrough for implementing the task reminders and notifications feature. Follow the phases in order for incremental delivery.

## Prerequisites

- Backend: Python 3.11+, FastAPI, SQLModel, uv package manager
- Frontend: Node.js 18+, Next.js 16+, TypeScript 5.x
- Database: Neon PostgreSQL connection configured
- Authentication: Existing JWT auth system working
- Existing Task CRUD functionality operational

## Implementation Phases

### Phase 1: Database Schema (Backend)

**Time Estimate**: 30 minutes
**Deliverable**: Reminder table created and tested

#### Steps:

1. **Create Reminder Model** (`backend/src/models/reminder.py`):
   ```python
   from datetime import datetime
   from typing import Optional
   from sqlmodel import Field, SQLModel

   class Reminder(SQLModel, table=True):
       id: Optional[int] = Field(default=None, primary_key=True)
       user_id: str = Field(foreign_key="user.id", index=True)
       task_id: int = Field(
           foreign_key="task.id",
           sa_column_kwargs={"ondelete": "CASCADE"}
       )
       remind_at: datetime = Field(index=True)
       repeat_interval_minutes: Optional[int] = Field(default=None, gt=0)
       repeat_count: Optional[int] = Field(default=None, gt=0)
       triggered_count: int = Field(default=0, ge=0)
       is_active: bool = Field(default=True, index=True)
       created_at: datetime = Field(default_factory=datetime.utcnow)
   ```

2. **Update Database Module** (`backend/src/database.py`):
   ```python
   def create_tables() -> None:
       from src.models.task import Task
       from src.models.user import User
       from src.models.reminder import Reminder  # Add this import

       SQLModel.metadata.create_all(engine)
   ```

3. **Run Migration**:
   ```bash
   cd backend
   uv run python -c "from src.database import create_tables; create_tables()"
   ```

4. **Verify Table Created**:
   ```bash
   # Connect to Neon PostgreSQL and check
   psql $DATABASE_URL -c "\d reminder"
   ```

**Acceptance Criteria**:
- [ ] Reminder table exists in database
- [ ] Foreign keys reference user and task tables
- [ ] Indexes created on user_id, remind_at, is_active
- [ ] Cascade delete configured for task_id

---

### Phase 2: Reminder Service Logic (Backend)

**Time Estimate**: 45 minutes
**Deliverable**: Core reminder evaluation logic implemented

#### Steps:

1. **Create Reminder Service** (`backend/src/services/reminder_service.py`):
   ```python
   from datetime import datetime, timedelta
   from typing import List
   from sqlmodel import Session, select
   from src.models.reminder import Reminder
   from src.models.task import Task

   def get_due_reminders(user_id: str, db: Session) -> List[dict]:
       """Fetch and process due reminders for user."""
       now = datetime.utcnow()
       statement = (
           select(Reminder, Task)
           .join(Task, Reminder.task_id == Task.id)
           .where(Reminder.user_id == user_id)
           .where(Reminder.is_active == True)
           .where(Reminder.remind_at <= now)
           .order_by(Reminder.remind_at)
       )

       results = db.exec(statement).all()
       due_reminders = []

       for reminder, task in results:
           # Process reminder (update state)
           process_reminder(reminder, db)

           # Build response
           due_reminders.append({
               "id": reminder.id,
               "remind_at": reminder.remind_at,
               "triggered_count": reminder.triggered_count,
               "repeat_count": reminder.repeat_count,
               "task_id": task.id,
               "task_title": task.title,
               "task_description": task.description,
           })

       return due_reminders

   def process_reminder(reminder: Reminder, db: Session) -> None:
       """Process a due reminder: increment count, handle repeats."""
       reminder.triggered_count += 1

       # Check if more repeats remain
       if (
           reminder.repeat_interval_minutes is not None
           and reminder.repeat_count is not None
           and reminder.triggered_count < reminder.repeat_count
       ):
           # Schedule next repeat
           reminder.remind_at += timedelta(
               minutes=reminder.repeat_interval_minutes
           )
       else:
           # No more repeats, deactivate
           reminder.is_active = False

       db.add(reminder)
       db.commit()
   ```

2. **Test Service Logic**:
   ```python
   # backend/tests/test_reminder_service.py
   from datetime import datetime, timedelta
   from src.services.reminder_service import get_due_reminders, process_reminder
   from src.models.reminder import Reminder

   def test_get_due_reminders(db_session, test_user, test_task):
       # Create overdue reminder
       reminder = Reminder(
           user_id=test_user.id,
           task_id=test_task.id,
           remind_at=datetime.utcnow() - timedelta(hours=1)
       )
       db_session.add(reminder)
       db_session.commit()

       # Fetch due reminders
       due = get_due_reminders(test_user.id, db_session)

       assert len(due) == 1
       assert due[0]["task_id"] == test_task.id
   ```

**Acceptance Criteria**:
- [ ] get_due_reminders returns overdue reminders with task details
- [ ] process_reminder increments triggered_count
- [ ] Repeating reminders calculate next remind_at correctly
- [ ] Exhausted reminders are deactivated (is_active=false)
- [ ] Unit tests pass

---

### Phase 3: Reminder API Endpoints (Backend)

**Time Estimate**: 60 minutes
**Deliverable**: REST API endpoints for reminder CRUD

#### Steps:

1. **Create API Router** (`backend/src/api/reminders.py`):
   ```python
   from fastapi import APIRouter, Depends, HTTPException, status
   from sqlmodel import Session
   from src.database import get_db
   from src.middleware.auth import verify_jwt
   from src.models.reminder import Reminder
   from src.services.reminder_service import get_due_reminders
   from datetime import datetime
   from typing import Optional

   router = APIRouter(prefix="/api/{user_id}/reminders", tags=["reminders"])

   @router.post("", status_code=status.HTTP_201_CREATED)
   async def create_reminder(
       user_id: str,
       task_id: int,
       remind_at: datetime,
       repeat_interval_minutes: Optional[int] = None,
       repeat_count: Optional[int] = None,
       db: Session = Depends(get_db),
       jwt_user_id: str = Depends(verify_jwt),
   ):
       if user_id != jwt_user_id:
           raise HTTPException(status_code=403, detail="Forbidden")

       reminder = Reminder(
           user_id=user_id,
           task_id=task_id,
           remind_at=remind_at,
           repeat_interval_minutes=repeat_interval_minutes,
           repeat_count=repeat_count,
       )
       db.add(reminder)
       db.commit()
       db.refresh(reminder)
       return reminder

   @router.get("/due")
   async def get_due_reminders_endpoint(
       user_id: str,
       db: Session = Depends(get_db),
       jwt_user_id: str = Depends(verify_jwt),
   ):
       if user_id != jwt_user_id:
           raise HTTPException(status_code=403, detail="Forbidden")

       return get_due_reminders(user_id, db)

   @router.delete("/{reminder_id}")
   async def delete_reminder(
       user_id: str,
       reminder_id: int,
       db: Session = Depends(get_db),
       jwt_user_id: str = Depends(verify_jwt),
   ):
       if user_id != jwt_user_id:
           raise HTTPException(status_code=403, detail="Forbidden")

       reminder = db.get(Reminder, reminder_id)
       if not reminder or reminder.user_id != user_id:
           raise HTTPException(status_code=404, detail="Reminder not found")

       db.delete(reminder)
       db.commit()
       return {"message": "Reminder deleted"}
   ```

2. **Register Router** (`backend/src/main.py`):
   ```python
   from src.api import reminders

   app.include_router(reminders.router)
   ```

3. **Test API Endpoints**:
   ```bash
   uv run pytest backend/tests/test_reminder_api.py -v
   ```

**Acceptance Criteria**:
- [ ] POST /api/{user_id}/reminders creates reminder
- [ ] GET /api/{user_id}/reminders/due returns due reminders
- [ ] DELETE /api/{user_id}/reminders/{id} deletes reminder
- [ ] All endpoints enforce JWT auth
- [ ] user_id mismatch returns 403
- [ ] API tests pass

---

### Phase 4: Frontend API Client (Frontend)

**Time Estimate**: 30 minutes
**Deliverable**: TypeScript client for reminder API

#### Steps:

1. **Create API Client** (`frontend/src/lib/api/reminders.ts`):
   ```typescript
   import { authFetch } from './auth';  // Existing auth fetch wrapper

   export interface Reminder {
     id: number;
     user_id: string;
     task_id: number;
     remind_at: string;
     repeat_interval_minutes?: number;
     repeat_count?: number;
     triggered_count: number;
     is_active: boolean;
     created_at: string;
   }

   export interface ReminderWithTask extends Reminder {
     task_title: string;
     task_description?: string;
   }

   export async function createReminder(
     userId: string,
     data: {
       task_id: number;
       remind_at: string;
       repeat_interval_minutes?: number;
       repeat_count?: number;
     }
   ): Promise<Reminder> {
     const response = await authFetch(`/api/${userId}/reminders`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(data),
     });
     return response.json();
   }

   export async function getDueReminders(userId: string): Promise<ReminderWithTask[]> {
     const response = await authFetch(`/api/${userId}/reminders/due`);
     return response.json();
   }

   export async function deleteReminder(
     userId: string,
     reminderId: number
   ): Promise<void> {
     await authFetch(`/api/${userId}/reminders/${reminderId}`, {
       method: 'DELETE',
     });
   }
   ```

**Acceptance Criteria**:
- [ ] API client exports typed functions
- [ ] All functions use authFetch for JWT attachment
- [ ] TypeScript types match backend schemas

---

### Phase 5: Reminder Creation UI (Frontend)

**Time Estimate**: 60 minutes
**Deliverable**: Form to create reminders

#### Steps:

1. **Create ReminderForm Component** (`frontend/src/components/reminders/ReminderForm.tsx`):
   ```typescript
   "use client";

   import { useState } from 'react';
   import { createReminder } from '@/lib/api/reminders';

   export function ReminderForm({ taskId, userId, onSuccess }: {
     taskId: number;
     userId: string;
     onSuccess: () => void;
   }) {
     const [date, setDate] = useState('');
     const [time, setTime] = useState('');
     const [repeatInterval, setRepeatInterval] = useState<number | ''>('');
     const [repeatCount, setRepeatCount] = useState<number | ''>('');

     const handleSubmit = async (e: React.FormEvent) => {
       e.preventDefault();

       const reminderTime = new Date(`${date}T${time}`);
       await createReminder(userId, {
         task_id: taskId,
         remind_at: reminderTime.toISOString(),
         repeat_interval_minutes: repeatInterval || undefined,
         repeat_count: repeatCount || undefined,
       });

       onSuccess();
     };

     return (
       <form onSubmit={handleSubmit} className="space-y-4">
         <div>
           <label className="block text-sm font-medium">Date</label>
           <input
             type="date"
             value={date}
             onChange={(e) => setDate(e.target.value)}
             required
             className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
           />
         </div>
         <div>
           <label className="block text-sm font-medium">Time</label>
           <input
             type="time"
             value={time}
             onChange={(e) => setTime(e.target.value)}
             required
             className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
           />
         </div>
         <div>
           <label className="block text-sm font-medium">
             Repeat Interval (minutes, optional)
           </label>
           <input
             type="number"
             value={repeatInterval}
             onChange={(e) => setRepeatInterval(Number(e.target.value) || '')}
             min="1"
             max="1440"
             className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
           />
         </div>
         <div>
           <label className="block text-sm font-medium">
             Repeat Count (optional)
           </label>
           <input
             type="number"
             value={repeatCount}
             onChange={(e) => setRepeatCount(Number(e.target.value) || '')}
             min="1"
             max="100"
             className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
           />
         </div>
         <button
           type="submit"
           className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
         >
           Set Reminder
         </button>
       </form>
     );
   }
   ```

**Acceptance Criteria**:
- [ ] Form accepts date, time, repeat interval, repeat count
- [ ] Date/time converts to ISO 8601 UTC
- [ ] Validation prevents invalid values
- [ ] Success callback triggered after creation

---

### Phase 6: Notification UI (Frontend)

**Time Estimate**: 90 minutes
**Deliverable**: Navbar badge, dropdown, and modal for notifications

#### Steps:

1. **Create NotificationBadge** (`frontend/src/components/reminders/NotificationBadge.tsx`):
   ```typescript
   "use client";

   export function NotificationBadge({ count }: { count: number }) {
     if (count === 0) return null;

     return (
       <span className="absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
         {count > 99 ? '99+' : count}
       </span>
     );
   }
   ```

2. **Create NotificationDropdown** (`frontend/src/components/reminders/NotificationDropdown.tsx`):
   ```typescript
   "use client";

   import { ReminderWithTask } from '@/lib/api/reminders';

   export function NotificationDropdown({
     notifications,
     onClickNotification,
     onDeleteNotification,
   }: {
     notifications: ReminderWithTask[];
     onClickNotification: (notification: ReminderWithTask) => void;
     onDeleteNotification: (id: number) => void;
   }) {
     return (
       <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg z-50">
         {notifications.length === 0 ? (
           <div className="p-4 text-center text-gray-500">
             No notifications
           </div>
         ) : (
           <ul className="max-h-96 overflow-y-auto">
             {notifications.map((notif) => (
               <li
                 key={notif.id}
                 className="p-4 border-b hover:bg-gray-50 cursor-pointer"
               >
                 <div onClick={() => onClickNotification(notif)}>
                   <h4 className="font-semibold">{notif.task_title}</h4>
                   <p className="text-sm text-gray-600">
                     {new Date(notif.remind_at).toLocaleString()}
                   </p>
                 </div>
                 <button
                   onClick={(e) => {
                     e.stopPropagation();
                     onDeleteNotification(notif.id);
                   }}
                   className="mt-2 text-sm text-red-600 hover:text-red-800"
                 >
                   Dismiss
                 </button>
               </li>
             ))}
           </ul>
         )}
       </div>
     );
   }
   ```

3. **Create NotificationModal** (`frontend/src/components/reminders/NotificationModal.tsx`):
   ```typescript
   "use client";

   import { ReminderWithTask } from '@/lib/api/reminders';

   export function NotificationModal({
     notification,
     onClose,
     onDelete,
   }: {
     notification: ReminderWithTask | null;
     onClose: () => void;
     onDelete: (id: number) => void;
   }) {
     if (!notification) return null;

     return (
       <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
         <div className="bg-white rounded-lg p-6 max-w-md w-full">
           <h2 className="text-xl font-bold mb-4">Reminder</h2>
           <div className="space-y-2">
             <p><strong>Task:</strong> {notification.task_title}</p>
             {notification.task_description && (
               <p><strong>Description:</strong> {notification.task_description}</p>
             )}
             <p><strong>Reminder Time:</strong> {new Date(notification.remind_at).toLocaleString()}</p>
             {notification.repeat_count && (
               <p><strong>Repeats:</strong> {notification.triggered_count} / {notification.repeat_count}</p>
             )}
           </div>
           <div className="mt-6 flex gap-2">
             <button
               onClick={() => {
                 onDelete(notification.id);
                 onClose();
               }}
               className="flex-1 bg-red-600 text-white py-2 rounded-md hover:bg-red-700"
             >
               Dismiss
             </button>
             <button
               onClick={onClose}
               className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400"
             >
               Close
             </button>
           </div>
         </div>
       </div>
     );
   }
   ```

**Acceptance Criteria**:
- [ ] Notification badge shows count
- [ ] Dropdown displays notification list
- [ ] Modal shows full reminder details
- [ ] Delete button removes notification

---

### Phase 7: Integration (Frontend + Backend)

**Time Estimate**: 45 minutes
**Deliverable**: End-to-end working notification system

#### Steps:

1. **Update Tasks Page** to integrate reminder components
2. **Update Navbar** to show notification icon with badge
3. **Add useEffect** to fetch due reminders on page load/login
4. **Test End-to-End**:
   - Create reminder → saved in database
   - Login after reminder time → popup appears
   - Navbar shows correct count
   - Delete reminder → never reappears

**Acceptance Criteria**:
- [ ] All user stories from spec.md are testable
- [ ] UI is responsive on mobile and desktop
- [ ] JWT auth enforced on all API calls
- [ ] Data syncs correctly between frontend and backend

---

## Testing Checklist

### Backend Tests
- [ ] Reminder model saves to database
- [ ] get_due_reminders returns only overdue reminders
- [ ] process_reminder handles one-time reminders
- [ ] process_reminder handles repeating reminders
- [ ] Cascade delete works (delete task → reminders deleted)
- [ ] API endpoints return correct status codes
- [ ] JWT validation rejects unauthorized requests

### Frontend Tests
- [ ] ReminderForm submits correct data
- [ ] NotificationBadge displays count correctly
- [ ] NotificationDropdown renders notification list
- [ ] NotificationModal shows reminder details
- [ ] Delete action removes notification from UI

### Integration Tests
- [ ] Create reminder → appears in database
- [ ] Login with due reminder → notification shows
- [ ] Delete reminder → 404 on subsequent fetch
- [ ] Repeat reminder triggers correct number of times

---

## Common Issues and Solutions

**Issue**: Reminders not triggering
- **Solution**: Check server time vs. remind_at timestamp (must be UTC)

**Issue**: 403 Forbidden on API calls
- **Solution**: Verify user_id in URL matches JWT claim

**Issue**: Cascade delete not working
- **Solution**: Ensure `ondelete="CASCADE"` in SQLModel Field

**Issue**: Notification count incorrect
- **Solution**: Ensure frontend refetches due reminders after deletion

---

## Next Steps

After completing all phases:
1. Run full test suite: `npm test && uv run pytest`
2. Test manually with multiple users
3. Verify responsive UI on mobile devices
4. Review code against constitution principles
5. Create pull request with all changes

For questions, refer to:
- [spec.md](./spec.md) - Requirements
- [plan.md](./plan.md) - Architecture decisions
- [data-model.md](./data-model.md) - Database schema
- [contracts/reminders.openapi.yaml](./contracts/reminders.openapi.yaml) - API contracts
