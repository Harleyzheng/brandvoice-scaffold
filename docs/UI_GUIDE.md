# BrandVoice Studio - UI Guide

## Overview

BrandVoice Studio provides an intuitive, modern web interface for processing TikTok videos into LLM training data. This guide walks you through every feature and workflow.

---

## Getting Started

### Initial Setup

1. **Start the Backend API:**
```bash
python api/server.py
```
Backend runs on `http://localhost:8000`

2. **Start the Frontend (new terminal):**
```bash
cd web
npm install  # First time only
npm start
```
Frontend opens at `http://localhost:3000`

---

## Interface Overview

### Main Layout

```
┌─────────────────────────────────────────────────────┐
│  🎭 BrandVoice Studio              🌙  ⚙️ Settings  │
├─────────────────────────────────────────────────────┤
│  [Creators]  [History]                              │
│                                                     │
│  Main Content Area                                  │
│  - Drop zone / Processing view / Results           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Key Features

- **Dark Mode**: Toggle between light and dark themes
- **Settings**: Configure API keys and processing preferences
- **Tabs**: Switch between Creators and History views
- **Real-time Updates**: Progress updates every 3 seconds

---

## Workflows

### Workflow 1: Process New Creator Videos

#### Step 1: Upload JSON File

**Two Options:**

A. **Drag & Drop:**
   - Drag your TikTok JSON file onto the drop zone
   - File is validated immediately

B. **Click to Browse:**
   - Click the drop zone
   - Select JSON file from file picker

**What Happens:**
- File is uploaded to server
- Videos are counted
- Existing videos are detected
- Configuration modal opens

#### Step 2: Configure Processing

The configuration modal shows:

```
┌───────────────────────────────────────────────────┐
│  Configure Processing: reidhoffman.json       [×] │
├───────────────────────────────────────────────────┤
│  📊 Found 35 videos in JSON                       │
│  📋 12 videos already processed (will skip)       │
│                                                   │
│  Process Settings:                               │
│  - Videos to process: 23 (adjustable)            │
│  - Batch size: 10 (parallel processing)          │
│                                                   │
│  Parameter Configuration:                        │
│  ○ Auto-detect (AI analyzes & suggests)          │
│  ● Manual override:                              │
│    - Language: English ▼                         │
│    - Max chars: 150                              │
│    - Style: [custom instructions]                │
│                                                   │
│  Confirmation Mode:                              │
│  ● Interactive (review AI suggestions)           │
│  ○ Auto-confirm (use AI suggestions)            │
│  ○ Non-interactive (silent mode)                │
│                                                   │
│  [Cancel]  [Start Processing]                    │
└───────────────────────────────────────────────────┘
```

**Configuration Options:**

1. **Videos to Process:** Adjust how many videos to process
2. **Batch Size:** Number of parallel operations (default: 10)
3. **Parameter Mode:**
   - **Auto-detect:** AI analyzes content and suggests parameters
   - **Manual override:** Specify language, max chars, and style
4. **Confirmation Mode:**
   - **Interactive:** Review and modify AI suggestions before JSONL generation
   - **Auto-confirm:** Show suggestions but proceed automatically
   - **Non-interactive:** Fully automated, no prompts

Click **Start Processing** to begin.

#### Step 3: Monitor Progress

The processing view shows real-time updates:

```
┌─────────────────────────────────────────────────────┐
│  Processing: Reid Hoffman                 [⏸ Pause] │
├─────────────────────────────────────────────────────┤
│  Overall Progress: ████████░░░░  35%  8/23 videos   │
│  Current Phase: 📝 Extracting Transcripts           │
│  Estimated time: ~45 minutes                        │
│                                                     │
│  Videos:                                            │
│  ┌──────────────────────────────────────────────┐  │
│  │ ✅ Video 1: "The Future of AI"               │  │
│  │    ✅ Parse metadata     (2s)                │  │
│  │    ✅ Extract transcript (8m 23s)            │  │
│  │    ✅ Generate CSV       (1s)                │  │
│  │    [View Transcript] [OpusClip Project]      │  │
│  │                                              │  │
│  │ ⏳ Video 3: "Building Teams"                 │  │
│  │    ✅ Parse metadata     (1s)                │  │
│  │    ⏳ Extract transcript (3m / ~8m)          │  │
│  │       └─ OpusClip: Processing scenes...      │  │
│  │    ⏳ Generate CSV (Pending)                 │  │
│  │                                              │  │
│  │ ... (more videos)                            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Progress Indicators:**
- ✅ Completed (green)
- ⏳ In Progress (blue, animated)
- ⏸ Paused (yellow)
- ❌ Error (red)
- ⏭ Skipped (gray)

**Interactive Features:**
- Click any video to expand/collapse details
- **Expand All**: Show all video details
- **Collapse All**: Minimize all videos
- **Export Progress Log**: Download processing log

