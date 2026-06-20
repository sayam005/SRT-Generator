"""
groq_transliterate.py — Convert Devanagari transcript to Hinglish (Roman script).

Uses Groq LLM with batched segment processing (~20 segments per call).
"""

from typing import List

from models.schemas import Segment


async def transliterate_chunks(
    chunk_segments: List[List[Segment]],
) -> List[List[Segment]]:
    """Transliterate Devanagari segments to Hinglish using Groq.

    Batches ~20 segments per API call to stay within token limits.
    Preserves original timestamps; only text is transliterated.

    Args:
        chunk_segments: List of segment lists (one per chunk), text in Devanagari.

    Returns:
        Same structure with text converted to Roman script (Hinglish).
    """
    raise NotImplementedError("Phase 4: Groq transliteration")
