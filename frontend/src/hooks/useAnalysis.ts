import { useState, useCallback, useRef, useEffect } from 'react';
import { AnalysisRequest, AnalysisResponse } from '../types/api';
import { apiClient } from '../api/client';
import { saveReport } from '../lib/db';

export function useAnalysis() {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollTimer = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (pollTimer.current) {
      clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }, []);

  const startPolling = useCallback((id: string) => {
    stopPolling();
    const POLL_INTERVAL = 500;
    let consecutiveErrors = 0;

    const poll = async () => {
      try {
        const result = await apiClient.getAnalysis(id);
        consecutiveErrors = 0;
        setAnalysis(result);

        if (['completed', 'partial', 'failed', 'cancelled'].includes(result.status)) {
          setLoading(false);
          // If completed with a report, save automatically to IndexedDB history
          if (result.status === 'completed' && result.report) {
            try {
              await saveReport(result);
            } catch (saveErr) {
              console.warn('Failed to save report to local history database:', saveErr);
            }
          }
          return;
        }

        pollTimer.current = window.setTimeout(poll, POLL_INTERVAL);
      } catch (err) {
        consecutiveErrors += 1;
        if (consecutiveErrors >= 5) {
          setError(err instanceof Error ? err.message : 'Polling status check failed');
          setLoading(false);
        } else {
          // Retry briefly on transient network blip
          pollTimer.current = window.setTimeout(poll, 800);
        }
      }
    };

    pollTimer.current = window.setTimeout(poll, 250);
  }, [stopPolling]);

  const submit = useCallback(async (req: AnalysisRequest): Promise<string> => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.submitAnalysis(req);
      setAnalysis(res);
      startPolling(res.id);
      return res.id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed');
      setLoading(false);
      throw err;
    }
  }, [startPolling]);

  const cancel = useCallback(async (id: string) => {
    stopPolling();
    try {
      await apiClient.cancelAnalysis(id);
      setAnalysis(prev => (prev ? { ...prev, status: 'cancelled', stage: 'cancelled' } : null));
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Cancellation failed');
    }
  }, [stopPolling]);

  const loadExisting = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.getAnalysis(id);
      setAnalysis(res);
      if (!['completed', 'partial', 'failed', 'cancelled'].includes(res.status)) {
        startPolling(res.id);
      } else {
        setLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analysis report');
      setLoading(false);
    }
  }, [startPolling]);

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return { submit, cancel, loadExisting, analysis, loading, error, setAnalysis };
}
