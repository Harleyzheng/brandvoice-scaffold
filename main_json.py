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

Usage:
    python main_json.py --json reidhoffman.json --batch-size 10
    python main_json.py --json reidhoffman.json --output custom_output/ --count 10
"""

import argparse
import asyncio
import os
import sys
from typing import Optional, List, Dict
from dotenv import load_dotenv

from utils.json_processor import TikTokJSONProcessor
from utils.transcript_extractor import TranscriptExtractor
from utils.csv_generator import CSVGenerator
from opus_client import OpusClipClient

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


async def process_json_file(
    json_path: str,
    count: Optional[int] = None,
    output_dir: str = "output",
    batch_size: int = 10,
    opus_api_key: Optional[str] = None
) -> str:
    """
    Main workflow: Parse JSON → Extract transcripts → Generate CSV

    Args:
        json_path: Path to JSON file with TikTok API response
        count: Number of top videos to process (None = all)
        output_dir: Output directory for CSV
        batch_size: Number of videos to process in parallel
        opus_api_key: OpusClip API key (optional, will use env var if not provided)

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

    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
    print(f"📄 CSV File: {csv_path}")
    print(f"📊 Total Videos: {len(videos_with_transcripts)}")

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
  python main_json.py --json reidhoffman.json
  python main_json.py --json reidhoffman.json --count 10 --output my_data/
  python main_json.py --json reidhoffman.json --batch-size 5

Notes:
  - JSON file should contain TikTok API response with video data
  - Requires OPUSCLIP_API_KEY in .env file
  - Videos are automatically sorted by view count (descending)
  - Processing time: ~5-10 minutes per video via OpusClip
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
            opus_api_key=api_key
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
