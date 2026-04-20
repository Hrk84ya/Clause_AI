import { User, Bot } from 'lucide-react';
import { QueryResponse } from '../../types';
import SourceCitation from './SourceCitation';

interface ChatMessageProps {
  message: QueryResponse;
}

const confidenceColors: Record<string, string> = {
  high: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
  low: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
};

export default function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div className="space-y-4">
      {/* User question */}
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 rounded-full bg-indigo-100 p-2 dark:bg-indigo-900/40">
          <User className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-900 dark:text-white">{message.question}</p>
        </div>
      </div>

      {/* Assistant answer */}
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 rounded-full bg-gray-100 p-2 dark:bg-gray-700">
          <Bot className="h-4 w-4 text-gray-600 dark:text-gray-400" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-700 dark:text-gray-300">{message.answer}</p>
          <div className="mt-2 flex items-center gap-2">
            <span
              className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                confidenceColors[message.confidence] || confidenceColors.medium
              }`}
            >
              {message.confidence} confidence
            </span>
          </div>
          <SourceCitation sources={message.source_chunks} />
        </div>
      </div>
    </div>
  );
}
