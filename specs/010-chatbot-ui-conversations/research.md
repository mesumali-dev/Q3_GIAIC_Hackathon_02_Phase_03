# Research Findings: Custom Chatbot UI & Threaded Conversations

## Executive Summary

This research document outlines the key findings and decisions for implementing a custom chatbot UI with threaded conversations. The implementation will integrate with the existing stateless chat API while maintaining clear separation between UI and AI logic.

## Decision: Why Custom UI over ChatKit

### Rationale
- **Control and customization**: Custom UI allows precise control over user experience and feature set
- **Integration simplicity**: Direct integration with existing backend without third-party dependencies
- **Architecture alignment**: Maintains clean separation between frontend UI and backend AI logic
- **Cost considerations**: Eliminates third-party service costs and vendor lock-in
- **Brand consistency**: Ensures UI aligns with application's visual identity

### Alternatives considered
1. **OpenAI ChatKit**: Would introduce external dependency and limit customization
2. **Third-party chat widgets**: Would create tight coupling between UI and AI logic
3. **Custom wrapper around existing UI**: Would add unnecessary complexity

## Decision: Thread-to-conversation_id mapping strategy

### Rationale
- **Backend as source of truth**: Each thread directly corresponds to a conversation_id stored in the database
- **UUID-based identification**: Using UUIDs from backend for secure, unique conversation identification
- **Client-side caching**: Temporary client state for UI responsiveness while relying on backend for persistence
- **URL routing**: Conversation ID in URL parameters for direct linking and browser history

### Implementation approach
- Thread list component fetches conversation summaries from `/api/{user_id}/conversations`
- Each thread item stores the conversation_id locally for quick reference
- Active conversation state maintained with conversation_id during session

## Decision: Frontend state vs backend authority

### Rationale
- **Backend as authoritative source**: All conversation state originates from backend database
- **Frontend as projection**: UI renders data from backend with optimistic updates where appropriate
- **Refresh resilience**: UI reconstructs state from backend after page refresh
- **Real-time consistency**: Backend state is always considered correct in case of conflicts

### Implementation approach
- Fetch conversation list on initial load
- Fetch individual conversation history when selected
- Send messages via API and update UI based on successful responses
- Implement error recovery to resync with backend state when needed

## Decision: Message ordering and pagination strategy

### Rationale
- **Chronological display**: Messages displayed in chronological order (oldest to newest)
- **Performance optimization**: Pagination for long conversations to prevent memory issues
- **User experience**: Load more functionality for accessing older messages
- **Backend efficiency**: Leverage existing database indexing for ordered retrieval

### Implementation approach
- Default: Load most recent N messages (e.g., 50)
- Load more: Fetch additional batches of messages when user scrolls up
- New messages: Append to bottom of existing conversation view
- Sorting: Backend handles chronological ordering based on created_at timestamps

## Decision: Error display and retry behavior

### Rationale
- **User-friendly messaging**: Clear, actionable error messages without exposing technical details
- **Automatic retries**: Smart retry mechanism for transient failures
- **Graceful degradation**: UI remains functional during partial failures
- **State preservation**: Maintain user input during error conditions

### Implementation approach
- Network errors: Display user-friendly message with retry button
- Authentication errors: Redirect to login flow
- API errors: Show specific error messages from backend
- Retry logic: Exponential backoff for network requests
- Input preservation: Keep user message in input field during retries

## Best Practices for Chat Interface Implementation

### UI/UX Best Practices
- **Loading states**: Visual indicators during API calls
- **Message attribution**: Clear distinction between user and assistant messages
- **Responsive design**: Works across mobile and desktop devices
- **Keyboard shortcuts**: Support for Enter to send, Ctrl+Enter for new line
- **Auto-scrolling**: Scroll to bottom when new messages arrive

### Technical Best Practices
- **Component modularity**: Reusable components for different parts of the chat interface
- **Type safety**: Strong typing for message and conversation objects
- **Accessibility**: ARIA labels and keyboard navigation support
- **Performance**: Virtual scrolling for long message lists if needed
- **Security**: Proper sanitization of message content before display

## Frontend Architecture Considerations

### Component Structure
- **ThreadList**: Sidebar showing all user conversations
- **ChatWindow**: Main area displaying conversation history
- **MessageInput**: Input area with send button
- **MessageItem**: Individual message display with role-based styling

### State Management
- **Conversation selection**: Track currently active conversation
- **Message queue**: Temporary storage for unsent messages
- **Loading states**: Track API request statuses
- **Error states**: Handle various error conditions

## Backend API Integration Points

### Existing Endpoints to Utilize
- `POST /api/{user_id}/chat`: Send messages and manage conversations
- Need to implement: `GET /api/{user_id}/conversations`: List all user conversations
- Need to implement: `GET /api/{user_id}/conversations/{id}`: Get conversation details
- Need to implement: `GET /api/{user_id}/conversations/{id}/messages`: Get conversation messages

### Potential Enhancements
- Pagination parameters for message retrieval
- Metadata endpoints for conversation titles/summaries
- Last activity timestamps for conversation sorting