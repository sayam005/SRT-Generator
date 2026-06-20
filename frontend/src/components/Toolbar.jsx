/**
 * Toolbar.jsx — Action bar for SRT download, preview regeneration, and local save.
 */

import { getSrtUrl } from "../api";

/**
 * @param {{
 *   jobId: string|null,
 *   onRegeneratePreview: () => void,
 *   onSaveLocal: () => void,
 *   isComplete: boolean
 * }} props
 */
export default function Toolbar({
    jobId,
    onSaveLocal,
    isComplete = false,
}) {
    const handleDownloadSrt = () => {
        if (!jobId) return;
        const url = getSrtUrl(jobId);
        const a = document.createElement("a");
        a.href = url;
        a.download = `subtitles_${jobId}.srt`;
        a.click();
    };

    return (
        <div id="toolbar" className="toolbar">
            <button
                className="btn btn-primary"
                onClick={handleDownloadSrt}
                disabled={!isComplete}
                title="Download SRT file"
            >
                📥 Download SRT
            </button>

            <button
                className="btn btn-ghost"
                onClick={onSaveLocal}
                disabled={!isComplete}
                title="Save edits to localStorage as backup"
            >
                💾 Save Locally
            </button>
        </div>
    );
}
