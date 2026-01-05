---
name: nextjs
description: Next.js App Router development with strict conventions. Apply when creating, modifying, or discussing Next.js code. Enforces co-located components, Server Components by default, Tailwind + shadcn/ui styling, TypeScript strict mode, Zod validation, and specific TSX formatting rules. Triggers on any Next.js App Router context.
---

# Next.js Development Skill

## Core Principles

1. **Server Components by default** — Client Components are the exception
2. **Co-locate by feature** — Components live next to their page
3. **Strict TypeScript** — `any` is forbidden
4. **Zod everywhere** — Validate all inputs
5. **Tailwind + shadcn/ui** — Customize, don't import black-box kits

## TSX Formatting Rules

### Same-Line JSX
Every JSX element opens and closes on the same line when possible:

```tsx
// Correct
<button className="btn" onClick={handleClick}></button>
<StatsCard title="Revenue"></StatsCard>

// Avoid
<button
  className="btn"
  onClick={handleClick}
>
</button>
```

### Comment Rule
Add a comment ABOVE every non-trivial block.

**Trivial (no comment):**
- Simple JSX return: `return <div></div>`
- Simple assignment: `const isAdmin = role === "admin"`
- One-line obvious function

**Non-trivial (comment required):**
- Data fetching
- Loops (`map`, `filter`, `reduce`)
- Conditional logic
- Functions
- Side effects
- Data transformations

```tsx
// Fetch user data from database
export async function getUser(id: string) {
  return db.user.findUnique({ where: { id } });
}

// Render list of users
users.map((user) => <UserCard key={user.id} user={user}></UserCard>);
```

## When to Use Client Components

Only add `"use client"` when needed:
- Interactivity (onClick, onChange, etc.)
- Browser-only APIs (localStorage, window)
- Local state or effects (useState, useEffect)
- Third-party client libraries

## Data Fetching Patterns

| Pattern | Use Case |
|---------|----------|
| Direct DB calls in Server Components | Reading data for pages |
| Server Actions | Mutations (create, update, delete) |
| Route Handlers | Webhooks, external API consumers, auth callbacks |

## State Management

| Tool | Use Case |
|------|----------|
| URL state (searchParams) | Filters, pagination, shareable state |
| React Context | App-wide UI state (theme, sidebar) |
| Zustand | Complex client state |
| Redux | Only if absolutely necessary |

## File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `logic.ts` | Server-side business logic (DB queries, transforms, auth checks) |
| `loading.tsx` | Suspense fallback |
| `error.tsx` | Error boundary |
| `components/` | Co-located route-specific components |

**Rule:** If it runs on the server and is not UI → it belongs in `logic.ts`.

## Anti-Patterns to Avoid

- Making everything a Client Component
- Fetching data in `useEffect`
- Global state for simple UI state
- Over-abstracting too early
- Huge barrel files

## References

- **Folder structure template**: See [references/structure.md](references/structure.md)
- **Code patterns & examples**: See [references/patterns.md](references/patterns.md)
- **Feature checklist**: See [references/checklist.md](references/checklist.md)
