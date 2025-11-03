import React, { useState } from 'react';
import { X, Eye, EyeOff } from 'lucide-react';

function SettingsModal({ settings, onClose, onSave }) {
  const [formData, setFormData] = useState(settings);
  const [showOpusKey, setShowOpusKey] = useState(false);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);

  const handleSave = () => {
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Settings
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
          {/* API Configuration */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              API Configuration
            </h3>
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  OpusClip API Key:
                </label>
                <div className="flex gap-2">
                  <input
                    type={showOpusKey ? 'text' : 'password'}
                    value={formData.opusclipApiKey}
                    onChange={(e) => setFormData({...formData, opusclipApiKey: e.target.value})}
                    placeholder="Enter your OpusClip API key"
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                             focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    onClick={() => setShowOpusKey(!showOpusKey)}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    {showOpusKey ? (
                      <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  OpenAI API Key:
                </label>
                <div className="flex gap-2">
                  <input
                    type={showOpenAIKey ? 'text' : 'password'}
                    value={formData.openaiApiKey}
                    onChange={(e) => setFormData({...formData, openaiApiKey: e.target.value})}
                    placeholder="Enter your OpenAI API key"
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                             focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    {showOpenAIKey ? (
                      <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Default Processing Settings */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Default Processing Settings
            </h3>
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Batch size:
                </label>
                <input
                  type="number"
                  value={formData.batchSize}
                  onChange={(e) => setFormData({...formData, batchSize: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Timeout per video (minutes):
                </label>
                <input
                  type="number"
                  value={formData.timeoutMinutes}
                  onChange={(e) => setFormData({...formData, timeoutMinutes: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.autoSave}
                  onChange={(e) => setFormData({...formData, autoSave: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Auto-save progress
                </span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.notificationSound}
                  onChange={(e) => setFormData({...formData, notificationSound: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Notification sound
                </span>
              </label>
            </div>
          </div>

          {/* Output Directories */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Output Directories
            </h3>
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  CSV output:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={formData.outputDir}
                    onChange={(e) => setFormData({...formData, outputDir: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                             focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                                   hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-sm">
                    Change
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Training data:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={formData.trainingDataDir}
                    onChange={(e) => setFormData({...formData, trainingDataDir: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                             focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                                   hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-sm">
                    Change
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Theme */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Theme
            </h3>
            <div className="flex gap-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Light</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  defaultChecked
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Dark</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="theme"
                  value="auto"
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Auto</span>
              </label>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                     transition-colors font-medium"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;


