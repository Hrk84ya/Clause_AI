import apiClient from './client';
import {
  DocumentUploadResponse,
  DocumentListResponse,
  DocumentDetail,
  DocumentStatusResponse,
  DocumentFilters,
} from '../types';

export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<DocumentUploadResponse>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const listDocuments = async (filters?: DocumentFilters): Promise<DocumentListResponse> => {
  const { data } = await apiClient.get<DocumentListResponse>('/documents', { params: filters });
  return data;
};

export const getDocument = async (id: string): Promise<DocumentDetail> => {
  const { data } = await apiClient.get<DocumentDetail>(`/documents/${id}`);
  return data;
};

export const getDocumentStatus = async (id: string): Promise<DocumentStatusResponse> => {
  const { data } = await apiClient.get<DocumentStatusResponse>(`/documents/${id}/status`);
  return data;
};

export const deleteDocument = async (id: string): Promise<void> => {
  await apiClient.delete(`/documents/${id}`);
};
