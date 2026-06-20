"""
deepgram.py — Transcribe audio files using Deepgram Nova-2.

Handles both single-file and parallel chunk transcription.
"""

import asyncio
from typing import List

from models.schemas import Segment


async def transcribe_file(audio_path: str) -> List[Segment]:
    """Transcribe a single audio file via Deepgram.

    Uses model="nova-2", language="hi", with utterances and punctuation.

    Args:
        audio_path: Path to the audio file.

    Returns:
        List of Segments with Devanagari text and timestamps.
    """
    raise NotImplementedError("Phase 3: Deepgram transcription")


async def transcribe_chunks_parallel(
    chunk_paths: List[str],
) -> List[List[Segment]]:
    """Transcribe multiple audio chunks in parallel.

    Uses asyncio.gather to run all Deepgram calls concurrently.

    Args:
        chunk_paths: List of paths to chunk audio files.

    Returns:
        List of segment lists, one per chunk.
    """
    raise NotImplementedError("Phase 3: parallel transcription")
