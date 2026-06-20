# Planning Hinglish SRT subtitle generator tool

**Session ID:** ses_12b8e5d82ffesFLPl3Vl1AwcYW
**Created:** 6/17/2026, 12:47:57 PM
**Updated:** 6/17/2026, 10:22:25 PM

---

## User

I’m planning to make a tool that can generate SRT files for my editing software to handle captions and subtitles.

The process would involve uploading a recorded video of myself speaking in a mix of Hindi and English. The tool should then translate that into Hinglish subtitles and generate an SRT file that I can upload to software like Premiere Pro or After Effects.

I want to take an iterative approach. I don’t need it to be production-level with a lot of features yet; I just need a bare-bones tool right now because I have an urgent need to generate these files.

Here is my current thinking for the stack:

Backend:
I already know Python and Flask, but I might learn Fast API for this. Python seems like a good choice so I can use modules like MoviePy for previews and other features in future
Frontend:
I don’t really know JavaScript, but I think using React and coding a simple, bare-bones interface would be enough for now.
Transcription/Translation:
I’m planning to use Deepgram to produce the subtitles into devnagri script and then have groq lm convert it into hinglish const prompt = `You are a Hinglish transcript cleaner and TRANSLITERATOR.

CRITICAL INSTRUCTION:
You MUST convert ALL Devanagari script (Hindi) into Roman script (English alphabet).
Example: "लेकिन" -> "lekin", "थोड़ा" -> "thoda", "क्या" -> "kya"

RULES:
1. TRANSLITERATE EVERYTHING: Output must contain ONLY Roman/Latin characters. NO Devanagari allowed.
2. Keep English words exactly as spoken.
3. Maintain the natural code-mixed flow.
4. Fix punctuation and spelling.

INPUT: Raw transcript (contains Devanagari)
OUTPUT: JSON object with a "segments" key containing the array of corrected segments.

Format: { "segments": [{"start": 0.0, "end": 3.5, "text": "Namaste dosto, aaj hum seekhenge"}] }

Raw transcript:
${rawTranscriptText}`;
I want to start with this basic application and then make it more complex later on. For now, I just need a working tool to create my SRT files, and I’ll add customization further down the road.

What do you think? 

---

## Assistant (Plan · Nemotron 3 Ultra Free · 1105.2s)

_Thinking:_

The user wants to build a tool for generating SRT files from video recordings with Hindi/English mixed speech. They want Hinglish subtitles (Hindi transliterated to Roman script). They've outlined their stack preferences and have a prompt for the translation step.

This is a planning phase - I need to analyze their requirements and create a plan. Let me think through the architecture:

1. **Backend**: Python (Flask or FastAPI) - they know Flask, considering FastAPI
2. **Frontend**: React (bare-bones, they don't know JS well)
3. **Transcription**: Deepgram API
4. **Translation/Transliteration**: Groq LLM with their prompt
5. **Output**: SRT file generation

Key components needed:
- Video upload endpoint
- Audio extraction (MoviePy)
- Deepgram transcription with timestamps
- Groq LLM processing for Hinglish conversion
- SRT file generation
- Frontend for upload and download

Since they want iterative/bare-bones first, I should focus on MVP. Let me ask some clarifying questions to make the plan solid.

Your plan makes sense for an MVP. A few clarifying questions to shape the implementation:


**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "Do you have Deepgram and Groq API keys ready, or do you need help with setup?",
      "header": "API Keys",
      "options": [
        {
          "label": "Ready to go",
          "description": "I have both API keys"
        },
        {
          "label": "Need guidance",
          "description": "Help me get/set up API keys"
        }
      ]
    },
    {
      "question": "For the frontend, do you want a React app served separately, or a simple HTML page served by Flask/FastAPI?",
      "header": "Frontend approach",
      "options": [
        {
          "label": "React + Vite",
          "description": "Separate frontend (more learning, standard)"
        },
        {
          "label": "Simple HTML/JS",
          "description": "Single-file template served by backend (simpler, faster)"
        }
      ]
    },
    {
      "question": "How will you deploy/run this initially?",
      "header": "Deployment",
      "options": [
        {
          "label": "Local only",
          "description": "Run locally on my machine"
        },
        {
          "label": "Cloud (Render/Vercel/etc)",
          "description": "Deploy to a cloud platform"
        }
      ]
    },
    {
      "question": "Should the tool support batch processing multiple videos, or single video at a time for now?",
      "header": "Batch support",
      "options": [
        {
          "label": "Single video",
          "description": "One upload at a time (simpler)"
        },
        {
          "label": "Multiple videos",
          "description": "Queue multiple files"
        }
      ]
    }
  ]
}
```

**Output:**
```
User has answered your questions: "Do you have Deepgram and Groq API keys ready, or do you need help with setup?"="Need guidance", "For the frontend, do you want a React app served separately, or a simple HTML page served by Flask/FastAPI?"="React + Vite", "How will you deploy/run this initially?"="Local only", "Should the tool support batch processing multiple videos, or single video at a time for now?"="Single video". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · Nemotron 3 Ultra Free · 139.2s)

