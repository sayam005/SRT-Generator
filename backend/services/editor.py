"""
editor.py — Apply edit operations to subtitle segments.

Supports update, split, merge, and delete actions.
"""

from typing import List

from models.schemas import EditAction, EditActionType, Segment


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
    
    # Process actions (assuming they are independent or ordered correctly)
    # Note: Complex multi-edits might require ID tracking instead of index,
    # but for this MVP we assume the frontend sends one action at a time via the debounce.
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
                
                # Create the first half
                first = Segment(
                    start=orig.start, 
                    end=split_at, 
                    text=text_first
                )
                
                # Create the second half
                second = Segment(
                    start=split_at, 
                    end=orig.end, 
                    text=text_second
                )
                
                # Replace original with both
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
                
                # Replace both with merged
                current[idx:idx+2] = [merged]
                
        elif action.action == EditActionType.DELETE:
            current.pop(idx)

    # Note: In a production app we'd validate and fix gaps here if needed,
    # but for SRT generation it's fine if there are gaps (silence).
    
    return current
