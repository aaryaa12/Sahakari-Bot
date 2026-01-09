import React, { useState } from 'react';
import CitationView from './CitationView';

const MessageBubble = ({ message }) => {
  const [showCitations, setShowCitations] = useState(false);

  if (message.type === 'system') {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg text-sm">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="flex justify-start">
        <div className="max-w-3xl px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          <p>{message.content}</p>
        </div>
      </div>
    );
  }

  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-800'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300">
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center"
            >
              <span className="mr-2">
                {message.citations.length} source{message.citations.length > 1 ? 's' : ''}
              </span>
              <svg
                className={`w-4 h-4 transition-transform ${showCitations ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {showCitations && (
              <div className="mt-2 space-y-2">
                {message.citations.map((citation, idx) => (
                  <CitationView key={idx} citation={citation} index={idx + 1} />
                ))}
              </div>
            )}
          </div>
        )}

        <p className={`text-xs mt-2 ${isUser ? 'text-primary-100' : 'text-gray-500'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default MessageBubble;
