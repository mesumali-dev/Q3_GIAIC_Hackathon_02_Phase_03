# Quickstart: Task CRUD Implementation

**Feature**: 004-task-crud
**Date**: 2026-01-01

## Prerequisites

Ensure these are complete before implementation:

- [ ] 003-backend-auth-refactor merged and working
- [ ] Backend running: `cd backend && uv run uvicorn src.main:app --reload`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Database connection verified: health check passes
- [ ] Can register and login successfully

## Implementation Order

### Phase 1: Backend Task Model

```bash
# 1. Create Task model
touch backend/src/models/task.py

# 2. Register in models/__init__.py
# Add: from src.models.task import Task

# 3. Create schemas
touch backend/src/schemas/task.py

# 4. Restart backend to create table
```

### Phase 2: Backend Task Service

```bash
# 1. Create task service
touch backend/src/services/task.py

# Implements:
# - create_task(db, user_id, data) -> Task
# - get_tasks(db, user_id) -> list[Task]
# - get_task(db, user_id, task_id) -> Task | None
# - update_task(db, user_id, task_id, data) -> Task | None
# - delete_task(db, user_id, task_id) -> bool
# - toggle_complete(db, user_id, task_id) -> Task | None
```

### Phase 3: Backend Task Routes

```bash
# 1. Create task router
touch backend/src/api/tasks.py

# 2. Register in main.py
# Add: from src.api.tasks import router as tasks_router
# Add: app.include_router(tasks_router)
```

### Phase 4: Frontend Task API

```bash
# Update frontend/src/lib/api.ts
# Replace placeholder implementations with real API calls
```

### Phase 5: Frontend Task Pages

```bash
# 1. Create task list page
mkdir -p frontend/src/app/tasks
touch frontend/src/app/tasks/page.tsx

# 2. Create task creation page
mkdir -p frontend/src/app/tasks/new
touch frontend/src/app/tasks/new/page.tsx

# 3. Create task detail/edit page
mkdir -p "frontend/src/app/tasks/[id]"
touch "frontend/src/app/tasks/[id]/page.tsx"
```

### Phase 6: Frontend Components

```bash
# Create reusable components
touch frontend/src/components/TaskCard.tsx
touch frontend/src/components/TaskForm.tsx
touch frontend/src/components/TaskList.tsx
touch frontend/src/components/ConfirmDialog.tsx
```

## Testing Checkpoints

### After Phase 3 (Backend Complete)

```bash
# Test with curl

# 1. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Get user ID from token (or from response)
USER_ID="your-user-id-here"

# 2. Create task
curl -X POST "http://localhost:8000/api/${USER_ID}/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Test description"}'

# 3. List tasks
curl "http://localhost:8000/api/${USER_ID}/tasks" \
  -H "Authorization: Bearer $TOKEN"

# 4. Toggle complete
curl -X PATCH "http://localhost:8000/api/${USER_ID}/tasks/{task_id}/complete" \
  -H "Authorization: Bearer $TOKEN"

# 5. Delete task
curl -X DELETE "http://localhost:8000/api/${USER_ID}/tasks/{task_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### After Phase 6 (Full Integration)

1. Login as User A
2. Create 3 tasks
3. Verify tasks appear in list
4. Toggle one task complete
5. Edit another task
6. Delete a task
7. Logout
8. Login as User B
9. Verify User A's tasks are NOT visible
10. Create task as User B
11. Logout, login as User A
12. Verify User B's task is NOT visible

## Key Files to Modify

### Backend

| File | Action | Purpose |
|------|--------|---------|
| `src/models/task.py` | Create | Task SQLModel entity |
| `src/models/__init__.py` | Modify | Export Task |
| `src/schemas/task.py` | Create | Pydantic request/response schemas |
| `src/services/task.py` | Create | Task business logic |
| `src/api/tasks.py` | Create | FastAPI router |
| `src/main.py` | Modify | Register tasks router |
| `src/database.py` | Modify | Import Task for table creation |

### Frontend

| File | Action | Purpose |
|------|--------|---------|
| `src/lib/api.ts` | Modify | Real task API methods |
| `src/app/tasks/page.tsx` | Create | Task list page |
| `src/app/tasks/new/page.tsx` | Create | Create task page |
| `src/app/tasks/[id]/page.tsx` | Create | Task detail/edit page |
| `src/components/TaskCard.tsx` | Create | Task display component |
| `src/components/TaskForm.tsx` | Create | Task create/edit form |
| `src/components/TaskList.tsx` | Create | Task list container |
| `src/components/ConfirmDialog.tsx` | Create | Delete confirmation |
| `middleware.ts` | Modify | Protect /tasks routes |

## Common Issues

### 403 Forbidden on task operations

**Cause**: user_id in route doesn't match JWT
**Fix**: Ensure frontend sends correct user_id from stored auth

### Tasks not appearing after creation

**Cause**: Database table not created
**Fix**: Restart backend to trigger `create_tables()`

### 401 on protected routes

**Cause**: Token expired or missing
**Fix**: Check localStorage for token, verify expiry

### Validation errors on create

**Cause**: Title empty or too long
**Fix**: Add client-side validation before API call

## Success Criteria Verification

- [ ] Create task works
- [ ] Task list shows all user tasks
- [ ] Toggle completion persists
- [ ] Edit task saves changes
- [ ] Delete removes task permanently
- [ ] User A cannot see User B's tasks
- [ ] Unauthenticated users redirected to login
- [ ] Mobile layout works (320px+)
