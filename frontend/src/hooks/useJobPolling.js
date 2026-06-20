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
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        setIsPolling(false);
    }, []);

    useEffect(() => {
        if (!jobId) {
            stopPolling();
            return;
        }

        const poll = async () => {
            try {
                const data = await getJobStatus(jobId);
                setJob(data);
                setError(null);

                // Stop polling on terminal states
                if (data.status === "complete" || data.status === "failed") {
                    stopPolling();
                }
            } catch (err) {
                setError(err.message);
                stopPolling();
            }
        };

        // Initial fetch
        setIsPolling(true);
        poll();

        // Start interval
        intervalRef.current = setInterval(poll, intervalMs);

        return () => stopPolling();
    }, [jobId, intervalMs, stopPolling]);

    return { job, error, isPolling };
}
