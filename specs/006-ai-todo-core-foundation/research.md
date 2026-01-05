# Research: AI-Native Todo Core Foundation (Phase 1)

**Feature Branch**: `006-ai-todo-core-foundation`
**Date**: 2026-01-04
**Status**: Complete

## Research Summary

This document captures research findings for Phase 1 implementation decisions. All unknowns from the Technical Context have been resolved.

---

## Decision 1: Why SQLModel over raw SQL or SQLAlchemy

### Decision
Use SQLModel as the ORM for all database operations.

### Rationale
1. **Already in use**: The existing codebase uses SQLModel for the User and Task models
2. **Type safety**: SQLModel combines Pydantic validation with SQLAlchemy ORM, providing type-safe models and automatic validation
3. **FastAPI integration**: Native compatibility with FastAPI request/response models
4. **Reduced boilerplate**: Single model definition serves both database schema and API serialization
5. **Python 3.11+ compatibility**: Full support for modern Python type annotations

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Raw SQL | No type safety, manual result parsing, harder to maintain relationships |
| SQLAlchemy Core | Requires separate Pydantic models for API serialization, more boilerplate |
| SQLAlchemy ORM (without SQLModel) | Doesn't integrate as cleanly with FastAPI, requires model conversion |
| Prisma (Python) | Less mature Python support, different paradigm from existing code |

### Implementation Notes
- Continue using `SQLModel` base class for all new models
- Use `Field()` for column definitions with constraints
- Use `Relationship()` for entity relationships (not needed for Phase 1 scope)

---

## Decision 2: Why Neon Serverless PostgreSQL for stateless architecture

### Decision
Use Neon Serverless PostgreSQL as the single source of truth for all data.

### Rationale
1. **Already configured**: Database connection is established in `backend/src/database.py`
2. **Serverless compatibility**: Connection pooling handles serverless cold starts
3. **Stateless enabler**: All state lives in the database, enabling horizontal scaling
4. **PostgreSQL features**: Full ACID compliance, foreign keys, indexes for referential integrity
5. **Cost efficiency**: Pay-per-use model aligns with serverless backend

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Local PostgreSQL | Not suitable for production, requires server management |
| SQLite | No concurrent write support, not suitable for multi-instance deployment |
| MongoDB | No referential integrity, schema flexibility not needed for this use case |
| In-memory cache | Violates stateless requirement, data loss on restart |

### Implementation Notes
- Use `pool_pre_ping=True` to verify connections before use (already configured)
- Ensure all models are imported before `create_tables()` runs
- Connection string from `DATABASE_URL` environment variable

---

## Decision 3: Separation between repository and service layers

### Decision
Combine repository and service logic into a single service layer (following existing pattern).

### Rationale
1. **Existing pattern**: Current codebase uses `*_service.py` modules that handle both data access and business logic
2. **Appropriate complexity**: For this feature scope, a separate repository layer adds unnecessary abstraction
3. **Constitution alignment**: "Prefer the smallest viable diff" - adding a new layer is not justified
4. **Clear responsibilities**: Services handle user-scoped queries and business rules directly

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Repository + Service + Unit of Work | Over-engineering for current scope; adds 3 files per entity |
| Repository pattern only | Mixes concerns; business rules scattered across routes |
| ORM-only (no service) | Business logic in routes violates separation of concerns |

### Implementation Notes
- Create `conversation_service.py` following `task_service.py` pattern
- All service functions take `db: Session` and `user_id: UUID` as first parameters
- Services return domain models directly (no DTOs between layers)

---

## Decision 4: Conversation persistence strategy vs in-memory context

### Decision
Persist all conversations and messages to PostgreSQL; no in-memory caching.

### Rationale
1. **Stateless requirement**: Backend MUST NOT store business state in memory (FR-017)
2. **Durability**: Conversations are valuable for AI context in Phase 2; must survive restarts
3. **Multi-instance**: Any backend instance must serve any user's conversation
4. **Audit trail**: Persistent messages enable debugging and compliance

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Redis for conversations | Adds infrastructure complexity; data still needs PostgreSQL backup |
| In-memory with periodic flush | Violates stateless requirement; data loss risk |
| File-based storage | Not suitable for concurrent access or multi-instance |
| Hybrid (hot in Redis, cold in PostgreSQL) | Over-engineering for Phase 1; premature optimization |

