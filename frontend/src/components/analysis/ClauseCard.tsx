import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { Clause } from '../../types';
import RiskBadge from './RiskBadge';

interface ClauseCardProps {
  clause: Clause;
}

export default function ClauseCard({ clause }: ClauseCardProps) {
  const [expanded, setExpanded] = useState(false);

  const clauseLabel = clause.clause_type
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  return (
    <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-3">
          {expanded ? (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronRight className="h-4 w-4 text-gray-400" />
          )}
          <div>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {clauseLabel}
            </span>
            {clause.section_reference && (
              <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                {clause.section_reference}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {clause.page_number && (
            <span className="text-xs text-gray-400">p. {clause.page_number}</span>
          )}
          <RiskBadge level={clause.risk_level} />
        </div>
      </button>

      {expanded && (
        <div className="border-t border-gray-200 px-4 py-4 dark:border-gray-700">
          <div className="mb-3">
            <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Original Text
            </h4>
            <p className="text-sm italic text-gray-700 dark:text-gray-300">
              "{clause.verbatim_text}"
            </p>
          </div>

          {clause.plain_english && (
            <div className="mb-3">
              <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                Plain English
              </h4>
              <p className="text-sm text-gray-700 dark:text-gray-300">{clause.plain_english}</p>
            </div>
          )}

          {clause.risk_reason && (
            <div>
              <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                Risk Reason
              </h4>
              <p className="text-sm text-gray-700 dark:text-gray-300">{clause.risk_reason}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
