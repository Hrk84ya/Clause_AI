/**
 * Format an ISO date string to a human-readable format.
 */
export const formatDate = (iso: string): string => {
  const date = new Date(iso);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format an ISO date string to include time.
 */
export const formatDateTime = (iso: string): string => {
  const date = new Date(iso);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Format a relative time string (e.g., "2 hours ago").
 */
export const formatRelativeTime = (iso: string): string => {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatDate(iso);
};

/**
 * Format a risk score (0-100) to a display string.
 */
export const formatRiskScore = (score: number | null): string => {
  if (score === null || score === undefined) return 'N/A';
  return `${Math.round(score)}/100`;
};

/**
 * Get a risk label from a numeric score.
 */
export const getRiskLabel = (score: number | null): string => {
  if (score === null || score === undefined) return 'Unknown';
  if (score >= 80) return 'Critical';
  if (score >= 60) return 'High';
  if (score >= 40) return 'Medium';
  if (score >= 20) return 'Low';
  return 'Minimal';
};

/**
 * Get a risk color class from a numeric score.
 */
export const getRiskColor = (score: number | null): string => {
  if (score === null || score === undefined) return 'text-gray-500';
  if (score >= 80) return 'text-red-600 dark:text-red-400';
  if (score >= 60) return 'text-orange-600 dark:text-orange-400';
  if (score >= 40) return 'text-yellow-600 dark:text-yellow-400';
  if (score >= 20) return 'text-blue-600 dark:text-blue-400';
  return 'text-green-600 dark:text-green-400';
};

/**
 * Format file size in bytes to a human-readable string.
 */
export const formatFileSize = (bytes: number | null): string => {
  if (bytes === null || bytes === undefined) return 'Unknown';
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, i);
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
};

/**
 * Capitalize the first letter of a string.
 */
export const capitalize = (s: string): string => {
  return s.charAt(0).toUpperCase() + s.slice(1);
};

/**
 * Format a doc_type slug to a display string.
 */
export const formatDocType = (docType: string | null): string => {
  if (!docType) return 'Unknown';
  return docType
    .split('_')
    .map((w) => capitalize(w))
    .join(' ');
};
