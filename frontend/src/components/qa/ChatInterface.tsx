import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { QueryResponse } from '../../types';
import { askQuestion, getQueryHistory } from '../../api/queries';
import ChatMessage from './ChatMessage';
import EmptyState from '../common/EmptyState';
import { MessageSquare } from 'lucide-react';

interface ChatInterfaceProps {
  documentId: string;
}

export default function ChatInterface({ documentId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<QueryResponse[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const res = await getQueryHistory(documentId);
        setMessages(res.items);
      } catch {
        // History load failure is non-critical
      } finally {
        setIsLoadingHistory(false);
      }
    };
    loadHistory();
  }, [documentId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || isLoading) return;

    setInput('');
    setIsLoading(true);

    try {
      const response = await askQuestion(documentId, question);
      setMessages((prev) => [...prev, response]);
    } catch {
      // Show a placeholder error message
      const errorMsg: QueryResponse = {
        id: crypto.randomUUID(),
        question,
        answer: 'Sorry, I was unable to process your question. Please try again.',
        source_chunks: [],
        confidence: 'low',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[500px] flex-col rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoadingHistory ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : messages.length === 0 ? (
          <EmptyState
            icon={<MessageSquare className="mx-auto h-10 w-10" />}
            title="Ask a question"
            description="Ask anything about this document and get AI-powered answers with source citations."
          />
        ) : (
          <div className="space-y-6">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 border-t border-gray-200 p-4 dark:border-gray-700"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this document..."
          className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="rounded-lg bg-indigo-600 p-2 text-white transition-colors hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Send question"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
