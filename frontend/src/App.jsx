/**
 * App.jsx — Root component for the Hinglish SRT Generator.
 *
 * Orchestrates upload → processing → editing → download flow.
 */

import { useState, useCallback } from "react";
import { createJob, getPreviewUrl } from "./api";
import { useJobPolling } from "./hooks/useJobPolling";
import { useSegmentEdit } from "./hooks/useSegmentEdit";

import UploadZone from "./components/UploadZone";
import SegmentEditor from "./components/SegmentEditor";
import PreviewPlayer from "./components/PreviewPlayer";
import PositionControls from "./components/PositionControls";
import Toolbar from "./components/Toolbar";

import "./App.css";

export default function App() {
  // --- Job state ---
  const [jobId, setJobId] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const { job, error: pollError, isPolling } = useJobPolling(jobId);

  // --- Segment editing ---
  const {
    segments,
    syncSegments,
    updateSegment,
    splitSegment,
    mergeSegment,
    deleteSegment,
    isSaving,
  } = useSegmentEdit(jobId, job?.segments || []);

  // --- Subtitle settings ---
  const [position, setPosition] = useState("bottom");
  const [fontSize, setFontSize] = useState(24);
  const [currentTime, setCurrentTime] = useState(0);

  // Sync segments from server when job updates
  const prevSegmentsRef = useState(null);
  if (job?.segments && job.segments !== prevSegmentsRef[0]) {
    prevSegmentsRef[0] = job.segments;
    syncSegments(job.segments);
  }

  // --- Handlers ---
  const handleUpload = useCallback(async (file, language) => {
    setUploadError(null);
    try {
      const data = await createJob(file, language);
      setJobId(data.job_id);
    } catch (err) {
      setUploadError(err.message);
    }
  }, []);

  const handleSaveLocal = useCallback(() => {
    if (!jobId || !segments.length) return;
    localStorage.setItem(
      `srt-backup-${jobId}`,
      JSON.stringify({ segments, position, fontSize })
    );
    alert("Saved to localStorage!");
  }, [jobId, segments, position, fontSize]);

  const isComplete = job?.status === "complete";
  const isFailed = job?.status === "failed";
  const isProcessing = job && !isComplete && !isFailed;
  const previewUrl = isComplete ? getPreviewUrl(jobId, position, fontSize) : null;

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎬 Hinglish SRT Generator</h1>
        <p className="subtitle">
          Hindi+English video → Hinglish subtitles
        </p>
      </header>

      <main className="app-main">
        {/* Upload section */}
        {!jobId && (
          <UploadZone onUpload={handleUpload} disabled={false} />
        )}

        {uploadError && (
          <div className="error-banner">❌ {uploadError}</div>
        )}

        {/* Processing status */}
        {isProcessing && (
          <div className="processing-status">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${job.progress_percent}%` }}
              />
            </div>
            <p className="status-text">
              {job.current_stage} ({job.progress_percent}%)
            </p>
          </div>
        )}

        {/* Error state */}
        {isFailed && (
          <div className="error-banner">
            ❌ Pipeline failed: {job.error}
          </div>
        )}

        {pollError && (
          <div className="error-banner">❌ Polling error: {pollError}</div>
        )}

        {/* Editor + Preview layout (shown when complete) */}
        {isComplete && (
          <>
            <Toolbar
              jobId={jobId}
              onRegeneratePreview={() => {
                // Changing the preview URL key by appending a timestamp forces the browser to fetch the new video
                const timestamp = new Date().getTime();
                const videoEl = document.querySelector("#preview-player video");
                if (videoEl) {
                  videoEl.src = getPreviewUrl(jobId, position, fontSize) + `&t=${timestamp}`;
                  videoEl.load();
                }
              }}
              onSaveLocal={handleSaveLocal}
              isComplete={isComplete}
            />

            <div className="editor-layout">
              <div className="editor-panel">
                <SegmentEditor
                  segments={segments}
                  onUpdate={updateSegment}
                  onSplit={splitSegment}
                  onMerge={mergeSegment}
                  onDelete={deleteSegment}
                  currentTime={currentTime}
                  isSaving={isSaving}
                />
              </div>

              <div className="preview-panel">
                <PreviewPlayer
                  previewUrl={previewUrl}
                  onTimeUpdate={setCurrentTime}
                />
                <PositionControls
                  position={position}
                  fontSize={fontSize}
                  onPositionChange={setPosition}
                  onFontSizeChange={setFontSize}
                />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
