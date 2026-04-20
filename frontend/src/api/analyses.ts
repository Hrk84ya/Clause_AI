import apiClient from './client';
import { AnalysisResponse, SummaryResponse, CompareResponse } from '../types';

export const getAnalysis = async (documentId: string): Promise<AnalysisResponse> => {
  const { data } = await apiClient.get<AnalysisResponse>(`/analyses/${documentId}`);
  return data;
};

export const getSummary = async (
  documentId: string,
  level: string = 'standard'
): Promise<SummaryResponse> => {
  const { data } = await apiClient.get<SummaryResponse>(`/analyses/${documentId}/summary`, {
    params: { level },
  });
  return data;
};

export const compareDocuments = async (
  docIdA: string,
  docIdB: string
): Promise<CompareResponse> => {
  const { data } = await apiClient.post<CompareResponse>(`/analyses/${docIdA}/compare`, {
    compare_with_document_id: docIdB,
  });
  return data;
};
