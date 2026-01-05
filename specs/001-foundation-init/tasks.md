# Tasks: Foundation & Project Initialization

**Input**: Design documents from `/specs/001-foundation-init/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests explicitly requested in feature specification. Test tasks included only for health endpoint verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend uses Python with uv package manager
- Frontend uses TypeScript with npm package manager

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic monorepo structure

- [x] T001 Create monorepo directory structure with backend/ and frontend/ at project root
- [x] T002 [P] Create root-level .gitignore with Python and Node.js patterns
- [x] T003 [P] Create root-level .env.example with shared environment variables (BETTER_AUTH_SECRET)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Initialize uv project in backend/ with `uv init`
- [x] T005 Install backend dependencies with `uv add fastapi uvicorn[standard] sqlmodel python-dotenv pyjwt`
- [x] T006 [P] Create backend/src/__init__.py package marker
- [x] T007 [P] Create backend/src/middleware/__init__.py package marker
- [x] T008 Initialize Next.js 16+ project in frontend/ with App Router, TypeScript, and Tailwind

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Developer Starts Backend Server (Priority: P1) 🎯 MVP

**Goal**: Backend server starts without errors and responds to health check requests

**Independent Test**: Run `uv run uvicorn src.main:app --reload` and verify GET /health returns 200 OK

### Implementation for User Story 1

- [x] T009 [US1] Create config.py for environment loading in backend/src/config.py
- [x] T010 [P] [US1] Create database.py connection placeholder in backend/src/database.py
- [x] T011 [P] [US1] Create JWT verification middleware placeholder in backend/src/middleware/auth.py
- [x] T012 [US1] Create main.py FastAPI app with health endpoint in backend/src/main.py
- [x] T013 [US1] Create .env.example with backend environment variables in backend/.env.example
- [x] T014 [US1] Create CLAUDE.md with backend development guidance in backend/CLAUDE.md
- [x] T015 [US1] Create test_health.py to verify health endpoint in backend/tests/test_health.py
- [x] T016 [US1] Verify backend starts with `uv run uvicorn src.main:app --reload --port 8000`

**Checkpoint**: Backend server is fully functional and independently testable

---

## Phase 4: User Story 2 - Developer Starts Frontend Server (Priority: P2)

**Goal**: Frontend server starts without errors and displays placeholder page

**Independent Test**: Run `npm run dev` and verify http://localhost:3000 renders placeholder page

### Implementation for User Story 2

- [x] T017 [US2] Create root layout.tsx with basic HTML structure in frontend/src/app/layout.tsx
- [x] T018 [US2] Create placeholder home page.tsx in frontend/src/app/page.tsx
- [x] T019 [P] [US2] Create globals.css with Tailwind directives in frontend/src/app/globals.css
- [x] T020 [P] [US2] Create Better Auth placeholder configuration in frontend/src/lib/auth.ts
- [x] T021 [P] [US2] Create API client placeholder in frontend/src/lib/api.ts
- [x] T022 [US2] Create .env.example with frontend environment variables in frontend/.env.example
- [x] T023 [US2] Create CLAUDE.md with frontend development guidance in frontend/CLAUDE.md
- [x] T024 [US2] Verify frontend starts with `npm run dev` and renders at http://localhost:3000

**Checkpoint**: Frontend server is fully functional and independently testable

---

## Phase 5: User Story 3 - Developer Reviews Project Structure (Priority: P3)

**Goal**: Project structure is documented and matches conventions

**Independent Test**: Examine directory structure and verify CLAUDE.md files exist at root, backend, and frontend

### Implementation for User Story 3

- [x] T025 [US3] Create root-level CLAUDE.md with project-wide guidance in CLAUDE.md
- [x] T026 [US3] Verify directory structure matches plan.md specification
- [x] T027 [US3] Verify all .env.example files document required environment variables

**Checkpoint**: Project structure is complete and documented

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T028 Run backend server and verify health endpoint responds correctly
- [x] T029 Run frontend server and verify placeholder page renders
- [x] T030 Verify no console errors or warnings in either server
- [x] T031 Run quickstart.md validation steps to confirm setup instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion (can run parallel to US1)
- **User Story 3 (Phase 5)**: Depends on US1 and US2 completion (needs files to verify)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Can run in parallel with US1
- **User Story 3 (P3)**: Requires US1 and US2 completion - Verification story

### Within Each User Story

- Configuration before implementation
- Placeholders before main application
- Main application before documentation
- Documentation before verification

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T006 and T007 can run in parallel (different init files)
- T010 and T011 can run in parallel (different placeholder files)
- T019, T020, and T021 can run in parallel (different frontend files)
- User Story 1 and User Story 2 can run in parallel after Foundational phase

---

## Parallel Example: User Story 1

```bash
# Launch parallelizable US1 tasks together:
Task: "Create database.py connection placeholder in backend/src/database.py"
Task: "Create JWT verification middleware placeholder in backend/src/middleware/auth.py"
```

## Parallel Example: User Story 2

```bash
# Launch parallelizable US2 tasks together:
Task: "Create globals.css with Tailwind directives in frontend/src/app/globals.css"
Task: "Create Better Auth placeholder configuration in frontend/src/lib/auth.ts"
Task: "Create API client placeholder in frontend/src/lib/api.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test backend server independently
5. Proceed to User Story 2 if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test backend independently → Backend MVP!
3. Add User Story 2 → Test frontend independently → Full scaffold!
4. Add User Story 3 → Verify structure → Documentation complete!
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend)
   - Developer B: User Story 2 (Frontend)
3. Both complete, then verify User Story 3 together

---

## Summary

| Phase | Tasks | Parallel Tasks | Story |
|-------|-------|----------------|-------|
| Setup | 3 | 2 | - |
| Foundational | 5 | 2 | - |
| User Story 1 | 8 | 2 | Backend |
| User Story 2 | 8 | 3 | Frontend |
| User Story 3 | 3 | 0 | Structure |
| Polish | 4 | 0 | - |
| **Total** | **31** | **9** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No business logic implemented - placeholders only
