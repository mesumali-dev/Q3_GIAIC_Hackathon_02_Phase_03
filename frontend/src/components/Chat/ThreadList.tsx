'use client';

import React, { useEffect, useState } from 'react';
import ThreadItem from './ThreadItem';
import { ConversationSummary, getUserConversations } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { FaPlus, FaHistory, FaTrash } from 'react-icons/fa';

interface ThreadListProps {
  onSelectThread: (threadId: string) => void;
  onNewConversation: () => void;
  selectedThreadId: string | null;
}

const ThreadList: React.FC<ThreadListProps> = ({
  onSelectThread,
  onNewConversation,
  selectedThreadId,
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
    try {
      const response = await getUserConversations(user.id);

      if (response.data && response.data.conversations) {
        // Sort conversations by updated_at in descending order (most recent first)
        const sortedConversations = [...response.data.conversations].sort((a, b) =>
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );

        // Map the response to the expected format
        const mappedConversations = sortedConversations.map(conv => ({
          id: conv.id,
          title: conv.title || `Conversation ${new Date(conv.created_at).toLocaleDateString()}`,
          created_at: conv.created_at,
          updated_at: conv.updated_at
        }));
        setConversations(mappedConversations);
      } else {
        console.error('Failed to load conversations:', response.error);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (isLoading) {
    return (
      <div className="p-4 flex flex-col items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-orange-500 mb-2"></div>
        <p className="text-gray-500 text-sm">Loading conversations...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with title and new conversation button */}
      <div className="p-3 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-amber-50">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <FaHistory className="text-orange-500" />
            <h3 className="font-semibold text-gray-700">Conversations</h3>
          </div>
          <span className="text-xs bg-orange-100 text-orange-800 rounded-full px-2 py-1">
            {conversations.length}
          </span>
        </div>
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg px-4 py-2.5 hover:from-orange-600 hover:to-amber-600 focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all shadow-sm"
        >
          <FaPlus className="text-sm" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversations list */}
      <div className="overflow-y-auto flex-1">
        {conversations.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`p-3 hover:bg-orange-50 transition-colors cursor-pointer ${
                  conv.id === selectedThreadId ? 'bg-orange-50 border-l-4 border-orange-500' : ''
                }`}
                onClick={() => onSelectThread(conv.id)}
              >
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-gray-800 truncate text-sm">
                    {conv.title}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDate(conv.updated_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center">
            <div className="mx-auto bg-gray-100 rounded-full w-12 h-12 flex items-center justify-center mb-3">
              <FaHistory className="text-gray-400" />
            </div>
            <h4 className="font-medium text-gray-700 mb-1">No conversations yet</h4>
            <p className="text-sm text-gray-500 mb-4">Start a new conversation to begin chatting</p>
            <button
              onClick={onNewConversation}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg px-4 py-2 text-sm hover:from-orange-600 hover:to-amber-600 transition-all"
            >
              <FaPlus className="text-xs" />
              Start Chatting
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreadList;