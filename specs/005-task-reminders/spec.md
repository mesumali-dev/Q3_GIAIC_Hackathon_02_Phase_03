# Feature Specification: Task Reminders & Notifications

**Feature Branch**: `005-task-reminders`
**Created**: 2026-01-02
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application – Part 4: Task Reminders & Notifications"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Basic Task Reminder (Priority: P1)

A user wants to set a one-time reminder for an important task so they don't forget to complete it.

**Why this priority**: Core functionality - without the ability to create reminders, no other reminder features can work. This is the minimum viable product for the reminder system.

**Independent Test**: Can be fully tested by creating a task, setting a reminder date/time, and verifying the reminder is saved and triggers a notification at the specified time. Delivers immediate value by allowing users to schedule reminders.

**Acceptance Scenarios**:

1. **Given** a user has an existing task, **When** they set a reminder date and time for that task, **Then** the reminder is saved and associated with the task
2. **Given** a user has set a reminder, **When** the reminder time arrives or has passed, **Then** a notification popup appears showing the task details
3. **Given** a user logs in, **When** there are due or overdue reminders, **Then** all due reminders are displayed immediately as notifications
4. **Given** a user has pending notifications, **When** they view the navbar, **Then** the notification count badge displays the correct number of unread notifications

---

### User Story 2 - View and Manage Notifications (Priority: P2)

A user wants to see all their notifications in one place and dismiss them after acknowledging.

**Why this priority**: Essential for usability - users need a way to review missed notifications and manage notification clutter. Without this, notifications become noise rather than helpful reminders.

**Independent Test**: Can be tested independently by creating several overdue reminders, logging in, and verifying that clicking the notification icon shows all notifications and allows deletion. Delivers value by giving users control over their notification inbox.

**Acceptance Scenarios**:

1. **Given** a user has unread notifications, **When** they click the notification icon in the navbar, **Then** a dropdown/list shows all current notifications with task details
2. **Given** a notification is displayed in the list, **When** the user clicks on it, **Then** a popup shows the full reminder details including task name and original reminder time
3. **Given** a user views a notification, **When** they delete it, **Then** the notification is removed from the UI and the navbar count decrements
4. **Given** a user deletes a notification, **When** they refresh the page or log out and back in, **Then** the deleted notification does not reappear

---

### User Story 3 - Create Repeating Task Reminders (Priority: P3)

A user wants to set a reminder that repeats at fixed intervals for recurring tasks (e.g., weekly status report, daily standup prep).

**Why this priority**: Advanced functionality - provides additional value for power users with recurring tasks but is not essential for basic reminder functionality. Most users will start with single reminders before needing repeating ones.

**Independent Test**: Can be tested independently by setting a reminder with a repeat interval (e.g., every 15 minutes) and repeat count (e.g., 2 times), then verifying notifications trigger at the correct intervals. Delivers value for users managing recurring responsibilities.

**Acceptance Scenarios**:

1. **Given** a user creates a reminder, **When** they specify a repeat interval (e.g., 15 minutes) and repeat count (e.g., 2 times), **Then** the reminder schedule is saved with the repeat configuration
2. **Given** a repeating reminder exists, **When** the initial reminder time arrives, **Then** a notification appears and the next repeat is scheduled
3. **Given** a repeating reminder has triggered, **When** the repeat interval elapses, **Then** another notification appears for the same task
4. **Given** a repeating reminder has triggered the configured number of times, **When** the final repeat completes, **Then** no additional notifications are created
5. **Given** a user deletes a repeating reminder, **When** they delete it, **Then** all future scheduled repeats are cancelled

---

### Edge Cases

- What happens when a user sets a reminder for a time in the past?
- What happens when the system time changes (timezone shift, daylight saving)?
- What happens if a user deletes the task that has reminders associated with it?
- How does the system handle reminders for tasks that span multiple days?
- What happens when a user has hundreds of overdue reminders from extended absence?
- How does the system handle concurrent reminder triggers (multiple reminders due at the same time)?
- What happens when a user sets a repeat interval of 0 or negative value?
- What happens when repeat count is set to 0 or an unreasonably large number?

## Requirements *(mandatory)*

### Functional Requirements

**Reminder Creation:**

- **FR-001**: System MUST allow users to create a reminder for any existing task
- **FR-002**: System MUST require users to specify a reminder date and time when creating a reminder
- **FR-003**: System MUST allow users to optionally specify a repeat interval in minutes (e.g., 15, 30, 60)
- **FR-004**: System MUST allow users to optionally specify a repeat count (number of times to repeat)
- **FR-005**: System MUST persist reminder data across user sessions
- **FR-006**: System MUST associate each reminder with exactly one task and one user

**Reminder Evaluation:**

- **FR-007**: System MUST check for due reminders when a user logs in
- **FR-008**: System MUST check for due reminders when a user loads or refreshes a page
- **FR-009**: System MUST consider a reminder "due" if the current time is equal to or past the reminder time
- **FR-010**: System MUST enforce user-scoped reminders via JWT authentication (users can only see their own reminders)
- **FR-011**: System MUST calculate next repeat time by adding the interval to the current reminder time
- **FR-012**: System MUST stop repeating reminders after the configured repeat count is reached

**Notification Display:**

