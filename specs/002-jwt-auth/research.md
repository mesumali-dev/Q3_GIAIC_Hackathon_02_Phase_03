# Research: JWT Authentication & Frontend UI

**Feature Branch**: `002-jwt-auth`
**Date**: 2025-12-30
**Status**: Complete

## Executive Summary

This research consolidates findings on Better Auth JWT integration for the Next.js frontend with FastAPI backend verification. The constitution mandates JWT-based authentication with shared secret verification.

---

## Decision 1: JWT Algorithm

### Decision
Use **HS256** (HMAC with SHA-256) symmetric algorithm for JWT signing and verification.

### Rationale
1. **Shared Secret Simplicity**: Single `BETTER_AUTH_SECRET` shared between frontend and backend
2. **No Network Calls**: Backend can verify tokens locally without fetching JWKS
3. **Constitution Compliance**: Aligns with `BETTER_AUTH_SECRET` environment variable mandate
4. **Performance**: Faster verification than asymmetric algorithms

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| EdDSA (Ed25519) | Default in Better Auth, more secure key management | Requires JWKS endpoint, HTTP call for each verification | Added complexity, network latency |
| RS256 | Industry standard, supports key rotation | Large keys, slower, requires JWKS | Over-engineered for hackathon scope |
| Session Cookies | Built-in CSRF protection, httpOnly | Same-origin only, cannot work with separate backend | Incompatible with FastAPI on different port/domain |

---

## Decision 2: Token Storage

### Decision
Store JWT token in **localStorage** on the frontend, accessed via Better Auth Bearer plugin.

### Rationale
1. **Cross-Origin Compatibility**: Required for API calls to FastAPI backend on different port
2. **Explicit Control**: Frontend attaches token to every request via Authorization header
3. **Constitution Compliance**: "Frontend MUST attach JWT token to every API request via Authorization header"

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| httpOnly Cookies | XSS-safe, automatic transmission | Same-origin only, complex CORS with FastAPI | Cannot work with separate backend domain |
| sessionStorage | Auto-clears on tab close | Same XSS vulnerability, loses session on tab close | Poor UX for multi-tab usage |
| Memory only | Most secure | Token lost on page refresh | Poor UX |

### Security Mitigations
- XSS protection via Content Security Policy (out of scope for Part 2)
- HTTPS in production (out of scope for Part 2)
- Token expiry enforcement (in scope)

---

## Decision 3: Better Auth Configuration

### Decision
Use Better Auth with **JWT plugin + Bearer plugin** combination.

### Configuration Structure

**Server-side (Next.js API Route)**:
```typescript
// src/lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  database: { ... }, // Prisma/Drizzle adapter for user storage
  plugins: [
    jwt({
      jwt: {
        algorithm: "HS256",
        expiresIn: "24h",
        definePayload: ({ user }) => ({
          sub: user.id,
          email: user.email,
        }),
      },
    }),
  ],
});
```

**Client-side**:
```typescript
// src/lib/auth-client.ts
import { createAuthClient } from "better-auth/client"
import { jwtClient } from "better-auth/client/plugins"

export const authClient = createAuthClient({
  plugins: [jwtClient()],
});
```

### Rationale
- JWT plugin enables token generation and JWKS exposure
- Bearer plugin handles token extraction from response headers
- Combined allows cross-origin API authentication

---

## Decision 4: Backend JWT Verification

### Decision
Implement FastAPI dependency using **PyJWT** with direct HS256 verification.

### Implementation Pattern
```python
# src/middleware/auth.py
import jwt
from fastapi import HTTPException, Depends, Header
from typing import Annotated

def verify_jwt(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Rationale
1. **Existing Dependency**: PyJWT already in `pyproject.toml`
2. **Constitution Compliance**: Uses `BETTER_AUTH_SECRET` from environment
3. **Stateless**: No session storage required
4. **FastAPI Integration**: Works as dependency injection

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| JWKS Verification | No shared secret in backend | Requires HTTP call to frontend, complexity | HS256 simpler for hackathon |
| FastAPI-Security | Built-in OAuth2 flows | Adds dependency, over-engineered | Direct PyJWT sufficient |
| Middleware (global) | Automatic on all routes | Less flexible for public endpoints | Dependency injection preferred |

---

## Decision 5: User ID Claim

### Decision
Use `sub` (subject) claim for user ID, following JWT RFC 7519 standard.

### JWT Payload Structure
```json
{
  "sub": "user_uuid_here",
  "email": "user@example.com",
  "iat": 1704067200,
  "exp": 1704153600
}
```

### Rationale
1. **Standard Compliance**: `sub` is the standard claim for subject/user identifier
2. **Better Auth Default**: Uses `user.id` as `sub` by default
3. **Backend Extraction**: `payload["sub"]` provides user ID for ownership verification

---

## Decision 6: Frontend UI Approach

### Decision
Use **minimal Tailwind CSS forms** without component libraries.

### Rationale
1. **Hackathon Priority**: Speed over design polish
2. **No Additional Dependencies**: Tailwind already configured
3. **Constitution Compliance**: "UI MUST be responsive using Tailwind CSS"

### UI Components
- `/login` page: Email + password form
- `/register` page: Email + password + confirm password form
- Both: Error display, loading states, redirect handling

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| shadcn/ui | Pre-built components, accessible | Adds setup complexity, dependencies | Over-engineered for hackathon |
| Headless UI | Accessible primitives | Still requires styling | Unnecessary abstraction |
| CSS Modules | Scoped styles | No utility classes, slower development | Tailwind already configured |

---

## Decision 7: Route Protection

### Decision
Use **Next.js middleware** for route protection with client-side redirect.

### Implementation Pattern
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value;
  const isAuthPage = ["/login", "/register"].includes(request.nextUrl.pathname);

  if (!token && !isAuthPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL("/", request.url));
  }
}
```

### Rationale
1. **Server-Side Redirect**: Prevents flash of protected content
2. **Next.js Native**: No additional dependencies
3. **Constitution Compliance**: "Frontend MUST redirect unauthenticated users to /login"

---

## Technical Context Resolution

| Item | Resolution |
|------|------------|
| JWT Algorithm | HS256 (symmetric, shared secret) |
| Token Storage | localStorage via Bearer plugin |
| Better Auth Plugins | jwt + jwtClient |
| Backend Verification | PyJWT with HS256 |
| User ID Claim | `sub` (standard JWT claim) |
| UI Framework | Tailwind CSS only |
| Route Protection | Next.js middleware |

---

## Dependencies Confirmed

### Frontend
- `better-auth` - Authentication library (to install)
- `next` 16+ - Already installed
- `tailwindcss` - Already installed

### Backend
- `pyjwt` - Already installed (`>=2.10.1`)
- `fastapi` - Already installed
- `python-dotenv` - Already installed

---

## Implementation Notes

1. **Database Requirement**: Better Auth requires a database adapter for user storage. Will use SQLModel with Neon PostgreSQL.

2. **API Route Handler**: Better Auth requires Next.js API route at `/api/auth/[...all]/route.ts` for handling auth endpoints.

3. **CORS Configuration**: Backend must allow requests from frontend origin with Authorization header.

4. **Environment Variables**:
   - Frontend: `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `NEXT_PUBLIC_API_URL`
   - Backend: `BETTER_AUTH_SECRET`, `DATABASE_URL`

---

## Sources

- [Better Auth JWT Plugin](https://www.better-auth.com/docs/plugins/jwt)
- [Better Auth Bearer Plugin](https://www.better-auth.com/docs/plugins/bearer)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
