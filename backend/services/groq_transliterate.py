"""
groq_transliterate.py — Convert Devanagari transcript to Hinglish (Roman script).

Uses Groq LLM with batched segment processing (~20 segments per call).
"""

import json
import asyncio
from typing import List

from groq import AsyncGroq
from config import settings
from models.schemas import Segment

# Groq System Prompt
SYSTEM_PROMPT = """You are a Hinglish transcript cleaner and TRANSLITERATOR.

CRITICAL INSTRUCTION:
You MUST convert ALL Devanagari script (Hindi) into Roman script (English alphabet).
Example: "लेकिन" -> "lekin", "थोड़ा" -> "thoda", "क्या" -> "kya"

RULES:
1. TRANSLITERATE EVERYTHING: Output must contain ONLY Roman/Latin characters. NO Devanagari allowed.
2. Keep English words exactly as spoken.
3. Maintain the natural code-mixed flow.
4. Fix punctuation and spelling.

SEGMENTATION RULES:
5. Each segment should be a complete thought (not cut mid-word or mid-phrase).
6. Merge very short adjacent fragments (1-2 words) into one coherent segment.
7. If a segment exceeds ~12 words, split at the most natural break point
   (commas, conjunctions like "aur"/"and"/"but", or after a complete clause).
8. Each segment should fit one line on screen (~60-70 characters).
9. Preserve exact start/end timestamps from the original segments.

OUTPUT FORMAT:
You must return only a valid JSON object in this exact schema, and nothing else.
The input may contain more segments than the output — you may merge short ones.
{ "segments": [{"start": 0.0, "end": 3.5, "text": "Namaste dosto, aaj hum seekhenge"}] }"""

# Initialize Groq client lazily
def get_groq_client():
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    return AsyncGroq(api_key=settings.GROQ_API_KEY)

async def _process_batch(segments: List[Segment]) -> List[Segment]:
    """Process a single batch of segments via Groq."""
    if not segments:
        return []

    input_json = {"segments": [s.model_dump() for s in segments]}
    client = get_groq_client()
    
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",  #TODO change this to 70b verstile variant  # Recommended for json/translation tasks
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transliterate these segments:\n{json.dumps(input_json)}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,  # Low temp for deterministic translation
    )

    try:
        content = response.choices[0].message.content
        result_json = json.loads(content)
        
        # We don't blindly trust the LLM timestamps, we only trust the LLM text.
        # We map the text back using the start timestamp or index to be safe.
        out_segments = []
        for i, raw_seg in enumerate(segments):
            # Try to find corresponding segment in LLM output by index or time
            llm_text = orig_text = raw_seg.text
            if i < len(result_json.get("segments", [])):
                llm_text = result_json["segments"][i].get("text", orig_text)
                
            out_segments.append(
                Segment(
                    start=raw_seg.start,
                    end=raw_seg.end,
                    text=llm_text
                )
            )
        return out_segments
    except Exception as e:
        # Fallback to original if something fails in parsing
        print(f"Groq batch parsing error: {e}")
        return segments


async def transliterate_chunks(
    chunk_segments: List[List[Segment]],
) -> List[List[Segment]]:
    """Transliterate Devanagari segments to Hinglish using Groq.

    Batches ~20 segments per API call to stay within token limits.
    Preserves original timestamps; only text is transliterated.

    Args:
        chunk_segments: List of segment lists (one per chunk).

    Returns:
        Same structure with text converted to Roman script.
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
        
    BATCH_SIZE = 20
    final_chunks = []
    
    for segments in chunk_segments:
        chunk_tasks = []
        # Split chunk into batches
        for i in range(0, len(segments), BATCH_SIZE):
            batch = segments[i:i + BATCH_SIZE]
            chunk_tasks.append(_process_batch(batch))
            
        # Run all batches for this chunk concurrently
        batch_results = await asyncio.gather(*chunk_tasks)
        
        # Flatten back into a single list of segments for this chunk
        flat_chunk = [seg for batch in batch_results for seg in batch]
        final_chunks.append(flat_chunk)
        
    return final_chunks
