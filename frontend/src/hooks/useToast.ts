import { useUIStore } from '../store/uiStore';

/**
 * Convenience hook for toast notifications.
 */
export const useToast = () => {
  const addToast = useUIStore((s) => s.addToast);
  const removeToast = useUIStore((s) => s.removeToast);
  const toasts = useUIStore((s) => s.toasts);

  return {
    toasts,
    success: (message: string) => addToast(message, 'success'),
    error: (message: string) => addToast(message, 'error'),
    info: (message: string) => addToast(message, 'info'),
    remove: removeToast,
  };
};
