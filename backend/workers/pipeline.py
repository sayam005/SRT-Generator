"""
pipeline.py — Job orchestrator that runs the full processing pipeline.

Manages state transitions: pending → extracting → transcribing →
transliterating → merging → generating_srt → generating_preview → complete.
"""

import traceback
from datetime import datetime

from config import settings
from models.schemas import VideoJob
from models.enums import JobStatus
from services import audio, deepgram, groq_transliterate, groq_merge, srt, preview


# In-memory job store — simple dict, persisted to JSON per job
jobs: dict[str, VideoJob] = {}


def get_job(job_id: str) -> VideoJob | None:
    """Retrieve a job by ID from the in-memory store."""
    return jobs.get(job_id)


def save_job(job: VideoJob) -> None:
    """Save/update a job in the in-memory store and persist to JSON."""
    import json
    from pathlib import Path

    job.updated_at = datetime.now()
    jobs[job.job_id] = job

    # Persist to disk
    job_file = Path(settings.jobs_path) / f"{job.job_id}.json"
    job_file.write_text(job.model_dump_json(indent=2), encoding="utf-8")


async def process_job(job_id: str, video_path: str) -> None:
    """Run the full transcription pipeline for a job.

    Orchestrates each service in sequence with error handling.
    Updates job status/progress at each stage so the frontend can poll.

    Args:
        job_id: Unique job identifier.
        video_path: Path to the uploaded video file.
    """
    job = get_job(job_id)
    if not job:
        return

    try:
        # Phase 1: Extract audio
        job.status = JobStatus.EXTRACTING
        job.current_stage = "Extracting audio..."
        job.progress_percent = 5
        save_job(job)
        job_dir = str(settings.temp_path / job_id)
        audio_path = await audio.extract_audio(video_path, job_dir)
        job.audio_path = audio_path
        save_job(job)

        # Phase 2: Chunk audio
        job.status = JobStatus.CHUNKING
        job.current_stage = "Chunking audio..."
        job.progress_percent = 15
        save_job(job)
        chunks = await audio.chunk_with_overlap(audio_path, job_dir)
        job.chunks = chunks
        save_job(job)

        # Phase 3: Transcribe
        job.status = JobStatus.TRANSCRIBING
        job.current_stage = "Transcribing with Deepgram..."
        job.progress_percent = 25
        save_job(job)
        
        chunk_paths = [c.path for c in chunks]
        chunk_segments = await deepgram.transcribe_chunks_parallel(
            chunk_paths, language=job.language
        )

        # Phase 4: Transliterate (Conditional)
        if job.language == "hi":
            job.status = JobStatus.TRANSLITERATING
            job.current_stage = "Transliterating to Hinglish..."
            job.progress_percent = 50
            save_job(job)
            transliterated_chunks = await groq_transliterate.transliterate_chunks(chunk_segments)
        else:
            # English mode -> already in Roman, skip transliteration
            transliterated_chunks = chunk_segments

        # Phase 5: Merge overlaps
        job.status = JobStatus.MERGING
        job.current_stage = "Merging overlapping chunks..."
        job.progress_percent = 65
        save_job(job)
        
        # Merge overlapping chunk segments into a single timeline
        final_segments = await groq_merge.merge_chunks(
            transliterated_chunks, 
            overlap_seconds=settings.OVERLAP_SECONDS
        )
        job.segments = final_segments
        save_job(job)

        # Phase 6: Generate SRT
        job.status = JobStatus.GENERATING_SRT
        job.current_stage = "Generating SRT file..."
        job.progress_percent = 80
        save_job(job)
        
        srt_bytes = srt.generate_srt(final_segments)
        srt_path = Path(settings.temp_path) / job_id / f"{job_id}.srt"
        srt_path.write_bytes(srt_bytes)
        
        job.srt_path = str(srt_path)
        save_job(job)

        # Phase 7: Generate preview
        job.status = JobStatus.GENERATING_PREVIEW
        job.current_stage = "Burning subtitles onto video..."
        job.progress_percent = 90
        save_job(job)
        
        try:
            preview_path = await preview.generate_preview(
                job_id=job.job_id,
                video_path=video_path,
                segments=final_segments,
                position=job.subtitle_position,
                font_size=job.font_size
            )
            job.preview_path = preview_path
        except Exception as e:
            # If preview fails (e.g. no ImageMagick), we don't fail the whole job
            print(f"Preview failed: {e}")
            job.error = "SRT generated successfully, but preview generation failed: " + str(e)
            
        save_job(job)

        # Done
        job.status = JobStatus.COMPLETE
        job.current_stage = "Complete"
        job.progress_percent = 100
        save_job(job)

    except Exception as e:
        job.status = JobStatus.FAILED
        job.current_stage = "Failed"
        job.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        save_job(job)
