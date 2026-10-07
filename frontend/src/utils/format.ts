import { ClaimOutcome } from '../types/api';

export function formatDate(isoString: string): string {
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return isoString;
  }
}

export function formatDateTime(isoString: string): string {
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

export function truncateText(text: string, maxLen: number): string {
  if (!text || text.length <= maxLen) return text || '';
  return text.slice(0, maxLen) + '...';
}

export function getOutcomeDisplay(outcome: ClaimOutcome): string {
  switch (outcome) {
    case 'supported':
      return 'Supported';
    case 'contradicted':
      return 'Contradicted';
    case 'conflicting':
      return 'Conflicting Evidence';
    case 'insufficient':
      return 'Insufficient Evidence';
    case 'not_checkable':
      return 'Not Checkable';
    default:
      return 'Unknown';
  }
}

export function cleanReason(reason?: string): string {
  if (!reason) return '';
  return reason.replace(/\s*\([a-z0-9\-_,\s]+\)\./gi, '.').trim();
}

