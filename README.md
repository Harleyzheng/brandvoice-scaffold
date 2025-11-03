# BrandVoice Scaffold

A Python library for extracting training data from social media platforms (TikTok) to prepare datasets for LLM fine-tuning. Scrapes video content, extracts transcripts, and converts the data into structured formats (CSV and JSONL) ready for model training.

**🎭 NEW: Web UI Available!** - An intuitive web interface is now available for processing videos with real-time progress tracking. See the [Web UI Guide](#web-ui) below.

## Features

- 📱 **TikTok Scraping**: Extract video metadata and content from TikTok channels
- 🔤 **Enhanced Transcript Extraction**: OpusClip API with visual context support
- 🤖 **AI-Powered Analysis**: GPT-5 analyzes content to suggest optimal training parameters
- 👤 **Human-in-the-Loop**: Interactive confirmation with auto-confirm and skip modes
- 📊 **Structured Output**: Generate CSV files with video metadata and transcripts
- 🎯 **JSONL Training Format**: Automated conversion with customizable parameters
- ⚡ **Parallel Processing**: Batch processing for efficient data collection
- 🔄 **Smart Deduplication**: Automatically skips previously processed videos
- 🎬 **Production Ready**: Clean library structure suitable for publishing

## Installation

```bash
pip install -r requirements.txt
playwright install
```

Set up your environment variables in `.env`:
```bash
OPUSCLIP_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional, for AI-powered parameter suggestions
```

## Quick Start

### Option 1: Web UI (Recommended) 🎭

The easiest way to use BrandVoice is through the web interface:

```bash
# Terminal 1: Start the backend
python api/server.py

# Terminal 2: Start the frontend
cd web
npm install  # First time only
npm start
```

Then open `http://localhost:3000` in your browser and:
1. Drop your TikTok JSON file
2. Configure processing settings
3. Monitor real-time progress
4. Download CSV and JSONL files

**Features:**
- 📊 Real-time progress tracking
- 🤖 AI-powered parameter suggestions
- 👤 Interactive confirmation workflow
- 🌙 Dark mode support
- 📱 Responsive design

See [UI_GUIDE.md](UI_GUIDE.md) for complete documentation.

### Option 2: Command Line (Automated Workflow)

Process TikTok data with AI-powered parameter suggestions in one command:

```bash
# Interactive mode - AI suggests parameters, you confirm
python main_json.py --json input/reidhoffman.json --count 10

# Auto-confirm mode - Uses AI suggestions automatically
python main_json.py --json input/reidhoffman.json --auto-confirm yes

# Non-interactive mode - Skips confirmation prompts
python main_json.py --json input/reidhoffman.json --skip-interactive

# Manual parameters - Skip AI analysis
python main_json.py --json input/reidhoffman.json --language English --max-char 150
```

This complete workflow:
1. ✅ Parses JSON and extracts video metadata
2. ✅ Extracts transcripts via OpusClip (with visual context)
3. ✅ Generates CSV output (`output/reidhoffman_TIMESTAMP.csv`)
4. ✅ Analyzes content with GPT-5 to suggest optimal parameters
5. ✅ Confirms parameters with you (interactive mode)
6. ✅ Converts to JSONL training format (`training_data/reidhoffman_TIMESTAMP.jsonl`)

### Option 3: Manual Workflow (Advanced)

If you prefer to control each step separately:

#### 1. Extract Videos from TikTok

```bash
python main_json.py --json input/channel_data.json --count 10 --language English --max-char 150
```

#### 2. Convert CSV to JSONL (Standalone)

```bash
python -m utils.jsonl_converter \
  --input output/reidhoffman_20251103_081855.csv \
  --output training_data/reidhoffman.jsonl \
  --language English \
  --max-char 200
```

## Library Structure

```
brandvoice-scaffold/
├── main_json.py            # 🎯 Main CLI - Automated workflow
├── web/                    # 🎭 Web UI (React)
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js          # Main application
│   │   └── index.js        # Entry point
│   ├── public/
│   ├── package.json
│   └── README.md           # Web UI documentation
├── api/                    # FastAPI backend for web UI
│   ├── server.py           # API server
│   └── requirements.txt    # API dependencies
├── clients/
│   └── opus_client.py      # OpusClip API client with visual context
├── utils/
│   ├── json_processor.py   # TikTok JSON parsing
│   ├── csv_generator.py    # CSV output with deduplication
│   ├── transcript_extractor.py  # Transcript extraction logic
│   └── jsonl_converter.py  # CSV to JSONL conversion
├── input/                  # Input JSON files (TikTok API responses)
│   ├── reidhoffman.json
│   ├── alexandrabotez.json
│   └── andreabotez.json
├── output/                 # Generated CSV files
├── training_data/          # Generated JSONL training files
├── uploads/                # Temporary uploads (web UI)
├── README.md               # Main documentation
├── UI_GUIDE.md             # Web UI user guide
├── DEPLOYMENT.md           # Deployment instructions
├── API_REFERENCE.md        # API documentation
└── requirements.txt        # Core dependencies
```

## Usage Examples

### As a Library

```python
from utils import TikTokJSONProcessor, CSVGenerator, JSONLConverter

# Parse TikTok data
processor = TikTokJSONProcessor()
videos = processor.process_json_file('channel_data.json')

# Generate CSV
csv_gen = CSVGenerator()
csv_gen.generate_csv(videos, 'output.csv')

# Convert to JSONL for training
converter = JSONLConverter(language='English', max_char=200)
converter.convert_csv_to_jsonl('output.csv', 'training.jsonl')
```

### CLI Usage

#### Complete Workflow (main_json.py)

```bash
# Full automated workflow with AI suggestions
python main_json.py --json reidhoffman.json --count 20 --batch-size 10
```

**Required Arguments:**
- `--json`: Path to TikTok API response JSON file

**Optional Arguments:**
- `--count`: Number of top videos to process (default: all)
- `--output`: Output directory for CSV (default: output/)
- `--batch-size`: Parallel processing batch size (default: 10)
- `--api-key`: OpusClip API key override
- `--openai-api-key`: OpenAI API key for content analysis
- `--language`: Language for JSONL (skips AI suggestion if provided)
- `--max-char`: Max description characters (skips AI suggestion if provided)
- `--style`: Custom style instructions for JSONL generation
- `--skip-interactive`: Use AI suggestions without confirmation
- `--auto-confirm`: Auto-confirm AI suggestions (shows but doesn't ask)

**Workflow Modes:**

1. **Interactive (Default)**: AI suggests parameters, you confirm
   ```bash
   python main_json.py --json input/reidhoffman.json
   ```

2. **Auto-confirm**: Shows AI suggestions and uses them automatically
   ```bash
   python main_json.py --json input/reidhoffman.json --auto-confirm yes
   ```

3. **Non-interactive**: Uses AI suggestions silently
   ```bash
   python main_json.py --json input/reidhoffman.json --skip-interactive
   ```

4. **Manual**: Skip AI analysis by providing both parameters
   ```bash
   python main_json.py --json input/reidhoffman.json --language English --max-char 150
   ```

#### Standalone JSONL Conversion

```bash
python -m utils.jsonl_converter \
  --input output/data.csv \
  --output training_data/output.jsonl \
  --language English \
  --max-char 200 \
  --style "Custom style instructions here"
```

**Arguments:**
- `--input`: Input CSV file (required)
- `--output`: Output JSONL file (required)
- `--language`: Content language (default: English)
- `--max-char`: Max description characters (default: 10)
- `--style`: Custom style instructions for system prompt

## Output Formats

### CSV Output

Generated CSV contains the following columns:

| Column | Description |
|--------|-------------|
| video_id | TikTok video ID |
| video_url | Full video URL |
| transcript | Complete video transcript |
| description | Video caption/description |
| hashtags | Comma-separated hashtags |
| view_count | Number of views |
| like_count | Number of likes |
| comment_count | Number of comments |
| share_count | Number of shares |
| duration | Video duration (seconds) |
| transcript_source | Source: `tiktok_captions`, `opusclip`, or `none` |

### JSONL Output (Training Format)

Each line contains a complete training example:

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "{\"language\": \"English\", \"text\": \"<transcript>\", \"max_char\": 200}"}]
    },
    {
      "role": "model",
      "parts": [{"text": "{\"description\": \"<description>\", \"hashtags\": [\"tag1\", \"tag2\"]}"}]
    }
  ],
  "systemInstruction": {
    "role": "system",
    "parts": [{"text": "<full system prompt>"}]
  }
}
```

## Workflow

### Automated End-to-End Pipeline

```
┌─────────────────────────────────┐
│ 1. TikTok Channel JSON          │
│    (API response data)          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ 2. Parse & Deduplicate Videos  │
│    - Parse JSON structure       │
│    - Extract metadata           │
│    - Check for duplicates       │
│    - Skip processed videos      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ 3. Extract Transcripts          │
│    - OpusClip API (parallel)    │
│    - Enhanced visual context    │
│    - Screenplay parsing         │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ 4. Generate CSV Output          │
│    - Structured video data      │
│    - Timestamped files          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ 5. AI Content Analysis (GPT-5) │
│    - Detect language            │
│    - Suggest max_char           │
│    - Provide reasoning          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ 6. Human Confirmation           │
│    - Review AI suggestions      │
│    - Modify if needed           │
│    - Or auto-confirm/skip       │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ 7. Convert to JSONL             │
│    - LLM training format        │
│    - Custom system prompts      │
│    - Saved to training_data/    │
└─────────────────────────────────┘
```

## Components

### Core Modules

- **[main_json.py](main_json.py)** - Main CLI entry point with automated workflow
  - Orchestrates entire pipeline from JSON to JSONL
  - Integrates AI analysis for parameter suggestions
  - Supports multiple execution modes (interactive, auto-confirm, non-interactive)
  
- **[clients/opus_client.py](clients/opus_client.py)** - OpusClip API client
  - Enhanced transcript extraction with visual context
  - Screenplay parsing (verbal + visual content)
  - Project submission and status polling
  - Exportable clips retrieval

### Utility Modules

- **[utils/json_processor.py](utils/json_processor.py)** - TikTok JSON parser
  - Parse TikTok API response structures
  - Extract video metadata and statistics
  
- **[utils/csv_generator.py](utils/csv_generator.py)** - CSV generation with deduplication
  - Generate timestamped CSV files
  - Smart duplicate detection across multiple runs
  - Transcript source tracking
  
- **[utils/transcript_extractor.py](utils/transcript_extractor.py)** - Transcript extraction utilities
  - Multi-source transcript extraction
  
- **[utils/jsonl_converter.py](utils/jsonl_converter.py)** - Training data conversion
  - CSV to JSONL conversion for LLM fine-tuning
  - Comprehensive system prompt engineering
  - Configurable language and character limits

## API Reference

See [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation.

## Requirements

```
tiktokapipy>=0.2.0
requests>=2.31.0
python-dotenv>=1.0.0
playwright>=1.40.0
openai>=1.0.0
```

**Note:** OpenAI is optional - only required for AI-powered parameter suggestions. The tool will work without it using default values.

## Performance Notes

- **OpusClip Processing**: 5-10 minutes per video
- **Parallel Processing**: Processes all videos in parallel (default batch size: 10)
- **Deduplication**: Automatically skips previously processed videos
- **AI Analysis**: GPT-5 analyzes first 5 videos to suggest parameters
- **CSV Encoding**: UTF-8 for multi-language support
- **JSONL Output**: Automatically saved to `training_data/` directory

## Troubleshooting

**Error: "OpusClip API key is required"**
- Set `OPUSCLIP_API_KEY` in your `.env` file
- Or pass `--api-key` argument to the CLI

**No OpenAI API Key (Warning)**
- Tool will use default values (English, 150 max chars)
- AI analysis requires `OPENAI_API_KEY` in `.env`
- Or pass `--openai-api-key` argument to enable AI suggestions

**All videos already processed**
- The tool detected all videos in the JSON have been processed before
- Check `output/` directory for existing CSV files
- This is expected behavior to avoid duplicate processing

**Error: "EmptyResponseException" (TikTok scraping)**
- TikTok is blocking your IP
- Use a proxy or reduce request frequency
- Note: Current workflow uses JSON input files, not direct scraping

**Python-dotenv warnings**
- These are harmless `.env` file parsing warnings
- Do not affect functionality

**Timeout waiting for OpusClip project**
- Default timeout is 10 minutes per video
- Some videos may take longer to process
- Check OpusClip dashboard for project status

## Key Features Explained

### 🤖 AI-Powered Parameter Suggestions

The tool uses GPT-5 to analyze your video content and suggest optimal parameters:
- **Language Detection**: Automatically detects the primary language used
- **Character Limit**: Suggests optimal description length based on content style
- **Smart Reasoning**: Provides explanations for its suggestions

```bash
# Example output:
🤖 AI Analysis:
   Language: English
   Max Characters: 150
   Reasoning: Content is conversational and concise, typical of tech/business 
              commentary. 150 chars suits the punchy, direct style of these videos.
