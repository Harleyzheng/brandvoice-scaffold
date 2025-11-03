#!/usr/bin/env python3
"""
CSV Generator for TikTok scraping results
"""

import csv
import os
import glob
from typing import List, Dict, Set
from datetime import datetime


class CSVGenerator:
    def __init__(self):
        self.fieldnames = [
            'video_id',
            'video_url',
            'transcript',
            'description',
            'hashtags',
            'view_count',
            'like_count',
            'comment_count',
            'share_count',
            'duration',
            'transcript_source',
        ]

    def format_hashtags(self, hashtags: List[str]) -> str:
        """
        Format hashtags list into a single comma-separated string.

        Args:
            hashtags: List of hashtag strings

        Returns:
            Comma-separated hashtag string
        """
        if not hashtags:
            return ""
        return ', '.join(hashtags)

    def prepare_row(self, video: Dict) -> Dict:
        """
        Prepare a video dictionary for CSV export.

        Args:
            video: Video metadata dictionary

        Returns:
            Formatted dictionary matching CSV fieldnames
        """
        return {
            'video_id': video.get('video_id', ''),
            'video_url': video.get('video_url', ''),
            'transcript': video.get('transcript', ''),
            'description': video.get('description', ''),
            'hashtags': self.format_hashtags(video.get('hashtags', [])),
            'view_count': video.get('view_count', 0),
            'like_count': video.get('like_count', 0),
            'comment_count': video.get('comment_count', 0),
            'share_count': video.get('share_count', 0),
            'duration': video.get('duration', 0),
            'transcript_source': video.get('transcript_source', 'unknown'),
        }

    def generate_csv(self, videos: List[Dict], output_path: str) -> str:
        """
        Generate CSV file from video data.

        Args:
            videos: List of video metadata dictionaries
            output_path: Path to output CSV file

        Returns:
            Path to generated CSV file
        """
        if not videos:
            print("⚠️  No videos to export")
            return ""

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)

                # Write header
                writer.writeheader()

                # Write rows
                for video in videos:
                    row = self.prepare_row(video)
                    writer.writerow(row)

            print(f"✅ CSV exported: {output_path}")
            print(f"   📊 {len(videos)} videos written")

            # Calculate statistics
            tiktok_captions = sum(1 for v in videos if v.get('transcript_source') == 'tiktok_captions')
            opusclip = sum(1 for v in videos if v.get('transcript_source') == 'opusclip')
            none = sum(1 for v in videos if v.get('transcript_source') in ['none', 'error'])

            print(f"   🔤 TikTok captions: {tiktok_captions}")
            print(f"   🎬 OpusClip: {opusclip}")
            if none > 0:
                print(f"   ❌ No transcript: {none}")

            return output_path

        except Exception as e:
            print(f"❌ Error generating CSV: {e}")
            raise

    def generate_filename(self, username: str, output_dir: str = "output") -> str:
        """
        Generate a timestamped filename for the CSV.

        Args:
            username: TikTok username
            output_dir: Output directory path

        Returns:
            Full path to output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{username}_{timestamp}.csv"
        return os.path.join(output_dir, filename)

    def get_existing_video_ids(self, channel_name: str, output_dir: str = "output") -> Set[str]:
        """
        Get all video IDs that have already been processed for a channel.
        
        Searches for all CSV files matching {channel_name}_*.csv pattern
        and extracts all video IDs from them.

        Args:
            channel_name: TikTok channel/username
            output_dir: Output directory containing CSV files

        Returns:
            Set of video IDs that have already been processed
        """
        existing_ids = set()
        
        # Check if output directory exists
        if not os.path.exists(output_dir):
            return existing_ids
        
        # Find all CSV files matching the channel pattern
        pattern = os.path.join(output_dir, f"{channel_name}_*.csv")
        csv_files = glob.glob(pattern)
        
        if not csv_files:
            return existing_ids
        
        # Read each CSV file and extract video IDs
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    # Check if video_id column exists
                    if 'video_id' not in reader.fieldnames:
                        print(f"⚠️  Warning: No 'video_id' column in {os.path.basename(csv_file)}")
                        continue
                    
                    # Extract all video IDs
                    for row in reader:
                        video_id = row.get('video_id', '').strip()
                        if video_id:
                            existing_ids.add(video_id)
                            
            except Exception as e:
                print(f"⚠️  Warning: Error reading {os.path.basename(csv_file)}: {e}")
                continue
        
        return existing_ids


def test_csv_generator():
    """Test CSV generation with sample data."""
    generator = CSVGenerator()

    # Sample data
    sample_videos = [
        {
            'video_id': '7234567890123456789',
            'video_url': 'https://www.tiktok.com/@test/video/7234567890123456789',
            'transcript': 'This is a test transcript with some text.',
            'description': 'Test video description #funny #test',
            'hashtags': ['funny', 'test', 'viral'],
            'view_count': 1500000,
            'like_count': 150000,
            'comment_count': 5000,
            'share_count': 2000,
            'duration': 15,
            'transcript_source': 'tiktok_captions',
        },
        {
            'video_id': '7234567890123456790',
            'video_url': 'https://www.tiktok.com/@test/video/7234567890123456790',
            'transcript': 'Another transcript from OpusClip.',
            'description': 'Another test video',
            'hashtags': ['comedy', 'standup'],
            'view_count': 2000000,
            'like_count': 200000,
            'comment_count': 8000,
            'share_count': 3000,
            'duration': 30,
            'transcript_source': 'opusclip',
        }
    ]

    # Generate CSV
    output_path = generator.generate_filename("test_user", "output")
    generator.generate_csv(sample_videos, output_path)

    print(f"\n✅ Test CSV generated: {output_path}")


if __name__ == "__main__":
    test_csv_generator()
