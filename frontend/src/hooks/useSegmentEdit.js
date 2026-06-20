/**
 * useSegmentEdit.js — Custom hook for managing segment edits with debouncing.
 */

import { useState, useCallback, useRef } from "react";
import { editSegments } from "../api";

/**
 * Manage local segment state and debounced PATCH calls.
 *
 * @param {string|null} jobId - Current job ID.
 * @param {Array} initialSegments - Segments from the server.
 * @returns {{ segments, syncSegments, updateSegment, splitSegment, mergeSegment, deleteSegment, isSaving }}
 */
export function useSegmentEdit(jobId, initialSegments = []) {
    const [segments, setSegments] = useState(initialSegments);
    const [isSaving, setIsSaving] = useState(false);
    const debounceRef = useRef(null);

    // Sync when new segments arrive from server
    const syncSegments = useCallback((newSegments) => {
        setSegments(newSegments);
    }, []);

    const sendEdit = useCallback(
        async (actions) => {
            if (!jobId) return;
            setIsSaving(true);
            try {
                const data = await editSegments(jobId, actions);
                setSegments(data.segments);
            } catch (err) {
                console.error("Edit failed:", err);
            } finally {
                setIsSaving(false);
            }
        },
        [jobId]
    );

    const updateSegment = useCallback(
        (index, changes) => {
            // Optimistic local update
            setSegments((prev) =>
                prev.map((seg, i) => (i === index ? { ...seg, ...changes } : seg))
            );

            // Debounced server sync
            if (debounceRef.current) clearTimeout(debounceRef.current);
            debounceRef.current = setTimeout(() => {
                sendEdit([{ index, action: "update", ...changes }]);
            }, 500);
        },
        [sendEdit]
    );

    const splitSegment = useCallback(
        (index, splitAt) => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            sendEdit([{ index, action: "split", split_at: splitAt }]);
        },
        [sendEdit]
    );

    const mergeSegment = useCallback(
        (index) => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            sendEdit([{ index, action: "merge" }]);
        },
        [sendEdit]
    );

    const deleteSegment = useCallback(
        (index) => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            sendEdit([{ index, action: "delete" }]);
        },
        [sendEdit]
    );

    return {
        segments,
        syncSegments,
        updateSegment,
        splitSegment,
        mergeSegment,
        deleteSegment,
        isSaving,
    };
}
