"""
preview.py — Burn subtitles onto video for preview.

Uses MoviePy CompositeVideoClip for full-quality output.
"""

from typing import List

from models.schemas import Segment


async def generate_preview(
    video_path: str,
    segments: List[Segment],
    position: str = "bottom",
    font_size: int = 24,
) -> str:
    """Generate a preview video with burned-in subtitles.

    Args:
        video_path: Path to the original video file.
        segments: Timed subtitle segments.
        position: Subtitle position — "top", "bottom", or custom margin %.
        font_size: Font size in pixels (16–48).

    Returns:
        Path to the generated preview video file.
    """
    raise NotImplementedError("Phase 9: preview generation")
