import { getRiskLabel, getRiskColor } from '../../utils/formatters';

interface RiskGaugeProps {
  score: number | null;
  size?: number;
}

export default function RiskGauge({ score, size = 120 }: RiskGaugeProps) {
  const normalizedScore = score !== null ? Math.min(100, Math.max(0, score)) : 0;
  const radius = (size - 16) / 2;
  const circumference = Math.PI * radius; // half circle
  const offset = circumference - (normalizedScore / 100) * circumference;
  const center = size / 2;

  const getStrokeColor = (s: number | null): string => {
    if (s === null) return '#9CA3AF';
    if (s >= 80) return '#DC2626';
    if (s >= 60) return '#EA580C';
    if (s >= 40) return '#CA8A04';
    if (s >= 20) return '#2563EB';
    return '#16A34A';
  };

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 16} viewBox={`0 0 ${size} ${size / 2 + 16}`}>
        {/* Background arc */}
        <path
          d={`M 8 ${center} A ${radius} ${radius} 0 0 1 ${size - 8} ${center}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-gray-200 dark:text-gray-700"
        />
        {/* Score arc */}
        <path
          d={`M 8 ${center} A ${radius} ${radius} 0 0 1 ${size - 8} ${center}`}
          fill="none"
          stroke={getStrokeColor(score)}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700"
        />
      </svg>
      <div className="-mt-4 text-center">
        <span className={`text-2xl font-bold ${getRiskColor(score)}`}>
          {score !== null ? Math.round(score) : '—'}
        </span>
        <p className="text-xs text-gray-500 dark:text-gray-400">{getRiskLabel(score)}</p>
      </div>
    </div>
  );
}
