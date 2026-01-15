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