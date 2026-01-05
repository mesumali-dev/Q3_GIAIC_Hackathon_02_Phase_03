# Tasks: Backend Authentication Refactor

**Input**: Design documents from `/specs/003-backend-auth-refactor/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Backend pytest tests included (11 test cases from plan.md testing strategy)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and prepare for refactor

- [x] T001 Install passlib[bcrypt] dependency in backend using `uv add "passlib[bcrypt]"`
- [x] T002 [P] Create backend/src/models/ directory if not exists
- [x] T003 [P] Create backend/src/services/ directory if not exists
- [x] T004 [P] Verify DATABASE_URL is set in backend/.env for Neon PostgreSQL

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create User SQLModel in backend/src/models/user.py per data-model.md
- [x] T006 Create backend/src/models/__init__.py with User export
- [x] T007 Create database session helper in backend/src/database.py with create_tables()
- [x] T008 Update backend/src/main.py to call create_tables() on startup
- [x] T009 Create auth service in backend/src/services/auth_service.py with password hashing functions
- [x] T010 [P] Create Pydantic schemas in backend/src/schemas/auth.py (RegisterRequest, LoginRequest, AuthResponse)
- [x] T011 [P] Create backend/src/schemas/__init__.py with exports

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: A new user can create an account by submitting email/password to backend API

**Independent Test**: POST /api/auth/register with valid data → 200 + JWT; POST with existing email → 409

### Tests for User Story 1

- [x] T012 [P] [US1] Add test_register_success in backend/tests/test_auth.py
- [x] T013 [P] [US1] Add test_register_duplicate_email (409) in backend/tests/test_auth.py
- [x] T014 [P] [US1] Add test_register_short_password (400) in backend/tests/test_auth.py
- [x] T015 [P] [US1] Add test_register_invalid_email (400) in backend/tests/test_auth.py

### Implementation for User Story 1

- [x] T016 [US1] Add create_user() function to backend/src/services/auth_service.py
- [x] T017 [US1] Add create_access_token() function to backend/src/services/auth_service.py
- [x] T018 [US1] Add POST /api/auth/register endpoint to backend/src/api/auth.py
- [x] T019 [US1] Handle 409 Conflict for duplicate email in register endpoint
- [x] T020 [US1] Handle 400 Bad Request for validation errors in register endpoint

**Checkpoint**: User Story 1 complete - users can register via backend API

---

## Phase 4: User Story 2 - User Login (Priority: P1)

**Goal**: An existing user can log in and receive a JWT token

**Independent Test**: POST /api/auth/login with valid credentials → 200 + JWT; wrong password → 401

### Tests for User Story 2

- [x] T021 [P] [US2] Add test_login_success in backend/tests/test_auth.py
- [x] T022 [P] [US2] Add test_login_wrong_password (401) in backend/tests/test_auth.py
- [x] T023 [P] [US2] Add test_login_nonexistent_email (401) in backend/tests/test_auth.py

### Implementation for User Story 2

- [x] T024 [US2] Add authenticate_user() function to backend/src/services/auth_service.py
- [x] T025 [US2] Add POST /api/auth/login endpoint to backend/src/api/auth.py
- [x] T026 [US2] Return same error message for wrong password and non-existent email (security)

**Checkpoint**: User Stories 1 and 2 complete - users can register AND login via backend

---

## Phase 5: User Story 3 - JWT Token Verification (Priority: P1)

**Goal**: Backend verifies JWT tokens and extracts user identity

**Independent Test**: GET /api/auth/verify with valid token → 200; expired → 401; missing → 401

### Tests for User Story 3

- [x] T027 [P] [US3] Add test_verify_valid_token in backend/tests/test_auth.py
- [x] T028 [P] [US3] Add test_verify_expired_token (401) in backend/tests/test_auth.py
- [x] T029 [P] [US3] Add test_verify_invalid_token (401) in backend/tests/test_auth.py
- [x] T030 [P] [US3] Add test_verify_missing_token (401) in backend/tests/test_auth.py

### Implementation for User Story 3

- [x] T031 [US3] Verify existing GET /api/auth/verify endpoint works with new User model
- [x] T032 [US3] Update JWT payload to include user email from database

**Checkpoint**: All P1 user stories complete - full backend auth working

---

## Phase 6: Frontend Cleanup (Blocking for US4, US5)

**Purpose**: Remove Better Auth and Prisma dependencies before frontend refactor

- [x] T033 Delete frontend/src/lib/auth.ts (Better Auth server config)
- [x] T034 [P] Delete frontend/src/lib/auth-client.ts (Better Auth client)
- [x] T035 [P] Delete frontend/src/app/api/auth/[...all]/ directory (Better Auth route)
- [x] T036 [P] Delete frontend/prisma/ directory
- [x] T037 [P] Delete frontend/src/generated/ directory (Prisma client)
- [x] T038 Remove better-auth, @prisma/client, prisma from frontend/package.json
- [x] T039 Run `npm install` in frontend to update node_modules

**Checkpoint**: Frontend cleaned up - ready for new auth implementation

---

## Phase 7: User Story 4 - User Logout (Priority: P2)

**Goal**: Logged-in user can log out, clearing JWT from frontend

**Independent Test**: Click logout → token cleared from localStorage → redirect to /login

### Implementation for User Story 4

- [x] T040 [US4] Add logout() function to frontend/src/lib/api.ts that clears localStorage token
- [x] T041 [US4] Update logout button in frontend/src/app/page.tsx to call logout()
- [x] T042 [US4] Ensure logout redirects to /login page

**Checkpoint**: User Story 4 complete - users can log out

---

## Phase 8: User Story 5 - Protected Route Access (Priority: P2)

**Goal**: Unauthenticated users redirected to /login; authenticated users redirected away from auth pages

**Independent Test**: Access / without token → redirect to /login; Access /login with token → redirect to /

### Implementation for User Story 5

- [x] T043 [US5] Create auth helper in frontend/src/lib/auth-helper.ts for token checking
- [x] T044 [US5] Add register() function to frontend/src/lib/api.ts calling POST /api/auth/register
- [x] T045 [US5] Add login() function to frontend/src/lib/api.ts calling POST /api/auth/login
- [x] T046 [US5] Update frontend/src/components/auth/RegisterForm.tsx to use api.ts register()
- [x] T047 [US5] Update frontend/src/components/auth/LoginForm.tsx to use api.ts login()
- [x] T048 [US5] Update frontend/middleware.ts to check localStorage token (client-side approach)
- [x] T049 [US5] Implement redirect to /login for unauthenticated users
- [x] T050 [US5] Implement redirect to / for authenticated users on /login and /register

**Checkpoint**: All user stories complete - full auth flow working

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and testing

- [x] T051 [P] Verify `npm list prisma` returns empty in frontend/
- [x] T052 [P] Verify `npm list better-auth` returns empty in frontend/
- [x] T053 Run all backend tests with `uv run pytest backend/tests/test_auth.py -v`
- [ ] T054 Run quickstart.md validation checklist
- [ ] T055 Manual E2E test: register → logout → login → verify → logout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US1, US2, US3 (Phase 3-5)**: All depend on Foundational phase completion
  - US1 and US2 are independent, can run in parallel
  - US3 depends on US1 (needs a user to create tokens)
- **Frontend Cleanup (Phase 6)**: Can start after Phase 2, BLOCKS US4, US5
- **US4, US5 (Phase 7-8)**: Depend on Frontend Cleanup
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|--------------------|
| US1 (Registration) | Foundational | Phase 2 complete |
| US2 (Login) | Foundational | Phase 2 complete |
| US3 (JWT Verify) | US1 | Phase 3 complete |
| US4 (Logout) | Frontend Cleanup | Phase 6 complete |
| US5 (Route Protection) | Frontend Cleanup | Phase 6 complete |

### Within Each User Story

- Tests written first (TDD approach)
- Service functions before API endpoints
- Backend before frontend

### Parallel Opportunities

**Phase 1 Parallel:**
```
T002 (models dir) | T003 (services dir) | T004 (verify env)
```

**Phase 2 Parallel:**
```
T010 (schemas) | T011 (schema init)
```

**Phase 3 Tests (all parallel):**
```
T012 | T013 | T014 | T015
```

**Phase 4 Tests (all parallel):**
```
T021 | T022 | T023
```

**Phase 5 Tests (all parallel):**
```
T027 | T028 | T029 | T030
```

**Phase 6 Cleanup (parallel):**
```
T034 | T035 | T036 | T037
```

**Phase 9 Verification (parallel):**
```
T051 | T052
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Login)
5. Complete Phase 5: User Story 3 (JWT Verify)
6. **STOP and VALIDATE**: Test backend auth independently with curl
7. Backend can demo registration, login, verification

### Full Implementation

1. Complete Phases 1-5 (MVP backend)
2. Complete Phase 6: Frontend Cleanup
3. Complete Phase 7: User Story 4 (Logout)
4. Complete Phase 8: User Story 5 (Route Protection)
5. Complete Phase 9: Polish
6. Full E2E test

### Parallel Team Strategy

With 2 developers after Phase 2 completes:
- **Dev A**: US1 (Registration) → US3 (JWT Verify)
- **Dev B**: US2 (Login) → Frontend Cleanup → US4, US5

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 55 |
| **Setup Tasks** | 4 |
| **Foundational Tasks** | 7 |
| **US1 Tasks** | 9 (4 tests + 5 impl) |
| **US2 Tasks** | 6 (3 tests + 3 impl) |
| **US3 Tasks** | 6 (4 tests + 2 impl) |
| **Cleanup Tasks** | 7 |
| **US4 Tasks** | 3 |
| **US5 Tasks** | 8 |
| **Polish Tasks** | 5 |
| **Parallel Opportunities** | 23 tasks marked [P] |
| **MVP Scope** | US1-US3 (Backend only) - 26 tasks |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are written before implementation (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend and Frontend can be worked on by different developers
