"""
deepgram.py — Transcribe audio files using Deepgram Nova-2.

Handles both single-file and parallel chunk transcription.
"""

import asyncio
from typing import List

from deepgram import DeepgramClient, PrerecordedOptions, FileSource

from config import settings
from models.schemas import Segment


# Initialize the client (will automatically use DEEPGRAM_API_KEY from env if available)
# Since we load it via pydantic-settings, we explicitly pass it in case it's not exported
try:
    deepgram_client = DeepgramClient(settings.DEEPGRAM_API_KEY)
except Exception:
    pass  # We'll fail on actual calls if not set


async def transcribe_file(audio_path: str, language: str = "hi") -> List[Segment]:
    """Transcribe a single audio file via Deepgram.

    Uses model="nova-2" with utterances and punctuation.

    Args:
        audio_path: Path to the audio file.
        language: Language code ("hi" for Hindi/Hinglish, "en" for English).

    Returns:
        List of Segments with Devanagari/English text and timestamps.
    """
    if not settings.DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY is not set")

    # We run the deepgram call in a sync executor because DeepgramClient
    # has a sync method `transcribe_file` that blocks. There is an async client
    # but the python SDK is constantly changing. We'll use the sync one safely.
    
    def _transcribe():
        with open(audio_path, "rb") as audio_file:
            payload: FileSource = {"buffer": audio_file}
            options = PrerecordedOptions(
                model="nova-2",
                language=language,
                smart_format=True,
                utterances=True,
                punctuate=True,
                diarize=False,
            )
            response = deepgram_client.listen.rest.v("1").transcribe_file(
                payload, options
            )
            return response

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _transcribe)

    # Parse response into Segments
    segments = []
    
    # Deepgram returns utterances if requested
    try:
        # Depending on SDK version, response might be a dict or an object array
        results = response.get("results", {}) if isinstance(response, dict) else getattr(response, "results", None)
        utterances = getattr(results, "utterances", None) or results.get("utterances", []) if results else []
        for u in utterances:
            # Handle both dicts and python objects returned by Deepgram
            transcript = u.get("transcript", "") if isinstance(u, dict) else getattr(u, "transcript", "")
            start = u.get("start", 0.0) if isinstance(u, dict) else getattr(u, "start", 0.0)
            end = u.get("end", 0.0) if isinstance(u, dict) else getattr(u, "end", 0.0)

            text = transcript.strip()
            if text:
                segments.append(Segment(start=start, end=end, text=text))
    except Exception as e:
        print(f"Failed to parse Deepgram utterances: {e}")
        import traceback; traceback.print_exc()
        # Fallback if utterances fail but we have words
        pass

    return segments


async def transcribe_chunks_parallel(
    chunk_paths: List[str], language: str = "hi"
) -> List[List[Segment]]:
    """Transcribe multiple audio chunks in parallel.

    Uses asyncio.gather to run all Deepgram calls concurrently.

    Args:
        chunk_paths: List of paths to chunk audio files.
        language: Target language.

    Returns:
        List of segment lists, one per chunk.
    """
    tasks = [transcribe_file(path, language) for path in chunk_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_results = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            raise RuntimeError(f"Deepgram failed on chunk {i}: {str(res)}") from res
        final_results.append(res)
        
    return final_results
