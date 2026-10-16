'use client';

import { useEffect, useRef, useState } from 'react';
import { FileUp, Loader2 } from 'lucide-react';
import { useAuthStore } from '@/lib/stores/auth-store';
import { authenticatedFetch } from '@/lib/api/authenticated-fetch';
import { useQueryClient } from '@tanstack/react-query';
import { AiIndexedDocuments, indexedDocumentsKey } from './ai-indexed-documents';

export function AiDocumentUpload({ workspaceId }: { workspaceId: string | null }) {
  const queryClient = useQueryClient();
  const input = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  useEffect(() => {
    const open = () => input.current?.click();
    window.addEventListener('ai-add-document', open);
    return () => window.removeEventListener('ai-add-document', open);
  }, []);
  async function upload(file?: File) {
    if (!file || !workspaceId) return;
    setBusy(true);
    setMessage('Indexing document for answers with sources…');
    try {
      const form = new FormData();
      form.append('workspace_id', workspaceId);
      form.append('file', file);
      const response = await authenticatedFetch('/api/ai/v1/retrieval/upload', {
        method: 'POST', body: form,
        headers: { Authorization: `Bearer ${useAuthStore.getState().accessToken}` },
      });
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Indexing failed. Please retry.');
      setMessage(`${result.filename}: ${result.indexed_chunks} chunks indexed. Ask a question about this file.`);
      await queryClient.invalidateQueries({ queryKey: indexedDocumentsKey(workspaceId) });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setBusy(false);
      if (input.current) input.current.value = '';
    }
  }
  return (
    <div>
    <div className="flex items-center gap-3 border-b border-krait-border px-4 py-2 text-xs text-text-secondary">
      <input ref={input} type="file" className="hidden" accept=".pdf,.txt,.md,.py,.js,.ts,.tsx,.jsx,.json,.csv,.yml,.yaml,.java,.go,.rs" onChange={e => upload(e.target.files?.[0])} />
      <button disabled={busy || !workspaceId} onClick={() => input.current?.click()} className="flex shrink-0 items-center gap-2 rounded-md px-2 py-1 hover:bg-white/5 disabled:opacity-50">
        {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileUp className="h-4 w-4" />} Add knowledge
      </button>
      <span role="status" className="truncate">{message || 'PDF, text, or code · 5 MB maximum · Powered by Groq'}</span>
    </div>
    <AiIndexedDocuments workspaceId={workspaceId} />
    </div>
  );
}
