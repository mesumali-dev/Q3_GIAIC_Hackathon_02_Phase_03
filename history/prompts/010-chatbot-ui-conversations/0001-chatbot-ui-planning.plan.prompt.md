---
id: 0001
title: chatbot-ui-planning
stage: plan
date: 2026-01-16
surface: agent
model: claude-haiku-4-5-20251001
feature: 010-chatbot-ui-conversations
branch: 010-chatbot-ui-conversations
user: unknown
command: /sp.plan
labels: ["chatbot", "ui", "conversations", "frontend", "api"]
links:
  spec: /specs/010-chatbot-ui-conversations/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - /specs/010-chatbot-ui-conversations/plan.md
 - /specs/010-chatbot-ui-conversations/research.md
 - /specs/010-chatbot-ui-conversations/data-model.md
 - /specs/010-chatbot-ui-conversations/contracts/api-contracts.md
 - /specs/010-chatbot-ui-conversations/quickstart.md
tests:
 - none
---

## Prompt

\

Phase: Phase 5 – Custom Chatbot UI & Threaded Conversations

Create:
- Custom chatbot UI
- Thread (conversation) management UI
- API integration layer
- Message rendering components

Steps:
1. Design basic chatbot layout:
   - Thread list panel
   - Active chat window
   - Message input box
2. Implement thread list:
   - Fetch user conversations
   - Create new conversation
   - Select existing conversation
3. Implement chat window:
   - Fetch messages for selected conversation
   - Render messages by role (user / assistant)
4. Implement message sending:
   - POST message to /api/{user_id}/chat
   - Pass conversation_id when available
5. Handle API response:
   - Update message list
   - Persist conversation_id for thread
6. Implement loading and error states
7. Ensure UI recovers correctly after refresh
8. Validate user-scoped data access

Decisions needing documentation:
- Why custom UI over ChatKit
- Thread-to-conversation_id mapping strategy
- Frontend state vs backend authority
- Message ordering and pagination strategy
- Error display and retry behavior

Testing strategy:
- Start a new conversation thread
- Continue an existing conversation
- Switch between multiple threads
- Refresh page and resume conversation
- Verify task operations via chat
- Validate behavior on API errors

Quality validation:
- Frontend holds no business logic
- Backend remains the single source of truth
- Threaded conversations behave deterministically
- UI is resilient to refreshes and navigation
- Clean separation between UI and AI system

Technical details:
- UI communicates only with Phase 4 chat API
- No AI logic in frontend
- No MCP tool awareness in UI
- Designed for future UI enhancements without backend changes

## Response snapshot

Successfully completed the planning phase for the Custom Chatbot UI & Threaded Conversations feature. Created comprehensive documentation including research findings, data models, API contracts, and implementation guide. The plan defines a custom chatbot UI that integrates with the existing stateless chat API while supporting threaded conversations with proper backend persistence.

## Outcome

- ✅ Impact: Completed comprehensive planning for chatbot UI with threaded conversations, including research, data models, API contracts, and implementation guide
- 🧪 Tests: none
- 📁 Files: Created/updated 5 files: plan.md, research.md, data-model.md, api-contracts.md, quickstart.md
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Clear separation of concerns between frontend UI and backend AI logic is crucial for maintainable architecture

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
