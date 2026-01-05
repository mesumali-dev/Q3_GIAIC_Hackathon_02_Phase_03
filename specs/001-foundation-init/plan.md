# Implementation Plan: Foundation & Project Initialization

**Branch**: `001-foundation-init` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-foundation-init/spec.md`

## Summary

Initialize the foundational monorepo structure for the AI-Native Todo Full-Stack Web Application. This phase establishes the project scaffold with FastAPI backend and Next.js frontend, including placeholder configurations for authentication, database connection, and API client. No business logic is implemented - only the minimal runnable structure required for future feature development.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, uvicorn (backend); Next.js 16+, Better Auth (frontend)
**Storage**: Neon PostgreSQL (placeholder connection only - no schema)
**Testing**: pytest (backend), Jest/Vitest (frontend) - setup only
**Target Platform**: Linux/macOS/Windows development, Docker-ready deployment
**Project Type**: Web application (monorepo with frontend + backend)
**Performance Goals**: Health check response < 100ms, server startup < 30 seconds
**Constraints**: No business logic, placeholders only, environment-based configuration
**Scale/Scope**: Single developer setup, foundation for multi-user Todo app

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status | Notes |
|-----------|------|--------|-------|
| I. Security by Default | No hardcoded secrets | ✅ PASS | All secrets via environment variables |
| I. Security by Default | JWT placeholder present | ✅ PASS | Middleware placeholder, no logic |
| II. Separation of Concerns | Backend/Frontend separated | ✅ PASS | Monorepo with /backend and /frontend |
| II. Separation of Concerns | No business logic in frontend | ✅ PASS | Placeholder page only |
| III. RESTful API Design | Health endpoint follows REST | ✅ PASS | GET /health returns status |
| VI. Frontend Standards | Better Auth placeholder | ✅ PASS | Config placeholder, no implementation |
| VII. Spec-Driven Development | Matches spec requirements | ✅ PASS | All FR-001 to FR-012 addressed |

**Gate Result**: PASS - All constitution principles satisfied for foundation phase.

## Project Structure

### Documentation (this feature)

```text
specs/001-foundation-init/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal for foundation)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── health.yaml      # Health endpoint contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment loading
│   ├── database.py          # Database connection placeholder
│   └── middleware/
│       └── auth.py          # JWT verification placeholder
├── tests/
│   └── test_health.py       # Health endpoint test
├── pyproject.toml           # uv/pip configuration
├── .env.example             # Environment template
└── CLAUDE.md                # Backend development guidance

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Placeholder home page
│   └── lib/
│       ├── auth.ts          # Better Auth placeholder
│       └── api.ts           # API client placeholder
├── package.json             # npm/pnpm configuration
├── tsconfig.json            # TypeScript configuration
├── tailwind.config.ts       # Tailwind configuration
├── .env.example             # Environment template
└── CLAUDE.md                # Frontend development guidance

# Root level
├── CLAUDE.md                # Project-wide guidance
├── .gitignore               # Git ignore rules
└── .env.example             # Root environment template (shared vars)
```

**Structure Decision**: Web application structure selected per constitution Section II (Separation of Concerns). Backend and frontend are separate directories with independent package management, enabling parallel development and deployment.

## Complexity Tracking

> No complexity violations - foundation phase uses minimal structure.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Execution Phases

### Phase 1: Repository Foundation

**Tasks**:
1. Create monorepo directory structure (backend/, frontend/)
2. Add root-level CLAUDE.md with project guidance
3. Add root-level .gitignore with Python and Node.js patterns
4. Add root-level .env.example with shared environment variables

**Files Created**:
- `/CLAUDE.md`
- `/.gitignore`
- `/.env.example`

### Phase 2: Backend Initialization

**Tasks**:
1. Initialize uv project with `uv init` in backend/
2. Install dependencies: `uv add fastapi uvicorn[standard] sqlmodel python-dotenv pyjwt`
3. Create src/ directory structure
4. Implement main.py with FastAPI app and health endpoint
5. Implement config.py for environment loading
6. Implement database.py placeholder
7. Implement middleware/auth.py JWT placeholder
8. Create .env.example with backend variables
9. Create CLAUDE.md with backend guidance
10. Create basic test for health endpoint

**Files Created**:
- `backend/pyproject.toml`
- `backend/src/__init__.py`
- `backend/src/main.py`
- `backend/src/config.py`
- `backend/src/database.py`
- `backend/src/middleware/__init__.py`
- `backend/src/middleware/auth.py`
- `backend/tests/test_health.py`
- `backend/.env.example`
- `backend/CLAUDE.md`

### Phase 3: Frontend Initialization

**Tasks**:
1. Initialize Next.js 16+ project with App Router
2. Configure TypeScript and Tailwind CSS
3. Create placeholder home page
4. Create Better Auth placeholder configuration
5. Create API client placeholder
6. Create .env.example with frontend variables
7. Create CLAUDE.md with frontend guidance

**Files Created**:
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tailwind.config.ts`
- `frontend/postcss.config.js`
- `frontend/next.config.ts`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/lib/auth.ts`
- `frontend/src/lib/api.ts`
- `frontend/.env.example`
- `frontend/CLAUDE.md`

## Key Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Package Manager (Backend) | uv | User specified; faster than pip, modern lockfile | pip, poetry |
| Package Manager (Frontend) | npm | Standard, widest compatibility | pnpm, yarn |
| Project Layout | Monorepo | User specified; simpler CI/CD, shared tooling | Separate repos |
| Router Type | App Router | User specified; Next.js 16+ requirement | Pages Router |
| Auth Library | Better Auth | Constitution requirement; JWT-based | NextAuth, custom |
| ORM | SQLModel | Constitution requirement; Pydantic integration | SQLAlchemy, Prisma |
| CSS Framework | Tailwind | User specified; utility-first, responsive | CSS modules, styled-components |

## Validation Checklist

- [ ] Backend starts with `uv run uvicorn src.main:app --reload`
- [ ] Frontend starts with `npm run dev`
- [ ] Health endpoint responds at `http://localhost:8000/health`
- [ ] Frontend placeholder page renders at `http://localhost:3000`
- [ ] No runtime errors or warnings
- [ ] All .env.example files document required variables
- [ ] CLAUDE.md files present at root, backend, and frontend
- [ ] No business logic implemented (placeholders only)
