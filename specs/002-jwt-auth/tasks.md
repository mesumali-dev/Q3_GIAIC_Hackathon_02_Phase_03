# Tasks: JWT Authentication & Frontend UI

**Input**: Design documents from `/specs/002-jwt-auth/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Manual testing only (no TDD requested in spec)

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

**Purpose**: Install dependencies and configure project structure

- [x] T001 Install Better Auth dependency in frontend/package.json
- [x] T002 [P] Install Prisma ORM in frontend/package.json for Better Auth database
- [x] T003 [P] Verify PyJWT is installed in backend/pyproject.toml (already present)
- [x] T004 Update frontend/.env.local with BETTER_AUTH_SECRET, BETTER_AUTH_URL, NEXT_PUBLIC_API_URL
- [x] T005 [P] Update backend/.env with BETTER_AUTH_SECRET and FRONTEND_URL for CORS

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create Prisma schema for Better Auth tables in frontend/prisma/schema.prisma
- [ ] T007 Run Prisma migrations to create user, session, account tables
- [x] T008 Configure Better Auth server with JWT plugin in frontend/src/lib/auth.ts
- [x] T009 Configure Better Auth client with jwtClient in frontend/src/lib/auth-client.ts
- [x] T010 Create Better Auth API route handler at frontend/src/app/api/auth/[...all]/route.ts
- [x] T011 [P] Add CORS middleware to backend/src/main.py allowing frontend origin
- [x] T012 [P] Create backend/src/api/__init__.py package marker

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: A new user can create an account and be automatically logged in

**Independent Test**: Navigate to /register, submit valid email/password, verify redirect to home and authenticated state

### Implementation for User Story 1

- [x] T013 [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [x] T014 [US1] Create /register page in frontend/src/app/register/page.tsx
- [x] T015 [US1] Implement form validation (email format, password min 8 chars) in RegisterForm.tsx
- [x] T016 [US1] Add loading state and error display to RegisterForm.tsx
- [x] T017 [US1] Implement sign-up submission using authClient.signUp.email() in RegisterForm.tsx
- [x] T018 [US1] Add success redirect to home page after registration in RegisterForm.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - new users can register

---

## Phase 4: User Story 2 - User Login (Priority: P1)

**Goal**: An existing user can log in and receive a JWT token

**Independent Test**: Navigate to /login with registered user, submit credentials, verify JWT stored and redirect to home

### Implementation for User Story 2

- [x] T019 [US2] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [x] T020 [US2] Create /login page in frontend/src/app/login/page.tsx
- [x] T021 [US2] Implement form validation (email format, password required) in LoginForm.tsx
- [x] T022 [US2] Add loading state and error display to LoginForm.tsx
- [x] T023 [US2] Implement sign-in submission using authClient.signIn.email() in LoginForm.tsx
- [x] T024 [US2] Add success redirect to home page after login in LoginForm.tsx
- [x] T025 [US2] Handle incorrect credentials error with user-friendly message in LoginForm.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can register AND login

---

## Phase 5: User Story 3 - Protected Route Access (Priority: P2)

**Goal**: Authenticated users have JWT attached to all API requests, unauthenticated users are redirected

**Independent Test**: Login, make API request, verify Authorization header present; try accessing protected page without login, verify redirect to /login

### Implementation for User Story 3

- [x] T026 [US3] Create Next.js middleware for route protection in frontend/middleware.ts
- [x] T027 [US3] Implement redirect to /login for unauthenticated users in middleware.ts
- [x] T028 [US3] Implement redirect away from /login /register for authenticated users in middleware.ts
- [x] T029 [US3] Update API client to retrieve JWT token in frontend/src/lib/api.ts
- [x] T030 [US3] Ensure API client attaches Authorization: Bearer header in frontend/src/lib/api.ts
- [x] T031 [US3] Handle 401 responses with redirect to login in frontend/src/lib/api.ts

**Checkpoint**: At this point, route protection works - unauthenticated users can't access protected pages

---

## Phase 6: User Story 4 - Backend JWT Verification (Priority: P2)

**Goal**: FastAPI backend verifies JWT tokens and extracts user_id for route handlers

**Independent Test**: Call GET /api/auth/verify with valid token → 200, invalid token → 401, no token → 401

### Implementation for User Story 4

- [x] T032 [US4] Implement JWT verification function in backend/src/middleware/auth.py
- [x] T033 [US4] Implement get_current_user dependency in backend/src/middleware/auth.py
- [x] T034 [US4] Add user_id extraction from JWT sub claim in backend/src/middleware/auth.py
- [x] T035 [US4] Handle expired token with 401 response in backend/src/middleware/auth.py
- [x] T036 [US4] Handle invalid signature with 401 response in backend/src/middleware/auth.py
- [x] T037 [US4] Handle missing Authorization header with 401 response in backend/src/middleware/auth.py
- [x] T038 [US4] Create /api/auth/verify endpoint in backend/src/api/auth.py
- [x] T039 [US4] Register auth router in backend/src/main.py
- [x] T040 [US4] Create backend/tests/test_auth.py with JWT verification tests

**Checkpoint**: At this point, backend JWT verification works - tokens are validated correctly

---

## Phase 7: User Story 5 - Responsive Authentication UI (Priority: P3)

**Goal**: Login and registration pages are responsive across all screen sizes (320px to 2560px)

**Independent Test**: View /login and /register at 320px, 768px, 1024px, 2560px widths; verify forms are usable

### Implementation for User Story 5

- [x] T041 [US5] Add responsive container styles to RegisterForm.tsx (mobile-first)
- [x] T042 [US5] Add responsive container styles to LoginForm.tsx (mobile-first)
- [x] T043 [US5] Ensure form inputs are touch-friendly on mobile (min height 44px) in both forms
- [x] T044 [US5] Add proper spacing and max-width for desktop in both forms
- [x] T045 [US5] Ensure validation messages are visible at all screen sizes

**Checkpoint**: All user stories complete - authentication system fully functional and responsive

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and improvements across all user stories

- [x] T046 [P] Update frontend/src/app/page.tsx home page to show auth status
- [x] T047 [P] Add sign out button/link to home page
- [x] T048 Verify BETTER_AUTH_SECRET is validated on backend startup in backend/src/config.py
- [ ] T049 Run quickstart.md validation checklist
- [ ] T050 Manual end-to-end test: register → logout → login → verify → logout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 (both P1) can proceed in parallel
  - US3 depends on US1 or US2 being complete (need auth to test)
  - US4 can proceed independently after Foundational
  - US5 depends on US1 and US2 forms existing
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Registration) | Foundational | Phase 2 complete |
| US2 (Login) | Foundational | Phase 2 complete |
| US3 (Route Protection) | US1 or US2 | One auth flow works |
| US4 (Backend JWT) | Foundational | Phase 2 complete |
| US5 (Responsive UI) | US1 and US2 | Forms exist |

### Within Each User Story

- Form component before page
- Validation before submission
- Loading/error states before success handling

### Parallel Opportunities

**Phase 1 Parallel:**
```
T002 (Prisma install) | T003 (verify PyJWT) | T005 (backend env)
```

**Phase 2 Parallel:**
```
T011 (CORS) | T012 (api package)
```

**Phase 3+4 Parallel (after Phase 2):**
```
US1 tasks (T013-T018) | US2 tasks (T019-T025)
US4 tasks (T032-T040) can run independently
```

**Phase 8 Parallel:**
```
T046 (home page auth) | T047 (sign out)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Registration)
4. **STOP and VALIDATE**: Test registration independently
5. Can demo registration flow

