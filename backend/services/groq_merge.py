"""
groq_merge.py — Merge overlapping transcript chunks into a continuous timeline.

Uses Groq LLM for overlap-aware pairwise deduplication.
"""

from typing import List

from models.schemas import Segment


async def merge_chunks(
    chunk_segments: List[List[Segment]],
    overlap_seconds: int = 30,
) -> List[Segment]:
    """Merge overlapping chunk segments into a single continuous segment list.

    Processes pairwise: merge chunk[i] + chunk[i+1] using the overlap region
    as context for deduplication. Iterates until all chunks are merged.

    Args:
        chunk_segments: List of segment lists from transliteration.
        overlap_seconds: Duration of overlap between chunks.

    Returns:
        Single merged list of Segments with no duplicates.
    """
    raise NotImplementedError("Phase 5: Groq merge")