_Thinking:_

Good, now I have clarity. Let me create a comprehensive plan:

- API keys: Need guidance on Deepgram and Groq setup
- Frontend: React + Vite (separate)
- Deployment: Local only for now
- Batch: Single video at a time

Let me draft the plan now.

Here's your MVP plan:

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  React UI   │────▶│  FastAPI     │────▶│  Deepgram   │────▶│  Groq    │
│  (Vite)     │     │  Backend     │     │  Transcribe │     │  Hinglish│
└─────────────┘     └──────┬───────┘     └─────────────┘     └────┬─────┘
                           │                                        │
                           ▼                                        ▼
                    ┌──────────────┐                        ┌─────────────┐
                    │  MoviePy     │                        │  SRT Gen    │
                    │  (audio ext) │                        │  (output)   │
                    └──────────────┘                        └─────────────┘
```

---

## Project Structure

```
hinglish-srt/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── services/
│   │   ├── deepgram.py      # Transcription client
│   │   ├── groq.py          # Hinglish conversion client
│   │   ├── audio.py         # MoviePy audio extraction
│   │   └── srt.py           # SRT file generation
│   ├── models.py            # Pydantic models
│   ├── config.py            # Settings (API keys via env)
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadZone.jsx
│   │   │   ├── Progress.jsx
│   │   │   └── Result.jsx
│   │   └── api.js           # API calls
│   └── index.css
└── .env.example
```

---

## Implementation Steps

### 1. Backend Setup (FastAPI)
- Initialize FastAPI with CORS for React dev server
- Config via `pydantic-settings` + `.env`
- Endpoints:
  - `POST /api/transcribe` - upload video, return SRT
  - `GET /api/health` - health check

### 2. Audio Extraction (`services/audio.py`)
- Use `moviepy.editor.VideoFileClip` to extract audio to WAV
- Save to temp file, cleanup after

### 3. Deepgram Integration (`services/deepgram.py`)
- Use `deepgram-sdk` Python package
- Request: `model="nova-2", language="hi", smart_format=True, utterances=True`
- Returns segments with `start`, `end`, `transcript` (Devanagari)

### 4. Groq Integration (`services/groq.py`)
- Use `groq` Python package
- Your prompt template → send segments, get Hinglish JSON
- Parse/validate response

### 5. SRT Generation (`services/srt.py`)
- Format: `index\nstart --> end\ntext\n\n`
- Convert seconds to `HH:MM:SS,mmm`

### 6. Frontend (React + Vite)
- Simple drag-drop upload zone
- Progress polling / websocket for status
- Download SRT button
- Minimal styling (Tailwind or plain CSS)

### 7. API Key Setup Guidance
- **Deepgram**: Sign up at console.deepgram.com → API Keys → create key
- **Groq**: Sign up at console.groq.com → API Keys → create key
- Add to `.env`:
  ```
  DEEPGRAM_API_KEY=your_key
  GROQ_API_KEY=your_key
  ```

---

## Key Decisions

| Choice | Rationale |
|--------|-----------|
| FastAPI over Flask | Better async, auto-docs, type safety |
| Single-video MVP | Simpler state, faster iteration |
| Local-only | No deploy complexity yet |
| React + Vite | You want to learn React; Vite is fast |

---

## Risks to Watch

1. **Deepgram Hindi accuracy** - may need `model="nova-2-general"` or language detection
2. **Groq rate limits** - free tier has limits; batch segments in one call
3. **Large video files** - consider chunking or ffmpeg pre-processing later
4. **Timestamp drift** - ensure Deepgram utterances align with Groq output segments

---

Want me to proceed with implementation? I can start with the backend scaffold and core services, then the frontend.

---

## User

i also wanted to tell you about some additional details about the working like lets suppose i have a 10 min video so i upload that video and the audio part goes to deepgram to like properly convert longer videos we can implement like lets divide 10 min video into 5min batches and send it to different deepograms and their respective differrent groq and then implement another grog layer on top which can combine them together and see that one batch is 1 to 5min and the other is 5 to 10 min so it should combine accordingly not like both batches are 1 to 5min uk and i checked ig deepgram has limit to 10 mins around on native models so i think we should keep that batch cut at 8 mins around like break the transciption at 8 mins and then follow the procedure i told u and file limit is i think around 250mb which is i think good for a audio file as it will be only be sent to deepgram not the mp4 file right? an like moivepy will burn the subs in real time to show me on right side and we'll have the editing options on left side what do u think and i want the whole application to be as modular as it can be as i am not that experienced in programming so i'll need guidance in every step so what do u think commander

---

## Assistant (Plan · Nemotron 3 Ultra Free · 1152.9s)

_Thinking:_

The user is sharing more detailed requirements and wants me to plan the implementation. They're in "plan mode" so I should only read/analyze and create a comprehensive plan. Let me break down their requirements:

1. **Video chunking**: 10-min video → split into ~8-min chunks (Deepgram limit)
2. **Parallel processing**: Each chunk → Deepgram → Groq (Hinglish conversion)
3. **Combining layer**: Another Groq call to merge chunks with proper timestamp alignment
4. **MoviePy preview**: Burn subtitles in real-time for preview on right side
5. **Editing options**: Left side for editing
6. **Modular architecture**: Clean separation for learning/guidance
7. **File size**: Audio only to Deepgram (not MP4), ~250MB limit

Key technical considerations:
- Chunking at sentence boundaries, not hard time cuts
- Timestamp offset handling when merging
- Async/parallel processing for speed
- Real-time preview with MoviePy
- Modular service layer design

I should create a detailed plan covering:
1. Architecture with clear module boundaries
2. Chunking strategy (sentence-aware)
3. Parallel processing pipeline
4. Merge/align strategy
5. Preview system
6. Frontend-backend communication
7. Step-by-step implementation order

Let me ask some clarifying questions first to refine the plan.

Great detailed requirements. This is a solid plan with some nice architectural touches. Let me clarify a few things before finalizing the implementation plan:


**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "For chunking: should we split at exact 8-min marks, or detect silence/sentence boundaries near 8-min to avoid cutting mid-sentence?",
      "header": "Chunk strategy",
      "options": [
        {
          "label": "Sentence-aware (recommended)",
          "description": "Find nearest sentence end/start around 8-min mark"
        },
        {
          "label": "Hard time cuts",
          "description": "Exact 8-min splits, simpler but may cut words"
        }
      ]
    },
    {
      "question": "How should the merge layer handle overlapping/duplicate content at chunk boundaries?",
      "header": "Merge strategy",
      "options": [
        {
          "label": "Groq merge with context",
          "description": "Send adjacent chunk overlaps to Groq for smart dedup"
        },
        {
          "label": "Timestamp-based trim",
          "description": "Hard trim at exact boundary, drop overlaps"
        }
      ]
    },
    {
      "question": "For real-time preview: should MoviePy render the full video with burned subs, or generate a lightweight preview (lower res/fps)?",
      "header": "Preview quality",
      "options": [
        {
          "label": "Full quality",
          "description": "Exact output, slower"
        },
        {
          "label": "Lightweight proxy",
          "description": "720p/15fps, fast iteration"
        }
      ]
    },
    {
      "question": "Editing panel on left - what editing operations do you need initially?",
      "header": "Edit operations",
      "options": [
        {
          "label": "Text edit + timing adjust",
          "description": "Modify subtitle text, shift start/end times"
        },
        {
          "label": "Split/merge segments",
          "description": "Break or combine subtitle blocks"
        },
        {
          "label": "All of the above",
          "description": "Full subtitle editor"
        }
      ]
    }
  ]
}
```

