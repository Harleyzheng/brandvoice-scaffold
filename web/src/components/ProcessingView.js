import React, { useEffect, useState } from 'react';
import { Pause, ChevronDown, ChevronRight, Download } from 'lucide-react';

function ProcessingView({ job, onJobUpdate, onAIAnalysisReady }) {
  const [expandedVideos, setExpandedVideos] = useState(new Set());
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Poll for progress updates
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/progress/${job.jobId}`);
        if (response.ok) {
          const data = await response.json();
          setProgress(data.progress);
          onJobUpdate({
            ...job,
            videos: data.videos,
            currentPhase: data.currentPhase,
            estimatedTimeRemaining: data.estimatedTimeRemaining,
          });

          // Check if AI analysis is ready
          if (data.aiAnalysisReady && !data.aiAnalysisConfirmed) {
            onAIAnalysisReady();
          }

          // Check if completed
          if (data.status === 'completed') {
            onJobUpdate({
              ...job,
              status: 'completed',
              videos: data.videos,
              summary: data.summary,
            });
            clearInterval(pollInterval);
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(pollInterval);
  }, [job.jobId]);

  const toggleVideo = (videoId) => {
    const newExpanded = new Set(expandedVideos);
    if (newExpanded.has(videoId)) {
      newExpanded.delete(videoId);
    } else {
      newExpanded.add(videoId);
    }
    setExpandedVideos(newExpanded);
  };

  const expandAll = () => {
    setExpandedVideos(new Set(job.videos?.map(v => v.id) || []));
  };

  const collapseAll = () => {
    setExpandedVideos(new Set());
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'processing':
        return '⏳';
      case 'pending':
        return '⏳';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Calculating...';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 
                    dark:border-gray-700 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Processing: {job.creatorName}
          </h2>
          <button
            className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 
                     transition-colors flex items-center gap-2"
          >
            <Pause className="w-4 h-4" />
            Pause
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-700 dark:text-gray-300 mb-2">
            <span className="font-medium">Overall Progress:</span>
            <span>{progress}% ({job.videos?.filter(v => v.status === 'completed').length || 0}/{job.videos?.length || 0} videos)</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className="bg-primary-600 h-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Current Phase */}
        <div className="space-y-1">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            <span className="font-medium">Current Phase:</span> {job.currentPhase || '📝 Extracting Transcripts'}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Estimated time remaining: ~{job.estimatedTimeRemaining || '45 minutes'}
          </div>
        </div>
      </div>

      {/* Video List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 
                    dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Videos
          </h3>
          <div className="flex gap-2">
            <button
              onClick={expandAll}
              className="text-sm text-primary-600 dark:text-primary-400 hover:underline"
            >
              Expand All
            </button>
            <span className="text-gray-400">|</span>
            <button
              onClick={collapseAll}
              className="text-sm text-primary-600 dark:text-primary-400 hover:underline"
            >
              Collapse All
            </button>
            <span className="text-gray-400">|</span>
            <button className="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1">
              <Download className="w-4 h-4" />
              Export Progress Log
            </button>
          </div>
        </div>

        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {job.videos && job.videos.length > 0 ? (
            job.videos.map((video, index) => (
              <div
                key={video.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
              >
                <div
                  className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer 
                           flex items-center justify-between"
                  onClick={() => toggleVideo(video.id)}
                >
                  <div className="flex items-center gap-3 flex-1">
                    {expandedVideos.has(video.id) ? (
                      <ChevronDown className="w-5 h-5 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-500" />
                    )}
                    <span className="text-2xl">{getStatusIcon(video.status)}</span>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        Video {index + 1}: "{video.title || 'Untitled'}"
                      </p>
                      {video.status === 'processing' && video.currentStep && (
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {video.currentStep}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {expandedVideos.has(video.id) && (
                  <div className="px-4 pb-4 pl-12 space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <span className={video.steps?.metadata === 'completed' ? 'text-green-600' : 'text-gray-400'}>
                        {video.steps?.metadata === 'completed' ? '✅' : '⏳'}
                      </span>
                      <span className="text-gray-700 dark:text-gray-300">Parse metadata</span>
                      <span className="text-gray-500 dark:text-gray-400 ml-auto">
                        {video.steps?.metadataDuration || ''}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={video.steps?.transcript === 'completed' ? 'text-green-600' : 
                                     video.steps?.transcript === 'processing' ? 'text-blue-600' : 'text-gray-400'}>
                        {video.steps?.transcript === 'completed' ? '✅' : 
                         video.steps?.transcript === 'processing' ? '⏳' : '⏳'}
                      </span>
                      <span className="text-gray-700 dark:text-gray-300">Extract transcript</span>
                      <span className="text-gray-500 dark:text-gray-400 ml-auto">
                        {video.steps?.transcriptDuration || ''}
                      </span>
                    </div>
                    {video.steps?.transcript === 'processing' && (
                      <div className="pl-6 text-xs text-gray-500 dark:text-gray-400">
                        └─ OpusClip: {video.steps?.transcriptMessage || 'Processing scenes...'}
                      </div>
                    )}

                    <div className="flex items-center gap-2">
                      <span className={video.steps?.csv === 'completed' ? 'text-green-600' : 'text-gray-400'}>
                        {video.steps?.csv === 'completed' ? '✅' : '⏳'}
                      </span>
                      <span className="text-gray-700 dark:text-gray-300">Generate CSV entry</span>
                      <span className="text-gray-500 dark:text-gray-400 ml-auto">
                        {video.steps?.csvDuration || video.steps?.csv === 'pending' ? 'Pending' : ''}
                      </span>
                    </div>

                    {video.status === 'completed' && (
                      <div className="mt-3 pt-2 border-t border-gray-200 dark:border-gray-700 flex gap-2">
                        <button className="text-xs px-3 py-1 bg-primary-100 dark:bg-primary-900/30 
                                       text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 
                                       dark:hover:bg-primary-900/50 transition-colors">
                          View Transcript
                        </button>
                        <button className="text-xs px-3 py-1 bg-primary-100 dark:bg-primary-900/30 
                                       text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 
                                       dark:hover:bg-primary-900/50 transition-colors">
                          OpusClip Project
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              Initializing processing...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProcessingView;


