# BrandVoice Scaffold

A Python library for extracting training data from social media platforms (TikTok) to prepare datasets for LLM fine-tuning. Scrapes video content, extracts transcripts, and converts the data into structured formats (CSV and JSONL) ready for model training.

## Features

- 📱 **TikTok Scraping**: Extract video metadata and content from TikTok channels
- 🔤 **Transcript Extraction**: Native TikTok captions with OpusClip API fallback
- 📊 **Structured Output**: Generate CSV files with video metadata and transcripts
- 🤖 **LLM Training Format**: Convert CSV to JSONL format for fine-tuning
- ⚡ **Parallel Processing**: Batch processing for efficient data collection
- 🎯 **Production Ready**: Clean library structure suitable for publishing

## Installation

```bash
pip install -r requirements.txt
playwright install
```

Set up your environment variables in `.env`:
```bash
OPUSCLIP_API_KEY=your_api_key_here
```

## Quick Start

### 1. Extract Videos from TikTok

Process a TikTok channel and extract video metadata with transcripts:

```bash
python main_json.py --json input/channel_data.json --count 10 --output output/
```

This generates a CSV file like `output/reidhoffman_20251103_081855.csv`

### 2. Convert to Training Format

Convert the CSV to JSONL format for LLM fine-tuning:

```bash
python -m utils.jsonl_converter \
  --input output/reidhoffman_20251103_081855.csv \
  --output training_data.jsonl \
  --language English \
  --max-char 200
```

## Library Structure

```
brandvoice-scaffold/
├── scraper.py              # TikTok API wrapper
├── api_scraper.py          # Alternative API-based scraper
├── opus_client.py          # OpusClip API client for transcripts
├── main_json.py            # CLI for processing TikTok JSON data
├── utils/
│   ├── __init__.py
│   ├── csv_generator.py    # CSV output generation
│   ├── json_processor.py   # TikTok JSON parsing
│   ├── transcript_extractor.py  # Transcript extraction logic
│   └── jsonl_converter.py  # CSV to JSONL conversion
├── README.md
├── API_REFERENCE.md
└── requirements.txt
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

#### Process TikTok JSON Data

```bash
python main_json.py --json reidhoffman.json --count 20 --batch-size 10
```

Arguments:
- `--json`: Path to TikTok API response JSON file (required)
- `--count`: Number of top videos to process (default: all)
- `--output`: Output directory for CSV (default: output/)
- `--batch-size`: Parallel processing batch size (default: 10)
- `--api-key`: OpusClip API key override

#### Convert CSV to JSONL

```bash
python -m utils.jsonl_converter \
  --input output/data.csv \
  --output training.jsonl \
  --language English \
  --max-char 200 \
  --style "Custom style instructions here"
```

Arguments:
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

```
┌─────────────────────────────┐
│ 1. TikTok Channel JSON      │
│    (API response data)      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 2. Parse & Extract Videos  │
│    - Parse JSON structure   │
│    - Extract metadata       │
│    - Deduplicate videos     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 3. Extract Transcripts      │
│    ├─ Native TikTok captions│
│    └─ OpusClip API fallback │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 4. Generate CSV Output      │
│    (structured data)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 5. Convert to JSONL         │
│    (LLM training format)    │
└─────────────────────────────┘
```

## Components

### Core Modules

- **[scraper.py](scraper.py)** - TikTok API wrapper using `tiktokapipy`
- **[api_scraper.py](api_scraper.py)** - Alternative API-based scraper
- **[opus_client.py](opus_client.py)** - OpusClip API client for transcript extraction
- **[main_json.py](main_json.py)** - CLI entry point for processing TikTok data

### Utility Modules

- **[utils/json_processor.py](utils/json_processor.py)** - Parse TikTok API JSON responses
- **[utils/transcript_extractor.py](utils/transcript_extractor.py)** - Hybrid transcript extraction
- **[utils/csv_generator.py](utils/csv_generator.py)** - CSV output generation
- **[utils/jsonl_converter.py](utils/jsonl_converter.py)** - CSV to JSONL conversion for training

## API Reference

See [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation.

## Requirements

```
tiktokapipy>=0.2.0
requests>=2.31.0
python-dotenv>=1.0.0
playwright>=1.40.0
```

## Performance Notes

- **OpusClip Processing**: 5-10 minutes per video
- **Batch Processing**: Default 10 videos in parallel
- **Rate Limits**: TikTok may block with CAPTCHA if too aggressive
- **CSV Encoding**: UTF-8 for multi-language support

## Troubleshooting

**Error: "OpusClip API key is required"**
- Set `OPUSCLIP_API_KEY` in your `.env` file

**Error: "EmptyResponseException"**
- TikTok is blocking your IP. Use a proxy or reduce request frequency

**Python-dotenv warnings**
- These are harmless `.env` file parsing warnings and don't affect functionality

**RuntimeWarning when using `python -m`**
- Expected behavior, the script still works correctly

## Use Cases

- **Content Curation**: Collect training data from successful social media content
- **Brand Voice Training**: Fine-tune LLMs to match specific creator styles
- **Content Generation**: Train models to generate platform-appropriate captions
- **Analytics**: Analyze patterns in high-performing social media content

## License

This is a utility library for data preparation. Ensure compliance with platform terms of service when scraping social media content.

## Contributing

This is a clean library structure ready for:
- Publishing as a Python package
- Integration into larger data pipelines
- Extension to other social media platforms

---

**Note**: Always respect platform rate limits and terms of service when collecting data.