**Output:**
```
User has answered your questions: "For chunking: should we split at exact 8-min marks, or detect silence/sentence boundaries near 8-min to avoid cutting mid-sentence?"="how would it do it, how will it identify gaps in speech without even sending to deepgram first as we would need to first split the mp3 into 2 parts to even send to deepgram right", "How should the merge layer handle overlapping/duplicate content at chunk boundaries?"="Groq merge with context", "For real-time preview: should MoviePy render the full video with burned subs, or generate a lightweight preview (lower res/fps)?"="Full quality", "Editing panel on left - what editing operations do you need initially?"="3 + also the option to shift the position or burned subs for better preview". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · Nemotron 3 Ultra Free · 183.2s)

_Thinking:_

The user raised a great point about chunking - we can't detect sentence boundaries without transcription first. This is a chicken-and-egg problem. Let me think about the solution:

1. **Option A**: Split audio blindly at ~8 min, accept some mid-sentence cuts, then let Groq merge layer fix it
2. **Option B**: First pass - send full audio to Deepgram (if under 10 min limit), get timestamps, then chunk intelligently
3. **Option C**: Use a lightweight VAD (Voice Activity Detection) locally to find silence gaps, then split there

For videos >10 min, Option A is pragmatic. For ≤10 min, we can do single-pass.

The user wants:
- Groq merge with context (smart dedup)
- Full quality preview
- Full editor: text edit, timing adjust, split/merge segments, position shift for burned subs

Let me now create a comprehensive plan. I'll structure it with:
1. Architecture overview
2. Module breakdown
3. Data flow
4. Implementation phases
5. Key technical decisions
6. File structure
7. Step-by-step implementation order

I should present this clearly for the user to review before we start coding.

Excellent catch on the chunking chicken-and-egg problem. Here's the pragmatic solution:

**Chunking Strategy**: 
- **≤10 min**: Single Deepgram call (within native limit)
- **>10 min**: Blind split at ~8 min with 30-sec overlap → Groq merge layer handles dedup using the overlap as context

This avoids needing VAD or first-pass transcription. The overlap gives Groq enough context to seamlessly stitch.

---

## Comprehensive Implementation Plan

### 1. Architecture - Modular Service Layer

```
backend/
├── main.py                      # FastAPI app, routes, dependency injection
├── config.py                    # Pydantic Settings (.env)
├── models/
│   ├── __init__.py
│   ├── schemas.py               # Pydantic: VideoJob, Segment, SRTEntry, EditAction
│   └── enums.py                 # JobStatus, LanguageCode
├── services/
│   ├── __init__.py
│   ├── audio.py                 # MoviePy: extract, chunk, overlap
│   ├── deepgram.py              # Transcribe (single + batch)
│   ├── groq_transliterate.py    # Devanagari → Hinglish per chunk
│   ├── groq_merge.py            # Merge chunks with overlap context
│   ├── srt.py                   # Generate SRT from segments
│   ├── preview.py               # MoviePy: burn subs, generate proxy
│   └── editor.py                # Apply edits to segments
├── workers/
│   ├── __init__.py
│   └── pipeline.py              # Orchestrate: chunk → transcribe → transliterate → merge → srt
├── api/
│   ├── __init__.py
│   ├── routes_transcribe.py     # POST /api/jobs, GET /api/jobs/{id}
│   ├── routes_edit.py           # PATCH /api/jobs/{id}/segments
│   └── routes_preview.py        # GET /api/jobs/{id}/preview
└── utils/
    ├── __init__.py
    ├── time.py                  # SRT time formatting, offset math
    └── file.py                  # Temp file management, cleanup
