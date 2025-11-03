import React, { useState } from 'react';
import { X, FileJson, AlertCircle } from 'lucide-react';

function ConfigModal({ metadata, onClose, onStartProcessing }) {
  const [config, setConfig] = useState({
    videosToProcess: metadata.newVideos || 0,
    batchSize: 10,
    parameterMode: 'auto', // 'auto' or 'manual'
    language: 'English',
    maxChar: 150,
    style: '',
    confirmationMode: 'interactive' // 'interactive', 'auto-confirm', 'non-interactive'
  });

  const handleSubmit = () => {
    onStartProcessing(config);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Configure Processing: {metadata.filename}
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Metadata Info */}
          <div className="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <FileJson className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 text-sm">
              <p className="text-blue-900 dark:text-blue-100">
                📊 Found <strong>{metadata.totalVideos}</strong> videos in JSON
              </p>
              {metadata.existingVideos > 0 && (
                <p className="text-blue-700 dark:text-blue-300 mt-1">
                  📋 {metadata.existingVideos} videos already processed (will skip)
                </p>
              )}
            </div>
          </div>

          {/* Process Settings */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Process Settings
            </h3>
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Videos to process:
                </label>
                <input
                  type="number"
                  value={config.videosToProcess}
                  onChange={(e) => setConfig({...config, videosToProcess: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  (new only)
                </p>
              </div>
              
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Batch size:
                </label>
                <input
                  type="number"
                  value={config.batchSize}
                  onChange={(e) => setConfig({...config, batchSize: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Parameter Configuration */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Parameter Configuration
            </h3>
            <div className="space-y-3 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <label className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={config.parameterMode === 'auto'}
                  onChange={() => setConfig({...config, parameterMode: 'auto'})}
                  className="mt-1"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Auto-detect (AI will analyze & suggest)
                </span>
              </label>
              
              <label className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={config.parameterMode === 'manual'}
                  onChange={() => setConfig({...config, parameterMode: 'manual'})}
                  className="mt-1"
                />
                <div className="flex-1">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Manual override:
                  </span>
                  
                  {config.parameterMode === 'manual' && (
                    <div className="space-y-3 mt-3">
                      <div>
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                          Language:
                        </label>
                        <select
                          value={config.language}
                          onChange={(e) => setConfig({...config, language: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
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
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                          Max chars:
                        </label>
                        <input
                          type="number"
                          value={config.maxChar}
                          onChange={(e) => setConfig({...config, maxChar: parseInt(e.target.value)})}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
                                   focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                          Style:
                        </label>
                        <input
                          type="text"
                          placeholder="Optional custom instructions"
                          value={config.style}
                          onChange={(e) => setConfig({...config, style: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
                                   focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </label>
            </div>
          </div>

          {/* Confirmation Mode */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Confirmation Mode
            </h3>
            <div className="space-y-2 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <label className="flex items-center gap-3">
                <input
                  type="radio"
                  checked={config.confirmationMode === 'interactive'}
                  onChange={() => setConfig({...config, confirmationMode: 'interactive'})}
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Interactive (review AI suggestions)
                </span>
              </label>
              
              <label className="flex items-center gap-3">
                <input
                  type="radio"
                  checked={config.confirmationMode === 'auto-confirm'}
                  onChange={() => setConfig({...config, confirmationMode: 'auto-confirm'})}
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Auto-confirm (use AI suggestions)
                </span>
              </label>
              
              <label className="flex items-center gap-3">
                <input
                  type="radio"
                  checked={config.confirmationMode === 'non-interactive'}
                  onChange={() => setConfig({...config, confirmationMode: 'non-interactive'})}
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Non-interactive (silent mode)
                </span>
              </label>
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
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                     transition-colors font-medium"
          >
            Start Processing
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfigModal;


