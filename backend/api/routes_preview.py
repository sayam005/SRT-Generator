"""
routes_preview.py — Serve original video and SRT download endpoints.

Subtitles are rendered on the frontend as an overlay; no burning needed.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from workers.pipeline import jobs

router = APIRouter(prefix="/api", tags=["preview"])


@router.get("/jobs/{job_id}/preview")
async def get_preview(job_id: str):
    """Stream the original video for frontend subtitle overlay."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")

    if not job.video_path or not Path(job.video_path).exists():
        raise HTTPException(404, "Video not available")

    return FileResponse(
        job.video_path,
        media_type="video/mp4",
        filename=f"video_{job_id}.mp4",
    )


@router.get("/jobs/{job_id}/srt")
async def download_srt(job_id: str):
    """Download the generated SRT file."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")

    if not job.srt_path or not Path(job.srt_path).exists():
        raise HTTPException(404, "SRT not yet generated")

    return FileResponse(
        job.srt_path,
        media_type="text/plain",
        filename=f"subtitles_{job_id}.srt",
    )
