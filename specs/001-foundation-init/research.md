# Research: Foundation & Project Initialization

**Feature**: 001-foundation-init
**Date**: 2025-12-30
**Status**: Complete

## Research Summary

This document captures research decisions for the foundation phase. Since this is a scaffold-only phase with no business logic, research focuses on tooling choices and best practices for project initialization.

---

## Decision 1: Package Manager for Backend (uv)

**Decision**: Use uv for Python package management

**Rationale**:
- User explicitly specified `uv init` and `uv add` commands
- uv is 10-100x faster than pip for dependency resolution
- Modern lockfile format ensures reproducible builds
- Compatible with standard pyproject.toml format
- Developed by Astral (makers of ruff), actively maintained

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| pip | Slower, no built-in lockfile |
| poetry | Slower than uv, more complex |
| pipenv | Slower, less active development |

**Implementation**:
```bash
cd backend
uv init
uv add fastapi uvicorn[standard] sqlmodel python-dotenv pyjwt
```

---

## Decision 2: Package Manager for Frontend (npm)

**Decision**: Use npm for Node.js package management

**Rationale**:
- Widest compatibility with Next.js ecosystem
- Standard choice, requires no additional setup
- package-lock.json provides reproducible builds
- Simpler onboarding for new developers

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| pnpm | Faster but requires separate install |
| yarn | Additional tool, marginal benefits |
| bun | Newer, less ecosystem compatibility |

**Implementation**:
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --src-dir
```

---

## Decision 3: Monorepo Structure

**Decision**: Use monorepo with /backend and /frontend directories

**Rationale**:
- User explicitly specified monorepo layout
- Simpler CI/CD configuration (single pipeline)
- Shared environment variables at root level
- Easier cross-project refactoring
- Single repository for issue tracking

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Separate repositories | Harder to coordinate releases |
| Mono-package (Turborepo) | Over-engineering for this project |

**Implementation**:
```text
/
├── backend/     # Python FastAPI
├── frontend/    # Next.js TypeScript
├── CLAUDE.md    # Root guidance
└── .env.example # Shared vars
```

---

## Decision 4: Next.js App Router

**Decision**: Use App Router instead of Pages Router

**Rationale**:
- User explicitly specified "Next.js 16+ App Router"
- App Router is the recommended approach for new projects
- Server Components provide better performance
- Layouts and streaming built-in
- Better support for React 18+ features

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Pages Router | Legacy, not recommended for new projects |

**Implementation**:
- Create project with `--app` flag
- Place pages in `src/app/` directory
- Use `layout.tsx` for shared layouts

---

## Decision 5: JWT Verification Location

**Decision**: JWT verification in backend middleware, not frontend

**Rationale**:
- Constitution Principle I requires backend JWT verification
- Frontend tokens can be tampered with client-side
- Backend is the security boundary
- Frontend only stores and sends tokens

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Frontend-only verification | Security violation, tokens can be forged |
| Both frontend and backend | Redundant, adds complexity |

**Implementation**:
- Backend: `middleware/auth.py` verifies JWT on protected routes
- Frontend: `lib/auth.ts` stores token and adds to requests

---

## Decision 6: Environment-Based Secrets

**Decision**: All secrets via environment variables, never hardcoded

**Rationale**:
- Constitution Principle I mandates no hardcoded secrets
- Industry standard for security
- Enables different configs per environment
- Prevents accidental commits of secrets

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Hardcoded values | Security violation |
| Config files | Risk of accidental commit |
| Secret managers | Over-engineering for foundation |

**Implementation**:
- `.env.example` templates with placeholder values
- `.gitignore` excludes `.env` files
- Documentation of all required variables

---

## Best Practices Research

### FastAPI Project Structure

Based on FastAPI best practices:
- Entry point in `src/main.py`
- Configuration in `src/config.py` using pydantic-settings pattern
- Routers in `src/api/` directory
- Models in `src/models/` directory
- Middleware in `src/middleware/` directory

### Next.js 16+ App Router Structure

Based on Next.js documentation:
- Pages in `src/app/` with folder-based routing
- Shared components in `src/components/`
- Utilities in `src/lib/`
- Global styles in `src/app/globals.css`
- Root layout in `src/app/layout.tsx`

### Better Auth Integration

Based on Better Auth documentation:
- Configuration in `src/lib/auth.ts`
- Session provider in layout
- API routes for auth callbacks
- JWT token storage in httpOnly cookies

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Which Python version? | 3.11+ (uv default, FastAPI compatible) |
| Which TypeScript version? | 5.x (Next.js 16+ default) |
| Which Tailwind version? | 3.x (Next.js create-next-app default) |
| Database driver for Neon? | asyncpg (placeholder only for foundation) |

---

## Next Steps

1. Proceed to data-model.md (minimal for foundation)
2. Create health endpoint contract
3. Generate quickstart.md with setup instructions
