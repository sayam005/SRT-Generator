"""
srt.py — Generate SRT subtitle files from segments.
"""

from typing import List
from models.schemas import Segment
from utils.time import seconds_to_srt


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
    lines = []
    for i, seg in enumerate(segments, start=1):
        start_srt = seconds_to_srt(seg.start)
        end_srt = seconds_to_srt(seg.end)
        
        lines.append(str(i))
        lines.append(f"{start_srt} --> {end_srt}")
        # Ensure we don't have existing newlines breaking the SRT format
        clean_text = seg.text.replace("\n", " ").strip()
        lines.append(clean_text)
        lines.append("")  # Empty line between segments
        
    # Join with CRLF for strict SRT compliance (though LF usually works too)
    content = "\r\n".join(lines)
    return content.encode("utf-8")
