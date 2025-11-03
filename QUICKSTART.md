# BrandVoice Studio - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

Before you start, make sure you have:

- ✅ **Python 3.11+** ([Download](https://www.python.org/downloads/))
- ✅ **Node.js 16+** ([Download](https://nodejs.org/))
- ✅ **OpusClip API Key** ([Get one](https://www.opus.pro/))
- ⭕ **OpenAI API Key** (Optional, for AI features)

## Installation

### Step 1: Clone or Download

```bash
git clone <repository-url>
cd brandvoice-scaffold
```

### Step 2: Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
pip install -r api/requirements.txt
playwright install
```

**Frontend:**
```bash
cd web
npm install
cd ..
```

### Step 3: Configure API Keys

Create a `.env` file in the project root:

```bash
OPUSCLIP_API_KEY=your_opusclip_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

## Launch Application

### Option A: Using Start Script (Easiest)

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

The script will:
- ✅ Check dependencies
- ✅ Start backend API on port 8000
- ✅ Start frontend UI on port 3000
- ✅ Open browser automatically

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
python api/server.py
```

**Terminal 2 - Frontend:**
```bash
cd web
npm start
```

## First Use

### 1. Open Application

Navigate to `http://localhost:3000` in your browser.

### 2. Upload JSON File

- Drag and drop a TikTok JSON file, or
- Click to browse and select a file

### 3. Configure Settings

In the modal that appears:
- Adjust video count if needed
- Choose "Auto-detect" for AI-powered parameters
- Select "Interactive" mode to review suggestions
- Click **Start Processing**

### 4. Monitor Progress

Watch real-time updates as videos are processed:
- See each video's status
- View transcript extraction progress
- Monitor OpusClip API calls

### 5. Download Results

Once complete:
- Download CSV file (video metadata + transcripts)
- Download JSONL file (training data)
- View individual video transcripts

## Example Workflow

Here's a complete example:

```bash
# 1. Start the application
./start.sh

# 2. In browser (http://localhost:3000):
#    - Upload input/reidhoffman.json
#    - Set videos to process: 10
#    - Choose "Auto-detect" parameters
#    - Click "Start Processing"

# 3. Wait 80-100 minutes (10 videos × ~8-10 min each)

# 4. Download results:
#    - output/reidhoffman_20251103_HHMMSS.csv
#    - training_data/reidhoffman_20251103_HHMMSS.jsonl
```

## Testing Without Processing

To test the UI without processing real videos:

1. Use the mock data mode (see `api/server.py`)
2. Or process just 1-2 videos initially
3. Test with small JSON files first

## Common Issues

### Backend won't start

**Error:** `Port 8000 already in use`

**Solution:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

### Frontend won't start

**Error:** `Port 3000 already in use`

**Solution:**
```bash
# Use a different port
cd web
PORT=3001 npm start  # macOS/Linux
set PORT=3001 && npm start  # Windows
```

### Module not found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r api/requirements.txt
```

### CORS errors

**Solution:**
- Ensure backend runs on port 8000
- Ensure frontend runs on port 3000
- Check firewall settings

## Next Steps

Now that you're up and running:

1. **Read the UI Guide:** [UI_GUIDE.md](UI_GUIDE.md) for detailed features
2. **Explore Settings:** Configure API keys and preferences
3. **Try Different Modes:** Test interactive vs. auto-confirm
4. **Process Multiple Creators:** Upload different JSON files
5. **Review Training Data:** Check the JSONL format

## Getting Help

- 📖 **Full Documentation:** [README.md](README.md)
- 🎨 **UI Features:** [UI_GUIDE.md](UI_GUIDE.md)
- 🚀 **Deployment:** [DEPLOYMENT.md](DEPLOYMENT.md)
- 📚 **API Reference:** [API_REFERENCE.md](API_REFERENCE.md)

## Tips for Success

### 1. Start Small
Process 2-3 videos first to verify everything works.

### 2. Monitor API Usage
- OpusClip: ~$0.05-0.10 per video
- OpenAI: ~$0.01 per analysis

### 3. Use Auto-confirm for Large Batches
For 50+ videos, use auto-confirm mode to avoid manual intervention.

### 4. Keep Browser Tab Open
The UI needs to stay open to show progress updates.

### 5. Check Output Regularly
Verify generated files look correct after first few videos.

## Keyboard Shortcuts

- `Cmd/Ctrl + K` - Focus search
- `Esc` - Close modal
- `Cmd/Ctrl + D` - Toggle dark mode

## Video Tutorial

*Coming soon: Video walkthrough of the complete workflow*

## Feedback

Found an issue or have a suggestion? Please create an issue on GitHub.

---

**Ready to go? Run `./start.sh` and start processing! 🚀**


