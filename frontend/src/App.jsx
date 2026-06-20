/**
 * App.jsx — Root component for the Hinglish SRT Generator.
 *
 * Orchestrates upload → processing → editing → download flow.
 */

import { useState, useCallback, useEffect } from "react";
import { createJob, getPreviewUrl } from "./api";
import { useJobPolling } from "./hooks/useJobPolling";
import { useSegmentEdit } from "./hooks/useSegmentEdit";

import UploadZone from "./components/UploadZone";
import SegmentEditor from "./components/SegmentEditor";
import PreviewPlayer from "./components/PreviewPlayer";
import PositionControls from "./components/PositionControls";
import Toolbar from "./components/Toolbar";

import "./App.css";

// Phase icons and labels for the rich progress display
const PHASE_MAP = {
  extracting: { icon: "🎵", label: "Extracting audio from video", phase: 1 },
  chunking: { icon: "✂️", label: "Splitting audio into chunks", phase: 2 },
  transcribing: { icon: "🗣️", label: "Transcribing with Deepgram AI", phase: 3 },
  transliterating: { icon: "🔤", label: "Transliterating to Hinglish (Groq)", phase: 4 },
  merging: { icon: "🔗", label: "Merging overlapping segments", phase: 5 },
  generating_srt: { icon: "📝", label: "Generating SRT subtitle file", phase: 6 },
  generating_preview: { icon: "🎬", label: "Burning subtitles into preview", phase: 7 },
};

const TOTAL_PHASES = 7;

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
  const [prevSegments, setPrevSegments] = useState(null);
  useEffect(() => {
    if (job?.segments && job.segments !== prevSegments) {
      setPrevSegments(job.segments);
      syncSegments(job.segments);
    }
  }, [job?.segments]);

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

  const handleReset = useCallback(() => {
    setJobId(null);
    setUploadError(null);
    setPrevSegments(null);
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
  const isProcessing = jobId && !isComplete && !isFailed;
  const previewUrl = isComplete ? getPreviewUrl(jobId) : null;

  // Get current phase info
  const currentPhase = job?.status ? PHASE_MAP[job.status] : null;

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

        {/* Rich Processing Status */}
        {isProcessing && (
          <div className="processing-card">
            {/* Animated header */}
            <div className="processing-header">
              <div className="processing-spinner"></div>
              <h2>Processing your video...</h2>
            </div>

            {/* Progress bar */}
            <div className="progress-container">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${job?.progress_percent || 0}%` }}
                />
              </div>
              <span className="progress-percent">{job?.progress_percent || 0}%</span>
            </div>

            {/* Phase timeline */}
            <div className="phase-timeline">
              {Object.entries(PHASE_MAP).map(([key, phase]) => {
                const currentPhaseNum = currentPhase?.phase || 0;
                const isDone = phase.phase < currentPhaseNum;
                const isActive = phase.phase === currentPhaseNum;
                const isPending = phase.phase > currentPhaseNum;

                return (
                  <div
                    key={key}
                    className={`phase-step ${isDone ? "done" : ""} ${isActive ? "active" : ""} ${isPending ? "pending" : ""}`}
                  >
                    <div className="phase-icon">
                      {isDone ? "✅" : phase.icon}
                    </div>
                    <div className="phase-info">
                      <span className="phase-label">{phase.label}</span>
                      {isActive && (
                        <span className="phase-active-indicator">
                          <span className="dot-pulse"></span>
                          In progress...
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Current stage text from backend */}
            {job?.current_stage && (
              <div className="current-stage-text">
                💬 {job.current_stage}
              </div>
            )}
          </div>
        )}

        {/* Error state */}
        {isFailed && (
          <div className="error-card">
            <div className="error-icon">❌</div>
            <h3>Pipeline Failed</h3>
            <p>{job.error}</p>
            <button className="btn btn-primary" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}

        {pollError && (
          <div className="error-banner">❌ Polling error: {pollError}</div>
        )}

        {/* Editor + Preview layout (shown when complete) */}
        {isComplete && (
          <>
            <div className="success-banner">
              ✅ Processing complete! {segments.length} segments ready for editing.
            </div>

            <Toolbar
              jobId={jobId}
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
                  segments={segments}
                  fontSize={fontSize}
                  position={position}
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

            <button className="btn btn-ghost reset-btn" onClick={handleReset}>
              ← Upload another video
            </button>
          </>
        )}
      </main>
    </div>
  );
}
