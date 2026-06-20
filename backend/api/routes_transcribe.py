"""
routes_transcribe.py — Upload video and poll job status.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from config import settings
from models.schemas import VideoJob, JobResponse
from models.enums import JobStatus
from workers.pipeline import jobs, save_job

router = APIRouter(prefix="/api", tags=["transcribe"])


@router.post("/jobs", response_model=JobResponse)
async def create_job(file: UploadFile = File(...)):
    """Upload a video file and start a transcription job.

    Saves the file to the temp directory, creates a job record,
    and kicks off the background pipeline.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(400, "No file provided")

    allowed_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(400, f"Unsupported format: {ext}. Use: {allowed_exts}")

    # Save uploaded file
    job_id = uuid.uuid4().hex[:12]
    job_dir = settings.temp_path / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    video_path = job_dir / f"input{ext}"

    content = await file.read()
    video_path.write_bytes(content)

    # Create job record
    job = VideoJob(job_id=job_id, video_path=str(video_path))
    save_job(job)

    # Start pipeline in background
    import asyncio
    from workers.pipeline import process_job

    asyncio.create_task(process_job(job_id, str(video_path)))

    return _job_to_response(job)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Poll job status, get segments, preview/srt URLs when complete."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    return _job_to_response(job)


def _job_to_response(job: VideoJob) -> JobResponse:
    """Convert internal VideoJob to API response."""
    srt_url = f"/api/jobs/{job.job_id}/srt" if job.srt_path else None
    preview_url = f"/api/jobs/{job.job_id}/preview" if job.preview_path else None

    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        progress_percent=job.progress_percent,
        current_stage=job.current_stage,
        error=job.error,
        segments=job.segments,
        srt_url=srt_url,
        preview_url=preview_url,
        subtitle_position=job.subtitle_position,
        font_size=job.font_size,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
