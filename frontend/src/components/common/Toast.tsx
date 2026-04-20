import { X, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { useUIStore } from '../../store/uiStore';

const iconMap = {
  success: <CheckCircle className="h-5 w-5 text-green-500" />,
  error: <AlertTriangle className="h-5 w-5 text-red-500" />,
  info: <Info className="h-5 w-5 text-blue-500" />,
};

const bgMap = {
  success: 'bg-green-50 border-green-200 dark:bg-green-900/30 dark:border-green-800',
  error: 'bg-red-50 border-red-200 dark:bg-red-900/30 dark:border-red-800',
  info: 'bg-blue-50 border-blue-200 dark:bg-blue-900/30 dark:border-blue-800',
};

export default function ToastContainer() {
  const toasts = useUIStore((s) => s.toasts);
  const removeToast = useUIStore((s) => s.removeToast);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 rounded-lg border px-4 py-3 shadow-lg transition-all ${bgMap[toast.type]}`}
        >
          {iconMap[toast.type]}
          <span className="text-sm text-gray-800 dark:text-gray-200">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="ml-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Dismiss notification"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
