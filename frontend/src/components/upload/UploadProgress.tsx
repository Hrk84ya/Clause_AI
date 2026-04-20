interface UploadProgressProps {
  progress: number; // 0-100
  label?: string;
}

export default function UploadProgress({ progress, label }: UploadProgressProps) {
  return (
    <div className="w-full">
      {label && (
        <div className="mb-1 flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">{label}</span>
          <span className="font-medium text-gray-900 dark:text-white">{Math.round(progress)}%</span>
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className="h-full rounded-full bg-indigo-600 transition-all duration-300"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
    </div>
  );
}
