import { DocumentStatus } from '../../types';

const statusConfig: Record<DocumentStatus, { label: string; classes: string }> = {
  pending: {
    label: 'Pending',
    classes: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  },
  processing: {
    label: 'Processing',
    classes: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  },
  completed: {
    label: 'Completed',
    classes: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  },
  failed: {
    label: 'Failed',
    classes: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  },
};

interface StatusBadgeProps {
  status: DocumentStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.classes}`}
    >
      {status === 'processing' && (
        <span className="mr-1.5 h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
      )}
      {config.label}
    </span>
  );
}