- **FR-013**: System MUST display a popup notification immediately when due reminders are detected
- **FR-014**: System MUST display a notification count badge on the navbar showing the number of unread notifications
- **FR-015**: System MUST show notification details (task name, reminder time, message) in the popup
- **FR-016**: System MUST provide a notification list view accessible via the navbar notification icon
- **FR-017**: System MUST allow users to click a notification to view its full details

**Reminder Deletion:**

- **FR-018**: System MUST allow users to delete individual reminders/notifications
- **FR-019**: System MUST remove the reminder schedule from the database when deleted
- **FR-020**: System MUST remove the notification entry from the database when deleted
- **FR-021**: System MUST immediately update the UI when a notification is deleted (remove from list, decrement badge count)
- **FR-022**: System MUST ensure deleted reminders never reappear after page refresh or re-login

**Data Constraints:**

- **FR-023**: System MUST reject reminders with invalid date/time formats
- **FR-024**: System MUST handle reminders set for past times by treating them as immediately due
- **FR-025**: System MUST validate repeat interval as a positive integer (if provided)
- **FR-026**: System MUST validate repeat count as a positive integer (if provided)

**Backend API:**

- **FR-027**: System MUST provide an API endpoint to create reminders
- **FR-028**: System MUST provide an API endpoint to fetch due reminders for the authenticated user
- **FR-029**: System MUST provide an API endpoint to delete reminders by ID
- **FR-030**: System MUST return appropriate HTTP status codes for all API operations (2xx for success, 4xx for client errors, 5xx for server errors)

### Key Entities

- **Reminder**: Represents a scheduled notification for a task
  - Attributes: reminder ID, task reference, user reference, initial reminder time, repeat interval (optional), repeat count (optional), times triggered, created timestamp
  - Relationships: belongs to one Task, belongs to one User

- **Notification**: Represents a triggered reminder that needs user acknowledgment
  - Attributes: notification ID, reminder reference, task reference, user reference, trigger time, viewed status, created timestamp
  - Relationships: originated from one Reminder, associated with one Task, belongs to one User

- **Task**: Existing entity representing a user's todo item
  - New relationship: can have zero or more Reminders

- **User**: Existing entity representing an authenticated user
  - New relationship: can have zero or more Reminders and Notifications

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a reminder and see it trigger within 5 seconds of the specified time
- **SC-002**: Users can set up a repeating reminder and receive exactly the configured number of notifications
- **SC-003**: 100% of due reminders are displayed when a user logs in or refreshes the page
- **SC-004**: Deleted reminders and notifications are removed from the UI instantly and never reappear
- **SC-005**: Notification count badge accurately reflects the number of unread notifications at all times
- **SC-006**: Users can configure and save a reminder in under 30 seconds using the reminder UI
- **SC-007**: System handles at least 50 concurrent due reminders for a single user without performance degradation
- **SC-008**: Reminder data persists across multiple login/logout cycles without data loss
- **SC-009**: Users can distinguish between different reminder notifications by task details
- **SC-010**: Zero unauthorized access to other users' reminders or notifications (enforced by JWT)

## Assumptions

- Users have an active internet connection when using the application (no offline support for reminders)
- System time on the server is accurate and synchronized (relies on server time for reminder evaluation)
- Reminders are evaluated on-demand (login, page load, refresh) rather than via background workers or scheduled jobs
- Notification popups use browser/in-app notifications (not email, SMS, or push notifications)
- Repeat intervals are specified in minutes for simplicity
- Maximum reasonable repeat count is 100 (to prevent abuse)
- Tasks cannot be deleted while they have active reminders (or reminders are cascade-deleted with tasks)
- The existing authentication system provides valid JWT tokens for user identification
- Database supports timestamp/datetime fields with timezone awareness
- Frontend uses Tailwind CSS for consistent styling with the rest of the application

## Constraints

- **No background workers**: Reminder evaluation must happen synchronously during API requests (login, page load, manual refresh)
- **No cron jobs**: Cannot use scheduled tasks or time-based triggers
- **Use existing auth**: Must leverage the current JWT-based authentication system
- **Use existing task system**: Must integrate with the current task CRUD functionality
- **Database compatibility**: Must work with the existing database schema and ORM (SQLModel)
- **Frontend framework**: Must use Next.js 16+ and Tailwind CSS
- **Backend framework**: Must use FastAPI and Python 3.11+
- **Stateless backend**: Each API request must independently evaluate due reminders (cannot rely on server-side state)

## Dependencies

- Existing User authentication system (JWT-based)
- Existing Task CRUD system (database tables, API endpoints, frontend components)
- Database with timestamp support (Neon PostgreSQL)
- Frontend routing and state management (Next.js)
- Backend ORM and validation (SQLModel, PyJWT)

## Out of Scope

- Email or SMS notifications (only in-app notifications)
- Push notifications to mobile devices
- Reminder snooze functionality
- Reminder editing (users must delete and recreate)
- Reminder templates or presets
- Bulk reminder operations (create multiple, delete multiple)
- Reminder sharing between users
- Natural language reminder input ("remind me tomorrow at 3pm")
- Calendar integration or sync
- Reminder priority levels
- Custom notification sounds or visual themes
- Reminder history or analytics
- Timezone selection (uses server/system timezone)