```

### 2. Core Data Flow

```
Upload Video
     │
 ├─▶ audio.extract_audio() → temp.wav
 │
 ├─▶ audio.chunk_with_overlap(wav, chunk_min=8, overlap_sec=30)
 │      → [chunk_0.wav, chunk_1.wav, ...]
 │
 ├─▶ PARALLEL: deepgram.transcribe(chunk) for each
 │      → [segments_0, segments_1, ...]  (Devanagari + timestamps)
 │
 ├─▶ PARALLEL: groq_transliterate.chunk(segments) for each
 │      → [hinglish_0, hinglish_1, ...]  (Roman script)
 │
 ├─▶ groq_merge.merge_chunks([hinglish_0, hinglish_1, ...], overlap_sec=30)
 │      → merged_segments (continuous timestamps, deduped)
 │
 ├─▶ srt.generate(merged_segments) → output.srt
 │
 ├─▶ preview.generate(video_path, merged_segments) → preview.mp4
 │
 └─▶ Return job_id, srt_url, preview_url
```

### 3. Key Technical Details

| Component | Implementation |
|-----------|----------------|
| **Chunking** | `ffmpeg -ss 0 -t 480 -i input.wav chunk_0.wav` + 30s overlap via `-ss 450` |
| **Deepgram** | `nova-2`, `language=hi`, `utterances=true`, `smart_format=true`, `punctuate=true` |
| **Groq Transliterate** | Your prompt + batch segments (max ~3000 tokens/call) |
| **Groq Merge** | Prompt: "Merge adjacent segments. Remove duplicates in overlap. Preserve timestamps. Output same JSON schema." |
| **SRT Format** | `HH:MM:SS,mmm --> HH:MM:SS,mmm` with proper escaping |
| **Preview** | `MoviePy: CompositeVideoClip([video, SubtitlesClip(srt)])` → write_videofile |
| **Editor State** | In-memory job store (dict) + persisted JSON for reload |

### 4. API Contract

```python
# POST /api/jobs
# Request: multipart/form-data (video file)
# Response: { "job_id": "uuid", "status": "processing" }

