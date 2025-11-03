import React, { useState } from 'react';
import { X, Copy, Download, ExternalLink } from 'lucide-react';

function TranscriptModal({ video, onClose }) {
  const [activeTab, setActiveTab] = useState('raw');

  const handleCopy = () => {
    navigator.clipboard.writeText(video.transcript || '');
    alert('Transcript copied to clipboard!');
  };

  const formatTranscript = (transcript) => {
    if (!transcript) return 'No transcript available';
    return transcript;
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Video Transcript: "{video.title || 'Untitled'}"
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 px-6 pt-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('raw')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'raw'
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Raw Text
          </button>
          <button
            onClick={() => setActiveTab('screenplay')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'screenplay'
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Screenplay Format
          </button>
          <button
            onClick={() => setActiveTab('visual')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'visual'
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Visual Context
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Transcript Content */}
          <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
            <div className="mb-3 text-sm text-gray-600 dark:text-gray-400">
              Source: OpusClip (with visual context)
            </div>
            
            {activeTab === 'raw' && (
              <div className="space-y-4">
                <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
                  {formatTranscript(video.transcript)}
                </p>
              </div>
            )}

            {activeTab === 'screenplay' && (
              <div className="space-y-4 font-mono text-sm">
                <div>
                  <div className="text-gray-500 dark:text-gray-400 mb-1">[00:00] Opening shot of office workspace</div>
                  <p className="text-gray-800 dark:text-gray-200">
                    "The future of artificial intelligence is not about replacing humans, it's about augmenting our capabilities."
                  </p>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400 mb-1">[00:12] Cut to close-up, gesturing</div>
                  <p className="text-gray-800 dark:text-gray-200">
                    "We're seeing this transformation across every industry - from healthcare to finance to education."
                  </p>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400 mb-1">[00:28] B-roll of AI interfaces</div>
                  <p className="text-gray-800 dark:text-gray-200">
                    "The companies that understand this will be the ones leading the next decade."
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'visual' && (
              <div className="space-y-3 text-sm">
                <p className="text-gray-700 dark:text-gray-300">
                  Visual elements and context extracted from the video:
                </p>
                <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-400">
                  <li>Office workspace setting with modern aesthetic</li>
                  <li>Speaker gesturing to emphasize points</li>
                  <li>B-roll footage of AI interfaces and technology</li>
                  <li>Professional lighting and composition</li>
                </ul>
              </div>
            )}

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-3 gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <span className="font-medium">Character count:</span> {video.transcriptLength || 342}
              </div>
              <div>
                <span className="font-medium">Word count:</span> {video.transcriptLength ? Math.floor(video.transcriptLength / 5) : 67}
              </div>
              <div>
                <span className="font-medium">Duration:</span> {video.duration || 45} seconds
              </div>
            </div>
          </div>

          {/* OpusClip Project */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              OpusClip Project
            </h3>
            <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-700 dark:text-gray-300">Project ID:</span>
                  <span className="text-gray-600 dark:text-gray-400 font-mono">{video.opusProjectId || 'opus_abc123'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700 dark:text-gray-300">Clips generated:</span>
                  <span className="text-gray-600 dark:text-gray-400">{video.clipsGenerated || 3}</span>
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <button className="flex-1 px-3 py-2 bg-primary-100 dark:bg-primary-900/30 
                                 text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 
                                 dark:hover:bg-primary-900/50 transition-colors flex items-center 
                                 justify-center gap-2 text-sm">
                  <ExternalLink className="w-4 h-4" />
                  Open in OpusClip Dashboard
                </button>
                <button className="px-3 py-2 border border-gray-300 dark:border-gray-600 
                                 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 
                                 dark:hover:bg-gray-700 transition-colors text-sm">
                  View Clips
                </button>
              </div>
            </div>
          </div>

          {/* Training Data Preview */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Training Data Preview
            </h3>
            <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg space-y-3 text-sm font-mono">
              <div>
                <div className="text-gray-600 dark:text-gray-400 mb-1">User Input:</div>
                <div className="p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200">
                  {`{"language": "English", "text": "${(video.transcript || '').substring(0, 50)}...", "max_char": 150}`}
                </div>
              </div>
              <div>
                <div className="text-gray-600 dark:text-gray-400 mb-1">Model Output:</div>
                <div className="p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200">
                  {`{"description": "${(video.description || 'AI transforms industries').substring(0, 50)}...", "hashtags": ["AI", "Innovation", "Tech"]}`}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleCopy}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 
                     dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 
                     transition-colors flex items-center gap-2"
          >
            <Copy className="w-4 h-4" />
            Copy Transcript
          </button>
          <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 
                           dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 
                           transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export JSON
          </button>
        </div>
      </div>
    </div>
  );
}

export default TranscriptModal;


