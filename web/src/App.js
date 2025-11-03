import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import Header from './components/Header';
import DropZone from './components/DropZone';
import ConfigModal from './components/ConfigModal';
import ProcessingView from './components/ProcessingView';
import ResultsView from './components/ResultsView';
import SettingsModal from './components/SettingsModal';
import AIAnalysisModal from './components/AIAnalysisModal';
import ChannelPage from './components/ChannelPage';
import { Settings } from 'lucide-react';

function MainApp() {
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showAIAnalysisModal, setShowAIAnalysisModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileMetadata, setFileMetadata] = useState(null);
  const [processingJob, setProcessingJob] = useState(null);
  const [activeTab, setActiveTab] = useState('creators');
  const [recentCreators, setRecentCreators] = useState([]);
  const [settings, setSettings] = useState({
    opusclipApiKey: '',
    openaiApiKey: '',
    batchSize: 10,
    timeoutMinutes: 10,
    autoSave: true,
    notificationSound: true,
    outputDir: 'output/',
    trainingDataDir: 'training_data/'
  });

  useEffect(() => {
    // Load dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    }

    // Load recent creators
    fetchRecentCreators();
  }, []);

  const fetchRecentCreators = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/recent-creators');
      if (response.ok) {
        const data = await response.json();
        setRecentCreators(data.creators || []);
      }
    } catch (error) {
      console.log('Could not fetch recent creators:', error);
    }
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode);
    if (newMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    
    // Upload file and get metadata
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setFileMetadata(data);
        setShowConfigModal(true);
      } else {
        alert('Failed to upload file');
      }
    } catch (error) {
      alert('Error uploading file: ' + error.message);
    }
  };

  const handleStartProcessing = async (config) => {
    setShowConfigModal(false);
    
    try {
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: selectedFile.name,
          ...config,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setProcessingJob({
          jobId: data.job_id,
          creatorName: data.creator_name,
          status: 'processing',
          videos: [],
          progress: 0,
        });
      } else {
        alert('Failed to start processing');
      }
    } catch (error) {
      alert('Error starting processing: ' + error.message);
    }
  };

  const handleAIAnalysisComplete = (analysis) => {
    setShowAIAnalysisModal(false);
    // Continue with JSONL generation using confirmed parameters
  };

  const handleSettingsSave = (newSettings) => {
    setSettings(newSettings);
    setShowSettings(false);
    localStorage.setItem('appSettings', JSON.stringify(newSettings));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Header 
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
        onSettingsClick={() => setShowSettings(true)}
      />
      
      <main className="container mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('creators')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'creators'
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Creators
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'history'
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            History
          </button>
        </div>

        {/* Main Content */}
        {!processingJob && activeTab === 'creators' && (
          <DropZone 
            onFileSelect={handleFileSelect}
            recentCreators={recentCreators}
            onCreatorClick={(creator) => {
              // Navigate to channel page
              navigate(`/channel/${creator.name.toLowerCase()}`);
            }}
          />
        )}

        {processingJob && processingJob.status === 'processing' && (
          <ProcessingView 
            job={processingJob}
            onJobUpdate={setProcessingJob}
            onAIAnalysisReady={() => setShowAIAnalysisModal(true)}
          />
        )}

        {processingJob && processingJob.status === 'completed' && (
          <ResultsView 
            job={processingJob}
            onNewCreator={() => {
              setProcessingJob(null);
              setSelectedFile(null);
              fetchRecentCreators();
            }}
          />
        )}
      </main>

      {/* Modals */}
      {showConfigModal && fileMetadata && (
        <ConfigModal
          metadata={fileMetadata}
          onClose={() => setShowConfigModal(false)}
          onStartProcessing={handleStartProcessing}
        />
      )}

      {showAIAnalysisModal && (
        <AIAnalysisModal
          onClose={() => setShowAIAnalysisModal(false)}
          onConfirm={handleAIAnalysisComplete}
        />
      )}

      {showSettings && (
        <SettingsModal
          settings={settings}
          onClose={() => setShowSettings(false)}
          onSave={handleSettingsSave}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/channel/:channelName" element={<ChannelPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


