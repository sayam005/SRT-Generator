"""
routes_preview.py — Preview video and SRT download endpoints.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from workers.pipeline import jobs, save_job
from services.preview import generate_preview

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

    # If position/font_size changed, regenerate
    if job.subtitle_position != position or job.font_size != font_size:
        # Trigger regeneration await
        try:
            new_path = await generate_preview(
                job_id=job.job_id,
                video_path=job.video_path,
                segments=job.segments,
                position=position,
                font_size=font_size
            )
            job.preview_path = new_path
            job.subtitle_position = position
            job.font_size = font_size
            save_job(job)
        except Exception as e:
            raise HTTPException(500, f"Failed to regenerate preview: {e}")

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
