"""
srt.py — Generate SRT subtitle files from segments.
"""

from typing import List

from models.schemas import Segment


def generate_srt(segments: List[Segment]) -> bytes:
    """Generate an SRT file from a list of segments.

    Format per entry:
        index
        HH:MM:SS,mmm --> HH:MM:SS,mmm
        text

    Args:
        segments: List of timed subtitle segments.

    Returns:
        SRT file content as UTF-8 bytes.
    """
    raise NotImplementedError("Phase 6: SRT generation")
