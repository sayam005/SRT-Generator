/**
 * SegmentEditor.jsx — Editable table of subtitle segments.
 */

import { useCallback } from "react";

/**
 * Format seconds to MM:SS.ms display.
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.round((seconds % 1) * 100);
    return `${mins}:${String(secs).padStart(2, "0")}.${String(ms).padStart(2, "0")}`;
}

/**
 * @param {{
 *   segments: Array,
 *   onUpdate: (index: number, changes: object) => void,
 *   onSplit: (index: number, splitAt: number) => void,
 *   onMerge: (index: number) => void,
 *   onDelete: (index: number) => void,
 *   currentTime: number,
 *   isSaving: boolean
 * }} props
 */
export default function SegmentEditor({
    segments = [],
    onUpdate,
    onSplit,
    onMerge,
    onDelete,
    currentTime = 0,
    isSaving = false,
}) {
    const isActive = useCallback(
        (seg) => currentTime >= seg.start && currentTime <= seg.end,
        [currentTime]
    );

    if (segments.length === 0) {
        return (
            <div id="segment-editor" className="segment-editor empty">
                <p>No segments yet. Upload a video to get started.</p>
            </div>
        );
    }

    return (
        <div id="segment-editor" className="segment-editor">
            <div className="editor-header">
                <h3>Segments ({segments.length})</h3>
                {isSaving && <span className="saving-indicator">Saving...</span>}
            </div>

            <div className="segments-table">
                <div className="table-header">
                    <span className="col-index">#</span>
                    <span className="col-start">Start</span>
                    <span className="col-end">End</span>
                    <span className="col-text">Text</span>
                    <span className="col-actions">Actions</span>
                </div>

                {segments.map((seg, index) => (
                    <div
                        key={index}
                        className={`segment-row ${isActive(seg) ? "active" : ""}`}
                        data-index={index}
                    >
                        <span className="col-index">{index + 1}</span>
                        <span className="col-start">{formatTime(seg.start)}</span>
                        <span className="col-end">{formatTime(seg.end)}</span>
                        <input
                            className="col-text"
                            value={seg.text}
                            onChange={(e) => onUpdate(index, { text: e.target.value })}
                            title={seg.text}
                        />
                        <span className="col-actions">
                            <button
                                title="Split at midpoint"
                                onClick={() =>
                                    onSplit(index, (seg.start + seg.end) / 2)
                                }
                            >
                                ✂️
                            </button>
                            <button
                                title="Merge with next"
                                onClick={() => onMerge(index)}
                                disabled={index === segments.length - 1}
                            >
                                🔗
                            </button>
                            <button
                                title="Delete"
                                onClick={() => onDelete(index)}
                            >
                                🗑️
                            </button>
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
