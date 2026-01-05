# Tasks: Task Reminders & Notifications

**Input**: Design documents from `specs/005-task-reminders/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/reminders.openapi.yaml

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- Tests not included per specification

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify existing project structure matches plan.md (backend/src/, frontend/src/)
- [x] T002 [P] Verify Python 3.11+ environment and uv package manager installed
- [x] T003 [P] Verify Node.js 18+ and npm/pnpm installed
- [x] T004 [P] Verify DATABASE_URL environment variable configured for Neon PostgreSQL
- [x] T005 [P] Verify BETTER_AUTH_SECRET environment variable configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database schema and shared utilities that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 [P] Create Reminder SQLModel entity in backend/src/models/reminder.py
- [x] T007 Update database.py to import Reminder model in backend/src/database.py
- [x] T008 Run database migration to create reminder table with indexes
- [x] T009 [P] Create ReminderCreate Pydantic schema in backend/src/models/reminder.py
- [x] T010 [P] Create ReminderRead Pydantic schema in backend/src/models/reminder.py
- [x] T011 [P] Create ReminderWithTask Pydantic schema in backend/src/models/reminder.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Basic Task Reminder (Priority: P1) 🎯 MVP

**Goal**: Users can create one-time reminders for tasks and receive notifications when due

**Independent Test**:
1. Create a task via existing task API
2. Set a reminder for that task with a date/time in the past (to trigger immediately)
3. Call GET /api/{user_id}/reminders/due
4. Verify reminder appears in response with task details
5. Verify reminder is deactivated after triggering once

**Acceptance Scenarios** (from spec.md):
- Reminder saved and associated with task
- Notification popup appears when reminder time arrives/passed
- Due reminders displayed immediately on login
- Navbar notification count badge shows correct number

### Backend Implementation for User Story 1

- [x] T012 [P] [US1] Implement get_due_reminders function in backend/src/services/reminder_service.py
- [x] T013 [P] [US1] Implement process_reminder function in backend/src/services/reminder_service.py
- [x] T014 [US1] Create POST /api/{user_id}/reminders endpoint in backend/src/api/reminders.py
- [x] T015 [US1] Create GET /api/{user_id}/reminders/due endpoint in backend/src/api/reminders.py
- [x] T016 [US1] Add JWT authentication dependency to reminder endpoints in backend/src/api/reminders.py
- [x] T017 [US1] Add user_id validation (JWT claim vs route param) in backend/src/api/reminders.py
- [x] T018 [US1] Register reminder router in backend/src/main.py

### Frontend Implementation for User Story 1

- [x] T019 [P] [US1] Create reminder API client in frontend/src/lib/api/reminders.ts
- [x] T020 [P] [US1] Create ReminderForm component in frontend/src/components/reminders/ReminderForm.tsx
- [x] T021 [P] [US1] Create NotificationModal component in frontend/src/components/reminders/NotificationModal.tsx
- [x] T022 [P] [US1] Create NotificationBadge component in frontend/src/components/reminders/NotificationBadge.tsx
- [x] T023 [US1] Update tasks page to integrate ReminderForm in frontend/src/app/(protected)/tasks/page.tsx
- [x] T024 [US1] Add notification fetch logic on page load in frontend/src/app/(protected)/tasks/page.tsx
- [x] T025 [US1] Implement popup display for due reminders on page load in frontend/src/app/(protected)/tasks/page.tsx
- [x] T026 [US1] Update Navbar to show NotificationBadge in frontend/src/components/navbar/Navbar.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can:
- Create one-time reminders
- See notification popup on login if reminders are due
- See notification count in navbar

---

## Phase 4: User Story 2 - View and Manage Notifications (Priority: P2)

**Goal**: Users can view all notifications in a list and delete/dismiss them

**Independent Test**:
1. Create multiple overdue reminders for different tasks
2. Login/refresh page to trigger notifications
3. Click notification icon in navbar
4. Verify dropdown shows all notifications with task details
5. Click a notification to see modal with full details
6. Delete a notification
7. Verify it's removed from UI and navbar count decrements
8. Refresh page and verify deleted notification doesn't reappear

**Acceptance Scenarios** (from spec.md):
- Clicking notification icon shows dropdown with all notifications and task details
- Clicking a notification shows popup with full reminder details
- Deleting notification removes it from UI and decrements count
- Deleted notification doesn't reappear after refresh/re-login

### Backend Implementation for User Story 2

- [x] T027 [US2] Create DELETE /api/{user_id}/reminders/{reminder_id} endpoint in backend/src/api/reminders.py
- [x] T028 [US2] Add ownership validation for delete operation in backend/src/api/reminders.py
- [x] T029 [US2] Handle 404 error when reminder not found or not owned by user in backend/src/api/reminders.py

### Frontend Implementation for User Story 2

- [x] T030 [P] [US2] Create NotificationDropdown component in frontend/src/components/reminders/NotificationDropdown.tsx
- [x] T031 [US2] Implement deleteReminder function in frontend/src/lib/api/reminders.ts
- [x] T032 [US2] Add click handler for notification icon to toggle dropdown in frontend/src/components/navbar/Navbar.tsx
- [x] T033 [US2] Wire up notification click to open modal with details in frontend/src/components/reminders/NotificationDropdown.tsx
- [x] T034 [US2] Wire up delete button to call API and update UI state in frontend/src/components/reminders/NotificationDropdown.tsx
- [x] T035 [US2] Update notification count after deletion in frontend/src/app/(protected)/tasks/page.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can:
- View all notifications in a dropdown
- Click notifications to see details
- Delete notifications
- Deleted notifications don't reappear

---

## Phase 5: User Story 3 - Create Repeating Task Reminders (Priority: P3)

**Goal**: Users can create reminders that repeat at fixed intervals for a specified number of times

**Independent Test**:
1. Create a task
2. Set a reminder with repeat_interval_minutes=1 and repeat_count=3
3. Wait 1 minute and call GET /api/{user_id}/reminders/due
4. Verify reminder triggered and next remind_at is 1 minute later
5. Wait another minute and fetch due reminders again
6. Verify second trigger
7. Wait another minute and fetch due reminders again
8. Verify third trigger and reminder is now deactivated (is_active=false)

**Acceptance Scenarios** (from spec.md):
- Reminder schedule saved with repeat configuration (interval + count)
- Notification appears at initial time and next repeat is scheduled
- Subsequent notifications appear at correct intervals
- No additional notifications after configured count reached
- Deleting repeating reminder cancels all future repeats

### Backend Implementation for User Story 3

- [x] T036 [US3] Add repeat interval validation (positive integer, max 1440) in backend/src/models/reminder.py
- [x] T037 [US3] Add repeat count validation (positive integer, max 100) in backend/src/models/reminder.py
- [x] T038 [US3] Update process_reminder to handle repeat logic in backend/src/services/reminder_service.py
- [x] T039 [US3] Calculate next remind_at by adding interval in backend/src/services/reminder_service.py
- [x] T040 [US3] Deactivate reminder when triggered_count reaches repeat_count in backend/src/services/reminder_service.py

### Frontend Implementation for User Story 3

- [x] T041 [US3] Add repeat_interval_minutes input to ReminderForm in frontend/src/components/reminders/ReminderForm.tsx
- [x] T042 [US3] Add repeat_count input to ReminderForm in frontend/src/components/reminders/ReminderForm.tsx
- [x] T043 [US3] Add validation for repeat interval (1-1440 minutes) in frontend/src/components/reminders/ReminderForm.tsx
- [x] T044 [US3] Add validation for repeat count (1-100) in frontend/src/components/reminders/ReminderForm.tsx
- [x] T045 [US3] Display repeat information in NotificationModal in frontend/src/components/reminders/NotificationModal.tsx
- [x] T046 [US3] Show triggered_count / repeat_count in notification details in frontend/src/components/reminders/NotificationModal.tsx

**Checkpoint**: All user stories should now be independently functional. Users can:
- Create one-time reminders (US1)
- View and manage notifications (US2)
- Create repeating reminders (US3)
- Each story works independently without breaking others

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T047 [P] Add error handling for invalid datetime formats in backend/src/api/reminders.py
- [x] T048 [P] Add error handling for negative intervals/counts in backend/src/api/reminders.py
- [x] T049 [P] Handle reminders for deleted tasks (cascade delete via foreign key) - verify in manual test
- [x] T050 [P] Add loading states to ReminderForm in frontend/src/components/reminders/ReminderForm.tsx
- [x] T051 [P] Add error message display to ReminderForm in frontend/src/components/reminders/ReminderForm.tsx
- [x] T052 [P] Improve responsive styling for mobile devices in frontend/src/components/reminders/
- [x] T053 [P] Add timestamp localization (display in user's timezone) in frontend/src/components/reminders/
- [x] T054 Verify all acceptance scenarios from spec.md work end-to-end
- [x] T055 Run quickstart.md validation steps
- [x] T056 Manual testing: Create reminder → login after time → verify popup
- [x] T057 Manual testing: Multiple users cannot see each other's reminders
- [x] T058 Manual testing: Repeat reminders trigger correct number of times
- [x] T059 Code cleanup and comment documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Phase 3**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Phase 4**: Can start after Foundational (Phase 2) - Builds on US1 components but should be independently testable
- **User Story 3 (P3) - Phase 5**: Can start after Foundational (Phase 2) - Extends US1 reminder creation but should be independently testable

### Within Each User Story

- Backend service logic before API endpoints
- API endpoints before frontend API client
- Frontend API client before UI components
- Core UI components before integration into pages
- Story complete and tested before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run in parallel (T002, T003, T004, T005)

**Phase 2 (Foundational)**: Tasks T006, T009, T010, T011 can run in parallel (different schema classes)

**Phase 3 (US1 Backend)**: T012 and T013 can run in parallel (different service functions)

**Phase 3 (US1 Frontend)**: T019, T020, T021, T022 can run in parallel (different component files)

**Phase 4 (US2 Frontend)**: T030 can start while T031 is in progress (different files)

**Phase 6 (Polish)**: T047, T048, T050, T051, T052, T053 can all run in parallel (different files)

---

## Parallel Example: User Story 1 Backend

```bash
# Launch backend service functions in parallel:
Task T012: "Implement get_due_reminders in backend/src/services/reminder_service.py"
Task T013: "Implement process_reminder in backend/src/services/reminder_service.py"