### Implementation Notes
- Each message stored as separate row with foreign key to conversation
- Chronological ordering via `created_at` timestamp with index
- Message content stored as TEXT (up to 50,000 characters per spec)

---

## Decision 5: User scoping strategy for multi-tenant safety

### Decision
Enforce user_id filtering at the service layer for every query.

### Rationale
1. **Defense in depth**: Even if route validation fails, service layer blocks cross-user access
2. **Existing pattern**: Current `task_service.py` uses this approach consistently
3. **Query optimization**: user_id is indexed, enabling efficient scoped queries
4. **Constitution compliance**: "All database queries MUST include user ID filter from authenticated JWT"

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Row-level security (PostgreSQL) | Requires database configuration changes, harder to test |
| Global query filter (SQLAlchemy) | Can be accidentally bypassed; less explicit |
| Middleware-only check | Single point of failure; doesn't protect direct DB access |

### Implementation Notes
- Every service function signature includes `user_id: UUID`
- Every `SELECT` query includes `WHERE ... user_id == user_id`
- 404 response for resources not owned by user (avoids enumeration)

---

## Decision 6: Message role enumeration

### Decision
Use string literals for message role: `"user"`, `"assistant"`, `"system"`.

### Rationale
1. **OpenAI compatibility**: Standard role names used by OpenAI API and most AI frameworks
2. **MCP alignment**: Phase 2 will integrate with MCP tools; standard roles simplify integration
3. **Extensibility**: String type allows future role additions without migrations
4. **Simplicity**: No enum type needed at database level

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| PostgreSQL ENUM type | Requires migration for new roles; adds database complexity |
| Integer codes | Loses semantic meaning; requires constant lookup |
| Python Enum only | Still stores as string; enum adds serialization complexity |

### Implementation Notes
- Store as VARCHAR(20) in database
- Validate at Pydantic schema level with `Literal["user", "assistant", "system"]`
- Future roles (e.g., "tool", "function") can be added without migration

---

## Decision 7: Cascade delete behavior for conversations

### Decision
Implement cascade delete: deleting a conversation removes all its messages.

### Rationale
1. **Spec requirement**: FR-011 specifies cascade delete behavior
2. **Data integrity**: Orphan messages would break referential integrity
3. **User expectation**: Deleting a conversation should clean up completely
4. **Storage efficiency**: No zombie data accumulation

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Soft delete (is_deleted flag) | Not required by spec; adds complexity |
| Archive before delete | Out of scope for Phase 1 |
| Block delete if messages exist | Poor UX; forces manual message deletion |

### Implementation Notes
- Use SQLAlchemy `cascade="all, delete-orphan"` on relationship (if using relationships)
- Or handle in service layer by deleting messages first, then conversation
- Test: verify message count is 0 after conversation delete

---

## Technology Best Practices Captured

### SQLModel with FastAPI
- Use `Session` dependency injection via `Depends(get_db)`
- Return model instances from services; convert to response schemas in routes
- Use `model_validate()` for Pydantic v2 compatibility

### Neon PostgreSQL
- Keep connections short-lived (serverless pattern)
- Use `pool_pre_ping=True` for connection health checks
- Avoid connection-dependent features like LISTEN/NOTIFY

### Stateless Backend Patterns
- No module-level state beyond engine configuration
- No global dictionaries or caches for business data
- All data flows: request → database → response

---

## Unresolved Items

None. All technical decisions have been made and documented.

---

## References

- Existing codebase: `backend/src/services/task_service.py` (pattern reference)
- Existing codebase: `backend/src/models/task.py` (model reference)
- Existing codebase: `backend/src/database.py` (connection pattern)
- Constitution: `.specify/memory/constitution.md` (constraints)
- Spec: `specs/006-ai-todo-core-foundation/spec.md` (requirements)