### Recommended Execution Order

1. **Phase 1**: Setup (T001-T005)
2. **Phase 2**: Foundational (T006-T012)
3. **Phase 3**: US1 Registration (T013-T018) - MVP!
4. **Phase 4**: US2 Login (T019-T025)
5. **Phase 6**: US4 Backend JWT (T032-T040) - Can parallel with US1/US2
6. **Phase 5**: US3 Route Protection (T026-T031)
7. **Phase 7**: US5 Responsive UI (T041-T045)
8. **Phase 8**: Polish (T046-T050)

### Parallel Team Strategy

With 2 developers after Phase 2 completes:
- **Dev A**: US1 (Registration) → US3 (Route Protection)
- **Dev B**: US4 (Backend JWT) → US2 (Login)

Then converge for US5 (Responsive) and Phase 8 (Polish)

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 50 |
| **Setup Tasks** | 5 |
| **Foundational Tasks** | 7 |
| **US1 Tasks** | 6 |
| **US2 Tasks** | 7 |
| **US3 Tasks** | 6 |
| **US4 Tasks** | 9 |
| **US5 Tasks** | 5 |
| **Polish Tasks** | 5 |
| **Parallel Opportunities** | 11 tasks marked [P] |
| **MVP Scope** | US1 (Registration) - 18 tasks total |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend and Frontend US4/US1-US2 can be developed in parallel
