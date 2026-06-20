/**
 * UploadZone.jsx — Drag-and-drop video upload component.
 */

import { useState, useRef } from "react";

/**
 * @param {{ onUpload: (file: File, language: string) => void, disabled: boolean }} props
 */
export default function UploadZone({ onUpload, disabled = false }) {
    const [isDragging, setIsDragging] = useState(false);
    const [language, setLanguage] = useState("hi");
    const fileInputRef = useRef(null);

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (disabled) return;

        const file = e.dataTransfer.files[0];
        if (file) onUpload(file, language);
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
        if (file) onUpload(file, language);
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

            <div className="language-selector" onClick={e => e.stopPropagation()}>
                <label className="radio-label">
                    <input
                        type="radio"
                        value="hi"
                        checked={language === "hi"}
                        onChange={(e) => setLanguage(e.target.value)}
                        disabled={disabled}
                    />
                    Hinglish (Hindi + English)
                </label>
                <label className="radio-label">
                    <input
                        type="radio"
                        value="en"
                        checked={language === "en"}
                        onChange={(e) => setLanguage(e.target.value)}
                        disabled={disabled}
                    />
                    English Only
                </label>
            </div>
        </div>
    );
}