# Then sequentially create API endpoints (depends on service functions):
Task T014: "Create POST /api/{user_id}/reminders endpoint"
Task T015: "Create GET /api/{user_id}/reminders/due endpoint"
```

## Parallel Example: User Story 1 Frontend

```bash
# Launch all component files in parallel:
Task T019: "Create reminder API client in frontend/src/lib/api/reminders.ts"
Task T020: "Create ReminderForm component in frontend/src/components/reminders/ReminderForm.tsx"
Task T021: "Create NotificationModal component in frontend/src/components/reminders/NotificationModal.tsx"
Task T022: "Create NotificationBadge component in frontend/src/components/reminders/NotificationBadge.tsx"

# Then integrate into pages (depends on components):
Task T023: "Update tasks page to integrate ReminderForm"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended for First Delivery

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T012-T026)
4. **STOP and VALIDATE**: Test User Story 1 independently using acceptance scenarios
5. Manual testing:
   - Create task
   - Set reminder for 1 minute in future
   - Wait 1 minute, refresh page
   - Verify notification popup appears
   - Verify navbar badge shows count
6. Deploy/demo if ready

**This gives you a working MVP with core reminder functionality!**

### Incremental Delivery (Recommended Approach)

1. Complete Setup (Phase 1) + Foundational (Phase 2) → Foundation ready
2. Add User Story 1 (Phase 3) → Test independently → Deploy/Demo (MVP!)
   - Users can now create basic reminders
