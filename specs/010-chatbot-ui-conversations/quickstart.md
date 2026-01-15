# Quickstart Guide: Custom Chatbot UI & Threaded Conversations

## Overview

This guide provides step-by-step instructions for implementing the custom chatbot UI with threaded conversations. The implementation integrates with the existing stateless chat API while maintaining separation between UI and AI logic.

## Prerequisites

- Backend: Python 3.11+, FastAPI, SQLModel, PyJWT
- Frontend: Node.js 18+, Next.js 16+, TypeScript 5.x
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT tokens

## Step 1: Backend API Extensions

### 1.1 Create Conversation API Routes

First, create the new API routes for conversation management in `backend/src/api/conversations.py`:

```python
"""
Conversation management API router.

Provides endpoints for listing, retrieving, and managing conversations.
Integrates with existing chat functionality while maintaining separation of concerns.

@see specs/010-chatbot-ui-conversations/contracts/api-contracts.md for API contract
"""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.database import get_db
from src.middleware.auth import CurrentUser, verify_user_ownership
from src.models.conversation import Conversation
from src.models.message import Message

router = APIRouter(prefix="/api", tags=["Conversations"])
logger = structlog.get_logger(__name__)


@router.get(
    "/{user_id}/conversations",
    summary="List user conversations",
    description="Retrieve a paginated list of conversations for the specified user.",
)
def list_conversations(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
    sort: str = "updated_desc",
) -> dict:
    """List all conversations for a user."""
    verify_user_ownership(current_user["user_id"], str(user_id))

    # Validate sort parameter
    valid_sorts = {"updated_desc", "updated_asc", "created_desc", "created_asc"}
    if sort not in valid_sorts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort parameter. Valid values: {', '.join(valid_sorts)}",
        )

    # Build query with sorting
    query = select(Conversation).where(Conversation.user_id == user_id)

    # Apply sorting
    if sort == "updated_desc":
        query = query.order_by(Conversation.updated_at.desc())
    elif sort == "updated_asc":
        query = query.order_by(Conversation.updated_at.asc())
    elif sort == "created_desc":
        query = query.order_by(Conversation.created_at.desc())
    elif sort == "created_asc":
        query = query.order_by(Conversation.created_at.asc())

    # Apply pagination
    query = query.offset(offset).limit(limit)

    conversations = db.exec(query).all()

    # Get total count for pagination metadata
    count_query = select(Conversation).where(Conversation.user_id == user_id)
    total_count = db.exec(count_query).count()

    return {
        "conversations": [
            {
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ],
        "count": total_count,
        "has_more": len(conversations) == limit and total_count > offset + limit,
    }


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    summary="Get conversation details",
    description="Retrieve details of a specific conversation.",
)
def get_conversation(
    user_id: UUID,
    conversation_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Get details of a specific conversation."""
    verify_user_ownership(current_user["user_id"], str(user_id))

    conversation = db.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "message_count": db.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).count(),
    }


@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    summary="Get conversation messages",
    description="Retrieve messages for a specific conversation.",
)
def get_conversation_messages(
    user_id: UUID,
    conversation_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
    sort: str = "asc",
) -> dict:
    """Get messages for a specific conversation."""
    verify_user_ownership(current_user["user_id"], str(user_id))

    conversation = db.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Validate sort parameter
    if sort not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid sort parameter. Valid values: asc, desc",
        )

    # Build query with sorting
    query = select(Message).where(Message.conversation_id == conversation_id)

    if sort == "asc":
        query = query.order_by(Message.created_at.asc())
    else:
        query = query.order_by(Message.created_at.desc())

    # Apply pagination
    query = query.offset(offset).limit(limit)
    messages = db.exec(query).all()

    # Get total count for pagination metadata
    count_query = select(Message).where(Message.conversation_id == conversation_id)
    total_count = db.exec(count_query).count()

    return {
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
        "count": total_count,
        "has_more": len(messages) == limit and total_count > offset + limit,
    }


@router.delete(
    "/{user_id}/conversations/{conversation_id}",
    summary="Delete a conversation",
    description="Delete a specific conversation and all its messages.",
)
def delete_conversation(
    user_id: UUID,
    conversation_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a conversation."""
    verify_user_ownership(current_user["user_id"], str(user_id))

    conversation = db.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Delete all messages in the conversation first (due to foreign key constraint)
    message_query = select(Message).where(Message.conversation_id == conversation_id)
    messages = db.exec(message_query).all()
    for message in messages:
        db.delete(message)

    # Delete the conversation
    db.delete(conversation)
    db.commit()


@router.post(
    "/{user_id}/conversations",
    summary="Create a new conversation",
    description="Create a new conversation.",
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    title: str | None = None,
) -> dict:
    """Create a new conversation."""
    verify_user_ownership(current_user["user_id"], str(user_id))

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
    }
```

