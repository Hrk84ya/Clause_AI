import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Shield, AlertTriangle, Upload, ArrowRight } from 'lucide-react';
import { useDocumentStore } from '../store/documentStore';
import { useToast } from '../hooks/useToast';
import DocumentCard from '../components/document/DocumentCard';
import DropZone from '../components/upload/DropZone';
import { SkeletonCard } from '../components/common/Skeleton';

export default function Dashboard() {
  const { documents, total, isLoading, fetchDocuments, uploadDocument } = useDocumentStore();
  const [showUpload, setShowUpload] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    fetchDocuments({ page: 1, page_size: 5 });
  }, [fetchDocuments]);

  const completedCount = documents.filter((d) => d.status === 'completed').length;
  const atRiskCount = documents.filter(
    (d) => d.risk_score !== null && d.risk_score >= 60
  ).length;

  const handleUpload = async (file: File) => {
    try {
      const res = await uploadDocument(file);
      toast.success('Document uploaded! Processing will begin shortly.');
      navigate(`/documents/${res.document_id}`);
    } catch (err: unknown) {
      toast.error((err as Error).message || 'Upload failed.');
    }
  };

  const metrics = [
    {
      label: 'Total Documents',
      value: total,
      icon: FileText,
      color: 'text-indigo-600 dark:text-indigo-400',
      bg: 'bg-indigo-50 dark:bg-indigo-900/30',
    },
    {
      label: 'Analyses Complete',
      value: completedCount,
      icon: Shield,
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-50 dark:bg-green-900/30',
    },
    {
      label: 'At-Risk Documents',
      value: atRiskCount,
      icon: AlertTriangle,
      color: 'text-orange-600 dark:text-orange-400',
      bg: 'bg-orange-50 dark:bg-orange-900/30',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          <Upload className="h-4 w-4" />
          Upload Document
        </button>
      </div>

      {showUpload && (
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <DropZone onUpload={handleUpload} />
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800"
          >
            <div className="flex items-center gap-3">
              <div className={`rounded-lg p-2 ${metric.bg}`}>
                <metric.icon className={`h-5 w-5 ${metric.color}`} />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{metric.label}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{metric.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Documents */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Recent Documents
          </h2>
          <button
            onClick={() => navigate('/documents')}
            className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
          >
            View all <ArrowRight className="h-4 w-4" />
          </button>
        </div>

        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center dark:border-gray-700 dark:bg-gray-800">
            <FileText className="mx-auto mb-3 h-10 w-10 text-gray-400" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No documents yet. Upload your first document to get started.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {documents.slice(0, 5).map((doc) => (
              <DocumentCard key={doc.id} document={doc} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
