#!/usr/bin/env python3
"""
Hybrid Transcript Extractor - Uses TikTok captions first, falls back to OpusClip
"""

import asyncio
from typing import List, Dict, Optional
from scraper import TikTokScraper
from opus_client import OpusClipClient


class TranscriptExtractor:
    def __init__(self, opus_api_key: Optional[str] = None):
        self.scraper = TikTokScraper()
        self.opus_client = OpusClipClient(api_key=opus_api_key)

    async def extract_transcript(self, video_info: Dict, username: str) -> Dict:
        """
        Extract transcript for a single video.
        Try TikTok captions first, fall back to OpusClip if unavailable.

        Args:
            video_info: Video metadata dictionary
            username: TikTok username

        Returns:
            Updated video_info with transcript and source
        """
        video_id = video_info['video_id']
        video_url = video_info['video_url']

        # Try TikTok captions first
        if video_info.get('has_captions', False):
            print(f"🔤 Attempting to extract TikTok captions for {video_id}")
            captions = await self.scraper.get_video_captions(video_id, username)

            if captions and len(captions.strip()) > 0:
                print(f"✅ Got TikTok captions ({len(captions)} chars)")
                video_info['transcript'] = captions
                video_info['transcript_source'] = 'tiktok_captions'
                return video_info

        # Fall back to OpusClip
        print(f"🎬 No TikTok captions, submitting to OpusClip for {video_id}")
        transcript = self.opus_client.get_transcript_from_video(video_url)

        if transcript and len(transcript.strip()) > 0:
            video_info['transcript'] = transcript
            video_info['transcript_source'] = 'opusclip'
        else:
            print(f"❌ Failed to get transcript for {video_id}")
            video_info['transcript'] = ""
            video_info['transcript_source'] = 'none'

        return video_info

    async def extract_transcripts_parallel(self, videos: List[Dict], username: str, batch_size: int = 10) -> List[Dict]:
        """
        Extract transcripts for multiple videos in parallel batches.

        Args:
            videos: List of video metadata dictionaries
            username: TikTok username
            batch_size: Number of videos to process in parallel (default 10)

        Returns:
            List of videos with transcripts
        """
        results = []

        # Process in batches
        for i in range(0, len(videos), batch_size):
            batch = videos[i:i + batch_size]
            print(f"\n📦 Processing batch {i // batch_size + 1} ({len(batch)} videos)")

            # Create tasks for parallel execution
            tasks = []
            for video in batch:
                task = self.extract_transcript(video, username)
                tasks.append(task)

            # Wait for all tasks in batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and add successful results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"⚠️  Error processing video {batch[j]['video_id']}: {result}")
                    # Add video with empty transcript
                    batch[j]['transcript'] = ""
                    batch[j]['transcript_source'] = 'error'
                    results.append(batch[j])
                else:
                    results.append(result)

            print(f"✅ Batch {i // batch_size + 1} complete")

        # Filter out videos with no transcript (unless you want to keep them)
        videos_with_transcripts = [v for v in results if v.get('transcript', '').strip()]
        skipped = len(results) - len(videos_with_transcripts)

        if skipped > 0:
            print(f"\n⚠️  Skipped {skipped} videos with no transcript")

        return videos_with_transcripts

    def extract_transcripts_parallel_sync(self, videos: List[Dict], username: str, batch_size: int = 10) -> List[Dict]:
        """
        Synchronous wrapper for extract_transcripts_parallel.

        Args:
            videos: List of video metadata dictionaries
            username: TikTok username
            batch_size: Number of videos to process in parallel

        Returns:
            List of videos with transcripts
        """
        return asyncio.run(self.extract_transcripts_parallel(videos, username, batch_size))


async def test_extractor():
    """Test the transcript extractor."""
    scraper = TikTokScraper()
    extractor = TranscriptExtractor()

    # Get sample videos
    test_username = "reidhoffman"
    videos = await scraper.get_user_videos(test_username, count=2)

    if not videos:
        print("No videos found for testing")
        return

    # Extract transcripts
    videos_with_transcripts = await extractor.extract_transcripts_parallel(videos, test_username, batch_size=2)

    # Display results
    print(f"\n📊 Transcript Extraction Results:")
    for i, video in enumerate(videos_with_transcripts, 1):
        print(f"\n{i}. Video ID: {video['video_id']}")
        print(f"   Source: {video.get('transcript_source', 'unknown')}")
        print(f"   Transcript length: {len(video.get('transcript', ''))} chars")
        print(f"   Transcript preview: {video.get('transcript', '')[:200]}...")


if __name__ == "__main__":
    asyncio.run(test_extractor())
