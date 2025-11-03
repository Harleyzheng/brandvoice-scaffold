# OpusClip Screenplay Extraction API Reference

This document shows the mapping between TypeScript and Python implementations for extracting screenplay/transcripts from OpusClip project results.

## API Methods

### 1. Get Exportable Clip

Fetches the exportable clip data including screenplay.

**TypeScript:**
```typescript
async function getExportableClip(
  apiSecretKey: string,
  projectId: string,
  clipId: string,
): Promise<ExportableClip>
```

**Python:**
```python
def get_exportable_clip(self, project_id: str, clip_id: str) -> Dict
```

**Usage:**
```python
client = OpusClipClient(api_key="your_api_key")
exportable_clip = client.get_exportable_clip("P2110204gITq", "1234567890")
```

---

### 2. Get Clip Transcript

Convenience method that combines getting the exportable clip and extracting the verbal transcript.

**TypeScript:**
```typescript
async function getClipTranscript(
  apiSecretKey: string,
  projectId: string,
  clipId: string,
): Promise<string>
```

**Python:**
```python
def get_clip_transcript(self, project_id: str, clip_id: str) -> str
```

**Usage:**
```python
client = OpusClipClient(api_key="your_api_key")
transcript = client.get_clip_transcript("P2110204gITq", "1234567890")
print(transcript)
```

---

### 3. Get Verbal Transcript

Standalone utility function that extracts only verbal lines from screenplay chapters.

**TypeScript:**
```typescript
function getVerbalTranscript(chapters: Chapter[]): string
```

**Python:**
```python
def get_verbal_transcript(chapters: List[Dict]) -> str
```

**Usage:**
```python
from opus_client import get_verbal_transcript

# Assuming you have chapters from exportable_clip
chapters = exportable_clip['screenplay']['chapters']
transcript = get_verbal_transcript(chapters)
```

---

## Screenplay Structure

The screenplay data structure from OpusClip API:

```json
{
  "screenplay": {
    "chapters": [
      {
        "lines": [
          {
            "type": "verbal",
            "content": "This is what was spoken..."
          },
          {
            "type": "visual",
            "content": "Camera pans to..."
          }
        ]
      }
    ]
  }
}
```

### Key Points:

1. **Chapters**: Top-level array containing screenplay segments
2. **Lines**: Each chapter contains multiple lines
3. **Type**: Lines can be "verbal" (spoken) or "visual" (camera directions, etc.)
4. **Content**: The actual text content
5. **Filtering**: Only lines with `type === "verbal"` are included in transcripts
6. **Joining**: Verbal content is joined with **no spaces** between lines

---

## Complete Example Workflow

### Python:

```python
from opus_client import OpusClipClient

# Initialize client
client = OpusClipClient(api_key="your_api_key")

# Submit a video and get project ID
project_response = client.submit_project("https://tiktok.com/@user/video/123")
project_id = project_response['projectId']

# Wait for completion
client.wait_for_project_completion(project_id)

# Get clips
clips = client.get_clips(project_id)
clip_id = clips[0]['clipId']

# Extract transcript (simple one-liner)
transcript = client.get_clip_transcript(project_id, clip_id)
print(transcript)
```

### TypeScript:

```typescript
// Get exportable clip
const exportableClip = await getExportableClip(apiKey, projectId, clipId);

// Extract transcript
const transcript = getVerbalTranscript(exportableClip.screenplay?.chapters || []);

// Or use convenience method
const transcript = await getClipTranscript(apiKey, projectId, clipId);
```

---

## Method Comparison Table

| Functionality | TypeScript | Python | Notes |
|---------------|-----------|---------|-------|
| Get exportable clip | `getExportableClip()` | `get_exportable_clip()` | Fetches clip data |
| Get transcript | `getClipTranscript()` | `get_clip_transcript()` | All-in-one convenience |
| Extract from chapters | `getVerbalTranscript()` | `get_verbal_transcript()` | Standalone utility |
| Extract from screenplay | N/A | `extract_transcript_from_screenplay()` | Helper method |

---

## Running Examples

See `example_screenplay_extraction.py` for complete usage examples:

```bash
python example_screenplay_extraction.py <project_id> <clip_id>
```

Example:
```bash
python example_screenplay_extraction.py P2110204gITq 1234567890
```

---

## Notes

- The Python implementation maintains feature parity with the TypeScript API
- All methods properly handle the nested `chapters → lines → content` structure
- Only "verbal" type lines are extracted (non-verbal content like camera directions are filtered out)
- Transcripts are joined without spaces (as per original TypeScript implementation)

