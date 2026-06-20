"""
routes_preview.py — Preview video and SRT download endpoints.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from workers.pipeline import jobs

router = APIRouter(prefix="/api", tags=["preview"])


@router.get("/jobs/{job_id}/preview")
async def get_preview(
    job_id: str,
    position: str = Query("bottom", regex="^(top|bottom)$"),
    font_size: int = Query(24, ge=16, le=48),
):
    """Stream the preview video with burned subtitles.

    If position/font_size differ from current preview, triggers regeneration.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")

    if not job.preview_path or not Path(job.preview_path).exists():
        raise HTTPException(404, "Preview not yet generated")

    # TODO: Check if position/font_size changed → regenerate

    return FileResponse(
        job.preview_path,
        media_type="video/mp4",
        filename=f"preview_{job_id}.mp4",
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
