import { DocumentDetail } from '../../types';
import RiskGauge from '../document/RiskGauge';
import { formatDate, formatFileSize, formatDocType } from '../../utils/formatters';

interface SummaryPanelProps {
  document: DocumentDetail;
  summary?: string | null;
}

export default function SummaryPanel({ document, summary }: SummaryPanelProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Risk Score */}
      <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <h3 className="mb-4 text-sm font-semibold text-gray-500 dark:text-gray-400">Risk Score</h3>
        <RiskGauge score={document.analysis?.risk_score ?? document.risk_score} />
      </div>

      {/* Metadata */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <h3 className="mb-4 text-sm font-semibold text-gray-500 dark:text-gray-400">
          Document Info
        </h3>
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Type</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {formatDocType(document.doc_type)}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Pages</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {document.page_count ?? '—'}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Size</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {formatFileSize(document.file_size_bytes)}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Uploaded</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {formatDate(document.created_at)}
            </dd>
          </div>
          {document.parties.length > 0 && (
            <div className="flex justify-between">
              <dt className="text-gray-500 dark:text-gray-400">Parties</dt>
              <dd className="text-right font-medium text-gray-900 dark:text-white">
                {document.parties.join(', ')}
              </dd>
            </div>
          )}
          {document.effective_date && (
            <div className="flex justify-between">
              <dt className="text-gray-500 dark:text-gray-400">Effective</dt>
              <dd className="font-medium text-gray-900 dark:text-white">
                {formatDate(document.effective_date)}
              </dd>
            </div>
          )}
          {document.expiry_date && (
            <div className="flex justify-between">
              <dt className="text-gray-500 dark:text-gray-400">Expires</dt>
              <dd className="font-medium text-gray-900 dark:text-white">
                {formatDate(document.expiry_date)}
              </dd>
            </div>
          )}
        </dl>
      </div>

      {/* Analysis Stats */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <h3 className="mb-4 text-sm font-semibold text-gray-500 dark:text-gray-400">
          Analysis Stats
        </h3>
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Clauses Found</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {document.analysis?.clause_count ?? '—'}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Anomalies</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {document.analysis?.anomaly_count ?? '—'}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500 dark:text-gray-400">Words</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {document.word_count?.toLocaleString() ?? '—'}
            </dd>
          </div>
        </dl>
      </div>

      {/* Summary */}
      {summary && (
        <div className="rounded-lg border border-gray-200 bg-white p-6 lg:col-span-3 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-3 text-sm font-semibold text-gray-500 dark:text-gray-400">Summary</h3>
          <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">{summary}</p>
        </div>
      )}
    </div>
  );
}
