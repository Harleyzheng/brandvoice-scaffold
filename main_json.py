#!/usr/bin/env python3
"""
TikTok JSON Processor - Main CLI Entry Point

Processes TikTok API response JSON files, extracts video IDs,
fetches transcripts via OpusClip, and outputs structured CSV data.

Workflow:
1. Parse JSON file (e.g., reidhoffman.json) for video IDs
2. Deduplicate video IDs
3. Process videos in batches via OpusClip
4. Generate CSV output
5. Analyze content with LLM to suggest optimal parameters
6. Confirm parameters with user (human-in-the-loop)
7. Convert CSV to JSONL training data format

Usage:
    python main_json.py --json reidhoffman.json --batch-size 10
    python main_json.py --json reidhoffman.json --output custom_output/ --count 10
"""

import argparse
import asyncio
import os
import sys
import csv
from typing import Optional, List, Dict, Tuple
from dotenv import load_dotenv

from utils.json_processor import TikTokJSONProcessor
from utils.csv_generator import CSVGenerator
from utils.jsonl_converter import JSONLConverter
from clients.opus_client import OpusClipClient

# Load environment variables
load_dotenv()


def analyze_content_with_llm(csv_path: str, anthropic_api_key: Optional[str] = None) -> Tuple[str, int]:
    """
    Use Claude to analyze CSV content and suggest optimal language and max_char values.
    
    Args:
        csv_path: Path to the CSV file
        anthropic_api_key: Anthropic API key (optional, will use env var if not provided)
    
    Returns:
        Tuple of (suggested_language, suggested_max_char)
    """
    try:
        from anthropic import Anthropic
        
        api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  No Anthropic API key found. Using defaults.")
            return ("English", 150)
        
        # Read sample of CSV data (first 5 rows)
        sample_data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 5:  # Only analyze first 5 videos
                    break
                sample_data.append({
                    'description': row.get('description', '')[:200],  # First 200 chars
                    'hashtags': row.get('hashtags', ''),
                    'transcript': row.get('transcript', '')[:300]  # First 300 chars
                })
        
        if not sample_data:
            return ("English", 150)
        
        # Prepare prompt for Claude
        prompt = f"""Analyze the following TikTok video data samples and suggest optimal parameters for JSONL training data conversion:

Sample Data:
{chr(10).join([f"Video {i+1}:\n  Description: {v['description']}\n  Hashtags: {v['hashtags']}\n  Transcript excerpt: {v['transcript'][:150]}..." for i, v in enumerate(sample_data)])}

Based on this content, please suggest:
1. The primary language used (e.g., English, Spanish, French, etc.)
2. An optimal maximum character limit for TikTok descriptions (typically 100-300 characters, considering TikTok's platform and the style of these videos)

Respond in JSON format:
{{
  "language": "detected language",
  "max_char": recommended_number,
  "reasoning": "brief explanation"
}}"""

        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        # Extract JSON from response (handle markdown code blocks)
        import json
        import re
        
        # Try to find JSON in code blocks first
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group(1))
        else:
            # Try to parse the whole response as JSON
            response_json = json.loads(response_text)
        
        suggested_language = response_json.get('language', 'English')
        suggested_max_char = response_json.get('max_char', 150)
        reasoning = response_json.get('reasoning', '')
        
        print(f"\n🤖 AI Analysis:")
        print(f"   Language: {suggested_language}")
        print(f"   Max Characters: {suggested_max_char}")
        print(f"   Reasoning: {reasoning}")
        
        return (suggested_language, suggested_max_char)
        
    except Exception as e:
        print(f"⚠️  Error analyzing content with LLM: {e}")
        print("   Using default values.")
        return ("English", 150)


