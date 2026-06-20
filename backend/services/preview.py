"""
preview.py — Burn subtitles onto video for preview.

Uses MoviePy CompositeVideoClip for full-quality output.
"""

import sys
from pathlib import Path
from typing import List

from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
)
from moviepy.video.tools.subtitles import SubtitlesClip

from config import settings
from models.schemas import Segment
from services.srt import generate_srt


async def generate_preview(
    job_id: str,
    video_path: str,
    segments: List[Segment],
    position: str = "bottom",
    font_size: int = 24,
) -> str:
    """Generate a preview video with burned-in subtitles.

    Since we're on Windows, we'll use a basic TextClip approach 
    that doesn't strictly depend on ImageMagick if possible, or 
    we'll catch the ImageMagick error gracefully.

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
    
    # We write a temp SRT file just for Moviepy to consume
    srt_path = Path(settings.temp_path) / job_id / "temp_preview.srt"
    srt_path.write_bytes(generate_srt(segments))
    
    # Run MoviePy generation in a thread
    import asyncio
    loop = asyncio.get_event_loop()
    
    def _burn():
        video = VideoFileClip(video_path)
        
        # Generator function for TextClips
        def generator(txt):
            # We add a subtle dark background to subtitles for readability
            bg = ColorClip(
                size=(video.w, int(font_size * 2)), 
                color=(0,0,0)
            ).with_opacity(0.6)
            
            txt_clip = TextClip(
                font="Arial", 
                text=txt, 
                font_size=font_size, 
                color='white',
                stroke_color='black',
                stroke_width=1,
                method='caption',
                size=(video.w - 40, None)
            )
            
            # Center the text on the bg
            composite = CompositeVideoClip([
                bg,
                txt_clip.with_position('center')
            ])
            return composite

        try:
            # Create subtitles clip using the generator
            subtitles = SubtitlesClip(str(srt_path), generator)
            
            # Position it
            pos_y = ('center', video.h - int(font_size * 3)) if position == "bottom" else ('center', 50)
            
            result = CompositeVideoClip([
                video, 
                subtitles.with_position(pos_y)
            ])

            # Write the result (using minimal settings for faster preview)
            result.write_videofile(
                str(output_path),
                fps=video.fps,
                preset="ultrafast",
                threads=4,
                logger=None
            )
        except Exception as e:
            # If ImageMagick isn't installed, Moviepy SubtitlesClip will fail.
            # In that case, we'll fallback to not generating a preview and throwing an error.
            raise RuntimeError(f"Preview generation failed (is ImageMagick installed?): {str(e)}")
        finally:
            video.close()
            # Clean up temp SRT
            if srt_path.exists():
                srt_path.unlink()

    await loop.run_in_executor(None, _burn)
    return str(output_path)
