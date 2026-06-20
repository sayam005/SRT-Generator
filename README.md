# Hinglish SRT Generator

A local-first tool that transcribes Hindi+English video speech into Hinglish (Roman script) subtitles with an editing UI.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **ffmpeg** (must be on PATH)
- **Deepgram API key** — [console.deepgram.com](https://console.deepgram.com)
- **Groq API key** — [console.groq.com](https://console.groq.com)

## Setup

```bash
# 1. Clone & configure
cp .env.example .env
# Edit .env with your API keys

# 2. Backend (uses virtual environment)
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Usage

1. Open `http://localhost:5173`
2. Drag & drop a video file
3. Wait for transcription pipeline to complete
4. Edit segments, adjust subtitle position
5. Download SRT for Premiere Pro / After Effects

## Architecture

```
Video → Extract Audio → Chunk (8min + 30s overlap)
  → Deepgram (Hindi/Devanagari) → Groq Transliterate (Hinglish)
  → Groq Merge (dedup overlaps) → SRT + Burned Preview
```
