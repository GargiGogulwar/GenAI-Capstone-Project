'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText } from 'lucide-react';
import { authenticatedFetch } from '@/lib/api/authenticated-fetch';
import { useAuthStore } from '@/lib/stores/auth-store';

export interface IndexedDocument {
  document_id: string;
  filename: string;
  indexed_chunks: number;
}

export const indexedDocumentsKey = (workspaceId: string | null) => ['ai-indexed-documents', workspaceId];

export function AiIndexedDocuments({ workspaceId }: { workspaceId: string | null }) {
  const { data, isPending, error, refetch } = useQuery({
    queryKey: indexedDocumentsKey(workspaceId),
    enabled: !!workspaceId,
    queryFn: async () => {
      const token = useAuthStore.getState().accessToken;
      const response = await authenticatedFetch(`/api/ai/v1/retrieval/documents?workspace_id=${encodeURIComponent(workspaceId!)}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error('Unable to load indexed documents');
      return response.json() as Promise<{ documents: IndexedDocument[] }>;
    },
  });
  if (!workspaceId) return null;
  return (
    <details className="border-b border-krait-border px-4 py-2 text-xs text-text-secondary" open>
      <summary className="cursor-pointer font-medium text-text-primary">
        Indexed for AI chat{data ? ` (${data.documents.length})` : ''}
      </summary>
      <p className="mt-1 text-text-tertiary">These sources ground AI answers; canvas attachments are managed separately.</p>
      {isPending ? <p role="status" className="mt-2">Loading indexed documents…</p> : error ? (
        <div role="alert" className="mt-2">Unable to load indexed documents.{' '}
          <button onClick={() => void refetch()} className="text-venom-yellow">Retry</button>
        </div>
      ) : !data?.documents.length ? (
        <p className="mt-2">No indexed documents yet. Use Add knowledge in AI Agent to upload a file.</p>
      ) : (
        <ul className="mt-2 max-h-32 space-y-1 overflow-y-auto">
          {data.documents.map(document => (
            <li key={document.document_id} className="flex items-center gap-2">
              <FileText className="h-3 w-3 shrink-0" />
              <span className="min-w-0 flex-1 truncate" title={document.filename}>{document.filename}</span>
              <span className="shrink-0">{document.indexed_chunks} {document.indexed_chunks === 1 ? 'chunk' : 'chunks'} indexed</span>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}
