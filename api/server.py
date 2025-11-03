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
            'config': config.dict(),
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
    """Background task to process videos"""
    job = jobs_store[job_id]
    config = job['config']
    file_info = job['fileInfo']
    
    try:
        # Initialize processors
        processor = TikTokJSONProcessor()
        csv_generator = CSVGenerator()
        
        # Parse videos
        job['currentPhase'] = 'Parsing videos'
        videos_data = file_info['videos'][:config['videosToProcess']]
        
        # Get existing video IDs
        # Extract channel name from filename (remove .json extension)
        channel_name = file_info['filename'].replace('.json', '')
        existing_video_ids = csv_generator.get_existing_video_ids(channel_name)
        
        # Filter new videos
        new_videos = []
        for video in videos_data:
            video_id = video.get('id', video.get('video', {}).get('id', ''))
            if video_id not in existing_video_ids:
                new_videos.append(video)
        
        total = len(new_videos)
        job['videos'] = []
        
        # Process each video
        for idx, video_data in enumerate(new_videos):
            video_id = video_data.get('id', video_data.get('video', {}).get('id', ''))
            video_desc = video_data.get('desc', video_data.get('description', 'Untitled'))
            
            video_status = {
                'id': video_id,
                'title': video_desc[:50],
                'status': 'processing',
                'currentStep': 'Parsing metadata',
                'steps': {
                    'metadata': 'processing',
                    'transcript': 'pending',
                    'csv': 'pending'
                }
            }
            
            job['videos'].append(video_status)
            job['currentPhase'] = f'Processing video {idx + 1}/{total}'
            
            # Step 1: Parse metadata
            await asyncio.sleep(0.5)  # Simulate work
            video_status['steps']['metadata'] = 'completed'
            video_status['steps']['metadataDuration'] = '1s'
            video_status['currentStep'] = 'Extracting transcript'
            video_status['steps']['transcript'] = 'processing'
            
            # Step 2: Extract transcript (this would take longer in reality)
            # Simulating OpusClip processing time
            video_status['steps']['transcriptMessage'] = 'Submitting to OpusClip...'
            await asyncio.sleep(2)  # Simulate OpusClip processing
            
            video_status['steps']['transcript'] = 'completed'
            video_status['steps']['transcriptDuration'] = '8m 23s'
            video_status['currentStep'] = 'Generating CSV entry'
            video_status['steps']['csv'] = 'processing'
            
            # Step 3: Generate CSV entry
            await asyncio.sleep(0.3)
            video_status['steps']['csv'] = 'completed'
            video_status['steps']['csvDuration'] = '1s'
            video_status['status'] = 'completed'
            video_status['currentStep'] = None
            
            # Update progress
            job['progress'] = int(((idx + 1) / total) * 100)
        
        # Generate CSV file
        job['currentPhase'] = 'Generating CSV file'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{job['creatorName']}_{timestamp}.csv"
        csv_path = Path('output') / csv_filename
        csv_path.parent.mkdir(exist_ok=True)
        
        # Save CSV (simplified version)
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write('video_id,video_url,transcript,description,hashtags,view_count,like_count,comment_count,share_count,duration,transcript_source\n')
            for video in job['videos']:
                f.write(f'{video["id"]},,Sample transcript,Sample description,,1000000,50000,1000,500,45,opusclip\n')
        
        # AI Analysis (if in auto mode)
        if config['parameterMode'] == 'auto':
            job['currentPhase'] = 'AI Content Analysis'
            job['aiAnalysisReady'] = True
            await asyncio.sleep(2)  # Simulate AI analysis
        
        # Generate JSONL
        job['currentPhase'] = 'Generating training data'
        jsonl_filename = f"{job['creatorName']}_{timestamp}.jsonl"
        jsonl_path = Path('training_data') / jsonl_filename
        jsonl_path.parent.mkdir(exist_ok=True)
        
        # Save JSONL (simplified version)
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for video in job['videos']:
                example = {
                    'contents': [
                        {
                            'role': 'user',
                            'parts': [{'text': f'{{"language": "{config["language"]}", "text": "Sample transcript", "max_char": {config["maxChar"]}}}'}]
                        },
                        {
                            'role': 'model',
                            'parts': [{'text': '{"description": "Sample description", "hashtags": ["tag1", "tag2"]}'}]
                        }
                    ]
                }
                f.write(json.dumps(example) + '\n')
        
        # Complete
        job['status'] = 'completed'
        job['progress'] = 100
        job['currentPhase'] = 'Complete'
        job['csvFilename'] = csv_filename
        job['jsonlFilename'] = jsonl_filename
        job['summary'] = {
            'processed': len(new_videos),
            'skipped': len(videos_data) - len(new_videos),
            'totalTime': '1h 23m'
        }
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = str(e)
        logger.error(f"Error processing job {job_id}: {e}")
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
            
            # Convert to list
            for creator_name, data in creator_data.items():
                creators.append({
                    'name': data['name'],
                    'videoCount': data['videoCount'],
                    'csvFilename': data['latestCsv'],
                    'jsonlFilename': data['latestJsonl'],
                    'stats': {
                        'totalViews': 5000000,  # Mock data
                        'totalLikes': 250000
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

