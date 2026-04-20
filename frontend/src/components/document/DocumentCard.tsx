import { FileText, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { DocumentSummary } from '../../types';
import StatusBadge from './StatusBadge';
import { formatDate, formatDocType, formatRiskScore, getRiskColor } from '../../utils/formatters';

interface DocumentCardProps {
  document: DocumentSummary;
  onDelete?: (id: string) => void;
}

export default function DocumentCard({ document, onDelete }: DocumentCardProps) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/documents/${document.id}`)}
      className="group cursor-pointer rounded-lg border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-indigo-50 p-2 dark:bg-indigo-900/30">
            <FileText className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate text-sm font-medium text-gray-900 dark:text-white">
              {document.title}
            </h3>
            <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
              {formatDocType(document.doc_type)} · {formatDate(document.created_at)}
            </p>
          </div>
        </div>
        <StatusBadge status={document.status} />
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
          {document.page_count !== null && <span>{document.page_count} pages</span>}
          {document.risk_score !== null && (
            <span className={getRiskColor(document.risk_score)}>
              Risk: {formatRiskScore(document.risk_score)}
            </span>
          )}
        </div>
        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(document.id);
            }}
            className="rounded p-1 text-gray-400 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
            aria-label="Delete document"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
