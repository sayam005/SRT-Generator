/**
 * SegmentEditor.jsx — Editable card-based layout of subtitle segments.
 *
 * Each segment gets its own card with:
 *  - Editable start/end timestamps
 *  - Auto-expanding textarea for subtitle text
 *  - Split / Merge / Delete actions
 */

import { useCallback, useRef, useEffect, useState } from "react";

/**
 * Format seconds to HH:MM:SS.ms display for editing.
 */
function formatTime(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.round((seconds % 1) * 1000);
    if (hrs > 0) {
        return `${hrs}:${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
    }
    return `${mins}:${String(secs).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
}

/**
 * Parse a time string like "1:23.456" or "0:05.200" back to seconds.
 */
function parseTime(str) {
    try {
        const parts = str.split(":");
        let hours = 0, mins = 0, secs = 0;
        if (parts.length === 3) {
            hours = parseInt(parts[0], 10) || 0;
            mins = parseInt(parts[1], 10) || 0;
            secs = parseFloat(parts[2]) || 0;
        } else if (parts.length === 2) {
            mins = parseInt(parts[0], 10) || 0;
            secs = parseFloat(parts[1]) || 0;
        } else {
            secs = parseFloat(parts[0]) || 0;
        }
        return hours * 3600 + mins * 60 + secs;
    } catch {
        return null;
    }
}

/**
 * Auto-resizing textarea component.
 */
function AutoTextarea({ value, onChange, className }) {
    const ref = useRef(null);

    const resize = useCallback(() => {
        const el = ref.current;
        if (el) {
            el.style.height = "auto";
            el.style.height = el.scrollHeight + "px";
        }
    }, []);

    useEffect(() => {
        resize();
    }, [value, resize]);

    return (
        <textarea
            ref={ref}
            className={className}
            value={value}
            onChange={(e) => {
                onChange(e);
                resize();
            }}
            rows={1}
            onInput={resize}
        />
    );
}

/**
 * Editable timestamp input — shows formatted time, allows inline editing,
 * and commits the parsed value on blur or Enter.
 */
function TimeInput({ value, onChange, className }) {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState("");

    const formatted = formatTime(value);

    const startEdit = () => {
        setDraft(formatted);
        setEditing(true);
    };

    const commit = () => {
        const parsed = parseTime(draft);
        if (parsed !== null && parsed >= 0) {
            onChange(parsed);
        }
        setEditing(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            commit();
        } else if (e.key === "Escape") {
            setEditing(false);
        }
    };

    if (editing) {
        return (
            <input
                className={`${className} time-editing`}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={commit}
                onKeyDown={handleKeyDown}
                autoFocus
            />
        );
    }

    return (
        <span
            className={`${className} time-display`}
            onClick={startEdit}
            title="Click to edit timestamp"
        >
            {formatted}
        </span>
    );
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
                <h3>📝 Segments ({segments.length})</h3>
                {isSaving && <span className="saving-indicator">💾 Saving...</span>}
            </div>

            <div className="segments-list">
                {segments.map((seg, index) => (
                    <div
                        key={index + "-" + seg.start}
                        className={`segment-card ${isActive(seg) ? "active" : ""}`}
                        data-index={index}
                    >
                        <div className="segment-card-header">
                            <span className="segment-number">#{index + 1}</span>
                            <TimeInput
                                className="segment-time-input"
                                value={seg.start}
                                onChange={(val) => onUpdate(index, { start: val })}
                            />
                            <span className="time-arrow">→</span>
                            <TimeInput
                                className="segment-time-input"
                                value={seg.end}
                                onChange={(val) => onUpdate(index, { end: val })}
                            />
                            <span className="segment-duration">
                                {(Number(seg.end) - Number(seg.start)).toFixed(1)}s
                            </span>
                        </div>

                        <AutoTextarea
                            className="segment-textarea"
                            value={seg.text}
                            onChange={(e) => onUpdate(index, { text: e.target.value })}
                        />

                        <div className="segment-card-actions">
                            <button
                                className="seg-action-btn"
                                title="Split at midpoint"
                                onClick={() =>
                                    onSplit(index, (Number(seg.start) + Number(seg.end)) / 2)
                                }
                            >
                                ✂️ Split
                            </button>
                            <button
                                className="seg-action-btn"
                                title="Merge with next"
                                onClick={() => onMerge(index)}
                                disabled={index === segments.length - 1}
                            >
                                🔗 Merge
                            </button>
                            <button
                                className="seg-action-btn delete"
                                title="Delete"
                                onClick={() => onDelete(index)}
                            >
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
