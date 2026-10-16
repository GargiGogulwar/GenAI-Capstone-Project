'use client';

import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/stores/auth-store';

export function AiProvidersView() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['groq-capabilities'],
    queryFn: async () => {
      const response = await fetch('/api/ai/v1/retrieval/capabilities', {
        headers: { Authorization: `Bearer ${useAuthStore.getState().accessToken}` },
      });
      if (!response.ok) throw new Error('Could not load AI configuration');
      return response.json() as Promise<{ configured: boolean; model: string; fast_model: string; concepts: string[] }>;
    },
  });
  return (
    <section className="space-y-5 p-6 text-text-primary">
      <h2 className="text-lg font-semibold">Groq AI</h2>
      <p className="text-sm text-text-secondary">One server key powers chat, repository reviews, specialist agents, and summaries. Document embeddings run locally.</p>
      {isLoading ? <p>Checking configuration…</p> : error ? <p role="alert">{error.message}</p> : (
        <>
          <p role="status">{data?.configured ? 'Groq key configured' : 'Set GROQ_API_KEY in the server .env file, then restart the AI service.'}</p>
          <dl className="space-y-2 text-sm">
            <div><dt className="text-text-secondary">Primary model</dt><dd>{data?.model}</dd></div>
            <div><dt className="text-text-secondary">Fast model</dt><dd>{data?.fast_model}</dd></div>
            <div><dt className="text-text-secondary">Retrieval</dt><dd>Local MiniLM embeddings + PostgreSQL pgvector + full-text search</dd></div>
          </dl>
          <div className="flex flex-wrap gap-2">{data?.concepts.map(concept => <span key={concept} className="rounded border border-krait-border px-2 py-1 text-xs">{concept}</span>)}</div>
        </>
      )}
    </section>
  );
}
