import { RiskLevel } from '../../types';

const riskConfig: Record<string, { label: string; classes: string }> = {
  critical: {
    label: 'Critical',
    classes: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  },
  high: {
    label: 'High',
    classes: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  },
  medium: {
    label: 'Medium',
    classes: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
  },
  low: {
    label: 'Low',
    classes: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  },
  info: {
    label: 'Info',
    classes: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  },
};

interface RiskBadgeProps {
  level: RiskLevel | string | null;
}

export default function RiskBadge({ level }: RiskBadgeProps) {
  if (!level) return null;
  const config = riskConfig[level] || riskConfig.info;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.classes}`}
    >
      {config.label}
    </span>
  );
}