```

### 🔄 Smart Deduplication

Prevents wasting time and API credits on already-processed videos:
- Scans existing CSV files in `output/` directory
- Identifies videos by ID across multiple runs
- Only processes new videos not seen before

```bash
# Example output:
📋 Found 35 existing video(s) in previous CSV files
⏭️  Skipping 10 duplicate video(s)
✅ Processing 5 new video(s)
```

### 👤 Human-in-the-Loop Modes

Choose your level of automation:
1. **Interactive**: Review and modify AI suggestions (default)
2. **Auto-confirm**: See suggestions but proceed automatically
3. **Non-interactive**: Fully automated with AI suggestions
4. **Manual**: Bypass AI and specify parameters directly

### 🎬 Enhanced Transcript Extraction

OpusClip integration provides rich context:
- **Verbal Content**: Actual spoken words from the video
- **Visual Context**: Scene descriptions and visual elements
- **Screenplay Format**: Structured chapters with timing
- **Quality Assurance**: Multiple clips available per video

## Use Cases

- **Content Curation**: Collect training data from successful social media content
- **Brand Voice Training**: Fine-tune LLMs to match specific creator styles
- **Content Generation**: Train models to generate platform-appropriate captions
- **Analytics**: Analyze patterns in high-performing social media content

## Example Workflow

### Processing Multiple Creators

```bash
# Process Reid Hoffman's videos (interactive mode)
python main_json.py --json input/reidhoffman.json --count 20