# GET /api/jobs/{job_id}
# Response: { "job_id", "status", "srt_url", "preview_url", "segments": [...] }

# PATCH /api/jobs/{job_id}/segments
# Request: { "segments": [{ "index": 0, "text": "...", "start": 1.2, "end": 3.5 }, ...] }
# Response: Updated job with new preview_url

# GET /api/jobs/{job_id}/preview?position=top|bottom&font_size=24
# Returns: video/mp4 stream
```

### 5. Frontend (React + Vite) - Minimal Components

```
src/
├── App.jsx                      # Layout: Editor (left) | Preview (right)
├── api.js                       # Axios wrapper
├── components/
│   ├── UploadZone.jsx           # Drag-drop, shows progress
│   ├── SegmentEditor.jsx        # Editable table: index | start | end | text | actions
│   ├── PreviewPlayer.jsx        # <video> with timestamp sync
│   ├── PositionControls.jsx     # Subtitle position: top/bottom, margin, font size
│   └── Toolbar.jsx              # Download SRT, Regenerate, Save edits
└── hooks/
    ├── useJobPolling.js         # Poll /api/jobs/{id} until complete
    └── useSegmentEdit.js        # Optimistic updates + debounced PATCH
```

### 6. Implementation Phases

| Phase | Deliverable | Est. Time |
|-------|-------------|-----------|
| **0** | Project scaffold, config, `.env.example`, `requirements.txt`, `package.json` | 30 min |
| **1** | `audio.py`: extract, chunk_with_overlap (ffmpeg subprocess) | 45 min |
| **2** | `deepgram.py`: transcribe_file(), transcribe_chunks_parallel() | 45 min |
| **3** | `groq_transliterate.py`: chunked transliteration with your prompt | 30 min |
| **4** | `groq_merge.py`: overlap-aware merge prompt + parsing | 45 min |
| **5** | `srt.py`: generate_srt(segments) → bytes | 20 min |
| **6** | `pipeline.py`: orchestrate full flow, job state management | 60 min |
| **7** | FastAPI routes: `/jobs`, `/jobs/{id}`, `/jobs/{id}/segments`, `/jobs/{id}/preview` | 60 min |
| **8** | `preview.py`: burn_subtitles(), generate_preview() | 45 min |
| **9** | `editor.py`: apply_edits(segments, actions) → new_segments | 30 min |
| **10** | React frontend: UploadZone + polling + SegmentEditor + PreviewPlayer | 90 min |
| **11** | PositionControls + Toolbar + Download SRT | 30 min |
| **12** | Integration test: 10-min video → SRT + preview + edit → new preview | 30 min |

**Total**: ~7-8 hours of focused coding

### 7. Critical Implementation Notes

1. **Temp file cleanup**: Use `tempfile.TemporaryDirectory()` context manager per job
2. **Async throughout**: FastAPI + `asyncio.gather()` for parallel Deepgram/Groq calls
3. **Job store**: Simple in-memory `dict[job_id, JobState]` + JSON persistence to `./jobs/`
4. **Error handling**: Each service raises custom exceptions → caught in pipeline → job.status = "failed"
5. **Progress updates**: WebSocket or SSE for real-time UI (start with polling, upgrade later)
6. **Groq token limits**: Batch segments ~20 per call; merge receives 2 chunks at a time

### 8. File Structure (Complete)

```
hinglish-srt/
├── .env.example
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── enums.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audio.py
│   │   ├── deepgram.py
│   │   ├── groq_transliterate.py
│   │   ├── groq_merge.py
│   │   ├── srt.py
│   │   ├── preview.py
│   │   └── editor.py
│   ├── workers/
│   │   ├── __init__.py
│   │   └── pipeline.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_transcribe.py
│   │   ├── routes_edit.py
│   │   └── routes_preview.py
│   └── utils/
│       ├── __init__.py
│       ├── time.py
│       └── file.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── App.css
    │   ├── api.js
    │   ├── components/
    │   │   ├── UploadZone.jsx
    │   │   ├── SegmentEditor.jsx
    │   │   ├── PreviewPlayer.jsx
    │   │   ├── PositionControls.jsx
    │   │   └── Toolbar.jsx
    │   └── hooks/
    │       ├── useJobPolling.js
    │       └── useSegmentEdit.js
    └── public/
