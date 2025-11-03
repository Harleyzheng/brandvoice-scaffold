#!/usr/bin/env python3
"""
TikTok Channel Scraper using tiktokapipy
"""

import asyncio
from typing import List, Dict, Optional
from tiktokapipy.async_api import AsyncTikTokAPI


class TikTokScraper:
    def __init__(self):
        pass

    async def get_user_videos(self, username: str, count: int = 10) -> List[Dict]:
        """
        Get top videos from a TikTok user by view count.

        Args:
            username: TikTok username (without @)
            count: Number of videos to retrieve

        Returns:
            List of video metadata dictionaries
        """
        videos_data = []

        try:
            # Configure API with navigation retries and increased timeout
            async with AsyncTikTokAPI(
                navigation_retries=3,
                navigation_timeout=60
            ) as api:
                # Remove @ if present
                username = username.lstrip('@')

                print(f"📱 Fetching user: @{username}")
                user = await api.user(username)

                if not user:
                    print(f"❌ User @{username} not found")
                    return []

                print(f"✅ Found user: {user.display_name} (@{username})")

                # Fetch videos
                video_count = 0
                async for video in user.videos:
                    if video_count >= count * 2:  # Fetch more than needed for sorting
                        break

                    try:
                        video_info = {
                            'video_id': video.id,
                            'video_url': f"https://www.tiktok.com/@{username}/video/{video.id}",
                            'description': video.desc or "",
                            'hashtags': [tag.name for tag in (video.challenges or [])],
                            'view_count': video.stats.play_count if video.stats else 0,
                            'like_count': video.stats.digg_count if video.stats else 0,
                            'comment_count': video.stats.comment_count if video.stats else 0,
                            'share_count': video.stats.share_count if video.stats else 0,
                            'has_captions': bool(video.video.subtitleInfos) if video.video else False,
                            'duration': video.video.duration if video.video else 0,
                        }

                        videos_data.append(video_info)
                        video_count += 1

                        print(f"  📹 Video {video_count}: {video.id} ({video_info['view_count']:,} views)")

                    except Exception as e:
                        print(f"⚠️  Error processing video {video_count + 1}: {e}")
                        continue

                # Sort by view count (descending) and take top N
                videos_data.sort(key=lambda x: x['view_count'], reverse=True)
                top_videos = videos_data[:count]

                print(f"\n✅ Retrieved {len(top_videos)} videos sorted by view count")

                return top_videos

        except Exception as e:
            print(f"❌ Error scraping TikTok user @{username}: {e}")
            return []

    async def get_video_captions(self, video_id: str, username: str) -> Optional[str]:
        """
        Extract native captions/subtitles from a TikTok video.

        Args:
            video_id: TikTok video ID
            username: TikTok username

        Returns:
            Caption text or None if not available
        """
        try:
            # Configure API with navigation retries and increased timeout
            async with AsyncTikTokAPI(
                navigation_retries=3,
                navigation_timeout=60
            ) as api:
                video = await api.video(video_id)

                if not video or not video.video:
                    return None

                # Check for subtitle info
                subtitle_infos = video.video.subtitleInfos
                if not subtitle_infos or len(subtitle_infos) == 0:
                    return None

                # Get first subtitle (usually English or original language)
                subtitle_info = subtitle_infos[0]
                subtitle_url = subtitle_info.get('url') or subtitle_info.get('UrlList', [None])[0]

                if not subtitle_url:
                    return None

                # Fetch subtitle content
                import requests
                response = requests.get(subtitle_url, timeout=10)
                response.raise_for_status()

                # Parse subtitle format (usually WebVTT or plain text)
                caption_text = response.text

                # Clean WebVTT format if present
                if 'WEBVTT' in caption_text:
                    lines = caption_text.split('\n')
                    text_lines = []
                    for line in lines:
                        # Skip WEBVTT headers, timestamps, and empty lines
                        if line.strip() and not line.startswith('WEBVTT') and '-->' not in line and not line.strip().isdigit():
                            text_lines.append(line.strip())
                    caption_text = ' '.join(text_lines)

                return caption_text.strip()

        except Exception as e:
            print(f"⚠️  Error fetching captions for video {video_id}: {e}")
            return None


async def test_scraper():
    """Test the scraper with a sample user."""
    scraper = TikTokScraper()

    # Test with a popular TikTok account
    test_username = "reidhoffman"
    videos = await scraper.get_user_videos(test_username, count=3)

    print(f"\n📊 Results:")
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. Video ID: {video['video_id']}")
        print(f"   URL: {video['video_url']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   Description: {video['description'][:100]}...")
        print(f"   Hashtags: {', '.join(video['hashtags'])}")
        print(f"   Has Captions: {video['has_captions']}")

        # Try to fetch captions if available
        if video['has_captions']:
            captions = await scraper.get_video_captions(video['video_id'], test_username)
            if captions:
                print(f"   Captions: {captions[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_scraper())
