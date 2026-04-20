import { useEffect, useRef, useState } from 'react';
import { getDocumentStatus } from '../api/documents';
import { DocumentStatus } from '../types';

interface UseDocumentStatusOptions {
  documentId: string | null;
  enabled?: boolean;
  interval?: number;
  onCompleted?: () => void;
  onFailed?: (error: string | null) => void;
}

/**
 * Polls document status every `interval` ms.
 * Stops when status is 'completed' or 'failed', or on unmount.
 */
export const useDocumentStatus = ({
  documentId,
  enabled = true,
  interval = 3000,
  onCompleted,
  onFailed,
}: UseDocumentStatusOptions) => {
  const [status, setStatus] = useState<DocumentStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!documentId || !enabled) return;

    const poll = async () => {
      try {
        const res = await getDocumentStatus(documentId);
        setStatus(res.status);

        if (res.status === 'completed') {
          clearTimer();
          onCompleted?.();
        } else if (res.status === 'failed') {
          clearTimer();
          setError(res.error_message);
          onFailed?.(res.error_message);
        }
      } catch {
        // Silently retry on network errors
      }
    };

    const clearTimer = () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };

    // Initial poll
    poll();
    timerRef.current = setInterval(poll, interval);

    return () => {
      clearTimer();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documentId, enabled, interval]);

  return { status, error };
};
