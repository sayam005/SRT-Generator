/**
 * useJobPolling.js — Custom hook to poll job status at intervals.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { getJobStatus } from "../api";

/**
 * Poll a job's status every `intervalMs` until it reaches a terminal state.
 *
 * @param {string|null} jobId - Job ID to poll, or null to disable.
 * @param {number} intervalMs - Polling interval in milliseconds (default 2000).
 * @returns {{ job: Object|null, error: string|null, isPolling: boolean }}
 */
export function useJobPolling(jobId, intervalMs = 2000) {
    const [job, setJob] = useState(null);
    const [error, setError] = useState(null);
    const [isPolling, setIsPolling] = useState(false);
    const intervalRef = useRef(null);

    const stopPolling = useCallback(() => {
        if (intervalRef.current) {
            clearTimeout(intervalRef.current);
            intervalRef.current = null;
        }
        setIsPolling(false);
    }, []);

    useEffect(() => {
        if (!jobId) {
            stopPolling();
            return;
        }

        let isCancelled = false;

        const poll = async () => {
            if (isCancelled) return;
            try {
                const data = await getJobStatus(jobId);
                if (isCancelled) return;

                setJob(data);
                setError(null);

                // Stop polling on terminal states
                if (data.status === "complete" || data.status === "failed") {
                    setIsPolling(false);
                    return; // Stop recursive polling
                }

                // Continue polling
                intervalRef.current = setTimeout(poll, intervalMs);
            } catch (err) {
                if (isCancelled) return;
                setError(err.message);
                setIsPolling(false);
            }
        };

        setIsPolling(true);
        poll();

        return () => {
            isCancelled = true;
            stopPolling();
        };
    }, [jobId, intervalMs, stopPolling]);

    return { job, error, isPolling };
}
