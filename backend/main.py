"""
main.py — FastAPI application entry point.

Run with: uvicorn main:app --reload --port 8000
"""

import os
import sys

ffmpeg_winget_path = r"C:\Users\sayam\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin"
if os.path.exists(ffmpeg_winget_path):
    if ffmpeg_winget_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_winget_path + os.pathsep + os.environ.get("PATH", "")
    os.environ["IMAGEIO_FFMPEG_EXE"] = os.path.join(ffmpeg_winget_path, "ffmpeg.exe")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.routes_transcribe import router as transcribe_router
from api.routes_edit import router as edit_router
from api.routes_preview import router as preview_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle handler."""
    # Startup: ensure required directories exist
    settings.ensure_dirs()
    print(f"📁 Temp dir: {settings.temp_path}")
    print(f"📁 Jobs dir: {settings.jobs_path}")
    print("🚀 Hinglish SRT Generator ready!")
    yield
    # Shutdown: nothing to clean up for now
    print("👋 Shutting down...")


app = FastAPI(
    title="Hinglish SRT Generator",
    description="Transcribe Hindi+English video to Hinglish subtitles",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(transcribe_router)
app.include_router(edit_router)
app.include_router(preview_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Hinglish SRT Generator"}
