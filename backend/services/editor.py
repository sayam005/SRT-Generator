"""
editor.py — Apply edit operations to subtitle segments.

Supports update, split, merge, delete, and cleanup operations.
"""

from typing import List

from models.schemas import EditAction, EditActionType, Segment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _word_count(text: str) -> int:
    """Count words in a text string."""
    return len(text.split())


def _merge_segments(a: Segment, b: Segment) -> Segment:
    """Merge two adjacent segments into one."""
    return Segment(
        start=a.start,
        end=b.end,
        text=f"{a.text} {b.text}".strip(),
    )


def _split_segment_at(segment: Segment, ratio: float, part1_text: str, part2_text: str) -> tuple:
    """Split a segment into two parts using a time ratio."""
    dur = segment.end - segment.start
    split_point = segment.start + dur * ratio
    part1 = Segment(start=segment.start, end=split_point, text=part1_text.strip())
    part2 = Segment(start=split_point, end=segment.end, text=part2_text.strip())
    return part1, part2


# ---------------------------------------------------------------------------
# Cleanup: default intelligent segmentation
# ---------------------------------------------------------------------------

def cleanup_segments(segments: List[Segment], max_words: int = 12) -> List[Segment]:
    """Clean up segments for natural subtitle display.

    Pass 1 — Merge short fragments:
      If adjacent segment has ≤ 3 words, merge with previous.
      Prevents fragmented display like "Hello" / "everyone" / "my name is Sayyam".

    Pass 2 — Split long segments:
      For each segment > max_words, split at the nearest word boundary.
      No semantic search — just cuts cleanly to keep segments short.
      Priority: length over grammatical completeness.

    Args:
        segments: List of segments to clean up.
        max_words: Maximum words per segment (default 12).

    Returns:
        Cleaned segment list.
    """
    if not segments:
        return []

    # Work on copies
    current = [s.model_copy() for s in segments]

    # --- Pass 1: Merge short fragments (≤ 3 words) ---
    merged = []
    for seg in current:
        if merged and _word_count(seg.text) <= 3:
            merged[-1] = _merge_segments(merged[-1], seg)
        else:
            merged.append(seg.model_copy())
    current = merged

    # --- Pass 2: Split long segments at word boundary ---
    result = []
    for seg in current:
        wc = _word_count(seg.text)
        if wc <= max_words:
            result.append(seg)
        else:
            # Cut at max_words — simple, clean, no semantic search
            words = seg.text.split()
            break_idx = max_words

            part1_text = " ".join(words[:break_idx])
            part2_text = " ".join(words[break_idx:])

            # Proportional timestamp split by word count
            ratio = break_idx / wc if wc > 0 else 0.5
            p1, p2 = _split_segment_at(seg, ratio, part1_text, part2_text)

            result.append(p1)

            # If part2 is still too long, split again (max 2 levels)
            if _word_count(p2.text) > max_words:
                words2 = p2.text.split()
                break_idx2 = max_words
                p2a_text = " ".join(words2[:break_idx2])
                p2b_text = " ".join(words2[break_idx2:])
                ratio2 = break_idx2 / len(words2) if words2 else 0.5
                p2a, p2b = _split_segment_at(p2, ratio2, p2a_text, p2b_text)
                result.append(p2a)
                if _word_count(p2b.text) > 0:
                    result.append(p2b)
            else:
                result.append(p2)

    return result


# ---------------------------------------------------------------------------
# Standard edit operations
# ---------------------------------------------------------------------------

def apply_edits(
    segments: List[Segment],
    actions: List[EditAction],
) -> List[Segment]:
    """Apply a batch of edit actions to a segment list.

    Handles:
    - update: change text of a segment (doesn't change timing here, but could)
    - split: divide a segment at a given timestamp
    - merge: combine a segment with the next one
    - delete: remove a segment

    After all actions, re-indexes and validates.

    Args:
        segments: Current list of segments.
        actions: Ordered list of edit actions to apply.

    Returns:
        Updated list of segments after all edits.
    """
    # Create a working copy
    current = [s.model_copy() for s in segments]

    for action in actions:
        idx = action.index
        if idx < 0 or idx >= len(current):
            continue

        if action.action == EditActionType.UPDATE:
            if action.text is not None:
                current[idx].text = action.text
            if action.start is not None:
                current[idx].start = action.start
            if action.end is not None:
                current[idx].end = action.end

        elif action.action == EditActionType.SPLIT:
            split_at = action.split_at
            if split_at is not None and current[idx].start <= split_at <= current[idx].end:
                orig = current[idx]

                # Split text roughly in half by words
                words = orig.text.split()
                mid = max(1, len(words) // 2) if words else 0

                text_first = " ".join(words[:mid]) if words else ""
                text_second = " ".join(words[mid:]) if words else ""

                first = Segment(start=orig.start, end=split_at, text=text_first)
                second = Segment(start=split_at, end=orig.end, text=text_second)

                current[idx:idx+1] = [first, second]

        elif action.action == EditActionType.MERGE:
            if idx < len(current) - 1:
                orig1 = current[idx]
                orig2 = current[idx + 1]

                merged = Segment(
                    start=orig1.start,
                    end=orig2.end,
                    text=f"{orig1.text} {orig2.text}"
                )

                current[idx:idx+2] = [merged]

        elif action.action == EditActionType.DELETE:
            current.pop(idx)

    return current
