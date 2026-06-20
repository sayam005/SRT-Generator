"""
groq_merge.py — Merge overlapping transcript chunks into a continuous timeline.

Uses Groq LLM for overlap-aware pairwise deduplication.
"""

import json
from typing import List

from groq import AsyncGroq
from config import settings
from models.schemas import Segment

def get_groq_client():
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    return AsyncGroq(api_key=settings.GROQ_API_KEY)

MERGE_PROMPT = """You are merging two adjacent transcript chunks (A and B) with a 30-second overlap.
Chunk A and Chunk B have overlapping content at the boundary. Your task is to produce a single continuous segment list.

RULES:
1. Remove duplicate content in the overlap region.
2. Output ONLY the merged list of segments.
3. Do NOT change the text content, just stitch them smartly.

OUTPUT FORMAT:
You must return only a valid JSON object in this exact schema, and nothing else.
{ "segments": [{"start": 0.0, "end": 3.5, "text": "..."}] }"""


async def _merge_pair(
    chunk_a: List[Segment], 
    chunk_b: List[Segment], 
    overlap_seconds: int
) -> List[Segment]:
    """Merge two chunks intelligently using Groq."""
    if not chunk_a: return chunk_b
    if not chunk_b: return chunk_a
    
    a_end = chunk_a[-1].end
    b_start = chunk_b[0].start
    
    # We only need to send the LLM the tail of A and the head of B
    # to find the deduplication point, to save tokens.
    overlap_start = a_end - overlap_seconds - 10
    overlap_end = b_start + overlap_seconds + 10
    
    # Isolate segments near the boundary
    a_boundary = [s for s in chunk_a if s.start >= overlap_start]
    b_boundary = [s for s in chunk_b if s.end <= overlap_end]
    
    # The safe ones that don't need merging
    a_safe = [s for s in chunk_a if s.start < overlap_start]
    b_safe = [s for s in chunk_b if s.end > overlap_end]
    
    input_json = {
        "chunk_a_tail": [s.model_dump() for s in a_boundary],
        "chunk_b_head": [s.model_dump() for s in b_boundary]
    }
    
    client = get_groq_client()
    
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant", #TODO change this to 70b verstile variant 
        messages=[
            {"role": "system", "content": MERGE_PROMPT},
            {"role": "user", "content": json.dumps(input_json)}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    
    try:
        content = response.choices[0].message.content
        result_json = json.loads(content)
        
        merged_boundary = [Segment(**s) for s in result_json.get("segments", [])]
        
        # Reconstruct the full list: Safe A -> Merged Boundary -> Safe B
        return a_safe + merged_boundary + b_safe
        
    except Exception as e:
        print(f"Groq merge failed: {e}. Falling back to simple concatenation.")
        # Fallback: just concatenate and hope for the best
        # Filter B to only include things starting strictly after A ends
        b_filtered = [s for s in chunk_b if s.start > a_end]
        return chunk_a + b_filtered


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
    if not chunk_segments:
        return []
        
    if len(chunk_segments) == 1:
        return chunk_segments[0]
        
    # Merge iteratively left-to-right
    current = chunk_segments[0]
    for nxt in chunk_segments[1:]:
        current = await _merge_pair(current, nxt, overlap_seconds)
        
    return current
