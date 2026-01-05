# Quickstart: JWT Authentication & Frontend UI

**Feature Branch**: `002-jwt-auth`
**Date**: 2025-12-30

This guide provides step-by-step instructions to set up and test the JWT authentication feature.

---

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.14+ (for backend)
- PostgreSQL database (Neon)
- Git

---

## 1. Environment Setup

### Frontend (.env.local)

Create `frontend/.env.local`:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET="your-32-character-minimum-secret-here"
BETTER_AUTH_URL="http://localhost:3000"

# Database (for Better Auth)
DATABASE_URL="postgresql://user:password@hostname/database?sslmode=require"

# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### Backend (.env)

Create `backend/.env`:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Database
DATABASE_URL="postgresql://user:password@hostname/database?sslmode=require"

# Authentication (MUST match frontend)
BETTER_AUTH_SECRET="your-32-character-minimum-secret-here"

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# CORS
FRONTEND_URL="http://localhost:3000"
```

### Generate Secret

```bash
# Generate a secure secret (use the same value in both .env files)
openssl rand -base64 32
```

---

## 2. Install Dependencies

### Frontend

```bash
cd frontend
npm install better-auth
npm install
```

### Backend

```bash
cd backend
uv sync
```

---

## 3. Database Migration

Better Auth requires database tables. Using Prisma:

```bash
cd frontend
npx prisma generate
npx prisma db push
```

Or with Drizzle:

```bash
cd frontend
npx drizzle-kit push
```

---

## 4. Start Development Servers

### Terminal 1: Backend

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

---

## 5. Test Authentication Flow

### 5.1 Register New User

```bash
# Via curl
curl -X POST http://localhost:3000/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'
```

Expected response:
```json
{
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "name": "Test User"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 5.2 Login

```bash
curl -X POST http://localhost:3000/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 5.3 Verify JWT on Backend

```bash
# Use token from login response
export TOKEN="eyJhbGciOiJIUzI1NiIs..."

curl -X GET http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
{
  "authenticated": true,
  "user_id": "uuid-here",
  "email": "test@example.com"
}
```

### 5.4 Test Invalid Token

```bash
curl -X GET http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer invalid-token"
```

Expected: 401 Unauthorized

### 5.5 Test Missing Token

```bash
curl -X GET http://localhost:8000/api/auth/verify
```

Expected: 401 Unauthorized

---

## 6. UI Testing

1. Navigate to `http://localhost:3000/register`
2. Enter email, password, and name
3. Submit form
4. Verify redirect to home page
5. Navigate to `http://localhost:3000/login`
6. Log out and verify redirect to login

---

## 7. Verification Checklist

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Register with valid credentials | Success, JWT issued | |
| Register with existing email | Error: email exists | |
| Login with valid credentials | Success, JWT issued | |
| Login with wrong password | 401 error | |
| Backend verify with valid JWT | 200 with user info | |
| Backend verify with invalid JWT | 401 error | |
| Backend verify with expired JWT | 401 error | |
| Backend verify without JWT | 401 error | |
| Access /login while authenticated | Redirect to home | |
| Access protected page while unauthenticated | Redirect to /login | |

---

## 8. Troubleshooting

### "Invalid token" Error

- Ensure `BETTER_AUTH_SECRET` matches in both frontend and backend
- Check token is not expired
- Verify JWT algorithm is HS256 in both configurations

### Database Connection Error

- Verify `DATABASE_URL` is correct
- Check Neon database is accessible
- Run migrations: `npx prisma db push`

### CORS Error

- Ensure backend CORS allows `http://localhost:3000`
- Check `FRONTEND_URL` in backend .env

### Token Not Sent

- Verify localStorage has `bearer_token` key
- Check API client includes Authorization header
- Inspect network requests in browser DevTools

---

## 9. API Documentation

- Frontend (Better Auth): http://localhost:3000/api/auth/reference
- Backend (FastAPI): http://localhost:8000/docs

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tasks in priority order (P1 first)
3. Test each user story independently
4. Proceed to Part 3 (Task CRUD) after auth is verified