#### Step 4: AI Analysis (if enabled)

After CSV generation, the AI analysis modal appears:

```
┌──────────────────────────────────────────────────┐
│  🤖 AI Content Analysis Complete            [×] │
├──────────────────────────────────────────────────┤
│  Analyzed 5 sample videos                        │
│                                                  │
│  Detected Language: English                      │
│  Suggested Max Characters: 150                   │
│                                                  │
│  Reasoning:                                      │
│  Content is conversational and concise, typical  │
│  of tech/business commentary. 150 chars suits    │
│  the punchy, direct style.                       │
│                                                  │
│  Modify Parameters (optional):                   │
│  Language:  [English ▼]                          │
│  Max chars: [150]                                │
│  Style:     [Optional custom...]                 │
│                                                  │
│  Sample Preview:                                 │
│  Input: "The future of AI in enterprise..."      │
│  Output: "AI transforms how businesses..."       │
│  Hashtags: #AI #Innovation #Tech                 │
│                                                  │
│  [Use Different Values]  [Confirm]               │
└──────────────────────────────────────────────────┘
```

**Options:**
- **Confirm:** Accept AI suggestions and generate JSONL
- **Modify:** Adjust language, max chars, or style before confirming
- **Use Different Values:** Return to manual configuration

#### Step 5: View Results

Once complete, the results view shows:

```
┌─────────────────────────────────────────────────────┐
│  ✅ Processing Complete: Reid Hoffman               │
├─────────────────────────────────────────────────────┤
│  Summary:                                          │
│  • Processed: 8 new videos                         │
│  • Skipped: 10 duplicates                          │
│  • Total time: 1h 23m                              │
│                                                     │
│  Generated Files:                                  │
│  📄 CSV Output                                     │
│     reidhoffman_20251103_114445.csv                │
│     [Download] [Preview] [View All 8 rows]         │
│                                                     │
│  📄 Training Data (JSONL)                          │
│     reidhoffman_20251103_114445.jsonl              │
│     [Download] [Preview] [View Samples]            │
│                                                     │
│  Video Details:                                    │
│  [Search...] [Filter: All ▼]                       │
│                                                     │
│  📹 "The Future of AI" (7387395749)                │
│  👁 2.3M views  ❤️ 45K likes  💬 892                │
│  ⏱ 45s  📝 342 chars                               │
│  [View Transcript] [OpusClip] [Training]          │
│                                                     │
│  [Process More] [New Creator] [Export All]         │
└─────────────────────────────────────────────────────┘
```

**Actions Available:**
1. **Download Files:** Get CSV and JSONL files
2. **Preview:** View file contents in browser
3. **View Transcript:** See detailed transcript with visual context
4. **OpusClip:** Open OpusClip project dashboard
5. **Search/Filter:** Find specific videos
6. **Process More:** Add more videos for same creator
7. **New Creator:** Start processing a different creator

---

### Workflow 2: View Previous Results

#### From Recent Creators

On the home screen, click any recent creator card:

```
┌─────────────┐
│ Reid Hoffman│
│ 12 videos   │
│ ✅ Complete │
└─────────────┘
```

This loads the results view for that creator with all previously processed videos.

#### From History Tab

Click the **History** tab to see:
- All processing jobs
- Timestamps
- Video counts
- Download links

---

## Detailed Feature Guide

### 1. Transcript Viewer

Click **View Transcript** on any video to open:

```
┌──────────────────────────────────────────────────────┐
│  Video Transcript: "The Future of AI"          [×]  │
├──────────────────────────────────────────────────────┤
│  [Raw Text] [Screenplay Format] [Visual Context]    │
│                                                      │
│  Source: OpusClip (with visual context)             │
│                                                      │
│  [00:00] Opening shot of office workspace          │
│  "The future of artificial intelligence..."         │
│                                                      │
│  OpusClip Project:                                  │
│  Project ID: opus_abc123                            │
│  Clips generated: 3                                 │
│  [Open in OpusClip Dashboard]                       │
│                                                      │
│  Training Data Preview:                             │
│  Input: {"language": "English", ...}                │
│  Output: {"description": "...", "hashtags": [...]}  │
│                                                      │
│  [Copy Transcript] [Export JSON]                    │
└──────────────────────────────────────────────────────┘
```

**Tabs:**
- **Raw Text:** Plain transcript text
- **Screenplay Format:** Timestamped with scene descriptions
- **Visual Context:** Visual elements and context

### 2. Settings Panel

Click the ⚙️ icon to configure:

