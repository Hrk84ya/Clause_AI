import { AlertTriangle, AlertCircle } from 'lucide-react';
import { Anomaly } from '../../types';

interface AnomalyAlertProps {
  anomaly: Anomaly;
}

export default function AnomalyAlert({ anomaly }: AnomalyAlertProps) {
  const isCritical = anomaly.severity === 'critical';

  return (
    <div
      className={`flex items-start gap-3 rounded-lg border p-4 ${
        isCritical
          ? 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
          : 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20'
      }`}
    >
      {isCritical ? (
        <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" />
      ) : (
        <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-yellow-500" />
      )}
      <div>
        <p
          className={`text-sm font-medium ${
            isCritical
              ? 'text-red-800 dark:text-red-300'
              : 'text-yellow-800 dark:text-yellow-300'
          }`}
        >
          {anomaly.anomaly_type
            .split('_')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ')}
        </p>
        <p
          className={`mt-1 text-sm ${
            isCritical
              ? 'text-red-700 dark:text-red-400'
              : 'text-yellow-700 dark:text-yellow-400'
          }`}
        >
          {anomaly.description}
        </p>
      </div>
    </div>
  );
}
