import apiClient from './client';
import { QueryResponse } from '../types';

export const askQuestion = async (
  documentId: string,
  question: string
): Promise<QueryResponse> => {
  const { data } = await apiClient.post<QueryResponse>(`/queries/${documentId}`, { question });
  return data;
};

export const getQueryHistory = async (
  documentId: string
): Promise<{ items: QueryResponse[] }> => {
  const { data } = await apiClient.get<{ items: QueryResponse[] }>(
    `/queries/${documentId}/history`
  );
  return data;
};
