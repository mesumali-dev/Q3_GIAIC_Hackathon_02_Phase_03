# Research: Backend Authentication Refactor

**Feature**: 003-backend-auth-refactor
**Date**: 2025-12-30
**Status**: Complete

## Research Questions

### Q1: Why move authentication from Better Auth to FastAPI backend?

**Decision**: Move ALL authentication logic to FastAPI backend using SQLModel

**Rationale**:
1. **Project Requirements**: The project specification explicitly states SQLModel as the only ORM. Better Auth requires Prisma or Drizzle.
2. **Architecture Alignment**: The constitution mandates "Backend (FastAPI): Business logic, authentication verification, data access"
3. **Simplicity**: Reduces frontend dependencies and complexity
4. **Control**: Full control over authentication flow, token format, and user data structure

**Alternatives Considered**:
- **Better Auth with Drizzle**: Would require adding Drizzle ORM alongside SQLModel, creating two data access patterns
- **Keep Better Auth with Prisma**: Violates project requirements (SQLModel only)
- **Use Auth0/Clerk**: External dependency, adds cost, reduces control

---

### Q2: What password hashing algorithm should be used?

**Decision**: bcrypt via `passlib[bcrypt]` library

**Rationale**:
1. **Industry Standard**: bcrypt is the most widely recommended algorithm for password hashing
2. **Adaptive**: Work factor can be increased as hardware improves
3. **Built-in Salt**: Automatically handles salt generation and storage
4. **Python Support**: Well-maintained `passlib` library with bcrypt backend

**Alternatives Considered**:
- **argon2**: Newer, winner of Password Hashing Competition, but less widespread adoption
- **scrypt**: Memory-hard, but more complex to configure
- **PBKDF2**: Older, still secure but bcrypt generally preferred
- **Plain SHA-256**: NEVER - not designed for password hashing

**Configuration**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

---

### Q3: How should JWT tokens be generated and validated?

**Decision**: PyJWT with HS256 algorithm and BETTER_AUTH_SECRET

**Rationale**:
1. **Already Installed**: PyJWT is already in backend dependencies (from 002-jwt-auth)
2. **Simple API**: Straightforward encode/decode methods
3. **Shared Secret**: Use existing BETTER_AUTH_SECRET for consistency
4. **Stateless**: No need for refresh tokens in current scope

**Alternatives Considered**:
- **python-jose**: More features but more complex
- **authlib**: Full OAuth library, overkill for simple JWT
- **RS256 asymmetric**: More secure for distributed systems, but adds key management complexity

**Configuration**:
```python
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
```

---

### Q4: Where should JWT tokens be stored on the client?

**Decision**: localStorage with Authorization header

**Rationale**:
1. **Explicit Control**: Frontend explicitly attaches token to requests
2. **Simple Implementation**: No cookie configuration needed
3. **Cross-Origin Support**: Works with separate backend domain
4. **Existing Pattern**: Matches 002-jwt-auth implementation

**Alternatives Considered**:
- **httpOnly Cookie**: More secure against XSS, but requires CSRF protection and cookie configuration
- **sessionStorage**: Cleared on tab close, less convenient for users
- **In-memory only**: Lost on page refresh, poor UX

**Security Considerations**:
- XSS vulnerability: Tokens accessible to JavaScript
- Mitigation: Proper Content-Security-Policy, input sanitization
- For higher security requirements, consider httpOnly cookies with refresh token rotation

---

### Q5: What User model fields are required?

**Decision**: Minimal user model with UUID primary key

**Fields**:
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | UUID | PRIMARY KEY | Unique identifier, hard to enumerate |
| email | str | UNIQUE, NOT NULL, indexed | Login identifier |
| hashed_password | str | NOT NULL | bcrypt hash |
| created_at | datetime | DEFAULT NOW() | Audit trail |
| updated_at | datetime | DEFAULT NOW(), ON UPDATE | Audit trail |

