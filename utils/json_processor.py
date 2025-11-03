#!/usr/bin/env python3
"""
JSON Processor - Parses TikTok API response JSON files
Extracts video IDs and metadata for transcript extraction
"""

import json
from typing import List, Dict, Set
import os


class TikTokJSONProcessor:
    def __init__(self):
        pass

    def extract_video_ids(self, json_data: dict) -> List[str]:
        """
        Recursively extract all "id" fields from JSON data.

        Args:
            json_data: Parsed JSON dictionary

        Returns:
            List of unique video IDs
        """
        video_ids = set()

        def recurse_extract(obj):
            if isinstance(obj, dict):
                # Check if this dict has an "id" field
                if 'id' in obj:
                    video_id = str(obj['id'])
                    # TikTok video IDs are typically 19 digits
                    if len(video_id) >= 15:
                        video_ids.add(video_id)

                # Recurse through all values
                for value in obj.values():
                    recurse_extract(value)

            elif isinstance(obj, list):
                for item in obj:
                    recurse_extract(item)

        recurse_extract(json_data)
        return sorted(list(video_ids))

    def parse_video_metadata(self, json_data: dict) -> List[Dict]:
        """
        Parse full video metadata from TikTok API response.

        Args:
            json_data: Parsed JSON dictionary from TikTok API

        Returns:
            List of video metadata dictionaries
        """
        videos = []

        # Try to find itemList in the JSON
        item_list = None

        if 'itemList' in json_data:
            item_list = json_data['itemList']
        elif 'data' in json_data and isinstance(json_data['data'], dict):
            if 'itemList' in json_data['data']:
                item_list = json_data['data']['itemList']

        if not item_list:
            print("⚠️  Could not find 'itemList' in JSON. Falling back to ID extraction only.")
            # Fall back to just extracting IDs
            video_ids = self.extract_video_ids(json_data)
            return [{'video_id': vid, 'video_url': f'https://www.tiktok.com/video/{vid}'} for vid in video_ids]

        # Parse full metadata from itemList
        for item in item_list:
            try:
                video_id = str(item.get('id', ''))
                author = item.get('author', {})
                username = author.get('uniqueId', 'unknown')
                stats = item.get('stats', {})
                video_data = item.get('video', {})

                # Extract description and hashtags from contents or direct fields
                description = item.get('desc', '')
                text_extra = item.get('textExtra', [])

                # Check if desc and textExtra are in contents array
                if 'contents' in item and isinstance(item['contents'], list) and len(item['contents']) > 0:
                    content = item['contents'][0]
                    description = content.get('desc', description)
                    text_extra = content.get('textExtra', text_extra)

                # Extract hashtags from challenges or textExtra
                hashtags = []

                # Try challenges first
                if 'challenges' in item:
                    hashtags = [c.get('title', '') for c in item['challenges'] if c.get('title')]

                # Also check textExtra
                if text_extra:
                    text_hashtags = [tag.get('hashtagName', '') for tag in text_extra if tag.get('hashtagName')]
                    hashtags.extend([h for h in text_hashtags if h not in hashtags])

                video_info = {
                    'video_id': video_id,
                    'video_url': f"https://www.tiktok.com/@{username}/video/{video_id}",
                    'description': description,
                    'hashtags': hashtags,
                    'view_count': stats.get('playCount', 0),
                    'like_count': stats.get('diggCount', 0),
                    'comment_count': stats.get('commentCount', 0),
                    'share_count': stats.get('shareCount', 0),
                    'has_captions': bool(video_data.get('subtitleInfos')),
                    'duration': video_data.get('duration', 0),
                    'create_time': item.get('createTime', 0),
                }

                videos.append(video_info)

            except Exception as e:
                print(f"⚠️  Error parsing video item: {e}")
                continue

        return videos

    def load_json_file(self, file_path: str) -> Dict:
        """
        Load and parse JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return {}

    def process_json_file(self, file_path: str) -> List[Dict]:
        """
        Main processing function: Load JSON, extract and deduplicate video data.

        Args:
            file_path: Path to JSON file

        Returns:
            List of unique video metadata dictionaries
        """
        print(f"📄 Loading JSON file: {file_path}")

        # Load JSON
        json_data = self.load_json_file(file_path)
        if not json_data:
            return []

        print("✅ JSON loaded successfully")

        # Try to parse full metadata first
        print("🔍 Parsing video metadata...")
        videos = self.parse_video_metadata(json_data)

        if not videos:
            print("⚠️  No videos found in standard format")
            return []

        # Deduplicate by video_id
        seen_ids = set()
        unique_videos = []

        for video in videos:
            video_id = video['video_id']
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                unique_videos.append(video)

        print(f"✅ Found {len(videos)} videos, {len(unique_videos)} unique")

        # Sort by view count (descending)
        unique_videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)

        return unique_videos

    def get_channel_name_from_path(self, file_path: str) -> str:
        """
        Extract channel name from JSON file path.

        Args:
            file_path: Path like "reidhoffman.json" or "path/to/reidhoffman.json"

        Returns:
            Channel name (without .json extension)
        """
        basename = os.path.basename(file_path)
        return os.path.splitext(basename)[0]


def test_json_processor():
    """Test the JSON processor with sample data."""
    processor = TikTokJSONProcessor()

    # Create sample JSON for testing
    sample_json = {
        "itemList": [
            {
                "id": "7234567890123456789",
                "author": {"uniqueId": "testuser"},
                "desc": "Test video description #test #viral",
                "stats": {
                    "playCount": 1500000,
                    "diggCount": 150000,
                    "commentCount": 5000,
                    "shareCount": 2000
                },
                "video": {"duration": 15, "subtitleInfos": []},
                "textExtra": [
                    {"hashtagName": "test", "name": "test"},
                    {"hashtagName": "viral", "name": "viral"}
                ]
            },
            {
                "id": "7234567890123456790",
                "author": {"uniqueId": "testuser"},
                "desc": "Another test video",
                "stats": {
                    "playCount": 2000000,
                    "diggCount": 200000,
                    "commentCount": 8000,
                    "shareCount": 3000
                },
                "video": {"duration": 30, "subtitleInfos": [{"url": "test.vtt"}]},
                "textExtra": []
            }
        ]
    }

    print("Testing JSON processor with sample data:\n")
    videos = processor.parse_video_metadata(sample_json)

    for i, video in enumerate(videos, 1):
        print(f"{i}. Video ID: {video['video_id']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   Description: {video['description']}")
        print(f"   Hashtags: {', '.join(video['hashtags'])}")
        print()


if __name__ == "__main__":
    test_json_processor()
