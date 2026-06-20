"""
time.py — Time format conversion utilities for SRT files.
"""


def seconds_to_srt(seconds: float) -> str:
    """Convert seconds (float) to SRT timestamp format.

    Args:
        seconds: Time in seconds (e.g. 65.123).

    Returns:
        SRT timestamp string (e.g. "00:01:05,123").

    Examples:
        >>> seconds_to_srt(0.0)
        '00:00:00,000'
        >>> seconds_to_srt(65.123)
        '00:01:05,123'
        >>> seconds_to_srt(3661.5)
        '01:01:01,500'
    """
    if seconds < 0:
        seconds = 0.0

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def srt_to_seconds(timestamp: str) -> float:
    """Convert an SRT timestamp string to seconds.

    Args:
        timestamp: SRT format string (e.g. "00:01:05,123").

    Returns:
        Time in seconds as float.

    Examples:
        >>> srt_to_seconds("00:01:05,123")
        65.123
        >>> srt_to_seconds("01:01:01,500")
        3661.5
    """
    time_part, millis_part = timestamp.split(",")
    h, m, s = time_part.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(millis_part) / 1000
