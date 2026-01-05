# Next.js Feature Checklist

Use this checklist when building new features to ensure consistency.

## New Route Checklist

- [ ] Create route folder under `app/`
- [ ] Add `page.tsx` (Server Component by default)
- [ ] Add `loading.tsx` with skeleton UI
- [ ] Add `error.tsx` with error boundary
- [ ] Create `logic.ts` for business logic
- [ ] Create `components/` folder for route-specific components

## Component Checklist

- [ ] Determine: Server or Client Component?
- [ ] If Client: add `"use client"` directive at top
- [ ] Add TypeScript interface for props
- [ ] Use Tailwind for styling
- [ ] Follow same-line JSX formatting
- [ ] Add comments above non-trivial blocks

## Data Fetching Checklist

- [ ] Read data: Direct DB call in Server Component
- [ ] Mutations: Server Action with `"use server"`
- [ ] External API: Route Handler in `app/api/`
- [ ] Validate all inputs with Zod
- [ ] Handle unauthorized access
- [ ] Use `revalidatePath` or `revalidateTag` after mutations

## Form Checklist

- [ ] Create Zod schema for validation
- [ ] Create Server Action for submission
- [ ] Use `useActionState` for form state
- [ ] Show loading state while pending
- [ ] Display validation errors
- [ ] Optimistic UI where appropriate

## TypeScript Checklist

- [ ] Strict mode enabled
- [ ] No `any` types (unless justified with comment)
- [ ] All function parameters typed
- [ ] Return types explicit for exported functions
- [ ] Zod schemas for runtime validation

## Code Style Checklist

- [ ] Same-line JSX formatting
- [ ] Comments above non-trivial blocks:
  - [ ] Data fetching
  - [ ] Loops (map, filter, reduce)
  - [ ] Conditional logic
  - [ ] Functions
  - [ ] Side effects
  - [ ] Data transformations
- [ ] No unnecessary abstractions
- [ ] No barrel files

## Testing Checklist

- [ ] Unit tests for critical logic in `logic.ts`
- [ ] Integration tests for forms and Server Actions
- [ ] E2E tests (Playwright) for core user flows
- [ ] Test behavior, not implementation

## State Management Checklist

- [ ] URL state for filters/pagination (shareable)
- [ ] React Context for UI state (theme, sidebar)
- [ ] Zustand for complex client state
- [ ] Avoid global state for simple UI state

## Performance Checklist

- [ ] Server Components by default
- [ ] Client Components only where needed
- [ ] Proper cache control (`revalidate`, `cache()`)
- [ ] Use Suspense for data fetching
- [ ] No data fetching in `useEffect`

## Before PR Checklist

- [ ] Run build: `npm run build`
- [ ] Run lint: `npm run lint`
- [ ] Run tests: `npm test`
- [ ] Check TypeScript: `npx tsc --noEmit`
- [ ] Manual test core flows
