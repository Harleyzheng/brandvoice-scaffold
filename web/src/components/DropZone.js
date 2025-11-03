import React, { useState, useRef } from 'react';
import { Upload, FileJson, CheckCircle } from 'lucide-react';

function DropZone({ onFileSelect, recentCreators, onCreatorClick }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.json')) {
        onFileSelect(file);
      } else {
        alert('Please upload a JSON file');
      }
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Drop Zone */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Drop TikTok JSON or Enter Channel URL
        </h2>
        
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-all duration-200
            ${isDragging 
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
            }
          `}
        >
          <FileJson className="w-16 h-16 mx-auto mb-4 text-gray-400 dark:text-gray-500" />
          <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
            Drop JSON file here
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            or click to browse
          </p>
          
          <div className="flex items-center justify-center gap-4 my-6">
            <div className="h-px bg-gray-300 dark:bg-gray-600 flex-1"></div>
            <span className="text-sm text-gray-500 dark:text-gray-400">OR</span>
            <div className="h-px bg-gray-300 dark:bg-gray-600 flex-1"></div>
          </div>
          
          <div className="flex items-center gap-2 max-w-md mx-auto" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              placeholder="Enter TikTok Channel URL"
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                             transition-colors font-medium">
              Fetch
            </button>
          </div>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileInput}
          className="hidden"
        />
      </div>

      {/* Recent Creators */}
      {recentCreators && recentCreators.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Creators
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentCreators.map((creator, index) => (
              <div
                key={index}
                onClick={() => onCreatorClick(creator)}
                className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 
                         dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500
                         cursor-pointer transition-all hover:shadow-md"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {creator.name}
                  </h3>
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                </div>
                
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {creator.videoCount} videos
                </p>
                
                {creator.stats && (
                  <div className="text-xs text-gray-500 dark:text-gray-500 space-y-1">
                    <div>👁 {formatNumber(creator.stats.totalViews)} views</div>
                    <div>❤️ {formatNumber(creator.stats.totalLikes)} likes</div>
                  </div>
                )}
                
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <span className="inline-flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    Complete
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DropZone;


