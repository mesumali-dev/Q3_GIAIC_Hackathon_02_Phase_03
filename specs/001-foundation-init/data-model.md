# Data Model: Foundation & Project Initialization

**Feature**: 001-foundation-init
**Date**: 2025-12-30
**Status**: Complete

## Overview

The foundation phase does not implement any data models. This document serves as a placeholder that will be expanded in subsequent phases when Task and User entities are introduced.

## Entities (Placeholder)

### Future Entities (Not Implemented in This Phase)

| Entity | Description | Phase |
|--------|-------------|-------|
| User | Authenticated user with JWT claims | Phase 2: Authentication |
| Task | Todo item owned by a user | Phase 3: Task Management |

## Current Phase: No Entities

The foundation phase focuses on project scaffold only:
- No database tables created
- No SQLModel models defined
- Database connection is a placeholder only

## Placeholder Configuration

### Database Connection (backend/src/database.py)

```python
# Placeholder - no actual connection in foundation phase
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")

# Engine will be created in Phase 2
# engine = create_async_engine(DATABASE_URL)
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | Neon PostgreSQL connection string | Phase 2+ |

## Future Schema (Preview)

When implemented in later phases:

```sql
-- Phase 2: Users (managed by Better Auth)
-- Better Auth handles user tables internally

-- Phase 3: Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

## Relationships (Future)

```text
User (1) -----> (*) Task
  |                  |
  |                  +-- user_id: FK to user
  +-- Managed by Better Auth
```

## Notes

- No migrations in foundation phase
- SQLModel entities will be created in Phase 3
- Better Auth manages user data separately
