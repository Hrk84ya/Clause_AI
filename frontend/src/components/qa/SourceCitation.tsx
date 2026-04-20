import { useState } from 'react';
import { ChevronDown, ChevronRight, BookOpen } from 'lucide-react';
import { SourceChunk } from '../../types';

interface SourceCitationProps {
  sources: SourceChunk[];
}

export default function SourceCitation({ sources }: SourceCitationProps) {
  const [expanded, setExpanded] = useState(false);

  if (sources.length === 0) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
      >
        <BookOpen className="h-3 w-3" />
        {expanded ? (
          <ChevronDown className="h-3 w-3" />
        ) : (
          <ChevronRight className="h-3 w-3" />
        )}
        {sources.length} source{sources.length !== 1 ? 's' : ''}
      </button>

      {expanded && (
        <div className="mt-2 space-y-2">
          {sources.map((source, i) => (
            <div
              key={source.chunk_id || i}
              className="rounded border border-gray-200 bg-gray-50 p-3 dark:border-gray-600 dark:bg-gray-700/50"
            >
              {source.section_title && (
                <p className="mb-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                  {source.section_title}
                </p>
              )}
              <p className="text-xs text-gray-700 dark:text-gray-300">
                "{source.excerpt}"
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
