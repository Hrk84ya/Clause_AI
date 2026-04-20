import { useEffect, useState } from 'react';
import { GitCompare, Loader2, ArrowRight } from 'lucide-react';
import { useDocumentStore } from '../store/documentStore';
import { compareDocuments } from '../api/analyses';
import { CompareResponse } from '../types';
import { useToast } from '../hooks/useToast';
import EmptyState from '../components/common/EmptyState';
import RiskBadge from '../components/analysis/RiskBadge';
import { formatRiskScore, getRiskColor } from '../utils/formatters';

export default function Compare() {
  const { documents, fetchDocuments, isLoading: docsLoading } = useDocumentStore();
  const [docA, setDocA] = useState('');
  const [docB, setDocB] = useState('');
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const toast = useToast();

  useEffect(() => {
    fetchDocuments({ page: 1, page_size: 100 });
  }, [fetchDocuments]);

  const completedDocs = documents.filter((d) => d.status === 'completed');

  const handleCompare = async () => {
    if (!docA || !docB) {
      toast.error('Please select two documents to compare.');
      return;
    }
    if (docA === docB) {
      toast.error('Please select two different documents.');
      return;
    }

    setIsComparing(true);
    setResult(null);
    try {
      const data = await compareDocuments(docA, docB);
      setResult(data);
    } catch (err: unknown) {
      toast.error(
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          'Comparison failed.'
      );
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Compare Documents</h1>

      {/* Selectors */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex flex-col items-center gap-4 sm:flex-row">
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Document A
            </label>
            <select
              value={docA}
              onChange={(e) => setDocA(e.target.value)}
              disabled={docsLoading}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Select a document...</option>
              {completedDocs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.title}
                </option>
              ))}
            </select>
          </div>

          <ArrowRight className="mt-5 hidden h-5 w-5 text-gray-400 sm:block" />

          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Document B
            </label>
            <select
              value={docB}
              onChange={(e) => setDocB(e.target.value)}
              disabled={docsLoading}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Select a document...</option>
              {completedDocs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.title}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleCompare}
            disabled={!docA || !docB || isComparing}
            className="mt-5 flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isComparing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <GitCompare className="h-4 w-4" />
            )}
            Compare
          </button>
        </div>
      </div>

      {/* Results */}
      {isComparing && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          <span className="ml-3 text-sm text-gray-500 dark:text-gray-400">
            Comparing documents...
          </span>
        </div>
      )}

      {result && !isComparing && (
        <div className="space-y-6">
          {/* Score comparison */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
              <h3 className="mb-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                Document A
              </h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {result.document_a.title}
              </p>
              <p className={`mt-1 text-sm font-medium ${getRiskColor(result.document_a.risk_score)}`}>
                Risk: {formatRiskScore(result.document_a.risk_score)}
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
              <h3 className="mb-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                Document B
              </h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {result.document_b.title}
              </p>
              <p className={`mt-1 text-sm font-medium ${getRiskColor(result.document_b.risk_score)}`}>
                Risk: {formatRiskScore(result.document_b.risk_score)}
              </p>
            </div>
          </div>

          {/* Summary */}
          {result.summary && (
            <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
              <h3 className="mb-3 text-sm font-semibold text-gray-500 dark:text-gray-400">
                Comparison Summary
              </h3>
              <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                {result.summary}
              </p>
            </div>
          )}

          {/* Differences table */}
          {result.differences.length > 0 && (
            <div className="overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
              <div className="border-b border-gray-200 px-6 py-4 dark:border-gray-700">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                  Key Differences
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50">
                    <tr>
                      <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                        Field
                      </th>
                      <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                        Document A
                      </th>
                      <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                        Document B
                      </th>
                      <th className="px-4 py-3 font-medium text-gray-500 dark:text-gray-400">
                        Significance
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {result.differences.map((diff, i) => (
                      <tr key={i}>
                        <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">
                          {diff.field.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </td>
                        <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                          {diff.document_a_value}
                        </td>
                        <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                          {diff.document_b_value}
                        </td>
                        <td className="px-4 py-3">
                          <RiskBadge level={diff.significance} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Unique clauses */}
          <div className="grid gap-4 sm:grid-cols-2">
            {result.clauses_only_in_a.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
                <h3 className="mb-3 text-sm font-semibold text-gray-500 dark:text-gray-400">
                  Only in Document A
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.clauses_only_in_a.map((clause) => (
                    <span
                      key={clause}
                      className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
                    >
                      {clause.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {result.clauses_only_in_b.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
                <h3 className="mb-3 text-sm font-semibold text-gray-500 dark:text-gray-400">
                  Only in Document B
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.clauses_only_in_b.map((clause) => (
                    <span
                      key={clause}
                      className="rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-700 dark:bg-purple-900/40 dark:text-purple-300"
                    >
                      {clause.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {result.differences.length === 0 &&
            result.clauses_only_in_a.length === 0 &&
            result.clauses_only_in_b.length === 0 && (
              <EmptyState
                icon={<GitCompare className="mx-auto h-10 w-10" />}
                title="No significant differences"
                description="These documents appear to be very similar."
              />
            )}
        </div>
      )}

      {!result && !isComparing && (
        <EmptyState
          icon={<GitCompare className="mx-auto h-12 w-12" />}
          title="Compare two documents"
          description="Select two analyzed documents above to see a side-by-side comparison of their clauses, risks, and key terms."
        />
      )}
    </div>
  );
}
