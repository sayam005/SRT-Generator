"""
file.py — File system utilities.
"""

import shutil
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Create a directory (and parents) if it doesn't exist.

    Args:
        path: Directory path to create.

    Returns:
        The resolved Path object.
    """
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def cleanup_temp(path: str | Path) -> None:
    """Remove a temporary directory and all its contents.

    Silently ignores if the path doesn't exist.

    Args:
        path: Directory path to remove.
    """
    p = Path(path)
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)
