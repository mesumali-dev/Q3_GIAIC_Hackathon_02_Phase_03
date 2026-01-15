'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ChatWindow from './Chat/ChatWindow';
import ThreadList from './Chat/ThreadList';
import { FaRobot, FaTimes, FaComment, FaBars } from 'react-icons/fa';

const FloatingChatbot: React.FC = () => {
  const { user, isAuthenticated, loading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showThreads, setShowThreads] = useState(false);

  // Only show the chatbot when user is authenticated
  const showChatbot = !loading && isAuthenticated && user;

  // Close chat when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      setIsOpen(false);
      setShowThreads(false);
    }
  }, [isAuthenticated]);

  if (!showChatbot) {
    return null;
  }

  const handleThreadSelect = (threadId: string) => {
    setConversationId(threadId);
    setShowThreads(false);
  };

  const handleNewConversation = () => {
    setConversationId(null);
    setShowThreads(false);
  };

  return (
    <>
      {/* Floating chat button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-orange-500 to-amber-500 text-white p-4 rounded-full shadow-lg hover:shadow-xl hover:from-orange-600 hover:to-amber-600 transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-50"
          aria-label="Open chat"
        >
          <FaRobot className="text-xl" />
        </button>
      )}

      {/* Floating chat window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-80 md:w-96 h-[500px] bg-white rounded-xl shadow-2xl border border-orange-100/50 flex flex-col overflow-hidden transition-all duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white p-3 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              {showThreads ? (
                <FaBars className="text-lg" />
              ) : (
                <FaRobot className="text-lg" />
              )}
              <span className="font-semibold">
                {showThreads ? 'Conversations' : 'AI Assistant'}
              </span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowThreads(!showThreads)}
                className="text-white hover:text-orange-100 focus:outline-none transition-colors"
                aria-label={showThreads ? "Back to chat" : "View conversations"}
              >
                {showThreads ? <FaRobot /> : <FaComment />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-orange-100 focus:outline-none transition-colors ml-1"
                aria-label="Close chat"
              >
                <FaTimes />
              </button>
            </div>
          </div>

          {/* Content area - Threads or Chat */}
          <div className="flex-1 overflow-hidden">
            {showThreads ? (
              <ThreadList
                onSelectThread={handleThreadSelect}
                onNewConversation={handleNewConversation}
                selectedThreadId={conversationId}
              />
            ) : (
              <ChatWindow
                conversationId={conversationId}
                onNewConversationCreated={(id) => setConversationId(id)}
              />
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChatbot;