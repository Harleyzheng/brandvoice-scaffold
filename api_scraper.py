#!/usr/bin/env python3
"""
TikTok API Scraper - Uses TikTok's internal /api/post/item_list/ endpoint
Much more reliable than browser automation
"""

import requests
import time
from typing import List, Dict, Optional
import json


class TikTokAPIScraper:
    def __init__(self):
        self.base_url = "https://www.tiktok.com"
        self.api_endpoint = "/api/post/item_list/"

    def get_sec_uid_from_username(self, username: str) -> Optional[str]:
        """
        Get secUid for a username by fetching their profile page.

        Args:
            username: TikTok username (without @)

        Returns:
            secUid string or None
        """
        username = username.lstrip('@')
        profile_url = f"{self.base_url}/@{username}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        try:
            print(f"🔍 Fetching secUid for @{username}...")
            response = requests.get(profile_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Extract secUid from page HTML (it's in the SIGI_STATE script tag)
            html = response.text

            # Look for secUid in the HTML
            if '"secUid":"' in html:
                start = html.find('"secUid":"') + len('"secUid":"')
                end = html.find('"', start)
                sec_uid = html[start:end]
                print(f"✅ Found secUid: {sec_uid[:20]}...")
                return sec_uid

            print(f"❌ Could not find secUid for @{username}")
            return None

        except Exception as e:
            print(f"❌ Error fetching secUid: {e}")
            return None

    def get_user_videos(self, username: str, sec_uid: Optional[str] = None, count: int = 10) -> List[Dict]:
        """
        Get videos from a TikTok user using the item_list API.

        Args:
            username: TikTok username (without @)
            sec_uid: secUid (will fetch if not provided)
            count: Number of videos to retrieve

        Returns:
            List of video metadata dictionaries
        """
        username = username.lstrip('@')

        # Get secUid if not provided
        if not sec_uid:
            sec_uid = self.get_sec_uid_from_username(username)
            if not sec_uid:
                return []

        print(f"\n📱 Fetching videos for @{username}")

        # Build API URL with parameters
        params = {
            'aid': '1988',
            'app_language': 'en',
            'app_name': 'tiktok_web',
            'browser_language': 'en-US',
            'browser_name': 'Mozilla',
            'browser_online': 'true',
            'browser_platform': 'MacIntel',
            'browser_version': '5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'channel': 'tiktok_web',
            'cookie_enabled': 'true',
            'count': str(min(count * 2, 35)),  # Fetch more for sorting, API max ~35
            'coverFormat': '2',
            'cursor': '0',
            'device_platform': 'web_pc',
            'focus_state': 'true',
            'from_page': 'user',
            'history_len': '2',
            'is_fullscreen': 'false',
            'is_page_visible': 'true',
            'language': 'en',
            'os': 'mac',
            'priority_region': '',
            'referer': '',
            'region': 'US',
            'screen_height': '1080',
            'screen_width': '1920',
            'secUid': sec_uid,
            'tz_name': 'America/Los_Angeles',
            'webcast_language': 'en',
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': f'https://www.tiktok.com/@{username}',
            'Sec-Ch-Ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        }

        try:
            url = f"{self.base_url}{self.api_endpoint}"
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for errors
            if data.get('status_code') != 0:
                print(f"❌ API returned error: {data.get('status_msg', 'Unknown error')}")
                return []

            # Extract video items
            item_list = data.get('itemList', [])

            if not item_list:
                print("❌ No videos found in response")
                return []

            print(f"✅ Found {len(item_list)} videos from API")

            # Parse video data
            videos = []
            for item in item_list:
                try:
                    video_id = item.get('id', '')
                    author = item.get('author', {})
                    author_username = author.get('uniqueId', username)
                    stats = item.get('stats', {})
                    video_data = item.get('video', {})

                    video_info = {
                        'video_id': video_id,
                        'video_url': f"https://www.tiktok.com/@{author_username}/video/{video_id}",
                        'description': item.get('desc', ''),
                        'hashtags': [tag.get('name', '') for tag in item.get('textExtra', []) if tag.get('hashtagName')],
                        'view_count': stats.get('playCount', 0),
                        'like_count': stats.get('diggCount', 0),
                        'comment_count': stats.get('commentCount', 0),
                        'share_count': stats.get('shareCount', 0),
                        'has_captions': bool(video_data.get('subtitleInfos')),
                        'duration': video_data.get('duration', 0),
                        'create_time': item.get('createTime', 0),
                    }

                    videos.append(video_info)
                    print(f"  📹 Video {len(videos)}: {video_id} ({video_info['view_count']:,} views)")

                except Exception as e:
                    print(f"⚠️  Error parsing video: {e}")
                    continue

            # Sort by view count (descending) and take top N
            videos.sort(key=lambda x: x['view_count'], reverse=True)
            top_videos = videos[:count]

            print(f"\n✅ Returning top {len(top_videos)} videos sorted by view count")

            return top_videos

        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse API response: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []

    def get_video_captions(self, video_id: str) -> Optional[str]:
        """
        Extract native captions/subtitles from a TikTok video.

        Args:
            video_id: TikTok video ID

        Returns:
            Caption text or None if not available
        """
        # This would require fetching the video detail page
        # For now, we'll rely on OpusClip for transcripts
        # Can implement if needed
        return None


def test_api_scraper():
    """Test the API scraper."""
    scraper = TikTokAPIScraper()

    # Test with Reid Hoffman
    test_username = "reidhoffman"
    videos = scraper.get_user_videos(test_username, count=10)

    print(f"\n📊 Results for @{test_username}:")
    print(f"Total videos fetched: {len(videos)}\n")

    for i, video in enumerate(videos, 1):
        print(f"{i}. Video ID: {video['video_id']}")
        print(f"   URL: {video['video_url']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   Likes: {video['like_count']:,}")
        print(f"   Description: {video['description'][:80]}...")
        print(f"   Hashtags: {', '.join(video['hashtags'][:5])}")
        print(f"   Has Captions: {video['has_captions']}")
        print()


if __name__ == "__main__":
    test_api_scraper()
