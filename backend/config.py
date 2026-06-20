"""
config.py — Application settings loaded from .env file.

Uses pydantic-settings for type-safe environment variable parsing.
"""

import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application configuration, loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- API Keys ---
    DEEPGRAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # --- Chunking ---
    MAX_CHUNK_MINUTES: int = 8
    OVERLAP_SECONDS: int = 30

    # --- Paths (relative to backend/) ---
    TEMP_DIR: str = "./temp"
    JOBS_DIR: str = "./jobs"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # --- Derived helpers ---

    @property
    def temp_path(self) -> Path:
        """Absolute path to the temp directory."""
        return (Path(__file__).resolve().parent / self.TEMP_DIR).resolve()

    @property
    def jobs_path(self) -> Path:
        """Absolute path to the jobs directory."""
        return (Path(__file__).resolve().parent / self.JOBS_DIR).resolve()

    def ensure_dirs(self) -> None:
        """Create temp and jobs directories if they don't exist."""
        self.temp_path.mkdir(parents=True, exist_ok=True)
        self.jobs_path.mkdir(parents=True, exist_ok=True)


# Singleton instance — import this everywhere
settings = Settings()
