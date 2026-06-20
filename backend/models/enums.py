"""
enums.py — Enumerations used across the application.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Tracks the current stage of a video processing job."""

    PENDING = "pending"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    TRANSCRIBING = "transcribing"
    TRANSLITERATING = "transliterating"
    MERGING = "merging"
    GENERATING_SRT = "generating_srt"
    GENERATING_PREVIEW = "generating_preview"
    COMPLETE = "complete"
    FAILED = "failed"


class EditActionType(str, Enum):
    """Supported segment edit operations."""

    UPDATE = "update"
    SPLIT = "split"
    MERGE = "merge"
    DELETE = "delete"
