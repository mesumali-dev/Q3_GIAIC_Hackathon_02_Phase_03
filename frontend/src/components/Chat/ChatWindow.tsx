'use client';

import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import {
  getConversationWithMessages,
  sendChatMessage,
  ChatRequest,
  MessageItem as MessageItemType,
  ChatResponse,
  createConversation
} from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

type MessageType = MessageItemType;

interface ChatWindowProps {
  conversationId: string | null;
  onNewConversationCreated?: (conversationId: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId, onNewConversationCreated }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (conversationId && user?.id) {
      loadConversationHistory();
    } else {
      // Reset messages when no conversation is selected
      setMessages([]);
    }
  }, [conversationId, user?.id]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversationHistory = async () => {
    if (!conversationId || !user?.id) return;

    setIsLoading(true);
    const response = await getConversationWithMessages(user.id, conversationId);

    if (response.data && response.data.messages) {
      // The API returns both conversation and messages in one response
      const transformedMessages = response.data.messages.map(msg => ({
        id: msg.id,
        conversation_id: msg.conversation_id,
        role: msg.role as 'user' | 'assistant' | 'system',
        content: msg.content,
        created_at: msg.created_at
      }));
      setMessages(transformedMessages);
    } else {
      console.error('Failed to load conversation history:', response.error);
    }

    setIsLoading(false);
  };

  const handleSendMessage = async (message: string) => {
    if (!user?.id || isSending) return;

    setIsSending(true);

    // Add the user's message optimistically
    const userMessage: MessageType = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId || '',
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      // Show typing indicator
      setIsTyping(true);

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
          conversation_id: chatResponse.conversation_id,
          role: 'assistant',
          content: chatResponse.assistant_message,
          created_at: chatResponse.created_at ? new Date(chatResponse.created_at).toISOString() : new Date().toISOString(),
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
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-3 bg-gray-50">
        <h2 className="text-lg font-semibold">
          {conversationId ? 'Active Conversation' : 'Start New Conversation'}
        </h2>
      </div>
      <div className="overflow-y-auto flex-1 p-4 space-y-2">
        <MessageList messages={messages} isLoading={false} />
        {isTyping && (
          <div className="flex items-start space-x-2 p-2">
            <div className="bg-gray-200 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
              <div className="text-gray-600 font-bold text-sm">AI</div>
            </div>
            <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isSending || !user?.id}
      />
    </div>
  );
};

export default ChatWindow;