def confirm_jsonl_parameters(suggested_language: str, suggested_max_char: int, 
                            cli_language: Optional[str], cli_max_char: Optional[int],
                            skip_interactive: bool = False) -> Tuple[str, int]:
    """
    Prompt user to confirm or modify JSONL conversion parameters.
    
    Args:
        suggested_language: LLM-suggested language
        suggested_max_char: LLM-suggested max character limit
        cli_language: Language from CLI argument (if provided)
        cli_max_char: Max char from CLI argument (if provided)
        skip_interactive: Skip user confirmation
    
    Returns:
        Tuple of (final_language, final_max_char)
    """
    # If CLI args were provided, use those directly
    if cli_language is not None and cli_max_char is not None:
        print(f"\n✅ Using CLI-provided parameters:")
        print(f"   Language: {cli_language}")
        print(f"   Max Characters: {cli_max_char}")
        return (cli_language, cli_max_char)
    
    # Use CLI args if provided, otherwise use LLM suggestions
    default_language = cli_language if cli_language is not None else suggested_language
    default_max_char = cli_max_char if cli_max_char is not None else suggested_max_char
    
    if skip_interactive:
        print(f"\n✅ Using suggested parameters (non-interactive mode):")
        print(f"   Language: {default_language}")
        print(f"   Max Characters: {default_max_char}")
        return (default_language, default_max_char)
    
    print("\n" + "=" * 60)
    print("📋 JSONL Conversion Parameters")
    print("=" * 60)
    print(f"Suggested Language: {default_language}")
    print(f"Suggested Max Characters: {default_max_char}")
    print()
    
    # Prompt for language
    language_input = input(f"Enter language [{default_language}]: ").strip()
    final_language = language_input if language_input else default_language
    
    # Prompt for max_char
    while True:
        max_char_input = input(f"Enter max characters [{default_max_char}]: ").strip()
        if not max_char_input:
            final_max_char = default_max_char
            break
        try:
            final_max_char = int(max_char_input)
            if final_max_char < 10:
                print("⚠️  Max characters must be at least 10. Try again.")
                continue
            break
        except ValueError:
            print("⚠️  Please enter a valid number. Try again.")
    
    print(f"\n✅ Confirmed parameters:")
    print(f"   Language: {final_language}")
    print(f"   Max Characters: {final_max_char}")
    
    return (final_language, final_max_char)


async def process_json_file(
    json_path: str,
    count: Optional[int] = None,
    output_dir: str = "output",
    batch_size: int = 10,
    opus_api_key: Optional[str] = None,
    language: Optional[str] = None,
    max_char: Optional[int] = None,
    style: str = "",
    skip_interactive: bool = False,
    anthropic_api_key: Optional[str] = None
) -> str:
    """
    Main workflow: Parse JSON → Extract transcripts → Generate CSV → Convert to JSONL

    Args:
        json_path: Path to JSON file with TikTok API response
        count: Number of top videos to process (None = all)
        output_dir: Output directory for CSV
        batch_size: Number of videos to process in parallel
        opus_api_key: OpusClip API key (optional, will use env var if not provided)
        language: Language for JSONL training data (optional, will be suggested by LLM if not provided)
        max_char: Max characters for description in JSONL (optional, will be suggested by LLM if not provided)
        style: Custom style instructions for JSONL (default: "")
        skip_interactive: Skip interactive confirmation prompts (default: False)
        anthropic_api_key: Anthropic API key for LLM analysis (optional, will use env var if not provided)

    Returns:
        Path to generated CSV file
    """
    print("=" * 60)
    print("🎬 TikTok JSON Processor")
    print("=" * 60)

    print("API Key: ", opus_api_key)

    # Get channel name from JSON filename
    processor = TikTokJSONProcessor()
    channel_name = processor.get_channel_name_from_path(json_path)

    print(f"\n📄 JSON File: {json_path}")
    print(f"📱 Channel: {channel_name}")
    print(f"🔄 Batch size: {batch_size}")
    print(f"📁 Output directory: {output_dir}\n")

    # Step 1: Parse JSON file
    print("=" * 60)
    print("STEP 1: Parsing JSON File")
    print("=" * 60)

    videos = processor.process_json_file(json_path)

    if not videos:
        print("❌ No videos found in JSON. Exiting.")
        return ""

    # Limit to count if specified
    if count and count < len(videos):
        print(f"\n📊 Limiting to top {count} videos (sorted by view count)")
        videos = videos[:count]

    print(f"\n✅ Processing {len(videos)} videos")

    # Display top videos
    print("\n📊 Top Videos:")
    for i, video in enumerate(videos[:5], 1):
        print(f"  {i}. ID: {video['video_id']} ({video.get('view_count', 0):,} views)")
        print(f"     {video.get('description', '')[:60]}...")

    if len(videos) > 5:
        print(f"  ... and {len(videos) - 5} more")

    # Step 2: Extract transcripts via OpusClip
    print("\n" + "=" * 60)
    print("STEP 2: Extracting Transcripts via OpusClip")
    print("=" * 60)

    opus_client = OpusClipClient(api_key=opus_api_key)
    videos_with_transcripts = await process_videos_with_opusclip(
        videos, opus_client, batch_size
    )

    if not videos_with_transcripts:
        print("❌ No transcripts extracted. Exiting.")
        return ""

    print(f"\n✅ Extracted {len(videos_with_transcripts)} transcripts")

    # Step 3: Generate CSV
    print("\n" + "=" * 60)
    print("STEP 3: Generating CSV")
    print("=" * 60)

    generator = CSVGenerator()
    output_path = generator.generate_filename(channel_name, output_dir)
    csv_path = generator.generate_csv(videos_with_transcripts, output_path)

    # Step 4: Analyze content and confirm JSONL parameters
    print("\n" + "=" * 60)
    print("STEP 4: Analyzing Content for JSONL Conversion")
    print("=" * 60)

    # Use LLM to analyze and suggest parameters
    suggested_language, suggested_max_char = analyze_content_with_llm(csv_path, anthropic_api_key)
    
    # Get final parameters with user confirmation
    final_language, final_max_char = confirm_jsonl_parameters(
        suggested_language=suggested_language,
        suggested_max_char=suggested_max_char,
        cli_language=language,
        cli_max_char=max_char,
        skip_interactive=skip_interactive
    )

    # Step 5: Convert CSV to JSONL
    print("\n" + "=" * 60)
    print("STEP 5: Converting CSV to JSONL Training Data")
    print("=" * 60)

    converter = JSONLConverter(language=final_language, max_char=final_max_char, style=style)
    
    # Generate JSONL output path (same directory as CSV, same base name)
    csv_dir = os.path.dirname(csv_path)
    csv_basename = os.path.splitext(os.path.basename(csv_path))[0]
    jsonl_path = os.path.join(csv_dir, f"{csv_basename}.jsonl")
    
    num_examples = converter.convert_csv_to_jsonl(csv_path, jsonl_path)

    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
    print(f"📄 CSV File: {csv_path}")
    print(f"📄 JSONL File: {jsonl_path}")
    print(f"📊 Total Videos: {len(videos_with_transcripts)}")
    print(f"📊 Training Examples: {num_examples}")

    return csv_path


