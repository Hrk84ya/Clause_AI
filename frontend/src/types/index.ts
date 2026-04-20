// User & Auth
export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterResponse {
  id: string;
  email: string;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Documents
export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type DocType = 'contract' | 'nda' | 'lease' | 'employment' | 'terms_of_service' | 'privacy_policy' | 'other';
export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface DocumentSummary {
  id: string;
  title: string;
  doc_type: DocType | null;
  status: DocumentStatus;
  page_count: number | null;
  word_count: number | null;
  risk_score: number | null;
  created_at: string;
}


export interface DocumentDetail extends DocumentSummary {
  original_filename: string;
  file_size_bytes: number | null;
  mime_type: string | null;
  parties: string[];
  effective_date: string | null;
  expiry_date: string | null;
  error_message: string | null;
  updated_at: string;
  analysis: {
    risk_score: number | null;
    clause_count: number;
    anomaly_count: number;
  } | null;
}

export interface DocumentUploadResponse {
  document_id: string;
  job_id: string;
  status: string;
  message: string;
}

export interface DocumentListResponse {
  items: DocumentSummary[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface DocumentStatusResponse {
  id: string;
  status: DocumentStatus;
  error_message: string | null;
}

// Analysis
export interface Clause {
  id: string;
  clause_type: string;
  verbatim_text: string;
  section_reference: string | null;
  page_number: number | null;
  plain_english: string | null;
  risk_level: RiskLevel | null;
  risk_reason: string | null;
}

export interface Anomaly {
  anomaly_type: 'missing_clause' | 'unusual_provision' | 'one_sided_language';
  description: string;
  severity: 'critical' | 'warning';
}

export interface AnalysisResponse {
  id: string;
  document_id: string;
  risk_score: number | null;
  summary_standard: string | null;
  clauses: Clause[];
  anomalies: Anomaly[];
}

export interface SummaryResponse {
  level: 'brief' | 'standard' | 'detailed';
  content: string;
}

export interface CompareResponse {
  document_a: { id: string; title: string; risk_score: number | null };
  document_b: { id: string; title: string; risk_score: number | null };
  differences: Array<{
    field: string;
    document_a_value: string;
    document_b_value: string;
    significance: string;
  }>;
  clauses_only_in_a: string[];
  clauses_only_in_b: string[];
  summary: string;
}

// Queries (RAG)
export interface SourceChunk {
  chunk_id: string;
  section_title: string | null;
  excerpt: string;
}

export interface QueryResponse {
  id: string;
  question: string;
  answer: string;
  source_chunks: SourceChunk[];
  confidence: 'high' | 'medium' | 'low';
  created_at: string;
}

// Jobs
export interface JobStatus {
  id: string;
  job_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

// UI
export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

// Filters
export interface DocumentFilters {
  doc_type?: DocType;
  risk_level?: RiskLevel;
  q?: string;
  page?: number;
  page_size?: number;
}