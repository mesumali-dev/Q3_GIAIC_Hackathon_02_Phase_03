# Implementation Tasks: Custom Chatbot UI & Threaded Conversations

**Feature**: Custom Chatbot UI & Threaded Conversations
**Branch**: `010-chatbot-ui-conversations`
**Spec**: `/specs/010-chatbot-ui-conversations/spec.md`

## Overview

This document contains the implementation tasks for the Custom Chatbot UI & Threaded Conversations feature. The implementation will create a custom chat interface that integrates with the existing stateless chat API while supporting threaded conversations with proper backend persistence.

## Dependencies

- Backend must have conversation and message models already implemented
- Backend must have existing `/api/{user_id}/chat` endpoint
- Authentication system (Better Auth) must be operational

## Parallel Execution Examples

**User Story 1**: Can be developed independently with stubbed API calls initially
**User Story 2**: Can be developed in parallel with US1 after basic API contracts are defined
**User Story 3**: Core messaging functionality that other stories depend on

## Implementation Strategy

**MVP Scope**: Focus on User Story 1 (Start New Conversation Thread) as the minimum viable product, then incrementally add other user stories. This ensures we have a working foundation that allows users to start and send messages in new conversations before adding more complex features like switching between conversations.

---

## Phase 1: Setup Tasks

- [x] T001 Set up project structure per implementation plan in backend/src/api/conversations.py and frontend/src/app/chat/
- [x] T002 Update backend dependencies to include new conversation API routes
- [x] T003 Update frontend dependencies for chat UI components

---

## Phase 2: Foundational Tasks

- [x] T004 [P] Implement Conversation API router in backend/src/api/conversations.py
- [x] T005 [P] Implement new API endpoints in backend according to contracts
- [x] T006 [P] Update frontend API client with new conversation methods
- [x] T007 [P] Create basic chat page structure in frontend/src/app/chat/page.tsx
- [x] T008 [P] Create shared types/interfaces for conversation data models

---

## Phase 3: User Story 1 - Start New Conversation Thread (Priority: P1)

**Goal**: Enable authenticated users to initiate new conversation threads to manage their tasks through natural language interaction.

**Independent Test**: Can be fully tested by logging in and clicking the "New Conversation" button, then sending a message to the assistant. The system should create a new conversation thread and return a response.

**Acceptance Scenarios**:
1. Given user is logged in and on the chat interface, When user clicks "New Conversation" button, Then a new conversation thread is created with a unique conversation_id and displayed in the conversation list
2. Given user has an active conversation, When user starts a new conversation, Then the new conversation becomes active and previous conversation remains accessible

### Tests (if requested)
- [ ] T009 [P] [US1] Create unit tests for new conversation creation endpoint
- [ ] T010 [P] [US1] Create integration tests for starting new conversations

### Implementation Tasks
- [x] T011 [P] [US1] Create POST /api/{user_id}/conversations endpoint in backend/src/api/conversations.py
- [x] T012 [US1] Implement conversation creation logic with validation
- [x] T013 [P] [US1] Create New Conversation button UI component
- [x] T014 [US1] Implement conversation creation API call in frontend
- [x] T015 [US1] Update UI to show new conversation as active after creation

---

## Phase 4: User Story 2 - Continue Existing Conversation Threads (Priority: P1)

**Goal**: Allow authenticated users to select and continue existing conversation threads to maintain context and continue task management conversations with the AI assistant.

**Independent Test**: Can be fully tested by selecting an existing conversation from the list and verifying that all previous messages are displayed and new messages can be sent and received.

**Acceptance Scenarios**:
1. Given user has multiple conversation threads, When user selects a previous conversation, Then the conversation history loads and displays all previous messages in chronological order
2. Given user is viewing an existing conversation, When user sends a new message, Then the message is added to the conversation and the assistant responds appropriately
3. Given user refreshes the page, When user returns to the application, Then the user can resume their previous conversations with the same state

### Tests (if requested)
- [ ] T016 [P] [US2] Create unit tests for getting conversation details endpoint
- [ ] T017 [P] [US2] Create integration tests for continuing conversations

### Implementation Tasks
- [x] T018 [P] [US2] Create GET /api/{user_id}/conversations/{conversation_id} endpoint in backend/src/api/conversations.py
- [x] T019 [P] [US2] Create GET /api/{user_id}/conversations/{conversation_id}/messages endpoint
- [x] T020 [US2] Implement conversation retrieval with validation
- [x] T021 [US2] Implement message retrieval with pagination
- [x] T022 [P] [US2] Create conversation selection UI in ThreadList component
- [x] T023 [US2] Implement conversation loading logic in frontend
- [x] T024 [US2] Implement message loading for selected conversation

---

## Phase 5: User Story 3 - Send and Receive Messages (Priority: P1)

**Goal**: Enable users to send messages to the AI assistant and receive responses that are clearly displayed with proper attribution to distinguish between user and assistant messages.

**Independent Test**: Can be fully tested by sending a message to the assistant and verifying that the response is correctly displayed with proper formatting and attribution.