# Process Botez Sisters' content (auto-confirm mode)
python main_json.py --json input/alexandrabotez.json --auto-confirm yes
python main_json.py --json input/andreabotez.json --auto-confirm yes
```

**Output Structure:**
```
output/
├── reidhoffman_20251103_114445.csv
├── alexandrabotez_20251103_120000.csv
└── andreabotez_20251103_121500.csv

training_data/
├── reidhoffman_20251103_114445.jsonl
├── alexandrabotez_20251103_120000.jsonl
└── andreabotez_20251103_121500.jsonl
```

### Re-running for New Videos

The tool automatically handles incremental updates:

```bash
# First run: Process 50 videos
python main_json.py --json input/reidhoffman.json --count 50

# Later: Process 100 videos (only processes the 50 new ones)
python main_json.py --json input/reidhoffman.json --count 100
```

### Custom Style Instructions

```bash
python main_json.py \
  --json input/reidhoffman.json \
  --language English \
  --max-char 200 \
  --style "Use inspirational tone. Always include call-to-action. 5 hashtags required."
```

## License

This is a utility library for data preparation. Ensure compliance with platform terms of service when scraping social media content.

## Contributing

This is a clean library structure ready for:
- Publishing as a Python package
- Integration into larger data pipelines
- Extension to other social media platforms

---

**Note**: Always respect platform rate limits and terms of service when collecting data.
