import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { AnalysisResponse } from '../types/api';

interface ClaimLensDB extends DBSchema {
  history: {
    key: string;
    value: AnalysisResponse;
    indexes: { 'by-date': string };
  };
}

let dbPromise: Promise<IDBPDatabase<ClaimLensDB>> | null = null;

export function getDb() {
  if (!dbPromise) {
    dbPromise = openDB<ClaimLensDB>('claimlens-history', 2, {
      upgrade(db) {
        if (db.objectStoreNames.contains('history')) {
          db.deleteObjectStore('history');
        }
        const store = db.createObjectStore('history', { keyPath: 'id' });
        store.createIndex('by-date', 'created_at');
      },
    });
  }
  return dbPromise;
}

export async function saveReport(analysis: AnalysisResponse): Promise<void> {
  const db = await getDb();
  await db.put('history', analysis);
}

export const saveHistory = saveReport;

export async function getHistory(): Promise<AnalysisResponse[]> {
  const db = await getDb();
  const tx = db.transaction('history', 'readonly');
  const index = tx.store.index('by-date');
  const all = await index.getAll();
  return all.reverse(); // Newest first
}

export async function getReportById(id: string): Promise<AnalysisResponse | undefined> {
  const db = await getDb();
  return db.get('history', id);
}

export async function deleteHistoryItem(id: string): Promise<void> {
  const db = await getDb();
  await db.delete('history', id);
}

export async function clearHistory(): Promise<void> {
  const db = await getDb();
  await db.clear('history');
}
