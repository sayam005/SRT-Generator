"""
config.py — Application settings loaded from .env file.

Uses pydantic-settings for type-safe environment variable parsing.
"""

import json
from pathlib import Path
from typing import Annotated, List

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_cors(v):
    if isinstance(v, list):
        return v
    v = str(v).strip()
    if not v:
        return ["*"]
    try:
        parsed = json.loads(v)
        if isinstance(parsed, list):
            return parsed
        return [str(parsed)]
    except (json.JSONDecodeError, ValueError):
        return [item.strip() for item in v.split(",") if item.strip()]


class Settings(BaseSettings):
    """All application configuration, loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
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
    CORS_ORIGINS: Annotated[List[str], BeforeValidator(_parse_cors)] = ["*"]

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
