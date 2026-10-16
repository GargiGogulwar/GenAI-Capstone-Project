import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, expect, it, vi } from 'vitest';
import { AiIndexedDocuments } from './ai-indexed-documents';
import { authenticatedFetch } from '@/lib/api/authenticated-fetch';

vi.mock('@/lib/api/authenticated-fetch', () => ({ authenticatedFetch: vi.fn() }));
afterEach(() => vi.clearAllMocks());

function renderDocuments() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}><AiIndexedDocuments workspaceId="workspace-a" /></QueryClientProvider>);
}

it('shows documents already indexed before the component mounts', async () => {
  vi.mocked(authenticatedFetch).mockResolvedValue(Response.json({ documents: [
    { document_id: 'abc', filename: 'layout.tsx', indexed_chunks: 1 },
  ] }));
  renderDocuments();
  expect(await screen.findByText('layout.tsx')).toBeInTheDocument();
  expect(screen.getByText('1 chunk indexed')).toBeInTheDocument();
  expect(authenticatedFetch).toHaveBeenCalledWith('/api/ai/v1/retrieval/documents?workspace_id=workspace-a', expect.any(Object));
});

it('shows a retryable error instead of claiming an unsuccessful list is empty', async () => {
  vi.mocked(authenticatedFetch).mockResolvedValue(new Response(null, { status: 503 }));
  renderDocuments();
  expect(await screen.findByRole('alert')).toHaveTextContent('Unable to load indexed documents');
  expect(screen.queryByText(/No indexed documents yet/)).not.toBeInTheDocument();
});