**Acceptance Scenarios**:
1. Given user is in an active conversation, When user submits a message, Then the message appears in the conversation thread with user attribution and is sent to the backend API
2. Given user message is being processed by the backend, When assistant response is received, Then the response appears in the conversation thread with assistant attribution
3. Given user sends malformed or invalid message, When message is submitted, Then appropriate error message is displayed to the user

### Tests (if requested)
- [ ] T025 [P] [US3] Create unit tests for sending messages via chat endpoint
- [ ] T026 [P] [US3] Create integration tests for message sending/receiving

### Implementation Tasks
- [x] T027 [P] [US3] Create MessageInput component in frontend/src/components/Chat/MessageInput.tsx
- [x] T028 [P] [US3] Create MessageList component in frontend/src/components/Chat/MessageList.tsx
- [x] T029 [P] [US3] Create MessageItem component in frontend/src/components/Chat/MessageItem.tsx
- [x] T030 [US3] Implement message sending logic with proper conversation_id handling
- [x] T031 [US3] Implement message display with role-based styling
- [x] T032 [US3] Add loading states for message sending/receiving
- [x] T033 [US3] Add error handling for message operations

---

## Phase 6: User Story 4 - Manage Multiple Conversations (Priority: P2)

**Goal**: Allow users to view a list of their conversation threads and switch between them to manage different task management contexts or topics.

**Independent Test**: Can be fully tested by creating multiple conversations and switching between them to verify that each maintains its own context and history.

**Acceptance Scenarios**:
1. Given user has multiple conversations, When user views the conversation list, Then all conversations are displayed with relevant metadata (title, last message, timestamp)
2. Given user is in one conversation, When user selects a different conversation from the list, Then the interface switches to display the selected conversation's content
3. Given user creates/deletes conversations, When conversation list is refreshed, Then the list accurately reflects the current state

### Tests (if requested)
- [ ] T034 [P] [US4] Create unit tests for listing conversations endpoint
- [ ] T035 [P] [US4] Create integration tests for conversation management

### Implementation Tasks
- [x] T036 [P] [US4] Create GET /api/{user_id}/conversations endpoint in backend/src/api/conversations.py
- [x] T037 [US4] Implement conversation listing with pagination and sorting
- [x] T038 [P] [US4] Create ThreadList component in frontend/src/components/Chat/ThreadList.tsx
- [x] T039 [P] [US4] Create ThreadItem component in frontend/src/components/Chat/ThreadItem.tsx
- [x] T040 [US4] Implement conversation listing in frontend with pagination
- [x] T041 [US4] Add conversation switching functionality
- [x] T042 [US4] Implement conversation metadata display (titles, timestamps)

---

## Phase 7: User Story 5 - View Conversation History (Priority: P2)

**Goal**: Enable users to view the complete history of messages within a conversation thread in chronological order to maintain context and review previous interactions.

**Independent Test**: Can be fully tested by opening a conversation with multiple messages and verifying that all messages are displayed in correct chronological order.

**Acceptance Scenarios**:
1. Given a conversation with multiple messages, When user opens the conversation, Then all messages are displayed in chronological order from oldest to newest
2. Given user scrolls through a long conversation, When messages are loaded, Then all messages remain properly attributed and formatted

### Tests (if requested)
- [ ] T043 [P] [US5] Create unit tests for message pagination endpoint
- [ ] T044 [P] [US5] Create integration tests for conversation history

### Implementation Tasks
- [x] T045 [P] [US5] Enhance message retrieval endpoint with pagination support
- [x] T046 [US5] Implement message ordering by created_at timestamp
- [x] T047 [P] [US5] Add infinite scroll or load more functionality to MessageList
- [x] T048 [US5] Ensure proper chronological ordering of messages in UI
- [x] T049 [US5] Add message timestamp display

---

## Phase 8: Polish & Cross-Cutting Concerns

### UI Polish
- [x] T050 [P] Implement responsive design for chat interface
- [x] T051 [P] Add loading spinners and skeleton screens
- [x] T052 Add proper error boundary components
- [ ] T053 Implement proper focus states and keyboard navigation
- [ ] T054 Add accessibility attributes (ARIA labels, etc.)

### Error Handling & Edge Cases
- [x] T055 [P] Implement proper error handling for network failures
- [x] T056 Handle conversation not found scenarios
- [x] T057 Handle authentication failures gracefully
- [x] T058 Implement retry mechanisms for failed operations
- [x] T059 Add proper error messages for user guidance

### Performance
- [ ] T060 [P] Optimize message rendering with virtualization if needed
- [ ] T061 Implement proper caching strategies
- [x] T062 Add loading states for API operations
- [x] T063 Optimize API calls to prevent over-fetching

### Security
- [x] T064 [P] Ensure all API endpoints validate user ownership
- [x] T065 Sanitize message content before display
- [x] T066 Validate conversation_id format before API calls
- [x] T067 Verify JWT authentication on all endpoints

### Documentation & Testing
- [x] T068 [P] Add JSDoc comments to all new functions/components
- [x] T069 Update API documentation with new endpoints
- [ ] T070 Add unit tests for critical business logic
- [ ] T071 Create end-to-end tests for key user journeys
- [x] T072 Update README with usage instructions