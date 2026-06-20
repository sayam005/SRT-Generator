"""
audio.py — Extract audio from video and chunk into overlapping segments.

Uses MoviePy for audio extraction and ffmpeg for chunking.
"""

from typing import List

from models.schemas import ChunkInfo


async def extract_audio(video_path: str) -> str:
    """Extract audio track from a video file as WAV.

    Args:
        video_path: Absolute path to the input video file.

    Returns:
        Path to the extracted WAV file.
    """
    raise NotImplementedError("Phase 2: audio extraction")


async def chunk_with_overlap(
    wav_path: str,
    chunk_minutes: int = 8,
    overlap_seconds: int = 30,
) -> List[ChunkInfo]:
    """Split a WAV file into overlapping chunks using ffmpeg.

    Chunk 0: 0–480s, Chunk 1: 450–930s, etc. (30s overlap).

    Args:
        wav_path: Path to the source WAV file.
        chunk_minutes: Duration of each chunk in minutes.
        overlap_seconds: Overlap between consecutive chunks in seconds.

    Returns:
        List of ChunkInfo with paths and timing metadata.
    """
    raise NotImplementedError("Phase 2: audio chunking")
