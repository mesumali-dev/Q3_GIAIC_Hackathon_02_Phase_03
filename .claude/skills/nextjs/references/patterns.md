# Next.js Code Patterns

## Table of Contents
- [Server Component](#server-component)
- [Client Component](#client-component)
- [Server Action](#server-action)
- [Route Handler](#route-handler)
- [logic.ts Pattern](#logicts-pattern)
- [Form with Validation](#form-with-validation)
- [Loading & Error States](#loading--error-states)

---

## Server Component

Default pattern for pages and data-fetching components:

```tsx
// app/dashboard/page.tsx
import { getDashboardData } from "./logic";
import { DashboardHeader } from "./components/DashboardHeader";
import { StatsCard } from "./components/StatsCard";

// Render dashboard with user stats
export default async function DashboardPage() {
  const data = await getDashboardData();

  return (
    <div className="space-y-6 p-6">
      <DashboardHeader title="Dashboard"></DashboardHeader>

      {/* Render stats cards */}
      <div className="grid grid-cols-3 gap-4">
        {data.stats.map((stat) => (
          <StatsCard key={stat.id} title={stat.label} value={stat.value}></StatsCard>
        ))}
      </div>
    </div>
  );
}
```

---

## Client Component

Only when interactivity is required:

```tsx
// app/dashboard/components/FilterDropdown.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface FilterDropdownProps {
  options: string[];
  onSelect: (value: string) => void;
}

// Dropdown for filtering dashboard data
export function FilterDropdown({ options, onSelect }: FilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Handle option selection
  const handleSelect = (option: string) => {
    onSelect(option);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <Button onClick={() => setIsOpen(!isOpen)}>Filter</Button>

      {/* Render dropdown options */}
      {isOpen && (
        <ul className="absolute mt-2 w-48 rounded-md border bg-white shadow-lg">
          {options.map((option) => (
            <li key={option} className="cursor-pointer px-4 py-2 hover:bg-gray-100" onClick={() => handleSelect(option)}>{option}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## Server Action

For mutations (create, update, delete):

```tsx
// app/tasks/actions.ts
"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { db } from "@/lib/db";
import { auth } from "@/lib/auth";

// Zod schema for task creation
const createTaskSchema = z.object({
  title: z.string().min(1).max(100),
  description: z.string().optional(),
});

// Create a new task for the current user
export async function createTask(formData: FormData) {
  const session = await auth();

  // Check authorization
  if (!session?.user) {
    throw new Error("Unauthorized");
  }

  // Validate input
  const parsed = createTaskSchema.safeParse({
    title: formData.get("title"),
    description: formData.get("description"),
  });

  if (!parsed.success) {
    return { error: "Invalid input" };
  }

  // Insert task into database
  await db.task.create({
    data: {
      ...parsed.data,
      userId: session.user.id,
    },
  });

  revalidatePath("/tasks");
  return { success: true };
}
```

---

## Route Handler

For webhooks, external APIs, auth callbacks:

```tsx
// app/api/webhooks/stripe/route.ts
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { db } from "@/lib/db";

// Zod schema for webhook payload
const webhookSchema = z.object({
  type: z.string(),
  data: z.object({
    id: z.string(),
    amount: z.number(),
  }),
});

// Handle Stripe webhook events
export async function POST(request: NextRequest) {
  // Parse and validate webhook payload
  const body = await request.json();
  const parsed = webhookSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  // Process payment event
  if (parsed.data.type === "payment.succeeded") {
    await db.payment.update({
      where: { stripeId: parsed.data.data.id },
      data: { status: "completed" },
    });
  }

  return NextResponse.json({ received: true });
}
```

---

## logic.ts Pattern

Server-side business logic, separate from UI:

```tsx
// app/dashboard/logic.ts
import { db } from "@/lib/db";
import { auth } from "@/lib/auth";

// Fetch dashboard data for current user
export async function getDashboardData() {
  const session = await auth();

  if (!session?.user) {
    throw new Error("Unauthorized");
  }

  // Fetch user stats from database
  const stats = await db.stat.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: "desc" },
  });

  // Calculate aggregated metrics
  const totalTasks = await db.task.count({
    where: { userId: session.user.id },
  });

  const completedTasks = await db.task.count({
    where: { userId: session.user.id, status: "completed" },
  });

  return {
    stats,
    metrics: {
      totalTasks,
      completedTasks,
      completionRate: totalTasks > 0 ? completedTasks / totalTasks : 0,
    },
  };
}

// Check if user has admin access
export async function checkAdminAccess(userId: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { role: true },
  });

  return user?.role === "admin";
}
```

---

## Form with Validation

Client form using Server Action:

```tsx
// app/tasks/components/TaskForm.tsx
"use client";

import { useActionState } from "react";
import { createTask } from "../actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Form for creating new tasks
export function TaskForm() {
  const [state, formAction, pending] = useActionState(createTask, null);

  return (
    <form action={formAction} className="space-y-4">
      <Input name="title" placeholder="Task title" required></Input>
      <Input name="description" placeholder="Description (optional)"></Input>

      <Button type="submit" disabled={pending}>{pending ? "Creating..." : "Create Task"}</Button>

      {/* Show error message */}
      {state?.error && <p className="text-sm text-red-500">{state.error}</p>}
    </form>
  );
}
```

---

## Loading & Error States

### loading.tsx

```tsx
// app/dashboard/loading.tsx
// Skeleton loader for dashboard
export default function DashboardLoading() {
  return (
    <div className="space-y-6 p-6">
      <div className="h-8 w-48 animate-pulse rounded bg-gray-200"></div>

      {/* Skeleton cards */}
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 animate-pulse rounded-lg bg-gray-200"></div>
        ))}
      </div>
    </div>
  );
}
```

### error.tsx

```tsx
// app/dashboard/error.tsx
"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

// Error boundary for dashboard route
export default function DashboardError({ error, reset }: ErrorProps) {
  // Log error to monitoring service
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center gap-4 p-6">
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```
