# Quickstart: Backend Authentication Refactor

**Feature**: 003-backend-auth-refactor
**Estimated Time**: 30-45 minutes

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- Neon PostgreSQL database (already configured)
- Environment variables set

## Step 1: Install Backend Dependencies

```bash
cd backend
uv add "passlib[bcrypt]"
uv sync
```

## Step 2: Run Database Migration

After implementing the User model:

```bash
cd backend
# Option A: Using SQLModel auto-create (development)
uv run python -c "from src.database import create_tables; create_tables()"

# Option B: Using Alembic (if configured)
alembic upgrade head
```

## Step 3: Start Backend Server

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

## Step 4: Remove Frontend Dependencies

```bash
cd frontend

# Remove Better Auth and Prisma
npm uninstall better-auth @prisma/client prisma

# Remove Prisma directory
rm -rf prisma/

# Remove generated Prisma client
rm -rf src/generated/

# Verify removal
npm list prisma  # Should show empty
npm list better-auth  # Should show empty
```

## Step 5: Start Frontend Server

```bash
cd frontend
npm install
npm run dev
```

## Step 6: Verify Setup

### Test Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com"
  }
}
```

### Test Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Test Token Verification

```bash
curl http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer <token_from_login>"
```

Expected response:
```json
{
  "authenticated": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com"
}
```

## Step 7: E2E Verification

1. Open http://localhost:3000/register
2. Create a new account with valid email/password
3. Verify redirect to home page
4. Check browser DevTools → Application → Local Storage for `access_token`
5. Click logout, verify redirect to /login
6. Login with created credentials
7. Verify redirect to home page

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"

# Authentication
BETTER_AUTH_SECRET="your-32-char-secret-here"
JWT_ALGORITHM="HS256"
JWT_EXPIRY_HOURS=24

# CORS
FRONTEND_URL="http://localhost:3000"
```

### Frontend (.env.local)

```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
```

## Validation Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Backend running | `curl localhost:8000/health` | `{"status": "ok"}` |
| Frontend running | Open `localhost:3000` | Page loads |
| No Prisma | `cd frontend && npm list prisma` | Empty |
| No Better Auth | `cd frontend && npm list better-auth` | Empty |
| Register works | POST /api/auth/register | 200 + token |
| Login works | POST /api/auth/login | 200 + token |
| Verify works | GET /api/auth/verify | 200 + user |

## Troubleshooting

### "Module not found: passlib"

```bash
cd backend
uv add "passlib[bcrypt]"
```

### "CORS error"

Check `FRONTEND_URL` in backend .env matches frontend origin.

### "Invalid token"

Ensure `BETTER_AUTH_SECRET` is the same in both frontend and backend .env files.

### "Table 'users' does not exist"

Run database migration:
```bash
cd backend
uv run python -c "from src.database import create_tables; create_tables()"
```

### Frontend still has Better Auth errors

1. Delete `node_modules` and reinstall:
```bash
cd frontend
rm -rf node_modules
npm install
```

2. Delete `.next` cache:
```bash
rm -rf .next
npm run dev
```