```

---

## Next Steps

1. **Confirm plan** - Any adjustments to phases or priorities?
2. **API keys** - I'll guide you through Deepgram/Groq setup when we hit Phase 2/3
3. **Start Phase 0** - Scaffold everything, then we iterate service by service

Want me to proceed with Phase 0 (project scaffold)? I'll create all directories, config files, and empty modules with type hints so you can see the full structure before we fill in logic.

---

## User

alright great now i am going to use this whole plan with antigravity ai agent so i need a detailed prompt to give it. make sure to include everything we talked about in the plan with the questions i answered too along with every detail of how it would work and what to do 

---

## Assistant (Plan · Nemotron 3 Ultra Free · 334.9s)

_Thinking:_

The user wants a detailed prompt for an AI agent (Antigravity) to implement this entire Hinglish SRT generator application. They want me to create a comprehensive prompt that includes all the details we discussed.

Since I'm in plan mode (read-only), I should create this prompt as a text output - not write it to a file. I'll compile everything into a thorough, well-structured prompt that the Antigravity agent can follow.

Let me organize all the information we've gathered:
1. Project overview and goals
2. Architecture decisions
3. Technical stack choices
4. Detailed implementation plan with phases
5. API contracts
6. Data flow
7. Key technical details
8. Frontend components
9. All the answers to the clarifying questions
10. Modular structure requirements

I'll present this as a comprehensive prompt they can copy-paste to Antigravity.

# Antigravity Agent Prompt: Hinglish SRT Generator

## Project Overview

Build a **modular, local-first tool** that:
1. Accepts a video file (Hindi+English speech)
2. Extracts audio → chunks at ~8 min with 30s overlap
3. Transcribes via Deepgram (Hindi/Devanagari)
4. Transliterates to Hinglish (Roman script) via Groq
5. Merges chunks with overlap-aware dedup via Groq
6. Generates SRT + burns subtitles for preview (MoviePy)
7. Provides React frontend for editing segments, adjusting position, downloading SRT

**Target**: Urgent MVP for Premiere Pro/After Effects workflow. Single video at a time, local only.

---

## Architecture Decisions (Finalized)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend | **FastAPI** (async, auto-docs, type safety) | Better than Flask for async pipeline |
| Frontend | **React + Vite** (separate, served on 5173) | User wants to learn React |
| Chunking | **Blind 8-min splits + 30s overlap** | No VAD needed; Groq merge handles dedup |
| Merge | **Groq with overlap context** | Smart stitching, preserves timestamps |
| Preview | **Full quality** (MoviePy CompositeVideoClip) | Exact output for editing decisions |
| Deployment | **Local only** | No cloud complexity yet |
| Batch | **Single video** | Simpler state management |
| Job Store | **In-memory dict + JSON persistence** | Simple, reloadable |

---

## Complete File Structure

```
hinglish-srt/
├── .env.example
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── enums.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audio.py
│   │   ├── deepgram.py
│   │   ├── groq_transliterate.py
│   │   ├── groq_merge.py
│   │   ├── srt.py
│   │   ├── preview.py
│   │   └── editor.py
│   ├── workers/
│   │   ├── __init__.py
│   │   └── pipeline.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_transcribe.py
│   │   ├── routes_edit.py
│   │   └── routes_preview.py
│   └── utils/
│       ├── __init__.py
│       ├── time.py
│       └── file.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── App.css
    │   ├── api.js
    │   ├── components/
    │   │   ├── UploadZone.jsx
    │   │   ├── SegmentEditor.jsx
    │   │   ├── PreviewPlayer.jsx
    │   │   ├── PositionControls.jsx
    │   │   └── Toolbar.jsx
    │   └── hooks/
    │       ├── useJobPolling.js
    │       └── useSegmentEdit.js
    └── public/
