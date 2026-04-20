import { create } from 'zustand';
import { Toast } from '../types';

interface UIState {
  isDarkMode: boolean;
  toasts: Toast[];
  toggleDarkMode: () => void;
  addToast: (message: string, type: Toast['type']) => void;
  removeToast: (id: string) => void;
}

const getInitialDarkMode = (): boolean => {
  if (typeof window === 'undefined') return false;
  const stored = localStorage.getItem('darkMode');
  if (stored !== null) return stored === 'true';
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

export const useUIStore = create<UIState>((set) => ({
  isDarkMode: getInitialDarkMode(),
  toasts: [],

  toggleDarkMode: () =>
    set((state) => {
      const next = !state.isDarkMode;
      localStorage.setItem('darkMode', String(next));
      if (next) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return { isDarkMode: next };
    }),

  addToast: (message, type) =>
    set((state) => {
      const id = crypto.randomUUID();
      const toast: Toast = { id, message, type };
      // Auto-remove after 5 seconds
      setTimeout(() => {
        useUIStore.getState().removeToast(id);
      }, 5000);
      return { toasts: [...state.toasts, toast] };
    }),

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));

// Initialize dark mode class on load
if (typeof window !== 'undefined') {
  if (getInitialDarkMode()) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}