async def process_videos_with_opusclip(
    videos: List[Dict],
    opus_client: OpusClipClient,
    batch_size: int = 10
) -> List[Dict]:
    """
    Process videos in batches using OpusClip for transcript extraction.

    Args:
        videos: List of video metadata dicts
        opus_client: OpusClip API client
        batch_size: Number of videos to process in parallel

    Returns:
        List of videos with transcripts
    """
    results = []

    # Submit all projects in parallel first
    print(f"\n📤 Submitting {len(videos)} projects to OpusClip...")
    project_submissions = []

    for i in range(0, len(videos), batch_size):
        batch = videos[i:i + batch_size]
        print(f"\n📦 Submitting batch {i // batch_size + 1} ({len(batch)} videos)")

        for video in batch:
            try:
                video_url = video['video_url']
                project_response = opus_client.submit_project(video_url)
                project_id = project_response.get('projectId')

                if project_id:
                    video['project_id'] = project_id
                    project_submissions.append(video)
                    print(f"  ✅ Submitted {video['video_id']} → Project {project_id}")
                else:
                    print(f"  ❌ Failed to submit {video['video_id']}")

            except Exception as e:
                print(f"  ❌ Error submitting {video['video_id']}: {e}")

    if not project_submissions:
        print("❌ No projects submitted successfully")
        return []

    print(f"\n✅ Submitted {len(project_submissions)} projects")
    print(f"⏳ Waiting for projects to complete (this may take 5-10 minutes per video)...")

    # Wait for all projects to complete in parallel
    async def wait_and_extract(video):
        try:
            project_id = video.get('project_id')
            video_id = video.get('video_id')
            if not project_id:
                return None

            print(f"\n{'='*60}")
            print(f"🎬 Processing video: {video_id}")
            print(f"   Project ID: {project_id}")
            print(f"{'='*60}")

            # Wait for completion (run in executor to avoid blocking)
            loop = asyncio.get_event_loop()
            completed = await loop.run_in_executor(
                None,
                opus_client.wait_for_project_completion,
                project_id,
                600  # 10 minute timeout
            )

            if not completed:
                print(f"\n❌ Project {project_id} (video {video_id}) timed out or failed")
                print(f"   Status: Not completed within timeout period")
                return None

            # Get exportable clips using new API
            print(f"\n📎 Fetching exportable clips for project {project_id}...")
            exportable_clips = opus_client.get_exportable_clips(project_id)
            print(f"   Number of clips: {len(exportable_clips)}")
            
            if not exportable_clips:
                print(f"\n⚠️  No exportable clips found for project {project_id}")
                print(f"   Video ID: {video_id}")
                return None

            # Get transcript from first clip
            first_clip = exportable_clips[0]
            print(f"\n📝 Extracting transcript from first clip...")
            print(f"   Clip ID: {first_clip.get('id', 'N/A')}")
            print(f"   Title: {first_clip.get('title', 'N/A')}")
            print(f"   Duration: {first_clip.get('durationMs', 0) / 1000:.2f}s")
            print(f"   Score: {first_clip.get('score', 'N/A')}")
            
            # Extract screenplay
            screenplay = first_clip.get('screenplay', {})
            if not screenplay:
                print(f"   ⚠️  WARNING: No screenplay found in clip data")
                print(f"   Available keys: {list(first_clip.keys())}")
                return None
            
            transcript = opus_client.extract_transcript_from_screenplay(screenplay)

            if transcript:
                video['transcript'] = transcript
                video['transcript_source'] = 'opusclip'
                print(f"\n✅ Successfully extracted transcript for {video_id}")
                print(f"   Project ID: {project_id}")
                print(f"   Transcript length: {len(transcript)} chars")
                print(f"   Preview: {transcript[:100]}...")
                return video
            else:
                print(f"\n⚠️  Empty transcript for video {video_id}")
                return None

        except Exception as e:
            print(f"\n❌ ERROR processing {video.get('video_id')}:")
            print(f"   Project ID: {video.get('project_id')}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            import traceback
            print(f"   Full traceback:")
            print(traceback.format_exc())

        return None

    # Process all in parallel
    tasks = [wait_and_extract(video) for video in project_submissions]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out None and exceptions
    valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]

    print(f"\n✅ Successfully extracted {len(valid_results)} transcripts")
    return valid_results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TikTok JSON Processor - Extract transcripts from TikTok API response JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (interactive mode with LLM suggestions)
  python main_json.py --json reidhoffman.json
  
  # Specify parameters directly (skips LLM analysis)
  python main_json.py --json reidhoffman.json --language English --max-char 150
  
  # Non-interactive mode (uses LLM suggestions automatically)
  python main_json.py --json reidhoffman.json --skip-interactive
  
  # Process limited videos
  python main_json.py --json reidhoffman.json --count 10 --output my_data/

