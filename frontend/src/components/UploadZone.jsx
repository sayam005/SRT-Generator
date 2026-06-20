/**
 * UploadZone.jsx — Drag-and-drop video upload component.
 */

import { useState, useRef } from "react";

/**
 * @param {{ onUpload: (file: File) => void, disabled: boolean }} props
 */
export default function UploadZone({ onUpload, disabled = false }) {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (disabled) return;

        const file = e.dataTransfer.files[0];
        if (file) onUpload(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const handleClick = () => {
        if (!disabled) fileInputRef.current?.click();
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) onUpload(file);
    };

    return (
        <div
            id="upload-zone"
            className={`upload-zone ${isDragging ? "dragging" : ""} ${disabled ? "disabled" : ""}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={handleClick}
        >
            <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                style={{ display: "none" }}
            />
            <div className="upload-icon">🎬</div>
            <p className="upload-text">
                {disabled
                    ? "Processing..."
                    : "Drag & drop a video file here, or click to select"}
            </p>
            <p className="upload-hint">
                Supports MP4, MKV, AVI, MOV, WebM
            </p>
        </div>
    );
}
