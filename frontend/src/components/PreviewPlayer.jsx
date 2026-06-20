/**
 * PreviewPlayer.jsx — Video preview player with segment sync.
 */

import { useRef, useState, useCallback, useEffect } from "react";

/**
 * @param {{
 *   previewUrl: string|null,
 *   onTimeUpdate: (currentTime: number) => void
 * }} props
 */
export default function PreviewPlayer({ previewUrl, onTimeUpdate }) {
    const videoRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);

    const handleTimeUpdate = useCallback(() => {
        if (videoRef.current && onTimeUpdate) {
            onTimeUpdate(videoRef.current.currentTime);
        }
    }, [onTimeUpdate]);

    useEffect(() => {
        setIsLoading(true);
    }, [previewUrl]);

    if (!previewUrl) {
        return (
            <div id="preview-player" className="preview-player placeholder">
                <div className="placeholder-icon">🎥</div>
                <p>Preview will appear here after processing</p>
            </div>
        );
    }

    return (
        <div id="preview-player" className="preview-player">
            {isLoading && <div className="loading-overlay">Loading preview...</div>}
            <video
                ref={videoRef}
                controls
                src={previewUrl}
                onTimeUpdate={handleTimeUpdate}
                onLoadedData={() => setIsLoading(false)}
                onError={() => setIsLoading(false)}
            >
                Your browser does not support video playback.
            </video>
        </div>
    );
}