```

---

## Detailed Service Specifications

### 1. `config.py` (Pydantic Settings)
```python
# Fields: DEEPGRAM_API_KEY, GROQ_API_KEY, MAX_CHUNK_MINUTES=8, OVERLAP_SECONDS=30
# TEMP_DIR, JOBS_DIR, CORS_ORIGINS=["http://localhost:5173"]
```

### 2. `models/schemas.py`
```python
# Segment: start: float, end: float, text: str
# VideoJob: job_id: str, status: JobStatus, video_path: str, audio_path: str,
#           chunks: List[ChunkInfo], segments: List[Segment], 
#           srt_path: str, preview_path: str, created_at, updated_at
# EditAction: index: int, text: str?, start: float?, end: float?, action: "update"|"split"|"merge"|"delete"
```

### 3. `services/audio.py`
- `extract_audio(video_path: str) -> str` — MoviePy `VideoFileClip.audio.write_audiofile(temp.wav)`
- `chunk_with_overlap(wav_path: str, chunk_min: int=8, overlap_sec: int=30) -> List[str]`
  - Use `ffmpeg -ss {start} -t {duration} -i input.wav -c copy output.wav`
  - Chunk 0: 0-480s, Chunk 1: 450-930s, etc. (30s overlap)
  - Returns list of temp chunk paths

### 4. `services/deepgram.py`
- `transcribe_file(audio_path: str) -> List[Segment]`
  - SDK: `deepgram.listen.prerecorded.v("1").transcribe_file()`
  - Options: `model="nova-2", language="hi", smart_format=True, utterances=True, punctuate=True`
  - Parse `utterances` → `[Segment(start, end, transcript)]` (Devanagari)
- `transcribe_chunks_parallel(chunk_paths: List[str]) -> List[List[Segment]]`
  - `asyncio.gather(*[transcribe_file(p) for p in chunk_paths])`

### 5. `services/groq_transliterate.py`
- `transliterate_chunks(chunk_segments: List[List[Segment]]) -> List[List[Segment]]`
  - Batch ~20 segments per call (token limit)
  - **Prompt** (your exact template):
    ```
    You are a Hinglish transcript cleaner and TRANSLITERATOR.

    CRITICAL INSTRUCTION:
    You MUST convert ALL Devanagari script (Hindi) into Roman script (English alphabet).
    Example: "लेकिन" -> "lekin", "थोड़ा" -> "thoda", "क्या" -> "kya"

    RULES:
    1. TRANSLITERATE EVERYTHING: Output must contain ONLY Roman/Latin characters. NO Devanagari allowed.
    2. Keep English words exactly as spoken.
    3. Maintain the natural code-mixed flow.
    4. Fix punctuation and spelling.

    INPUT: Raw transcript (contains Devanagari)
    OUTPUT: JSON object with a "segments" key containing the array of corrected segments.

    Format: { "segments": [{"start": 0.0, "end": 3.5, "text": "Namaste dosto, aaj hum seekhenge"}] }
    ```
  - Parse JSON response, preserve original timestamps

### 6. `services/groq_merge.py`
- `merge_chunks(chunk_segments: List[List[Segment]], overlap_sec: int=30) -> List[Segment]`
  - Process pairwise: merge chunk[i] + chunk[i+1] using overlap region as context
  - **Merge Prompt**:
    ```
    You are merging two adjacent transcript chunks with a 30-second overlap.
    Chunk A ends at {chunk_a_end}s, Chunk B starts at {chunk_b_start}s.
    The overlap region ({overlap_start}s - {overlap_end}s) appears in both.
    
    Task: Produce a single continuous segment list.
    - Remove duplicate content in the overlap
    - Preserve exact timestamps from the later chunk for overlap region
    - Maintain continuous numbering
    - Output same JSON schema: {"segments": [...]}
    ```
  - Iterate until all chunks merged

### 7. `services/srt.py`
- `generate_srt(segments: List[Segment]) -> bytes`
  - Format: `index\nHH:MM:SS,mmm --> HH:MM:SS,mmm\ntext\n\n`
  - `utils.time.seconds_to_srt(seconds: float) -> str`

### 8. `services/preview.py`
- `generate_preview(video_path: str, segments: List[Segment], position: str="bottom", font_size: int=24) -> str`
  - `MoviePy: CompositeVideoClip([video, SubtitlesClip(srt_generator)])`
  - `write_videofile(output.mp4, preset="medium", threads=4)`
  - Return preview path

### 9. `services/editor.py`
- `apply_edits(segments: List[Segment], actions: List[EditAction]) -> List[Segment]`
  - Handle update/split/merge/delete
  - Re-index, validate no overlaps/gaps

### 10. `workers/pipeline.py`
- `process_job(job_id: str, video_path: str) -> VideoJob`
  - Orchestrates full flow with try/except at each stage
  - Updates job.status: `pending → extracting → transcribing → transliterating → merging → generating_srt → generating_preview → complete`
  - On failure: `status = "failed", error = str(e)`

### 11. API Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/api/jobs` | POST | Upload video, create job, return job_id |
| `/api/jobs/{job_id}` | GET | Poll status, get segments, srt_url, preview_url |
| `/api/jobs/{job_id}/segments` | PATCH | Apply edits, regenerate preview |
| `/api/jobs/{job_id}/preview` | GET | Stream preview.mp4 (supports `?position=&font_size=`) |
| `/api/jobs/{job_id}/srt` | GET | Download SRT file |

