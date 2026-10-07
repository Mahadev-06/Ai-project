import { useState, useEffect, useCallback } from 'react';
import { AnalysisResponse } from '../types/api';
import { getHistory, saveHistory, deleteHistoryItem, clearHistory } from '../lib/db';

export function useHistory() {
  const [history, setHistory] = useState<AnalysisResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getHistory();
      setHistory(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const add = async (item: AnalysisResponse) => {
    await saveHistory(item);
    await loadHistory();
  };

  const remove = async (id: string) => {
    await deleteHistoryItem(id);
    await loadHistory();
  };

  const clear = async () => {
    await clearHistory();
    await loadHistory();
  };

  return { history, loading, add, remove, clear, refresh: loadHistory };
}
