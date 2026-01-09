import React from 'react';

const CitationView = ({ citation, index }) => {
  return (
    <div className="bg-white border border-gray-200 rounded p-3 text-sm">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className="font-semibold text-gray-700">Source {index}:</span>
            <span className="text-gray-600">{citation.source}</span>
            {citation.type && (
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                {citation.type.toUpperCase()}
              </span>
            )}
          </div>
          {citation.page && (
            <p className="text-gray-500 text-xs">Page/Sheet: {citation.page}</p>
          )}
          {citation.relevance_score && (
            <p className="text-gray-500 text-xs">
              Relevance: {(citation.relevance_score * 100).toFixed(1)}%
            </p>
          )}
        </div>
      </div>
      {citation.excerpt && (
        <div className="mt-2 p-2 bg-gray-50 rounded border-l-2 border-primary-500">
          <p className="text-xs text-gray-700 italic">
            "{citation.excerpt}"
          </p>
        </div>
      )}
    </div>
  );
};

export default CitationView;
