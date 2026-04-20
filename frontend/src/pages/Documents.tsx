import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Search, Trash2, FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { useDocumentStore } from '../store/documentStore';
import { useToast } from '../hooks/useToast';
import StatusBadge from '../components/document/StatusBadge';
import DropZone from '../components/upload/DropZone';
import EmptyState from '../components/common/EmptyState';
import { SkeletonTable } from '../components/common/Skeleton';
import { formatDate, formatDocType, formatRiskScore, getRiskColor } from '../utils/formatters';
import { DocType, RiskLevel } from '../types';

export default function Documents() {
  const {
    documents,
    total,
    page,
    pages,
    isLoading,
    fetchDocuments,
    deleteDocument,
    uploadDocument,
  } = useDocumentStore();
  const [showUpload, setShowUpload] = useState(false);
  const [search, setSearch] = useState('');
  const [docType, setDocType] = useState<DocType | ''>('');
  const [riskLevel, setRiskLevel] = useState<RiskLevel | ''>('');
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    fetchDocuments({ page: 1, page_size: 10 });
  }, [fetchDocuments]);

  const handleSearch = () => {
    fetchDocuments({
      q: search || undefined,
      doc_type: docType || undefined,
      risk_level: riskLevel || undefined,
      page: 1,
      page_size: 10,
    });
  };

  const handlePageChange = (newPage: number) => {
    fetchDocuments({
      q: search || undefined,
      doc_type: docType || undefined,
      risk_level: riskLevel || undefined,
      page: newPage,
      page_size: 10,
    });
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      toast.success('Document deleted.');
      setDeleteConfirm(null);
    } catch (err: unknown) {
      toast.error((err as Error).message || 'Failed to delete document.');
    }
  };

  const handleUpload = async (file: File) => {
    try {
      const res = await uploadDocument(file);
      toast.success('Document uploaded!');
      setShowUpload(false);
      navigate(`/documents/${res.document_id}`);
    } catch (err: unknown) {
      toast.error((err as Error).message || 'Upload failed.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Documents</h1>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          <Upload className="h-4 w-4" />
          Upload
        </button>
      </div>

      {showUpload && (
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <DropZone onUpload={handleUpload} />
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search documents..."
            className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-3 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value as DocType | '')}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        >
          <option value="">All Types</option>
          <option value="contract">Contract</option>
          <option value="nda">NDA</option>
          <option value="lease">Lease</option>
          <option value="employment">Employment</option>
          <option value="terms_of_service">Terms of Service</option>
          <option value="privacy_policy">Privacy Policy</option>
          <option value="other">Other</option>
        </select>
        <select
          value={riskLevel}
          onChange={(e) => setRiskLevel(e.target.value as RiskLevel | '')}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        >
          <option value="">All Risk Levels</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button
          onClick={handleSearch}
          className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Filter
        </button>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <SkeletonTable rows={5} />
        </div>
      ) : documents.length === 0 ? (
        <EmptyState
          icon={<FileText className="mx-auto h-12 w-12" />}
          title="No documents found"
          description="Upload a document to get started with AI-powered analysis."
          action={
            <button
              onClick={() => setShowUpload(true)}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Upload Document
            </button>
          }
        />
      ) : (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50">
                <tr>
                  <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">Name</th>
                  <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">Type</th>
                  <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">Status</th>
                  <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">Risk</th>
                  <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">Date</th>
                  <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {documents.map((doc) => (
                  <tr
                    key={doc.id}
                    onClick={() => navigate(`/documents/${doc.id}`)}
                    className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span className="font-medium text-gray-900 dark:text-white">
                          {doc.title}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                      {formatDocType(doc.doc_type)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={doc.status} />
                    </td>
                    <td className="px-4 py-3">
                      <span className={getRiskColor(doc.risk_score)}>
                        {formatRiskScore(doc.risk_score)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                      {formatDate(doc.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      {deleteConfirm === doc.id ? (
                        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="text-xs font-medium text-red-600 hover:text-red-700"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="text-xs text-gray-500 hover:text-gray-700"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirm(doc.id);
                          }}
                          className="rounded p-1 text-gray-400 hover:text-red-500"
                          aria-label="Delete document"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3 dark:border-gray-700">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Showing {documents.length} of {total} documents
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page <= 1}
                  className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50 dark:text-gray-400 dark:hover:bg-gray-700"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {page} / {pages}
                </span>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page >= pages}
                  className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50 dark:text-gray-400 dark:hover:bg-gray-700"
                  aria-label="Next page"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
