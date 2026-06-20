"""
editor.py — Apply edit operations to subtitle segments.

Supports update, split, merge, and delete actions.
"""

from typing import List

from models.schemas import EditAction, Segment


def apply_edits(
    segments: List[Segment],
    actions: List[EditAction],
) -> List[Segment]:
    """Apply a batch of edit actions to a segment list.

    Handles:
    - update: change text/timing of a segment
    - split: divide a segment at a given timestamp
    - merge: combine a segment with the next one
    - delete: remove a segment

    After all actions, re-indexes and validates no overlaps/gaps.

    Args:
        segments: Current list of segments.
        actions: Ordered list of edit actions to apply.

    Returns:
        Updated list of segments after all edits.
    """
    raise NotImplementedError("Phase 10: segment editing")
