import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, AlertTriangle } from 'lucide-react';
import { useDocumentStore } from '../store/documentStore';
import { useDocumentStatus } from '../hooks/useDocumentStatus';
import { useToast } from '../hooks/useToast';
import { getAnalysis } from '../api/analyses';
import { AnalysisResponse } from '../types';
import SummaryPanel from '../components/analysis/SummaryPanel';
import ClauseCard from '../components/analysis/ClauseCard';
import AnomalyAlert from '../components/analysis/AnomalyAlert';
import ChatInterface from '../components/qa/ChatInterface';
import ProcessingSpinner from '../components/document/ProcessingSpinner';
import { SkeletonCard } from '../components/common/Skeleton';

type Tab = 'overview' | 'clauses' | 'risks' | 'qa' | 'raw';

export default function DocumentView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { currentDocument, isLoading, fetchDocument } = useDocumentStore();
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const isProcessing =
    currentDocument?.status === 'pending' || currentDocument?.status === 'processing';

  const { status } = useDocumentStatus({
    documentId: id || null,
    enabled: isProcessing,
    onCompleted: () => {
      toast.success('Document analysis complete!');
      if (id) {
        fetchDocument(id);
        loadAnalysis(id);
      }
    },
    onFailed: (err) => {
      toast.error(err || 'Document processing failed.');
    },
  });

  useEffect(() => {
    if (id) {
      fetchDocument(id);
    }
  }, [id, fetchDocument]);

  useEffect(() => {
    if (currentDocument?.status === 'completed' && id) {
      loadAnalysis(id);
    }
  }, [currentDocument?.status, id]);

  const loadAnalysis = async (docId: string) => {
    setAnalysisLoading(true);
    try {
      const data = await getAnalysis(docId);
      setAnalysis(data);
    } catch {
      // Analysis may not be ready yet
    } finally {
      setAnalysisLoading(false);
    }
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'clauses', label: `Clauses${analysis ? ` (${analysis.clauses.length})` : ''}` },
    { key: 'risks', label: `Risks${analysis ? ` (${analysis.anomalies.length})` : ''}` },
    { key: 'qa', label: 'Q&A' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (!currentDocument) {
    return (
      <div className="py-16 text-center">
        <AlertTriangle className="mx-auto mb-4 h-10 w-10 text-gray-400" />
        <p className="text-gray-500 dark:text-gray-400">Document not found.</p>
        <button
          onClick={() => navigate('/documents')}
          className="mt-4 text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
        >
          Back to documents
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/documents')}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
          aria-label="Back to documents"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            {currentDocument.title}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {currentDocument.original_filename}
          </p>
        </div>
      </div>

      {/* Processing state */}
      {isProcessing && (
        <ProcessingSpinner
          message={
            status === 'processing'
              ? 'Analyzing document...'
              : 'Waiting to start processing...'
          }
        />
      )}

      {/* Failed state */}
      {currentDocument.status === 'failed' && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center dark:border-red-800 dark:bg-red-900/20">
          <AlertTriangle className="mx-auto mb-3 h-8 w-8 text-red-500" />
          <p className="font-medium text-red-800 dark:text-red-300">Processing Failed</p>
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {currentDocument.error_message || 'An error occurred during document analysis.'}
          </p>
        </div>
      )}

      {/* Completed state — tabs */}
      {currentDocument.status === 'completed' && (
        <>
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex gap-6">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`border-b-2 pb-3 text-sm font-medium transition-colors ${
                    activeTab === tab.key
                      ? 'border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {analysisLoading ? (
            <div className="space-y-4">
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : (
            <>
              {activeTab === 'overview' && (
                <SummaryPanel
                  document={currentDocument}
                  summary={analysis?.summary_standard}
                />
              )}

              {activeTab === 'clauses' && (
                <div className="space-y-3">
                  {analysis && analysis.clauses.length > 0 ? (
                    analysis.clauses.map((clause) => (
                      <ClauseCard key={clause.id} clause={clause} />
                    ))
                  ) : (
                    <div className="py-8 text-center">
                      <FileText className="mx-auto mb-3 h-8 w-8 text-gray-400" />
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        No clauses extracted yet.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'risks' && (
                <div className="space-y-3">
                  {analysis && analysis.anomalies.length > 0 ? (
                    analysis.anomalies.map((anomaly, i) => (
                      <AnomalyAlert key={i} anomaly={anomaly} />
                    ))
                  ) : (
                    <div className="py-8 text-center">
                      <AlertTriangle className="mx-auto mb-3 h-8 w-8 text-gray-400" />
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        No anomalies detected.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'qa' && id && <ChatInterface documentId={id} />}
            </>
          )}
        </>
      )}
    </div>
  );
}