### 1.2 Register the new router in `backend/src/api/__init__.py`:

```python
from .chat import router as chat_router
from .conversations import router as conversations_router

__all__ = ["chat_router", "conversations_router"]
```

### 1.3 Update `backend/src/main.py` to include the new router:

```python
from src.api import chat_router, conversations_router

app.include_router(chat_router)
app.include_router(conversations_router)
```

## Step 2: Frontend Implementation

### 2.1 Update API client in `frontend/src/lib/api.ts`

Add the new conversation management functions:

```typescript
// Add to existing interfaces
export interface ConversationSummary {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface MessageItem {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface GetConversationsResponse {
  conversations: ConversationSummary[];
  count: number;
  has_more: boolean;
}

export interface GetMessagesResponse {
  messages: MessageItem[];
  count: number;
  has_more: boolean;
}

// Add new API functions
export async function getUserConversations(
  userId: string,
  limit: number = 50,
  offset: number = 0,
  sort: string = "updated_desc"
): Promise<ApiResponse<GetConversationsResponse>> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
    sort,
  });
  return apiRequest<GetConversationsResponse>(
    `/api/${userId}/conversations?${params}`
  );
}

export async function getConversation(
  userId: string,
  conversationId: string
): Promise<ApiResponse<ConversationDetail>> {
  return apiRequest<ConversationDetail>(
    `/api/${userId}/conversations/${conversationId}`
  );
}

export async function getConversationMessages(
  userId: string,
  conversationId: string,
  limit: number = 50,
  offset: number = 0,
  sort: string = "asc"
): Promise<ApiResponse<GetMessagesResponse>> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
    sort,
  });
  return apiRequest<GetMessagesResponse>(
    `/api/${userId}/conversations/${conversationId}/messages?${params}`
  );
}

export async function createConversation(
  userId: string,
  title?: string
): Promise<ApiResponse<ConversationDetail>> {
  return apiRequest<ConversationDetail>(`/api/${userId}/conversations`, {
    method: 'POST',
    body: JSON.stringify({ title: title || null }),
  });
}

export async function deleteConversation(
  userId: string,
  conversationId: string
): Promise<ApiResponse<void>> {
  return apiRequest<void>(`/api/${userId}/conversations/${conversationId}`, {
    method: 'DELETE',
  });
}
```

### 2.2 Create Chat Components

Create the chat UI components in `frontend/src/components/Chat/`:

**MessageItem.tsx:**
```tsx
'use client';

import React from 'react';
import { MessageItem as MessageType } from '@/lib/api';

interface MessageItemProps {
  message: MessageType;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-200 text-gray-800 rounded-bl-none'
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

export default MessageItem;
```

**MessageList.tsx:**
```tsx
'use client';

import React from 'react';
import MessageItem from './MessageItem';
import { MessageItem as MessageType } from '@/lib/api';

interface MessageListProps {
  messages: MessageType[];
  isLoading?: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex justify-center items-center h-full text-gray-500">
        No messages yet. Start a conversation!
      </div>
    );
  }

  return (
    <div className="overflow-y-auto flex-1 p-4 space-y-2">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  );
};

export default MessageList;
```

**MessageInput.tsx:**
```tsx
'use client';

import React, { useState } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t p-4 bg-white">
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || disabled}
          className="bg-blue-500 text-white rounded-lg px-4 py-2 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default MessageInput;
```

**ThreadItem.tsx:**
```tsx
'use client';

import React from 'react';
import { ConversationSummary } from '@/lib/api';

interface ThreadItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onClick: () => void;
}

const ThreadItem: React.FC<ThreadItemProps> = ({ conversation, isActive, onClick }) => {
  return (
    <div
      className={`p-3 border-b cursor-pointer hover:bg-gray-50 ${
        isActive ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
      }`}
      onClick={onClick}
    >
      <div className="font-medium truncate">
        {conversation.title || `Conversation ${new Date(conversation.created_at).toLocaleDateString()}`}
      </div>
      <div className="text-xs text-gray-500 truncate">
        Updated: {new Date(conversation.updated_at).toLocaleString()}
      </div>
    </div>
  );
};

export default ThreadItem;
```

