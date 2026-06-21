"""
preview.py — Burn subtitles onto video for preview.

Uses MoviePy 2.1.1 API with Pillow-based TextClip (no ImageMagick needed).
"""

import asyncio
import sys
from pathlib import Path
from typing import List

from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
)
from moviepy.video.tools.subtitles import SubtitlesClip

from config import settings
from models.schemas import Segment
from services.srt import generate_srt

# Resolve font path — use full .ttf path for Pillow compatibility
if sys.platform == "win32":
    _FONT = "C:/Windows/Fonts/arial.ttf"
elif sys.platform == "darwin":
    _FONT = "/System/Library/Fonts/Helvetica.ttc"
else:
    _FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


async def generate_preview(
    job_id: str,
    video_path: str,
    segments: List[Segment],
    position: str = "bottom",
    font_size: int = 24,
) -> str:
    """Generate a preview video with burned-in subtitles.

    Args:
        job_id: The job ID for pathing.
        video_path: Path to the original video file.
        segments: Timed subtitle segments.
        position: Subtitle position — "top", "bottom".
        font_size: Font size in pixels.

    Returns:
        Path to the generated preview MP4 file.
    """
    output_path = Path(settings.temp_path) / job_id / f"preview_{job_id}.mp4"

    # Write a temp SRT file for MoviePy to consume
    srt_path = Path(settings.temp_path) / job_id / "temp_preview.srt"
    srt_path.write_bytes(generate_srt(segments))

    loop = asyncio.get_event_loop()

    def _burn():
        video = VideoFileClip(video_path)

        def make_sub(txt):
            return TextClip(
                font=_FONT,
                text=txt,
                font_size=font_size,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(video.w - 40, None),
            )

        try:
            subtitles = SubtitlesClip(str(srt_path), make_textclip=make_sub)

            if position == "bottom":
                pos_y = ("center", video.h - int(font_size * 3))
            else:
                pos_y = ("center", 50)

            result = CompositeVideoClip([
                video,
                subtitles.with_position(pos_y),
            ])

            result.write_videofile(
                str(output_path),
                fps=video.fps,
                preset="ultrafast",
                threads=4,
                logger=None,
            )
        except Exception as e:
            raise RuntimeError(f"Preview generation failed: {e}")
        finally:
            video.close()
            if srt_path.exists():
                srt_path.unlink()

    await loop.run_in_executor(None, _burn)
    return str(output_path)
