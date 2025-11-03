# BrandVoice Studio - Web UI

A modern, interactive web interface for processing TikTok videos into LLM training data.

## Features

- 📁 Drag & drop JSON file upload
- 📊 Real-time progress tracking
- 🤖 AI-powered parameter suggestions
- 👤 Interactive confirmation workflow
- 📈 Comprehensive results viewing
- 🌙 Dark mode support
- 📱 Responsive design

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.11+

### Installation

1. **Install frontend dependencies:**
```bash
cd web
npm install
```

2. **Install backend dependencies:**
```bash
cd ..
pip install -r api/requirements.txt
```

### Running the Application

1. **Start the backend API:**
```bash
# From project root
python api/server.py
```

The API will run on `http://localhost:8000`

2. **Start the frontend (in a new terminal):**
```bash
cd web
npm start
```

The UI will open in your browser at `http://localhost:3000`

## Usage

1. **Upload a JSON file** containing TikTok video data
2. **Configure processing parameters** in the modal that appears
3. **Monitor progress** in real-time as videos are processed
4. **Review AI suggestions** for language and character limits
5. **View results** and download CSV/JSONL files

## Architecture

### Frontend
- **Framework:** React 18
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **State:** React Hooks

### Backend
- **Framework:** FastAPI
- **Processing:** Integrates existing Python modules
- **Storage:** File-based (CSV/JSONL output)

## Project Structure

```
web/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   ├── DropZone.js
│   │   ├── ConfigModal.js
│   │   ├── ProcessingView.js
│   │   ├── ResultsView.js
│   │   ├── AIAnalysisModal.js
│   │   ├── SettingsModal.js
│   │   └── TranscriptModal.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
└── README.md

api/
├── server.py
└── requirements.txt
```

## API Endpoints

- `POST /api/upload` - Upload JSON file
- `POST /api/process` - Start processing job
- `GET /api/progress/{job_id}` - Get job progress
- `GET /api/recent-creators` - Get recent creators
- `GET /api/download/{filename}` - Download output files

## Development

### Frontend Development
```bash
cd web
npm start          # Start dev server
npm run build      # Build for production
```

### Backend Development
```bash
# Start with auto-reload
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

Settings can be configured in the UI:
- API keys (OpusClip, OpenAI)
- Batch size
- Timeout settings
- Output directories
- Theme preferences

## Troubleshooting

**CORS errors:**
- Ensure the backend is running on port 8000
- Check CORS settings in `api/server.py`

**File upload fails:**
- Verify JSON file format
- Check file size limits

**Progress not updating:**
- Ensure WebSocket/polling is working
- Check browser console for errors

## License

Part of the BrandVoice Scaffold project.