3. Add User Story 2 (Phase 4) → Test independently → Deploy/Demo
   - Users can now manage their notifications
4. Add User Story 3 (Phase 5) → Test independently → Deploy/Demo
   - Power users can now create repeating reminders
5. Complete Polish (Phase 6) → Final validation and deployment
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers (after Foundational phase complete):

1. Team completes Setup (Phase 1) + Foundational (Phase 2) together
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T012-T026) - Backend + Frontend for basic reminders
   - **Developer B**: User Story 2 (T027-T035) - Backend + Frontend for notification management
   - **Developer C**: User Story 3 (T036-T046) - Backend + Frontend for repeating reminders
3. Stories complete and integrate independently
4. Team reunites for Polish phase (T047-T059)

**Note**: This requires good communication to avoid merge conflicts, especially in shared files like `Navbar.tsx` and `page.tsx`. Consider splitting by layer instead:
- **Backend Developer**: T012-T018, T027-T029, T036-T040
- **Frontend Developer**: T019-T026, T030-T035, T041-T046

---

## Task Summary

**Total Tasks**: 59

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1 - MVP): 15 tasks (7 backend, 8 frontend)
- Phase 4 (User Story 2): 9 tasks (3 backend, 6 frontend)
- Phase 5 (User Story 3): 11 tasks (5 backend, 6 frontend)
- Phase 6 (Polish): 13 tasks

**By User Story**:
- US1 (Basic Reminders): 15 tasks
- US2 (Manage Notifications): 9 tasks
- US3 (Repeating Reminders): 11 tasks
- Infrastructure (Setup + Foundational): 11 tasks
- Polish: 13 tasks

**Parallel Opportunities Identified**: 18 tasks marked with [P]

**Independent Test Criteria**:
- US1: Create reminder → triggers notification → shows in navbar
- US2: View notifications → delete notification → count updates
- US3: Create repeating reminder → triggers multiple times → stops after count

**Suggested MVP Scope**: User Story 1 only (Phases 1-3, tasks T001-T026)

---

## Format Validation

✅ All tasks follow the required checklist format:
- Checkbox: `- [ ]`
- Task ID: Sequential (T001-T059)
- [P] marker: Present on 18 parallelizable tasks
- [Story] label: Present on all user story phase tasks (US1, US2, US3)
- Description: Includes exact file path for each task

✅ Tasks organized by user story for independent implementation
✅ Each story has clear goal and independent test criteria
✅ Dependencies clearly documented
✅ Parallel opportunities identified
✅ MVP scope defined (User Story 1)

---

## Notes

- **No Tests Included**: Per specification, tests were not explicitly requested, so test tasks are omitted
- **File Paths**: All tasks include exact file paths (backend/src/..., frontend/src/...)
- **[P] Parallelizable**: 18 tasks marked as parallelizable (different files, no dependencies)
- **[Story] Labels**: All implementation tasks labeled with their user story (US1, US2, US3)
- **Independence**: Each user story can be completed and tested without requiring other stories
- **Checkpoints**: Clear validation points after each phase
- **Incremental Value**: Each completed user story delivers working functionality
- **Commit Strategy**: Commit after each task or logical group for atomic changes
- **Stop Points**: Can stop and validate after any user story phase for incremental deployment
