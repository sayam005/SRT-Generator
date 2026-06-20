"""
routes_edit.py — Apply edits to subtitle segments.
"""

from fastapi import APIRouter, HTTPException

from models.schemas import EditRequest, JobResponse
from workers.pipeline import jobs, save_job
from api.routes_transcribe import _job_to_response
from services.editor import apply_edits
from services.srt import generate_srt
from pathlib import Path

router = APIRouter(prefix="/api", tags=["editing"])


@router.patch("/jobs/{job_id}/segments", response_model=JobResponse)
async def edit_segments(job_id: str, edit_request: EditRequest):
    """Apply edit actions to a job's segments and regenerate SRT.

    Accepts a batch of update/split/merge/delete actions.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")

    if not job.segments:
        raise HTTPException(400, "No segments to edit yet")

    # Apply text/timing edits
    if edit_request.actions:
        job.segments = apply_edits(job.segments, edit_request.actions)

    # Regenerate SRT
    srt_bytes = generate_srt(job.segments)
    if job.srt_path:
        Path(job.srt_path).write_bytes(srt_bytes)

    save_job(job)

    return _job_to_response(job)
