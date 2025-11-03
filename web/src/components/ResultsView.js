import React, { useState } from 'react';
import { Download, Search, Eye, Heart, MessageCircle, Clock, FileText, ChevronDown } from 'lucide-react';
import TranscriptModal from './TranscriptModal';

function ResultsView({ job, onNewCreator }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [showCsvPreview, setShowCsvPreview] = useState(false);
  const [showJsonlPreview, setShowJsonlPreview] = useState(false);
  const [csvPreviewData, setCsvPreviewData] = useState(null);
  const [jsonlPreviewData, setJsonlPreviewData] = useState(null);
  const [allOutputFiles, setAllOutputFiles] = useState([]);
  const [allTrainingFiles, setAllTrainingFiles] = useState([]);
  const [showAllFiles, setShowAllFiles] = useState(false);

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toString() || '0';
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0s';
    return `${seconds}s`;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (isoDate) => {
    const date = new Date(isoDate);
    return date.toLocaleString();
  };

  // Fetch all files from output and training folders
  React.useEffect(() => {
    const fetchAllFiles = async () => {
      try {
        const [outputResponse, trainingResponse] = await Promise.all([
          fetch('http://localhost:8000/api/files/output'),
          fetch('http://localhost:8000/api/files/training')
        ]);
        
        if (outputResponse.ok) {
          const data = await outputResponse.json();
          setAllOutputFiles(data.files || []);
        }
        
        if (trainingResponse.ok) {
          const data = await trainingResponse.json();
          setAllTrainingFiles(data.files || []);
        }
      } catch (error) {
        console.error('Error fetching file lists:', error);
      }
    };
    
    fetchAllFiles();
  }, []);

  const handleDownload = (filename) => {
    if (!filename) {
      alert('File not available');
      return;
    }
    window.open(`http://localhost:8000/api/download/${filename}`, '_blank');
  };

  const handlePreviewCsv = async () => {
    if (!job.csvFilename) {
      alert('CSV file not available');
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/api/preview/${job.csvFilename}`);
      if (response.ok) {
        const data = await response.json();
        setCsvPreviewData(data);
        setShowCsvPreview(true);
      } else {
        alert('Failed to load CSV preview');
      }
    } catch (error) {
      alert('Error loading preview: ' + error.message);
    }
  };

  const handlePreviewJsonl = async () => {
    if (!job.jsonlFilename) {
      alert('JSONL file not available');
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/api/preview/${job.jsonlFilename}`);
      if (response.ok) {
        const data = await response.json();
        setJsonlPreviewData(data);
        setShowJsonlPreview(true);
      } else {
        alert('Failed to load JSONL preview');
      }
    } catch (error) {
      alert('Error loading preview: ' + error.message);
    }
  };

  const handleViewAllRows = () => {
    if (!job.csvFilename) {
      alert('CSV file not available');
      return;
    }
    // Open CSV in new window with all rows
    window.open(`http://localhost:8000/api/view/${job.csvFilename}?format=table`, '_blank');
  };

  const handleViewSamples = () => {
    if (!job.jsonlFilename) {
      alert('JSONL file not available');
      return;
    }
    // Open JSONL samples in new window
    window.open(`http://localhost:8000/api/view/${job.jsonlFilename}?format=samples`, '_blank');
  };

  const handleExportAll = () => {
    if (!job.csvFilename && !job.jsonlFilename) {
      alert('No files available to export');
      return;
    }
    // Download both files
    if (job.csvFilename) {
      handleDownload(job.csvFilename);
    }
    if (job.jsonlFilename) {
      setTimeout(() => handleDownload(job.jsonlFilename), 500);
    }
  };

  const filteredVideos = job.videos?.filter(video => {
    if (searchQuery && !video.title?.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  }) || [];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Success Header */}
      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 
                    rounded-lg p-6 mb-6">
        <div className="flex items-start gap-3">
          <span className="text-3xl">✅</span>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-green-900 dark:text-green-100 mb-2">
              Processing Complete: {job.creatorName}
            </h2>
            
            {job.summary && (
              <div className="space-y-1 text-sm text-green-800 dark:text-green-200">
                <p>• Processed: <strong>{job.summary.processed}</strong> new videos</p>
                {job.summary.skipped > 0 && (
                  <p>• Skipped: <strong>{job.summary.skipped}</strong> duplicates</p>
                )}
                <p>• Total time: <strong>{job.summary.totalTime || 'N/A'}</strong></p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Generated Files */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 
                    dark:border-gray-700 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Generated Files
          </h3>
          <button
            onClick={() => setShowAllFiles(!showAllFiles)}
            className="text-sm px-3 py-1 border border-gray-300 dark:border-gray-600 
                       text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 
                       dark:hover:bg-gray-700 transition-colors flex items-center gap-1"
          >
            {showAllFiles ? 'Hide All Files' : 'Show All Files'}
            <ChevronDown className={`w-4 h-4 transition-transform ${showAllFiles ? 'rotate-180' : ''}`} />
          </button>
        </div>
        
        {!showAllFiles ? (
          <div className="space-y-4">
            {/* Current Job Files */}
            {/* CSV Output */}
            <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <h4 className="font-medium text-gray-900 dark:text-white">CSV Output</h4>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {job.csvFilename || 'output.csv'}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownload(job.csvFilename)}
                      className="text-sm px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 
                               transition-colors flex items-center gap-1"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                    <button 
                      onClick={handlePreviewCsv}
                      className="text-sm px-3 py-1 border border-gray-300 dark:border-gray-600 
                                     text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 
                                     dark:hover:bg-gray-700 transition-colors">
                      Preview
                    </button>
                    <button 
                      onClick={handleViewAllRows}
                      className="text-sm px-3 py-1 border border-gray-300 dark:border-gray-600 
                                     text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 
                                     dark:hover:bg-gray-700 transition-colors">
                      View All {job.videos?.length || 0} rows
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* JSONL Training Data */}
            <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <h4 className="font-medium text-gray-900 dark:text-white">Training Data (JSONL)</h4>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {job.jsonlFilename || 'training_data.jsonl'}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownload(job.jsonlFilename)}
                      className="text-sm px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 
                               transition-colors flex items-center gap-1"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                    <button 
                      onClick={handlePreviewJsonl}
                      className="text-sm px-3 py-1 border border-gray-300 dark:border-gray-600 
                                     text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 
                                     dark:hover:bg-gray-700 transition-colors">
                      Preview
                    </button>
                    <button 
                      onClick={handleViewSamples}
                      className="text-sm px-3 py-1 border border-gray-300 dark:border-gray-600 
                                     text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 
                                     dark:hover:bg-gray-700 transition-colors">
                      View Samples
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* All CSV Files */}
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5 text-green-600 dark:text-green-400" />
                CSV Output Files ({allOutputFiles.length})
              </h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {allOutputFiles.map((file) => (
                  <div key={file.name} className="p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg 
                                                   border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFileSize(file.size)} • {formatDate(file.modified)}
                        </p>
                      </div>
                      <div className="flex gap-1 ml-3">
                        <button
                          onClick={() => handleDownload(file.name)}
                          className="text-xs px-2 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 
                                   transition-colors"
                        >
                          <Download className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {allOutputFiles.length === 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                    No CSV files found
                  </p>
                )}
              </div>
            </div>

            {/* All JSONL Files */}
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                Training Data Files ({allTrainingFiles.length})
              </h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {allTrainingFiles.map((file) => (
                  <div key={file.name} className="p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg 
                                                   border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFileSize(file.size)} • {formatDate(file.modified)}
                        </p>
                      </div>
                      <div className="flex gap-1 ml-3">
                        <button
                          onClick={() => handleDownload(file.name)}
                          className="text-xs px-2 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 
                                   transition-colors"
                        >
                          <Download className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {allTrainingFiles.length === 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                    No JSONL files found
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Video Details */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 
                    dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Video Details
        </h3>

        {/* Search and Filter */}
        <div className="flex gap-3 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search videos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-900 text-gray-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-900 text-gray-900 dark:text-white
                     focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All</option>
            <option value="high-views">High Views</option>
            <option value="high-engagement">High Engagement</option>
          </select>
        </div>

        {/* Video List */}
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {filteredVideos.map((video, index) => (
            <div
              key={video.id}
              className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg 
                       hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-start gap-3 flex-1">
                  <span className="text-2xl">📹</span>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                      "{video.title || 'Untitled'}" ({video.id})
                    </h4>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {formatNumber(video.viewCount)} views
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="w-4 h-4" />
                        {formatNumber(video.likeCount)} likes
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="w-4 h-4" />
                        {formatNumber(video.commentCount)}
                      </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400 mt-2">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        Duration: {formatDuration(video.duration)}
                      </span>
                      <span className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        Transcript: {video.transcriptLength || 0} chars
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedVideo(video)}
                  className="text-sm px-3 py-1 bg-primary-100 dark:bg-primary-900/30 
                           text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 
                           dark:hover:bg-primary-900/50 transition-colors"
                >
                  View Transcript
                </button>
                <button className="text-sm px-3 py-1 bg-primary-100 dark:bg-primary-900/30 
                                 text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 
                                 dark:hover:bg-primary-900/50 transition-colors">
                  OpusClip
                </button>
                <button className="text-sm px-3 py-1 bg-primary-100 dark:bg-primary-900/30 
                                 text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 
                                 dark:hover:bg-primary-900/50 transition-colors">
                  Training
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex justify-center gap-3">
        <button 
          onClick={onNewCreator}
          className="px-6 py-2 border border-gray-300 dark:border-gray-600 
                         text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 
                         dark:hover:bg-gray-700 transition-colors font-medium">
          Process More Videos
        </button>
        <button
          onClick={onNewCreator}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                   transition-colors font-medium"
        >
          New Creator
        </button>
        <button 
          onClick={handleExportAll}
          className="px-6 py-2 border border-gray-300 dark:border-gray-600 
                         text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 
                         dark:hover:bg-gray-700 transition-colors font-medium flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export All
        </button>
      </div>

      {/* Transcript Modal */}
      {selectedVideo && (
        <TranscriptModal
          video={selectedVideo}
          onClose={() => setSelectedVideo(null)}
        />
      )}
    </div>
  );
}

export default ResultsView;