```
┌────────────────────────────────────────────────────┐
│  Settings                                     [×]  │
├────────────────────────────────────────────────────┤
│  API Configuration:                               │
│  OpusClip API Key: [••••••••••••••] [👁]         │
│  OpenAI API Key:   [••••••••••••••] [👁]         │
│                                                    │
│  Default Processing Settings:                     │
│  Batch size:        [10]                          │
│  Timeout per video: [10 minutes]                  │
│  ☑ Auto-save progress                             │
│  ☑ Notification sound                             │
│                                                    │
│  Output Directories:                              │
│  CSV output:    [output/]                         │
│  Training data: [training_data/]                  │
│                                                    │
│  Theme: ○ Light  ● Dark  ○ Auto                   │
│                                                    │
│  [Save Settings]                                   │
└────────────────────────────────────────────────────┘
```

Settings are saved to browser localStorage.

### 3. Search & Filter

In the results view, use search and filters:

- **Search:** Type video title or ID
- **Filters:**
  - All videos
  - High views (>1M)
  - High engagement (>10K likes)

### 4. Dark Mode

Toggle dark mode with the 🌙/☀️ icon in the header. Preference is saved.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Focus search |
| `Esc` | Close modal |
| `Cmd/Ctrl + D` | Toggle dark mode |

---

## Tips & Best Practices

### 1. Optimal Batch Size

- **Fast internet:** 15-20
- **Normal internet:** 10 (default)
- **Slow internet:** 5

### 2. Parameter Selection

- **Auto-detect:** Best for most cases
- **Manual:** Use when you know exact requirements
- **Interactive mode:** Recommended for first-time use

### 3. Processing Large Batches

For 50+ videos:
1. Use non-interactive mode
2. Increase batch size
3. Monitor progress occasionally
4. Let it run in background

### 4. Managing API Costs

OpusClip processing is ~$0.05-0.10 per video:
- Process only necessary videos
- Use preview mode first
- Leverage deduplication (automatic)

### 5. File Management

Files are saved with timestamps:
- `output/creator_YYYYMMDD_HHMMSS.csv`
- `training_data/creator_YYYYMMDD_HHMMSS.jsonl`

Keep organized by deleting old runs periodically.

---

## Troubleshooting

### Issue: Upload fails

**Solution:**
- Check JSON file format
- Verify file is valid JSON
- Ensure file size < 50MB

### Issue: Progress stuck

**Solution:**
- Check backend logs
- Verify OpusClip API key
- Check internet connection
- Restart backend if needed

### Issue: AI analysis not working

**Solution:**
- Verify OpenAI API key in settings
- Check API key has credits
- Fall back to manual parameters

### Issue: Dark mode not persisting

**Solution:**
- Check browser localStorage
- Clear browser cache
- Try different browser

### Issue: CORS errors

**Solution:**
- Ensure backend runs on port 8000
- Check frontend runs on port 3000
- Verify CORS settings in `api/server.py`

---

## API Integration

The UI communicates with these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload JSON file |
| `/api/process` | POST | Start processing |
| `/api/progress/{id}` | GET | Get job status |
| `/api/recent-creators` | GET | List recent creators |
| `/api/download/{file}` | GET | Download output |

For custom integrations, see `/api/server.py`.

---

## Advanced Features

### Custom Style Instructions

In manual parameter mode, add style instructions:

```
Use inspirational tone. 
Always include call-to-action. 
Exactly 5 hashtags required.
Focus on business audience.
```

These are embedded in the JSONL system prompt.

### Batch Comparison

Compare training data across creators:
1. Process multiple creators
2. View results for each
3. Compare styles and parameters
4. Adjust and reprocess if needed

### Resume Interrupted Jobs

If processing is interrupted:
1. Restart the application
2. Upload same JSON file
3. Deduplication automatically skips completed videos
4. Only new videos are processed

---

## Performance

### Expected Processing Times

| Task | Time per Video |
|------|----------------|
| Parse metadata | 1-2s |
| Extract transcript | 5-10 min |
| Generate CSV | <1s |
| AI analysis | 10-15s (total) |
| JSONL conversion | <1s |

**Total per video:** ~8-10 minutes average

### Concurrent Processing

With batch size 10:
- 10 videos process in parallel
- ~8-10 minutes for 10 videos
- ~80-100 minutes for 100 videos

---

## Security Notes

- API keys are stored in browser localStorage (encrypted)
- Uploaded files are temporary (deleted after processing)
- No data is sent to third parties except OpusClip/OpenAI APIs
- Always use HTTPS in production

---

## Getting Help

**Resources:**
- Main README: Project overview
- API Reference: `API_REFERENCE.md`
- Deployment Guide: `DEPLOYMENT.md`

**Support:**
- Check logs: Backend terminal output
- Browser console: Frontend errors
- GitHub Issues: Report bugs

---

## Changelog

### Version 1.0.0 (November 2025)
- Initial release
- Complete UI implementation
- Real-time progress tracking
- AI-powered parameter suggestions
- Dark mode support
- Responsive design

---

**Happy Processing! 🎭**


