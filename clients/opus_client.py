#!/usr/bin/env python3
"""
OpusClip API Client for transcript extraction
"""

import requests
import time
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def get_verbal_transcript(chapters: List[Dict]) -> str:
    """
    Extract verbal transcript from screenplay chapters.
    
    This is a standalone utility function that extracts only verbal lines
    from the chapter structure. Equivalent to TypeScript's getVerbalTranscript().
    
    Args:
        chapters: List of chapter dicts with 'lines' arrays
        
    Returns:
        Combined verbal transcript (joined without spaces)
    """
    if not chapters:
        return ""
    
    verbal_parts = []
    for chapter in chapters:
        lines = chapter.get('lines', [])
        for line in lines:
            if line.get('type') == 'verbal':
                content = line.get('content', '').strip()
                if content:
                    verbal_parts.append(content)
    
    return ''.join(verbal_parts)


def get_enhanced_transcript(chapters: List[Dict]) -> str:
    """
    Extract enhanced transcript from screenplay chapters including visual context.
    
    This function extracts:
    - Chapter summaries (prepended to each chapter)
    - Visual line descriptions (type: "visual")
    - Verbal content (type: "verbal")
    
    All combined with visual descriptions prefixed by "[Visual: ...]".
    
    Args:
        chapters: List of chapter dicts with 'lines' arrays and optional 'summary'
        
    Returns:
        Combined enhanced transcript with visual context
    """
    if not chapters:
        return ""
    
    parts = []
    for chapter in chapters:
        # Add chapter summary if present
        summary = chapter.get('summary', '').strip()
        if summary:
            parts.append(f"[Visual: {summary}]")
        
        # Process lines in order
        lines = chapter.get('lines', [])
        for line in lines:
            line_type = line.get('type')
            content = line.get('content', '').strip()
            
            if not content:
                continue
            
            if line_type == 'verbal':
                parts.append(content)
            elif line_type == 'visual':
                parts.append(f"[Visual: {content}]")
    
    return ' '.join(parts)

class OpusClipClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPUSCLIP_API_KEY')
        if not self.api_key:
            raise ValueError("OpusClip API key is required. Set OPUSCLIP_API_KEY in .env")

        self.base_url = "https://api.opus.pro/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def submit_project(self, video_url: str) -> Dict:
        """
        Submit a video URL to OpusClip for processing with skipCurate option.

        Args:
            video_url: TikTok video URL

        Returns:
            Project response with 'id' field (projectId)
        """
        endpoint = f"{self.base_url}/clip-projects"
        payload = {
            "videoUrl": video_url,
            "curationPref": {
                "model": "ClipAnything"
            }
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Response format: {"id": "P2110204gITq"}
            # Normalize to include 'projectId' for backward compatibility
            if 'id' in result and 'projectId' not in result:
                result['projectId'] = result['id']

            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to submit project for {video_url}: {e}")
            raise

    def get_project_status(self, project_id: str) -> Dict:
        """
        Get the status of a submitted project.

        Args:
            project_id: OpusClip project ID

        Returns:
            Project status information
        """
        endpoint = f"{self.base_url}/clip-projects/{project_id}"

        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get project status for {project_id}: {e}")
            raise

    def get_clips(self, project_id: str) -> List[Dict]:
        """
        Get all clips from a completed project.

        Args:
            project_id: OpusClip project ID

        Returns:
            List of clips with clipIds
        """
        endpoint = f"{self.base_url}/clips/{project_id}"

        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('clips', [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get clips for {project_id}: {e}")
            raise

    def get_exportable_clips(self, project_id: str) -> List[Dict]:
        """
        Get all exportable clips for a project using query parameter.

        Args:
            project_id: OpusClip project ID

        Returns:
            List of exportable clips with screenplay data
        """
        endpoint = f"{self.base_url}/exportable-clips"
        params = {"projectId": project_id}

        try:
            response = requests.get(endpoint, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Response structure: {'data': [...clips...], 'total': N}
            if isinstance(data, dict) and 'data' in data:
                return data.get('data', [])
            
            # Fallback: if response is already a list
            if isinstance(data, list):
                return data
            
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get exportable clips for {project_id}: {e}")
            raise

    def get_exportable_clip(self, project_id: str, clip_id: str) -> Dict:
        """
        Get exportable clip data including screenplay/transcript.

        Args:
            project_id: OpusClip project ID
            clip_id: Clip ID

        Returns:
            Exportable clip data with screenplay
        """
        endpoint = f"{self.base_url}/exportable-clips/{project_id}.{clip_id}"

        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get exportable clip {project_id}.{clip_id}: {e}")
            raise

    def wait_for_project_completion(self, project_id: str, max_wait_seconds: int = 600, poll_interval: int = 10) -> bool:
        """
        Poll project status until completion or timeout.

        Args:
            project_id: OpusClip project ID
            max_wait_seconds: Maximum time to wait (default 10 minutes)
            poll_interval: Seconds between status checks

        Returns:
            True if completed successfully, False if timeout or error
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            try:
                status = self.get_project_status(project_id)
                stage = status.get('stage', 'unknown')
                
                # Print poll status - only show stage
                elapsed = int(time.time() - start_time)
                print(f"\n🔄 Pull status for {project_id} (elapsed: {elapsed}s):")
                print(f"   Stage: {stage}")

                if stage == 'COMPLETE':
                    print(f"✅ Project {project_id} completed")
                    return True
                elif stage in ['FAILED', 'ERROR', 'STALLED']:
                    print(f"❌ Project {project_id} failed with stage: {stage}")
                    if stage == 'STALLED':
                        print(f"   ⏭️  Skipping stalled project - continuing with other projects")
                    print(f"   Error response: {status}")
                    return False

                # Still processing
                time.sleep(poll_interval)

            except Exception as e:
                print(f"\n⚠️  Error checking status for {project_id}:")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Error message: {str(e)}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                time.sleep(poll_interval)

        print(f"\n⏱️  Timeout waiting for project {project_id}")
        print(f"   Max wait time reached: {max_wait_seconds}s")
        return False

    def get_clip_transcript(self, project_id: str, clip_id: str) -> str:
        """
        Get the verbal transcript from a specific clip.
        
        This is a convenience method that combines get_exportable_clip
        and extract_transcript_from_screenplay.

        Args:
            project_id: OpusClip project ID
            clip_id: Clip ID

        Returns:
            Verbal transcript text
        """
        exportable_clip = self.get_exportable_clip(project_id, clip_id)
        screenplay = exportable_clip.get('screenplay', {})
        return self.extract_transcript_from_screenplay(screenplay)

    def extract_transcript_from_screenplay(self, screenplay: Dict) -> str:
        """
        Extract full transcript text from screenplay JSON.
        
        The screenplay structure from OpusClip API:
        {
            "chapters": [
                {
                    "lines": [
                        {"type": "verbal", "content": "text here"},
                        {"type": "visual", "content": "..."},
                        ...
                    ]
                },
                ...
            ]
        }

        Args:
            screenplay: Screenplay dict with chapters structure

        Returns:
            Combined transcript text (verbal lines only)
        """
        if not screenplay:
            return ""
        
        # Get chapters from screenplay and use the standalone function
        chapters = screenplay.get('chapters', [])
        return get_verbal_transcript(chapters)

    def extract_enhanced_transcript_from_screenplay(self, screenplay: Dict) -> str:
        """
        Extract enhanced transcript with visual context from screenplay JSON.
        
        This method extracts:
        - Chapter summaries (prepended to each chapter)
        - Visual line descriptions (type: "visual")
        - Verbal content (type: "verbal")
        
        The screenplay structure from OpusClip API:
        {
            "chapters": [
                {
                    "summary": "chapter visual description",
                    "lines": [
                        {"type": "verbal", "content": "text here"},
                        {"type": "visual", "content": "visual description"},
                        ...
                    ]
                },
                ...
            ]
        }

        Args:
            screenplay: Screenplay dict with chapters structure

        Returns:
            Combined enhanced transcript with visual context
        """
        if not screenplay:
            return ""
        
        # Get chapters from screenplay and use the enhanced extraction function
        chapters = screenplay.get('chapters', [])
        return get_enhanced_transcript(chapters)

    def get_transcript_from_video(self, video_url: str, max_wait_seconds: int = 600) -> Optional[str]:
        """
        Full workflow: Submit video, wait for completion, extract transcript.

        Args:
            video_url: TikTok video URL
            max_wait_seconds: Maximum time to wait for processing

        Returns:
            Transcript text or None if failed
        """
        try:
            # Step 1: Submit project
            print(f"📤 Submitting project for {video_url}")
            project_response = self.submit_project(video_url)
            project_id = project_response.get('projectId')

            if not project_id:
                print(f"❌ No projectId returned for {video_url}")
                return None

            # Step 2: Wait for completion
            print(f"⏳ Waiting for project {project_id} to complete...")
            if not self.wait_for_project_completion(project_id, max_wait_seconds):
                return None

            # Step 3: Get clips
            clips = self.get_clips(project_id)
            if not clips:
                print(f"❌ No clips found for project {project_id}")
                return None

            # Use first clip for transcript
            first_clip = clips[0]
            clip_id = first_clip.get('clipId')

            if not clip_id:
                print(f"❌ No clipId found in first clip")
                return None

            # Step 4: Get exportable clip with screenplay
            exportable_clip = self.get_exportable_clip(project_id, clip_id)
            screenplay = exportable_clip.get('screenplay', [])

            # Step 5: Extract transcript
            transcript = self.extract_transcript_from_screenplay(screenplay)
            print(f"✅ Extracted transcript ({len(transcript)} chars)")
            return transcript

        except Exception as e:
            print(f"❌ Failed to get transcript for {video_url}: {e}")
            return None


if __name__ == "__main__":
    # Test the client
    client = OpusClipClient()
    test_url = "https://www.tiktok.com/@test/video/123456789"
    transcript = client.get_transcript_from_video(test_url)
    print(f"Transcript: {transcript}")