---

## Frontend Component Specs

### `UploadZone.jsx`
- Drag-drop + click to select
- POST to `/api/jobs` with FormData
- Show progress: "Extracting audio..." → "Transcribing..." → "Generating preview..."

### `SegmentEditor.jsx`
- Table: `# | Start | End | Text (editable) | Actions`
- Actions: Split (at cursor), Merge (with next), Delete
- Debounced PATCH to `/api/jobs/{id}/segments` (500ms)

### `PreviewPlayer.jsx`
- `<video controls src={preview_url} />`
- Sync: highlight current segment in editor during playback
- `onTimeUpdate` → find segment at currentTime

### `PositionControls.jsx`
- Radio: Top / Bottom / Custom (margin %)
- Font size slider (16-48px)
- On change → refetch preview with query params

### `Toolbar.jsx`
- Download SRT button (GET `/api/jobs/{id}/srt`)
- Regenerate preview (after edits)
- Save edits locally (localStorage backup)

---

## API Key Setup (for Agent)

**Deepgram**: https://console.deepgram.com → API Keys → Create → Copy to `.env`
**Groq**: https://console.groq.com → API Keys → Create → Copy to `.env`

```bash
# .env.example
DEEPGRAM_API_KEY=your_deepgram_key
GROQ_API_KEY=your_groq_key
MAX_CHUNK_MINUTES=8
OVERLAP_SECONDS=30
TEMP_DIR=./temp
JOBS_DIR=./jobs
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Implementation Phases (Execute Sequentially)

1. **Scaffold** — All dirs, `__init__.py`, `requirements.txt`, `package.json`, configs
2. **Audio Service** — `extract_audio`, `chunk_with_overlap` (ffmpeg subprocess)
3. **Deepgram Service** — Single + parallel transcription
4. **Groq Transliterate** — Your prompt, batching, JSON parsing
5. **Groq Merge** — Overlap-aware pairwise merge
6. **SRT Generator** — Format + time utils
7. **Pipeline Orchestrator** — Job state machine, error handling
8. **FastAPI Routes** — All 4 endpoints + CORS
9. **Preview Service** — MoviePy burn + position/font params
10. **Editor Service** — Apply edits to segments
11. **React Frontend** — All 5 components + 2 hooks + API client
12. **Integration Test** — 10-min video → SRT → edit → new preview

---

## Critical Implementation Rules

1. **Async everywhere** — `async def`, `await`, `asyncio.gather` for parallel calls
2. **Temp cleanup** — `with tempfile.TemporaryDirectory() as tmp:` per job
3. **Type hints** — All functions, Pydantic models for validation
4. **Custom exceptions** — `TranscriptionError`, `TransliterationError`, `MergeError` → caught in pipeline
5. **Progress tracking** — Job stores `current_stage`, `progress_percent` for UI polling
6. **Token management** — Batch segments ≤20 per Groq call; merge receives 2 chunks max
7. **No hardcoded paths** — All via `config.settings`

---

## Questions Answered (Reference)

- **API Keys**: Need guidance (included setup URLs above)
- **Frontend**: React + Vite (separate dev server)
- **Deployment**: Local only
- **Batch**: Single video
- **Chunking**: Blind 8-min + 30s overlap (Groq merge handles dedup)
- **Merge**: Groq with overlap context
- **Preview**: Full quality
- **Editing**: Text edit, timing adjust, split/merge, position controls

---

## Success Criteria

- [ ] 10-min Hinglish video → SRT in <5 min
- [ ] Preview plays with burned subs at correct timestamps
- [ ] Edit segment text → preview regenerates with changes
- [ ] Move subtitle position (top/bottom) → preview updates
- [ ] Download SRT → imports correctly in Premiere Pro
- [ ] All temp files cleaned up after job
- [ ] Modular: each service independently testable

---

## Handoff Note for Agent

> This is a **learning project** — prioritize clarity over cleverness. Use explicit variable names, add docstrings, keep functions <50 lines. The user will read and modify this code. If you hit ambiguity, **ask** rather than assume. Start with Phase 1 scaffold and confirm each phase works before proceeding.

---

**Ready to begin?** Start with Phase 0 scaffold — create all directories, empty modules with type hints, config, requirements, and package.json. Then we'll iterate service by service.

---