**ThreadList.tsx:**
```tsx
'use client';

import React, { useEffect, useState } from 'react';
import ThreadItem from './ThreadItem';
import { ConversationSummary, getUserConversations } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface ThreadListProps {
  onSelectConversation: (conversationId: string) => void;
  activeConversationId: string | null;
  onCreateNewConversation: () => void;
}

const ThreadList: React.FC<ThreadListProps> = ({
  onSelectConversation,
  activeConversationId,
  onCreateNewConversation,
}) => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      loadConversations();
    }
  }, [user]);

  const loadConversations = async () => {
    if (!user?.id) return;

    setIsLoading(true);
    const response = await getUserConversations(user.id);

    if (response.data) {
      setConversations(response.data.conversations);
    }

    setIsLoading(false);
  };

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="p-3 border-b">
        <button
          onClick={onCreateNewConversation}
          className="w-full bg-blue-500 text-white rounded-lg px-4 py-2 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          + New Conversation
        </button>
      </div>
      <div className="overflow-y-auto max-h-[calc(100vh-200px)]">
        {conversations.map((conv) => (
          <ThreadItem
            key={conv.id}
            conversation={conv}
            isActive={conv.id === activeConversationId}
            onClick={() => onSelectConversation(conv.id)}
          />
        ))}
        {conversations.length === 0 && (
          <div className="p-4 text-gray-500 text-center">No conversations yet</div>
        )}
      </div>
    </div>
  );
};

export default ThreadList;
```

**ChatWindow.tsx:**
```tsx
'use client';

import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import {
  getConversationMessages,
  sendChatMessage,
  ChatRequest,
  MessageItem as MessageType,
  ChatResponse
} from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface ChatWindowProps {
  conversationId: string | null;
  onNewConversationCreated?: (conversationId: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId, onNewConversationCreated }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (conversationId && user?.id) {
      loadConversationHistory();
    } else {
      // Reset messages when no conversation is selected
      setMessages([]);
    }
  }, [conversationId, user?.id]);

  const loadConversationHistory = async () => {
    if (!conversationId || !user?.id) return;

    setIsLoading(true);
    const response = await getConversationMessages(user.id, conversationId);

    if (response.data) {
      // Transform the API response to match our MessageItem interface
      const transformedMessages = response.data.messages.map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant' | 'system',
        content: msg.content,
        created_at: msg.created_at
      }));
      setMessages(transformedMessages);
    }

    setIsLoading(false);
  };

  const handleSendMessage = async (message: string) => {
    if (!user?.id || isSending) return;

    setIsSending(true);

    // Add the user's message optimistically
    const userMessage: MessageType = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const request: ChatRequest = {
        message,
        conversation_id: conversationId || null,
      };

      const response = await sendChatMessage(user.id, request);

      if (response.data) {
        const chatResponse = response.data as ChatResponse;

        // Add the assistant's response
        const assistantMessage: MessageType = {
          id: `response-${Date.now()}`,
          role: 'assistant',
          content: chatResponse.assistant_message,
          created_at: chatResponse.created_at.toISOString(),
        };

        setMessages(prev => [...prev, assistantMessage]);

        // If this was a new conversation, notify the parent
        if (!conversationId && chatResponse.conversation_id) {
          onNewConversationCreated?.(chatResponse.conversation_id);
        }
      } else {
        // Remove the user's message if the API call failed
        setMessages(prev => prev.slice(0, -1));
        alert(response.error || 'Failed to send message');
      }
    } catch (error) {
      // Remove the user's message if there was an error
      setMessages(prev => prev.slice(0, -1));
      alert('Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-3 bg-gray-50">
        <h2 className="text-lg font-semibold">
          {conversationId ? 'Active Conversation' : 'Start New Conversation'}
        </h2>
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isSending || !conversationId}
      />
    </div>
  );
};

export default ChatWindow;
```

### 2.3 Create the main Chat Page

Create `frontend/src/app/chat/page.tsx`:

```tsx
'use client';

import React, { useState } from 'react';
import ThreadList from '@/components/Chat/ThreadList';
import ChatWindow from '@/components/Chat/ChatWindow';
import { useAuth } from '@/contexts/AuthContext';

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Please log in to access the chat.</p>
      </div>
    );
  }

  const handleSelectConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
  };

  const handleCreateNewConversation = () => {
    setActiveConversationId(null);
  };

  const handleNewConversationCreated = (conversationId: string) => {
    setActiveConversationId(conversationId);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Thread List Panel */}
      <div className="w-80 bg-white border-r flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold">Chat Conversations</h1>
        </div>
        <ThreadList
          onSelectConversation={handleSelectConversation}
          activeConversationId={activeConversationId}
          onCreateNewConversation={handleCreateNewConversation}
        />
      </div>

      {/* Chat Window */}
      <div className="flex-1 flex flex-col">
        <ChatWindow
          conversationId={activeConversationId}
          onNewConversationCreated={handleNewConversationCreated}
        />
      </div>
    </div>
  );
};

export default ChatPage;
```

