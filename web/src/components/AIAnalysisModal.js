import React, { useState } from 'react';
import { X, Bot } from 'lucide-react';

function AIAnalysisModal({ onClose, onConfirm, analysis }) {
  const [params, setParams] = useState({
    language: analysis?.language || 'English',
    maxChar: analysis?.maxChar || 150,
    style: analysis?.style || '',
  });

  const defaultAnalysis = analysis || {
    language: 'English',
    maxChar: 150,
    reasoning: 'Content is conversational and concise, typical of tech/business commentary. 150 chars suits the punchy, direct style of these videos.',
    sampleInput: 'The future of AI in enterprise is about augmenting human capabilities...',
    sampleOutput: 'AI transforms how businesses operate by augmenting human capabilities',
    sampleHashtags: ['AI', 'Innovation', 'Tech']
  };

  const handleConfirm = () => {
    onConfirm(params);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Bot className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              AI Content Analysis Complete
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Analyzed 5 sample videos to determine optimal parameters for JSONL generation:
          </p>

          {/* Analysis Results */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg space-y-3">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                Detected Language:
              </h3>
              <p className="text-gray-800 dark:text-gray-200">
                {defaultAnalysis.language}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                Suggested Max Characters:
              </h3>
              <p className="text-gray-800 dark:text-gray-200">
                {defaultAnalysis.maxChar}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                Reasoning:
              </h3>
              <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                {defaultAnalysis.reasoning}
              </p>
            </div>
          </div>

          {/* Modify Parameters */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Modify Parameters (optional):
            </h3>
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Language:
                </label>
                <select
                  value={params.language}
                  onChange={(e) => setParams({...params, language: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option>English</option>
                  <option>Spanish</option>
                  <option>French</option>
                  <option>German</option>
                  <option>Chinese</option>
                  <option>Japanese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Max chars:
                </label>
                <input
                  type="number"
                  value={params.maxChar}
                  onChange={(e) => setParams({...params, maxChar: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Style:
                </label>
                <input
                  type="text"
                  placeholder="Optional custom instructions"
                  value={params.style}
                  onChange={(e) => setParams({...params, style: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Sample Preview */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Sample Preview:
            </h3>
            <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg space-y-3 text-sm">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Input:</span>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  "{defaultAnalysis.sampleInput}"
                </p>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Output:</span>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  "{defaultAnalysis.sampleOutput}"
                </p>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Hashtags:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {defaultAnalysis.sampleHashtags.map((tag, i) => (
                    <span key={i} className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 
                                           text-primary-700 dark:text-primary-300 rounded text-xs">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 
                     dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Use Different Values
          </button>
          <button
            onClick={handleConfirm}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                     transition-colors font-medium"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}

export default AIAnalysisModal;


