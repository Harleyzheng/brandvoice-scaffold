from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import sys
import traceback
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))

from utils import TikTokJSONProcessor, CSVGenerator, JSONLConverter
from clients.opus_client import OpusClipClient

app = FastAPI(title="BrandVoice API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for jobs (in production, use a database)
jobs_store = {}
uploaded_files = {}

class ProcessConfig(BaseModel):
    filename: str
    videosToProcess: int
    batchSize: int = 10
    parameterMode: str = "auto"
    language: str = "English"
    maxChar: int = 150
    style: str = ""
    confirmationMode: str = "interactive"

class VideoStatus(BaseModel):
    id: str
    title: str
    status: str
    currentStep: Optional[str] = None
    steps: Optional[Dict[str, Any]] = None
    transcript: Optional[str] = None
    description: Optional[str] = None
    viewCount: Optional[int] = None
    likeCount: Optional[int] = None
    commentCount: Optional[int] = None
    duration: Optional[int] = None
    transcriptLength: Optional[int] = None
    opusProjectId: Optional[str] = None
    clipsGenerated: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "BrandVoice API is running"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and validate JSON file"""
    logger.info(f"Upload request received for file: {file.filename}")
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / f"{file_id}_{file.filename}"
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Parse JSON to get metadata
        processor = TikTokJSONProcessor()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract video count
            videos = []
            if isinstance(data, dict):
                videos = data.get('videos', data.get('itemList', []))
            elif isinstance(data, list):
                videos = data
            
            total_videos = len(videos)
            
            # Check for existing videos
            csv_generator = CSVGenerator()
            # Extract channel name from filename (remove .json extension)
            channel_name = file.filename.replace('.json', '')
            existing_video_ids = csv_generator.get_existing_video_ids(channel_name)
            
            video_ids = [v.get('id', v.get('video', {}).get('id', '')) for v in videos]
            existing_count = sum(1 for vid in video_ids if vid in existing_video_ids)
            new_count = total_videos - existing_count
            
            # Store file info
            uploaded_files[file_id] = {
                'filename': file.filename,
                'path': str(file_path),
                'videos': videos
            }
            
            return {
                "fileId": file_id,
                "filename": file.filename,
                "totalVideos": total_videos,
                "existingVideos": existing_count,
                "newVideos": new_count
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON file")
            
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/api/process")
async def start_processing(config: ProcessConfig, background_tasks: BackgroundTasks):
    """Start processing a video job"""
    try:
        # Find the file by filename
        file_info = None
        file_id = None
        for fid, info in uploaded_files.items():
            if info['filename'] == config.filename:
                file_info = info
                file_id = fid
                break
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Create job
        job_id = str(uuid.uuid4())
        creator_name = config.filename.replace('.json', '').replace('input/', '')
        
        jobs_store[job_id] = {
            'jobId': job_id,
            'creatorName': creator_name,
            'status': 'processing',
            'progress': 0,
            'currentPhase': 'Initializing',
            'videos': [],
            'config': config.model_dump(),
            'fileInfo': file_info,
            'createdAt': datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(process_videos, job_id)
        
        return {
            "job_id": job_id,
            "creator_name": creator_name,
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting processing: {str(e)}")

async def process_videos(job_id: str):
    """Background task to process videos - performs all the same steps as main.py"""
    job = jobs_store[job_id]
    config = job['config']
    file_info = job['fileInfo']
    start_time = datetime.now()
    
    try:
        # Initialize processors
        processor = TikTokJSONProcessor()
        csv_generator = CSVGenerator()
        
        # Get API key from environment
        opus_api_key = os.getenv('OPUSCLIP_API_KEY')
        if not opus_api_key:
            raise Exception("OPUSCLIP_API_KEY not found in environment variables")
        
        opus_client = OpusClipClient(api_key=opus_api_key)
        
        # STEP 1: Parse videos from JSON
        job['currentPhase'] = 'Parsing videos from JSON'
        job['progress'] = 5
        
        # Process the JSON file to get structured video data
        videos = processor.process_json_file(file_info['path'])
        
        if not videos:
            raise Exception("No videos found in JSON file")
        
        # Limit to requested count
        if config['videosToProcess'] and config['videosToProcess'] < len(videos):
            videos = videos[:config['videosToProcess']]
        
        logger.info(f"Parsed {len(videos)} videos from JSON")
        
        # STEP 2: Deduplicate - check for existing videos
        job['currentPhase'] = 'Checking for duplicate videos'
        job['progress'] = 10
        
        channel_name = file_info['filename'].replace('.json', '')
        existing_video_ids = csv_generator.get_existing_video_ids(channel_name, 'output')
        
        # Filter out existing videos
        new_videos = []
        skipped_videos = []
        for video in videos:
            video_id = video['video_id']
            if video_id in existing_video_ids:
                skipped_videos.append(video)
            else:
                new_videos.append(video)
        
        if not new_videos:
            job['status'] = 'completed'
            job['progress'] = 100
            job['currentPhase'] = 'Complete - All videos already processed'
            job['summary'] = {
                'processed': 0,
                'skipped': len(skipped_videos),
                'totalTime': str(datetime.now() - start_time)
            }
            return
        
        logger.info(f"Processing {len(new_videos)} new videos, skipping {len(skipped_videos)} duplicates")
        
        total = len(new_videos)
        job['videos'] = []
        
        # STEP 3: Submit projects to OpusClip
        job['currentPhase'] = f'Submitting {total} projects to OpusClip'
        job['progress'] = 15
        
        project_submissions = []
        batch_size = config.get('batchSize', 10)
        
        for i in range(0, len(new_videos), batch_size):
            batch = new_videos[i:i + batch_size]
            
            for video in batch:
                video_id = video['video_id']
                video_url = video['video_url']
                
                # Create video status entry
                video_status = {
                    'id': video_id,
                    'title': video.get('description', 'Untitled')[:50],
                    'status': 'processing',
                    'currentStep': 'Submitting to OpusClip',
                    'description': video.get('description', ''),
                    'viewCount': video.get('view_count', 0),
                    'likeCount': video.get('like_count', 0),
                    'commentCount': video.get('comment_count', 0),
                    'duration': video.get('duration', 0),
                    'steps': {
                        'metadata': 'completed',
                        'submission': 'processing',
                        'transcript': 'pending',
                        'csv': 'pending'
                    }
                }
                job['videos'].append(video_status)
                
                try:
                    # Submit project to OpusClip
                    project_response = opus_client.submit_project(video_url)
                    project_id = project_response.get('projectId')
                    
                    if project_id:
                        video['project_id'] = project_id
                        video_status['opusProjectId'] = project_id
                        video_status['steps']['submission'] = 'completed'
                        project_submissions.append((video, video_status))
                        logger.info(f"✅ Submitted {video_id} → Project {project_id}")
                    else:
                        video_status['status'] = 'failed'
                        video_status['steps']['submission'] = 'failed'
                        video_status['currentStep'] = 'Failed to submit'
                        logger.error(f"❌ Failed to submit {video_id}")
                        
                except Exception as e:
                    video_status['status'] = 'failed'
                    video_status['steps']['submission'] = 'failed'
                    video_status['currentStep'] = f'Error: {str(e)}'
                    logger.error(f"❌ Error submitting {video_id}: {e}")
        
        if not project_submissions:
            raise Exception("No projects submitted successfully")
        
        job['progress'] = 20
        
        # STEP 4: Wait for projects and extract transcripts
        job['currentPhase'] = f'Processing {len(project_submissions)} videos (this may take 5-10 min per video)'
        
        async def wait_and_extract(video_tuple):
            video, video_status = video_tuple
            try:
                project_id = video.get('project_id')
                video_id = video.get('video_id')
                
                if not project_id:
                    return None
                
                video_status['currentStep'] = 'Waiting for OpusClip processing'
                video_status['steps']['transcript'] = 'processing'
                
                # Wait for completion
                loop = asyncio.get_event_loop()
                completed = await loop.run_in_executor(
                    None,
                    opus_client.wait_for_project_completion,
                    project_id,
                    600  # 10 minute timeout
                )
                
                if not completed:
                    video_status['status'] = 'failed'
                    video_status['steps']['transcript'] = 'failed'
                    video_status['currentStep'] = 'Timeout waiting for OpusClip'
                    logger.error(f"❌ Project {project_id} (video {video_id}) timed out")
                    return None
                
                # Get exportable clips
                video_status['currentStep'] = 'Extracting transcript from clips'
                exportable_clips = opus_client.get_exportable_clips(project_id)
                
                if not exportable_clips:
                    video_status['status'] = 'failed'
                    video_status['steps']['transcript'] = 'failed'
                    video_status['currentStep'] = 'No clips found'
                    logger.warning(f"⚠️ No exportable clips for project {project_id}")
                    return None
                
                video_status['clipsGenerated'] = len(exportable_clips)
                
                # Extract transcript from first clip
                first_clip = exportable_clips[0]
                screenplay = first_clip.get('screenplay', {})
                
                if not screenplay:
                    video_status['status'] = 'failed'
                    video_status['steps']['transcript'] = 'failed'
                    video_status['currentStep'] = 'No screenplay found'
                    logger.warning(f"⚠️ No screenplay in clip for project {project_id}")
                    return None
                
                transcript = opus_client.extract_enhanced_transcript_from_screenplay(screenplay)
                
                if transcript:
                    video['transcript'] = transcript
                    video['transcript_source'] = 'opusclip'
                    video_status['transcript'] = transcript
                    video_status['transcriptLength'] = len(transcript)
                    video_status['steps']['transcript'] = 'completed'
                    video_status['currentStep'] = 'Transcript extracted'
                    logger.info(f"✅ Extracted transcript for {video_id} ({len(transcript)} chars)")
                    return video
                else:
                    video_status['status'] = 'failed'
                    video_status['steps']['transcript'] = 'failed'
                    video_status['currentStep'] = 'Empty transcript'
                    logger.warning(f"⚠️ Empty transcript for {video_id}")
                    return None
                    
            except Exception as e:
                video_status['status'] = 'failed'
                video_status['steps']['transcript'] = 'failed'
                video_status['currentStep'] = f'Error: {str(e)[:50]}'
                logger.error(f"❌ Error processing {video.get('video_id')}: {e}")
                return None
        
        # Process all videos in parallel
        tasks = [wait_and_extract(vt) for vt in project_submissions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        videos_with_transcripts = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        if not videos_with_transcripts:
            raise Exception("No transcripts extracted successfully")
        
        logger.info(f"✅ Extracted {len(videos_with_transcripts)} transcripts")
        
        # Update all completed videos
        for video_status in job['videos']:
            if video_status['steps']['transcript'] == 'completed':
                video_status['status'] = 'completed'
                video_status['currentStep'] = None
                video_status['steps']['csv'] = 'completed'
        
        job['progress'] = 70
        
        # STEP 5: Generate CSV file
        job['currentPhase'] = 'Generating CSV file'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{job['creatorName']}_{timestamp}.csv"
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        csv_path = output_dir / csv_filename
        
        csv_generator.generate_csv(videos_with_transcripts, str(csv_path))
        logger.info(f"✅ Generated CSV: {csv_path}")
        
        job['progress'] = 80
        
        # STEP 6: AI Analysis for JSONL parameters
        job['currentPhase'] = 'Analyzing content with AI'
        
        suggested_language = config['language']
        suggested_max_char = config['maxChar']
        
        # Only run AI analysis if in auto mode
        if config['parameterMode'] == 'auto':
            try:
                from openai import OpenAI
                openai_api_key = os.getenv('OPENAI_API_KEY')
                
                if openai_api_key:
                    # Read sample of CSV data
                    import csv
                    sample_data = []
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for i, row in enumerate(reader):
                            if i >= 5:
                                break
                            sample_data.append({
                                'description': row.get('description', '')[:200],
                                'hashtags': row.get('hashtags', ''),
                                'transcript': row.get('transcript', '')[:300]
                            })
                    
                    if sample_data:
                        # Prepare prompt
                        newline = '\n'
                        sample_text = newline.join([f"Video {i+1}:{newline}  Description: {v['description']}{newline}  Hashtags: {v['hashtags']}{newline}  Transcript: {v['transcript'][:150]}..." for i, v in enumerate(sample_data)])
                        
                        prompt = f"""Analyze the following TikTok video data and suggest optimal parameters:

Sample Data:
{sample_text}

Suggest:
1. Primary language (e.g., English, Spanish, etc.)
2. Optimal max character limit for descriptions (100-300)

Respond in JSON format:
{{
  "language": "detected language",
  "max_char": recommended_number,
  "reasoning": "brief explanation"
}}"""
                        
                        client = OpenAI(api_key=openai_api_key)
                        response = client.chat.completions.create(
                            model="gpt-4",
                            max_tokens=1024,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        response_text = response.choices[0].message.content
                        
                        # Parse JSON response
                        import re
                        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                        if json_match:
                            response_json = json.loads(json_match.group(1))
                        else:
                            response_json = json.loads(response_text)
                        
                        suggested_language = response_json.get('language', suggested_language)
                        suggested_max_char = response_json.get('max_char', suggested_max_char)
                        
                        logger.info(f"🤖 AI suggested: {suggested_language}, {suggested_max_char} chars")
            except Exception as e:
                logger.warning(f"⚠️ AI analysis failed: {e}")
        
        job['progress'] = 85
        
        # STEP 7: Convert to JSONL training data
        job['currentPhase'] = 'Converting to JSONL training data'
        
        converter = JSONLConverter(
            language=suggested_language,
            max_char=suggested_max_char,
            style=config.get('style', '')
        )
        
        jsonl_dir = Path('training_data')
        jsonl_dir.mkdir(exist_ok=True)
        jsonl_filename = f"{job['creatorName']}_{timestamp}.jsonl"
        jsonl_path = jsonl_dir / jsonl_filename
        
        num_examples = converter.convert_csv_to_jsonl(str(csv_path), str(jsonl_path))
        logger.info(f"✅ Generated JSONL: {jsonl_path} ({num_examples} examples)")
        
        # STEP 8: Complete
        job['status'] = 'completed'
        job['progress'] = 100
        job['currentPhase'] = 'Complete'
        job['csvFilename'] = csv_filename
        job['jsonlFilename'] = jsonl_filename
        
        elapsed_time = datetime.now() - start_time
        minutes = int(elapsed_time.total_seconds() / 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_str = f"{minutes}m {seconds}s"
        
        job['summary'] = {
            'processed': len(videos_with_transcripts),
            'skipped': len(skipped_videos),
            'totalTime': time_str,
            'trainingExamples': num_examples
        }
        
        logger.info(f"✅ Job {job_id} completed successfully in {time_str}")
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = str(e)
        job['currentPhase'] = f'Error: {str(e)}'
        logger.error(f"❌ Error processing job {job_id}: {e}")
        logger.error(traceback.format_exc())

@app.get("/api/progress/{job_id}")
async def get_progress(job_id: str):
    """Get job progress"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    
    return {
        "jobId": job_id,
        "status": job['status'],
        "progress": job['progress'],
        "currentPhase": job['currentPhase'],
        "videos": job['videos'],
        "aiAnalysisReady": job.get('aiAnalysisReady', False),
        "summary": job.get('summary'),
        "csvFilename": job.get('csvFilename'),
        "jsonlFilename": job.get('jsonlFilename'),
        "estimatedTimeRemaining": "45 minutes"
    }

@app.get("/api/recent-creators")
async def get_recent_creators():
    """Get recent creators from output directory"""
    try:
        creators = []
        output_dir = Path('output')
        training_dir = Path('training_data')
        
        if output_dir.exists():
            csv_files = sorted(list(output_dir.glob('*.csv')), key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Group by creator name
            creator_data = {}
            for csv_file in csv_files:
                name_parts = csv_file.stem.split('_')
                if len(name_parts) >= 2:
                    creator_name = name_parts[0]
                    
                    if creator_name not in creator_data:
                        creator_data[creator_name] = {
                            'name': creator_name.title(),
                            'videoCount': 0,
                            'csvFiles': [],
                            'jsonlFiles': [],
                            'latestCsv': None,
                            'latestJsonl': None
                        }
                    
                    # Count videos in CSV
                    try:
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            video_count = max(0, len(lines) - 1)  # Exclude header
                            creator_data[creator_name]['videoCount'] += video_count
                    except:
                        pass
                    
                    creator_data[creator_name]['csvFiles'].append(csv_file.name)
                    
                    # Find matching JSONL file
                    jsonl_file = training_dir / f"{csv_file.stem}.jsonl"
                    if jsonl_file.exists():
                        creator_data[creator_name]['jsonlFiles'].append(jsonl_file.name)
                    
                    # Set latest files (first one since sorted by modification time)
                    if creator_data[creator_name]['latestCsv'] is None:
                        creator_data[creator_name]['latestCsv'] = csv_file.name
                        if jsonl_file.exists():
                            creator_data[creator_name]['latestJsonl'] = jsonl_file.name
            
            # Convert to list and calculate real stats
            import csv as csv_module
            for creator_name, data in creator_data.items():
                # Calculate actual views and likes from latest CSV
                total_views = 0
                total_likes = 0
                if data['latestCsv']:
                    try:
                        csv_path = output_dir / data['latestCsv']
                        with open(csv_path, 'r', encoding='utf-8') as f:
                            reader = csv_module.DictReader(f)
                            for row in reader:
                                try:
                                    total_views += int(row.get('view_count', 0) or 0)
                                    total_likes += int(row.get('like_count', 0) or 0)
                                except (ValueError, TypeError):
                                    pass
                    except Exception as e:
                        logger.error(f"Error reading stats from {data['latestCsv']}: {e}")
                
                creators.append({
                    'name': data['name'],
                    'videoCount': data['videoCount'],
                    'csvFilename': data['latestCsv'],
                    'jsonlFilename': data['latestJsonl'],
                    'stats': {
                        'totalViews': total_views,
                        'totalLikes': total_likes
                    }
                })
        
        return {"creators": creators[:10]}  # Return top 10
        
    except Exception as e:
        logger.error(f"Error getting recent creators: {e}")
        logger.error(traceback.format_exc())
        return {"creators": []}

@app.get("/api/creator/{creator_name}")
async def get_creator_details(creator_name: str):
    """Get details for a specific creator"""
    try:
        output_dir = Path('output')
        training_dir = Path('training_data')
        
        # Find CSV files for this creator
        csv_files = sorted(
            [f for f in output_dir.glob(f"{creator_name.lower()}_*.csv")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        latest_csv = csv_files[0]
        latest_jsonl = training_dir / f"{latest_csv.stem}.jsonl"
        
        # Read video data from CSV
        import csv
        videos = []
        with open(latest_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                videos.append({
                    'id': row.get('video_id', ''),
                    'title': row.get('description', 'Untitled')[:100],
                    'viewCount': int(row.get('view_count', 0)) if row.get('view_count', '').isdigit() else 0,
                    'likeCount': int(row.get('like_count', 0)) if row.get('like_count', '').isdigit() else 0,
                    'commentCount': int(row.get('comment_count', 0)) if row.get('comment_count', '').isdigit() else 0,
                    'duration': int(row.get('duration', 0)) if row.get('duration', '').isdigit() else 0,
                    'transcript': row.get('transcript', ''),
                    'transcriptLength': len(row.get('transcript', ''))
                })
        
        return {
            'creatorName': creator_name.title(),
            'csvFilename': latest_csv.name,
            'jsonlFilename': latest_jsonl.name if latest_jsonl.exists() else None,
            'videos': videos,
            'summary': {
                'processed': len(videos),
                'skipped': 0,
                'totalTime': 'N/A'
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting creator details: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting creator details: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download output file"""
    try:
        # Check in output directory
        file_path = Path('output') / filename
        if not file_path.exists():
            # Check in training_data directory
            file_path = Path('training_data') / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@app.get("/api/preview/{filename}")
async def preview_file(filename: str):
    """Get preview of output file"""
    try:
        # Check in output directory
        file_path = Path('output') / filename
        if not file_path.exists():
            # Check in training_data directory
            file_path = Path('training_data') / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # For CSV files
        if filename.endswith('.csv'):
            import csv
            rows = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 10:  # Limit to 10 rows for preview
                        break
                    rows.append(row)
            
            return {
                "type": "csv",
                "rows": rows,
                "totalRows": len(rows),
                "previewLimit": 10
            }
        
        # For JSONL files
        elif filename.endswith('.jsonl'):
            samples = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 5:  # Limit to 5 samples for preview
                        break
                    try:
                        samples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return {
                "type": "jsonl",
                "samples": samples,
                "totalSamples": len(samples),
                "previewLimit": 5
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
    except Exception as e:
        logger.error(f"Error previewing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error previewing file: {str(e)}")

@app.get("/api/view/{filename}")
async def view_file(filename: str, format: str = "table"):
    """View full file contents"""
    try:
        # Check in output directory
        file_path = Path('output') / filename
        if not file_path.exists():
            # Check in training_data directory
            file_path = Path('training_data') / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # For CSV files - return as HTML table
        if filename.endswith('.csv') and format == "table":
            import csv
            rows = []
            headers = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                for row in reader:
                    rows.append(row)
            
            # Generate HTML table
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{filename}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; position: sticky; top: 0; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .container {{ max-width: 100%; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <h1>{filename}</h1>
                <p>Total rows: {len(rows)}</p>
                <div class="container">
                    <table>
                        <thead>
                            <tr>
                                {''.join(f'<th>{h}</th>' for h in headers)}
                            </tr>
                        </thead>
                        <tbody>
                            {''.join('<tr>' + ''.join(f'<td>{row.get(h, "")}</td>' for h in headers) + '</tr>' for row in rows)}
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            """
            
            return HTMLResponse(content=html)
        
        # For JSONL files - return formatted samples
        elif filename.endswith('.jsonl') and format == "samples":
            samples = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        samples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # Generate HTML for JSONL
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{filename}</title>
                <style>
                    body {{ font-family: 'Monaco', 'Courier New', monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }}
                    h1 {{ color: #4CAF50; }}
                    .sample {{ background: #252526; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #3e3e42; }}
                    .sample-header {{ color: #4CAF50; font-weight: bold; margin-bottom: 10px; }}
                    pre {{ margin: 0; white-space: pre-wrap; word-wrap: break-word; }}
                </style>
            </head>
            <body>
                <h1>{filename}</h1>
                <p>Total samples: {len(samples)}</p>
                {''.join(f'<div class="sample"><div class="sample-header">Sample {i+1}</div><pre>{json.dumps(sample, indent=2, ensure_ascii=False)}</pre></div>' for i, sample in enumerate(samples))}
            </body>
            </html>
            """
            
            return HTMLResponse(content=html)
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type or format")
        
    except Exception as e:
        logger.error(f"Error viewing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error viewing file: {str(e)}")

@app.get("/api/files/output")
async def list_output_files():
    """List all files in output directory"""
    try:
        output_dir = Path('output')
        if not output_dir.exists():
            return {"files": []}
        
        files = []
        for file_path in sorted(output_dir.glob('*.csv'), key=lambda x: x.stat().st_mtime, reverse=True):
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "type": "csv"
            })
        
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing output files: {e}")
        return {"files": []}

@app.get("/api/files/training")
async def list_training_files():
    """List all files in training_data directory"""
    try:
        training_dir = Path('training_data')
        if not training_dir.exists():
            return {"files": []}
        
        files = []
        for file_path in sorted(training_dir.glob('*.jsonl'), key=lambda x: x.stat().st_mtime, reverse=True):
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "type": "jsonl"
            })
        
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing training files: {e}")
        return {"files": []}

@app.get("/api/channel/{channel_name}")
async def get_channel_data(channel_name: str):
    """Get all data for a specific channel from input, output, and training_data directories"""
    try:
        channel_name_lower = channel_name.lower()
        
        # Input files
        input_dir = Path('input')
        input_files = []
        if input_dir.exists():
            for file_path in input_dir.glob(f'{channel_name_lower}*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        videos = []
                        if isinstance(data, dict):
                            videos = data.get('videos', data.get('itemList', []))
                        elif isinstance(data, list):
                            videos = data
                        
                        input_files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "type": "json",
                            "videoCount": len(videos)
                        })
                except Exception as e:
                    logger.error(f"Error reading input file {file_path}: {e}")
        
        # Output files
        output_dir = Path('output')
        output_files = []
        if output_dir.exists():
            for file_path in sorted(output_dir.glob(f'{channel_name_lower}_*.csv'), key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    import csv
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        
                        total_views = sum(int(row.get('view_count', 0) or 0) for row in rows if row.get('view_count', '').isdigit())
                        total_likes = sum(int(row.get('like_count', 0) or 0) for row in rows if row.get('like_count', '').isdigit())
                        
                        output_files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "type": "csv",
                            "videoCount": len(rows),
                            "totalViews": total_views,
                            "totalLikes": total_likes
                        })
                except Exception as e:
                    logger.error(f"Error reading output file {file_path}: {e}")
        
        # Training data files
        training_dir = Path('training_data')
        training_files = []
        if training_dir.exists():
            for file_path in sorted(training_dir.glob(f'{channel_name_lower}_*.jsonl'), key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    # Count examples in JSONL
                    example_count = 0
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                example_count += 1
                    
                    training_files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "type": "jsonl",
                        "exampleCount": example_count
                    })
                except Exception as e:
                    logger.error(f"Error reading training file {file_path}: {e}")
        
        if not input_files and not output_files and not training_files:
            raise HTTPException(status_code=404, detail=f"No data found for channel '{channel_name}'")
        
        return {
            "channelName": channel_name.title(),
            "input": input_files,
            "output": output_files,
            "training": training_files,
            "summary": {
                "totalInputFiles": len(input_files),
                "totalOutputFiles": len(output_files),
                "totalTrainingFiles": len(training_files),
                "totalVideos": sum(f.get('videoCount', 0) for f in output_files)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel data: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting channel data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