### 2.4 Update the main layout to include auth context

Update `frontend/src/app/layout.tsx` to include the auth provider:

```tsx
import { AuthProvider } from '@/contexts/AuthContext';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

## Step 3: Testing

### 3.1 Backend Tests

Create tests for the new API endpoints in `backend/tests/unit/test_conversations_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import patch
from uuid import uuid4

from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_list_conversations(client, db_session, authenticated_headers):
    # Create test conversations
    user_id = uuid4()
    conv1 = Conversation(user_id=user_id, title="Test Conversation 1")
    conv2 = Conversation(user_id=user_id, title="Test Conversation 2")
    db_session.add(conv1)
    db_session.add(conv2)
    db_session.commit()

    response = client.get(f"/api/{user_id}/conversations", headers=authenticated_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["conversations"]) == 2


def test_get_conversation(client, db_session, authenticated_headers):
    user_id = uuid4()
    conversation = Conversation(user_id=user_id, title="Test Conversation")
    db_session.add(conversation)
    db_session.commit()

    response = client.get(
        f"/api/{user_id}/conversations/{conversation.id}",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(conversation.id)
    assert data["title"] == "Test Conversation"


def test_create_conversation(client, db_session, authenticated_headers):
    user_id = uuid4()

    response = client.post(
        f"/api/{user_id}/conversations",
        json={"title": "New Conversation"},
        headers=authenticated_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Conversation"

    # Verify it was saved to the database
    saved_conv = db_session.get(Conversation, data["id"])
    assert saved_conv is not None
    assert saved_conv.title == "New Conversation"


def test_delete_conversation(client, db_session, authenticated_headers):
    user_id = uuid4()
    conversation = Conversation(user_id=user_id, title="To Delete")
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Test message"
    )
    db_session.add(conversation)
    db_session.add(message)
    db_session.commit()

    # Verify conversation and message exist
    assert db_session.get(Conversation, conversation.id) is not None
    assert db_session.get(Message, message.id) is not None

    response = client.delete(
        f"/api/{user_id}/conversations/{conversation.id}",
        headers=authenticated_headers
    )

    assert response.status_code == 204

    # Verify they were deleted
    assert db_session.get(Conversation, conversation.id) is None
    assert db_session.get(Message, message.id) is None
```

### 3.2 Frontend Tests

Create tests for the chat components in `frontend/tests/components/chat/`:

**MessageItem.test.tsx:**
```tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import MessageItem from '@/components/Chat/MessageItem';

describe('MessageItem', () => {
  const mockMessage = {
    id: '1',
    role: 'user',
    content: 'Hello, world!',
    created_at: new Date().toISOString(),
  };

  it('renders user message correctly', () => {
    render(<MessageItem message={mockMessage} />);
    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
  });

  it('applies correct styling for user messages', () => {
    render(<MessageItem message={{...mockMessage, role: 'user'}} />);
    const messageElement = screen.getByText('Hello, world!');
    expect(messageElement.parentElement).toHaveClass('bg-blue-500');
  });

  it('applies correct styling for assistant messages', () => {
    render(<MessageItem message={{...mockMessage, role: 'assistant'}} />);
    const messageElement = screen.getByText('Hello, world!');
    expect(messageElement.parentElement).toHaveClass('bg-gray-200');
  });
});
```

## Step 4: Run and Verify

### 4.1 Start the Backend
```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload --port 8000
```

### 4.2 Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4.3 Verify Functionality
1. Visit http://localhost:3000/chat
2. Test creating new conversations
3. Verify conversation listing works
4. Send messages and verify they appear in the UI
5. Switch between conversations and verify history loads
6. Test deleting conversations

## Troubleshooting

### Common Issues

1. **Authentication errors**: Ensure JWT token is properly set in frontend
2. **API endpoints not found**: Verify router is properly registered in main.py
3. **Database connection issues**: Check Neon PostgreSQL connection settings
4. **CORS errors**: Verify CORS settings in backend

### Debugging Tips

1. Check backend logs for detailed error messages
2. Use browser developer tools to inspect network requests
3. Verify user ID in JWT matches the one in API requests
4. Ensure conversation ownership is properly validated