**Rationale**:
1. **UUID over int**: Prevents user enumeration attacks
2. **Email as identifier**: Matches Better Auth behavior, user-friendly
3. **No name field**: Keep minimal, can add later if needed
4. **Timestamps**: Standard audit fields

**Alternatives Considered**:
- **Auto-increment int ID**: Easier to enumerate, security concern
- **Username + email**: More complex, not required by spec
- **Phone number**: Not in scope

---

### Q6: How should the frontend handle authentication state?

**Decision**: Check localStorage for token, validate via /api/auth/verify

**Flow**:
1. On app load, check localStorage for `access_token`
2. If token exists, call GET /api/auth/verify to validate
3. If valid, store user info in React state
4. If invalid (401), clear token and redirect to /login

**Rationale**:
1. **Simple**: No complex state management library needed
2. **Secure**: Server validates token, not just client
3. **Consistent**: Same pattern as existing implementation

**Alternatives Considered**:
- **Decode JWT client-side**: Can check expiry but can't verify signature
- **Context/Redux**: Adds complexity for simple auth state
- **Server-side sessions**: Requires backend state, violates stateless principle

---

### Q7: What about refresh tokens?

**Decision**: NOT implementing refresh tokens (out of scope)

**Rationale**:
1. **Spec Scope**: Specification does not require refresh tokens
2. **Complexity**: Adds token rotation logic, database storage
3. **24h Expiry**: Reasonable for development/MVP phase
4. **Future Enhancement**: Can add later if needed

**Alternatives Considered**:
- **Refresh token in httpOnly cookie**: More secure but complex
- **Sliding window expiry**: Extends token on activity
- **Short-lived access + refresh**: Standard pattern but overkill for current scope

---

## Technology Stack Validation

| Component | Technology | Status |
|-----------|------------|--------|
| Backend Framework | FastAPI | ✅ Already installed |
| ORM | SQLModel | ✅ Already installed |
| JWT Library | PyJWT | ✅ Already installed |
| Password Hashing | passlib[bcrypt] | ⚠️ Needs installation |
| Database | Neon PostgreSQL | ✅ Already configured |
| Frontend Framework | Next.js 16+ | ✅ Already installed |

**New Dependency Required**:
```bash
# backend
uv add passlib[bcrypt]
```

---

## Implementation Recommendations

### Backend

1. Create `backend/src/models/user.py` with User SQLModel
2. Create `backend/src/services/auth_service.py` with:
   - `hash_password(plain: str) -> str`
   - `verify_password(plain: str, hashed: str) -> bool`
   - `create_access_token(user: User) -> str`
   - `create_user(email: str, password: str) -> User`
   - `authenticate_user(email: str, password: str) -> User | None`
3. Add endpoints to `backend/src/api/auth.py`:
   - `POST /api/auth/register`
   - `POST /api/auth/login`
4. Keep existing `GET /api/auth/verify` endpoint
5. Add comprehensive tests

### Frontend

1. Remove Better Auth dependencies:
   - Delete `src/lib/auth.ts`
   - Delete `src/lib/auth-client.ts`
   - Delete `src/app/api/auth/[...all]/`
   - Delete `prisma/` directory
   - Remove from package.json: `better-auth`, `prisma`, `@prisma/client`
2. Update `src/lib/api.ts`:
   - Add `register(email, password)` function
   - Add `login(email, password)` function
   - Store token in localStorage on success
3. Update `RegisterForm.tsx` and `LoginForm.tsx`:
   - Call backend API instead of Better Auth
4. Update `middleware.ts`:
   - Check localStorage for token (client-side)
   - Or implement server-side auth check via API

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| XSS token theft | Medium | High | CSP headers, input sanitization |
| Brute force login | Medium | Medium | Rate limiting (future) |
| SQL injection | Low | High | SQLModel parameterized queries |
| Password exposure | Low | Critical | bcrypt hashing, no logging |

---

## References

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Passlib bcrypt](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
