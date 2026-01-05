# Next.js Project Structure

## Standard Folder Layout

```
src/
├── app/
│   ├── api/
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── route.ts
│   │   │   └── register/
│   │   │       └── route.ts
│   │   └── users/
│   │       └── route.ts
│   ├── dashboard/
│   │   ├── page.tsx
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── logic.ts
│   │   └── components/
│   │       ├── DashboardHeader.tsx
│   │       └── StatsCard.tsx
│   └── profile/
│       ├── page.tsx
│       ├── logic.ts
│       └── components/
│           └── ProfileForm.tsx
├── components/
│   └── ui/
│       ├── button.tsx
│       └── input.tsx
├── lib/
│   ├── db.ts
│   ├── auth.ts
│   └── zod.ts
├── types/
│   └── index.ts
└── hooks/
    └── use-debounce.ts
```

## Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `app/` | App Router routes and API handlers |
| `app/[route]/components/` | Route-specific components (co-located) |
| `app/[route]/logic.ts` | Server-side business logic for that route |
| `app/api/` | API route handlers |
| `components/ui/` | Shared UI components (shadcn/ui style) |
| `lib/` | Shared utilities (db, auth, validation) |
| `types/` | Shared TypeScript type definitions |
| `hooks/` | Shared React hooks (client-side only) |

## Route Structure Pattern

Each route folder follows this structure:

```
app/[feature]/
├── page.tsx           # Route UI (Server Component by default)
├── loading.tsx        # Suspense fallback
├── error.tsx          # Error boundary
├── logic.ts           # Business logic (server-side)
└── components/        # Route-specific components
    ├── FeatureHeader.tsx
    └── FeatureCard.tsx
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Route folders | kebab-case | `user-settings/` |
| Components | PascalCase | `UserCard.tsx` |
| Utilities | camelCase | `formatDate.ts` |
| Types | PascalCase | `User`, `ApiResponse` |
| Hooks | camelCase with `use` prefix | `useDebounce.ts` |

## What Goes Where

### `logic.ts` (Server-side business logic)
- Database queries
- Data aggregation/transformation
- External service calls
- Authorization checks
- Shared logic used by page.tsx, API routes, or Server Actions

### `components/` (Co-located)
- Components specific to that route
- Not reused elsewhere in the app
- Can be Server or Client Components

### `components/ui/` (Shared)
- Reusable UI primitives
- shadcn/ui components
- Used across multiple routes

### `lib/` (Shared utilities)
- Database client (`db.ts`)
- Auth utilities (`auth.ts`)
- Zod schemas (`zod.ts`)
- Helper functions