Notes:
  - JSON file should contain TikTok API response with video data
  - Requires OPUSCLIP_API_KEY in .env file
  - Optional: ANTHROPIC_API_KEY for LLM-powered parameter suggestions
  - Videos are automatically sorted by view count (descending)
  - Processing time: ~5-10 minutes per video via OpusClip
  - LLM analyzes content to suggest optimal language and max_char values
  - Interactive mode allows you to confirm or modify suggested parameters
        """
    )

    parser.add_argument(
        '--json',
        type=str,
        required=True,
        help='Path to JSON file with TikTok API response (e.g., reidhoffman.json)'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=None,
        help='Number of top videos to process (default: all videos in JSON)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output directory for CSV file (default: output/)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of videos to process in parallel (default: 10)'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='OpusClip API key (optional, will use OPUSCLIP_API_KEY from .env if not provided)'
    )

    parser.add_argument(
        '--language',
        type=str,
        default=None,
        help='Language for JSONL training data (optional, will be suggested by LLM if not provided)'
    )

    parser.add_argument(
        '--max-char',
        type=int,
        default=None,
        help='Max characters for description in JSONL (optional, will be suggested by LLM if not provided)'
    )

    parser.add_argument(
        '--style',
        type=str,
        default='',
        help='Custom style instructions for JSONL training data (default: none)'
    )

    parser.add_argument(
        '--skip-interactive',
        action='store_true',
        help='Skip interactive confirmation prompts, use LLM suggestions or CLI defaults directly'
    )

    parser.add_argument(
        '--anthropic-api-key',
        type=str,
        default=None,
        help='Anthropic API key for LLM content analysis (optional, will use ANTHROPIC_API_KEY from .env if not provided)'
    )

    args = parser.parse_args()

    # Check if JSON file exists
    if not os.path.exists(args.json):
        print(f"❌ Error: JSON file not found: {args.json}")
        sys.exit(1)

    # Validate API key
    api_key = args.api_key or os.getenv('OPUSCLIP_API_KEY')
    if not api_key:
        print("❌ Error: OpusClip API key is required.")
        print("   Set OPUSCLIP_API_KEY in .env or use --api-key argument")
        sys.exit(1)

    # Run the processor
    try:
        csv_path = asyncio.run(process_json_file(
            json_path=args.json,
            count=args.count,
            output_dir=args.output,
            batch_size=args.batch_size,
            opus_api_key=api_key,
            language=args.language,
            max_char=args.max_char,
            style=args.style,
            skip_interactive=args.skip_interactive,
            anthropic_api_key=args.anthropic_api_key
        ))

        if csv_path:
            print(f"\n🎉 Success! Data saved to: {csv_path}")
            sys.exit(0)
        else:
            print("\n❌ Failed to generate CSV")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
