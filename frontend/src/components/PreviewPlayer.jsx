/**
 * PreviewPlayer.jsx — Video player with real-time subtitle overlay.
 *
 * Renders subtitles as a CSS overlay synced to video currentTime.
 * No backend rendering needed — position/fontSize changes are instant.
 */

import { useRef, useState, useCallback, useMemo } from "react";

/**
 * Find the active subtitle segment for the current video time.
 */
function findActiveSegment(segments, time) {
    if (!segments || segments.length === 0) return null;
    return segments.find((s) => time >= s.start && time <= s.end) || null;
}

/**
 * @param {{
 *   previewUrl: string|null,
 *   segments: Array,
 *   fontSize: number,
 *   position: string,
 *   onTimeUpdate: (currentTime: number) => void
 * }} props
 */
export default function PreviewPlayer({
    previewUrl,
    segments = [],
    fontSize = 24,
    position = "bottom",
    onTimeUpdate,
}) {
    const videoRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);
    const [currentTime, setCurrentTime] = useState(0);

    const handleTimeUpdate = useCallback(() => {
        if (videoRef.current) {
            const t = videoRef.current.currentTime;
            setCurrentTime(t);
            if (onTimeUpdate) onTimeUpdate(t);
        }
    }, [onTimeUpdate]);

    const activeSeg = useMemo(
        () => findActiveSegment(segments, currentTime),
        [segments, currentTime]
    );

    // Subtitle overlay style
    const overlayStyle = useMemo(() => {
        const base = {
            position: "absolute",
            left: "50%",
            transform: "translateX(-50%)",
            maxWidth: "90%",
            textAlign: "center",
            fontSize: `${fontSize}px`,
            fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif",
            fontWeight: 600,
            color: "#ffffff",
            textShadow: "0 0 8px rgba(0,0,0,0.9), 2px 2px 4px rgba(0,0,0,0.7)",
            padding: "0.3em 0.8em",
            borderRadius: "6px",
            background: "rgba(0, 0, 0, 0.55)",
            backdropFilter: "blur(4px)",
            lineHeight: 1.4,
            pointerEvents: "none",
            transition: "opacity 0.15s ease",
            zIndex: 10,
        };

        if (position === "top") {
            base.top = "6%";
        } else {
            base.bottom = "12%";
        }

        return base;
    }, [fontSize, position]);

    if (!previewUrl) {
        return (
            <div id="preview-player" className="preview-player placeholder">
                <div className="placeholder-icon">🎥</div>
                <p>Preview will appear here after processing</p>
            </div>
        );
    }

    return (
        <div id="preview-player" className="preview-player" style={{ position: "relative" }}>
            {isLoading && <div className="loading-overlay">Loading video...</div>}

            <video
                ref={videoRef}
                controls
                src={previewUrl}
                onTimeUpdate={handleTimeUpdate}
                onLoadedData={() => setIsLoading(false)}
                onError={() => setIsLoading(false)}
                style={{ width: "100%", display: "block" }}
            >
                Your browser does not support video playback.
            </video>

            {/* Subtitle overlay */}
            {activeSeg && (
                <div style={overlayStyle}>
                    {activeSeg.text}
                </div>
            )}
        </div>
    );
}
