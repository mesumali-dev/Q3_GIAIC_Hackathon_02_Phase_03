# Backend Development Guidance

This file provides context-specific guidance for AI assistants working on the backend.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL (serverless)
- **Package Manager**: uv
- **Authentication**: JWT verification (tokens from Better Auth frontend)

## Project Structure

```
backend/
├── src/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection (placeholder)
│   ├── middleware/
│   │   ├── __init__.py      # Package marker
│   │   └── auth.py          # JWT verification (placeholder)
│   ├── models/              # SQLModel entities (future)
│   ├── services/            # Business logic (future)
│   └── api/                 # API routes (future)
├── tests/
│   └── test_health.py       # Health endpoint test
├── pyproject.toml           # Project configuration
├── .env.example             # Environment template
└── CLAUDE.md                # This file
```

## Key Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --reload --port 8000

# Run tests
uv run pytest

# Add a new dependency
uv add <package-name>
```

## Constitution Principles (Backend-Specific)

### Security by Default
- ALL endpoints (except /health) MUST require JWT authentication
- JWT secrets MUST come from BETTER_AUTH_SECRET environment variable
- NEVER hardcode secrets or tokens
- Validate user_id from JWT matches route parameter

### Data Integrity
- ALL database queries MUST filter by authenticated user_id
- Use SQLModel for type-safe database operations
- Backend MUST be stateless (no session storage)

### Error Handling
- 401 for missing/invalid JWT
- 403 for wrong user_id
- 404 for missing resources
- 422 for validation errors
- 500 with safe messages (no stack traces in production)

## API Endpoints (Future)

```
GET    /api/{user_id}/tasks           → List tasks
POST   /api/{user_id}/tasks           → Create task
GET    /api/{user_id}/tasks/{id}      → Get task
PUT    /api/{user_id}/tasks/{id}      → Update task
DELETE /api/{user_id}/tasks/{id}      → Delete task
PATCH  /api/{user_id}/tasks/{id}/complete → Toggle complete
```

## Current Status

- **Phase**: Foundation (Phase 1)
- **Health endpoint**: ✅ Implemented
- **Database**: Placeholder only
- **Authentication**: Placeholder only
- **Task CRUD**: Not implemented

## Development Notes

1. Always run `uv sync` after pulling changes
2. Copy `.env.example` to `.env` before running
3. Health check: `curl http://localhost:8000/health`
4. API docs available at `/docs` (Swagger UI)
