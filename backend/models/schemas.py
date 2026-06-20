"""
schemas.py — Pydantic models for all data structures.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import EditActionType, JobStatus


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

class Segment(BaseModel):
    """A single subtitle segment with timing and text."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Subtitle text content")


class ChunkInfo(BaseModel):
    """Metadata for one audio chunk."""

    index: int = Field(..., description="Chunk index (0-based)")
    path: str = Field(..., description="Path to the chunk audio file")
    start_sec: float = Field(..., description="Start time in the original audio")
    end_sec: float = Field(..., description="End time in the original audio")


# ---------------------------------------------------------------------------
# Job model
# ---------------------------------------------------------------------------

class VideoJob(BaseModel):
    """Full state for a video processing job."""

    job_id: str
    status: JobStatus = JobStatus.PENDING
    progress_percent: int = 0
    current_stage: str = "pending"
    error: Optional[str] = None
    language: str = Field(default="hi", description="Transcription language: 'hi' (Hinglish) or 'en' (English)")

    video_path: str = ""
    audio_path: str = ""
    chunks: List[ChunkInfo] = []
    segments: List[Segment] = []

    srt_path: str = ""
    preview_path: str = ""

    # Subtitle display settings
    subtitle_position: str = "bottom"
    font_size: int = 24

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# API request / response models
# ---------------------------------------------------------------------------

class EditAction(BaseModel):
    """A single edit action applied to a segment."""

    index: int = Field(..., description="Index of the segment to edit")
    action: EditActionType
    text: Optional[str] = None
    start: Optional[float] = None
    end: Optional[float] = None
    split_at: Optional[float] = Field(
        None, description="Timestamp to split at (for split action)"
    )


class EditRequest(BaseModel):
    """Batch of edit actions sent from the frontend."""

    actions: List[EditAction] = []


class JobResponse(BaseModel):
    """Serialized job state returned by the API."""

    job_id: str
    status: JobStatus
    progress_percent: int
    current_stage: str
    error: Optional[str] = None
    segments: List[Segment] = []
    srt_url: Optional[str] = None
    preview_url: Optional[str] = None
    subtitle_position: str = "bottom"
    font_size: int = 24
    language: str = "hi"
    created_at: datetime
    updated_at: datetime
