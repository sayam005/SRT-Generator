"""
audio.py — Extract audio from video and chunk into overlapping segments.

Uses MoviePy for audio extraction and ffmpeg for chunking.
"""

import asyncio
import math
import subprocess
from pathlib import Path
from typing import List

from moviepy import VideoFileClip

from config import settings
from models.schemas import ChunkInfo


async def extract_audio(video_path: str, output_dir: str) -> str:
    """Extract audio track from a video file as WAV.

    Runs MoviePy in a thread executor to avoid blocking the event loop.

    Args:
        video_path: Absolute path to the input video file.
        output_dir: Directory to save the extracted WAV.

    Returns:
        Path to the extracted WAV file.
    """
    wav_path = str(Path(output_dir) / "audio.wav")

    def _extract():
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(
            wav_path,
            codec="pcm_s16le",  # standard WAV
            fps=16000,          # 16kHz is enough for speech
            logger=None,        # suppress MoviePy progress bar
        )
        clip.close()

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _extract)

    return wav_path


async def chunk_with_overlap(
    wav_path: str,
    output_dir: str,
    chunk_minutes: int | None = None,
    overlap_seconds: int | None = None,
) -> List[ChunkInfo]:
    """Split a WAV file into overlapping chunks using ffmpeg.

    Example with defaults (8 min chunks, 30s overlap):
        Chunk 0: 0–480s
        Chunk 1: 450–930s
        Chunk 2: 900–1380s
        ...

    Args:
        wav_path: Path to the source WAV file.
        output_dir: Directory to save chunk files.
        chunk_minutes: Duration of each chunk in minutes (default from config).
        overlap_seconds: Overlap between consecutive chunks (default from config).

    Returns:
        List of ChunkInfo with paths and timing metadata.
    """
    chunk_min = chunk_minutes or settings.MAX_CHUNK_MINUTES
    overlap_sec = overlap_seconds or settings.OVERLAP_SECONDS
    chunk_sec = chunk_min * 60  # 8 min = 480s

    # Get total duration via ffprobe
    total_duration = await _get_duration(wav_path)

    chunks: List[ChunkInfo] = []
    chunk_index = 0
    start = 0.0

    while start < total_duration:
        # Duration for this chunk (may be shorter for the last one)
        duration = min(chunk_sec, total_duration - start)

        # Skip tiny leftover chunks (< 5 seconds)
        if duration < 5 and chunk_index > 0:
            break

        chunk_path = str(Path(output_dir) / f"chunk_{chunk_index:03d}.wav")

        # Use ffmpeg to extract the chunk (fast, no re-encoding with -c copy)
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(duration),
            "-i", wav_path,
            "-c", "copy",
            chunk_path,
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"ffmpeg chunk {chunk_index} failed: {stderr.decode()}"
            )

        chunks.append(
            ChunkInfo(
                index=chunk_index,
                path=chunk_path,
                start_sec=start,
                end_sec=start + duration,
            )
        )

        chunk_index += 1
        # Next chunk starts (chunk_duration - overlap) seconds later
        start += chunk_sec - overlap_sec

    return chunks


async def _get_duration(audio_path: str) -> float:
    """Get the duration of an audio file in seconds using ffprobe.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Duration in seconds.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

    return float(stdout.decode().strip())
