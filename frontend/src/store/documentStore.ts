import { create } from 'zustand';
import {
  DocumentSummary,
  DocumentDetail,
  DocumentFilters,
  DocumentUploadResponse,
} from '../types';
import * as docApi from '../api/documents';

interface DocumentState {
  documents: DocumentSummary[];
  currentDocument: DocumentDetail | null;
  total: number;
  page: number;
  pageSize: number;
  pages: number;
  filters: DocumentFilters;
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;
  fetchDocuments: (filters?: DocumentFilters) => Promise<void>;
  fetchDocument: (id: string) => Promise<void>;
  uploadDocument: (file: File) => Promise<DocumentUploadResponse>;
  deleteDocument: (id: string) => Promise<void>;
  setFilters: (filters: Partial<DocumentFilters>) => void;
  pollStatus: (id: string) => Promise<string>;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  currentDocument: null,
  total: 0,
  page: 1,
  pageSize: 10,
  pages: 0,
  filters: {},
  isLoading: false,
  isUploading: false,
  error: null,

  fetchDocuments: async (filters) => {
    set({ isLoading: true, error: null });
    try {
      const mergedFilters = { ...get().filters, ...filters };
      const res = await docApi.listDocuments(mergedFilters);
      set({
        documents: res.items,
        total: res.total,
        page: res.page,
        pageSize: res.page_size,
        pages: res.pages,
        filters: mergedFilters,
        isLoading: false,
      });
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to load documents.';
      set({ error: message, isLoading: false });
    }
  },

  fetchDocument: async (id) => {
    set({ isLoading: true, error: null, currentDocument: null });
    try {
      const doc = await docApi.getDocument(id);
      set({ currentDocument: doc, isLoading: false });
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to load document.';
      set({ error: message, isLoading: false });
    }
  },

  uploadDocument: async (file) => {
    set({ isUploading: true, error: null });
    try {
      const res = await docApi.uploadDocument(file);
      set({ isUploading: false });
      return res;
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Upload failed.';
      set({ error: message, isUploading: false });
      throw new Error(message);
    }
  },

  deleteDocument: async (id) => {
    try {
      await docApi.deleteDocument(id);
      set((state) => ({
        documents: state.documents.filter((d) => d.id !== id),
        total: state.total - 1,
      }));
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to delete document.';
      set({ error: message });
      throw new Error(message);
    }
  },

  setFilters: (filters) =>
    set((state) => ({ filters: { ...state.filters, ...filters } })),

  pollStatus: async (id) => {
    const res = await docApi.getDocumentStatus(id);
    return res.status;
  },
}));
