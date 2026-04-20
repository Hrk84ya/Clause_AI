import { Loader2 } from 'lucide-react';

interface ProcessingSpinnerProps {
  message?: string;
}

export default function ProcessingSpinner({
  message = 'Analyzing document...',
}: ProcessingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Loader2 className="mb-4 h-10 w-10 animate-spin text-indigo-600 dark:text-indigo-400" />
      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{message}</p>
      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        This may take a minute. The page will update automatically.
      </p>
    </div>
  );
}
