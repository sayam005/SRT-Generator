/**
 * api.js — HTTP client for the Hinglish SRT Generator backend.
 *
 * All API calls funnel through this module for consistency.
 */

const BASE_URL = "http://localhost:8000/api";

/**
 * Upload a video file and create a transcription job.
 * @param {File} file - The video file to upload.
 * @returns {Promise<Object>} JobResponse from the backend.
 */
export async function createJob(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${BASE_URL}/jobs`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
    }
    return res.json();
}

/**
 * Poll job status by ID.
 * @param {string} jobId
 * @returns {Promise<Object>} JobResponse with status, segments, urls.
 */
export async function getJobStatus(jobId) {
    const res = await fetch(`${BASE_URL}/jobs/${jobId}`);
    if (!res.ok) throw new Error("Failed to fetch job status");
    return res.json();
}

/**
 * Apply edit actions to a job's segments.
 * @param {string} jobId
 * @param {Array} actions - List of EditAction objects.
 * @returns {Promise<Object>} Updated JobResponse.
 */
export async function editSegments(jobId, actions) {
    const res = await fetch(`${BASE_URL}/jobs/${jobId}/segments`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actions }),
    });
    if (!res.ok) throw new Error("Failed to apply edits");
    return res.json();
}

/**
 * Get the preview video URL with position/font params.
 * @param {string} jobId
 * @param {string} position - "top" or "bottom"
 * @param {number} fontSize - 16-48
 * @returns {string} URL to the preview video.
 */
export function getPreviewUrl(jobId, position = "bottom", fontSize = 24) {
    return `${BASE_URL}/jobs/${jobId}/preview?position=${position}&font_size=${fontSize}`;
}

/**
 * Get the SRT download URL.
 * @param {string} jobId
 * @returns {string} URL to download the SRT file.
 */
export function getSrtUrl(jobId) {
    return `${BASE_URL}/jobs/${jobId}/srt`;
}
