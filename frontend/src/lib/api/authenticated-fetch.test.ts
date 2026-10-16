import { afterEach, expect, it, vi } from 'vitest';
import { authenticatedFetch } from './authenticated-fetch';
import { tryRefreshToken } from './client';

vi.mock('./client', () => ({ tryRefreshToken: vi.fn() }));
afterEach(() => { vi.unstubAllGlobals(); vi.clearAllMocks(); });

it('refreshes an expired upload session and preserves its body and cancellation signal', async () => {
  const form = new FormData();
  form.append('file', new File(['example'], 'notes.md'));
  const signal = new AbortController().signal;
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(new Response(null, { status: 401 }))
    .mockResolvedValueOnce(new Response('{}', { status: 200 }));
  vi.stubGlobal('fetch', fetchMock);
  vi.mocked(tryRefreshToken).mockResolvedValue('fresh-token');
  expect((await authenticatedFetch('/api/ai/v1/retrieval/upload', {
    method: 'POST', body: form, signal, headers: { Authorization: 'Bearer expired' },
  })).status).toBe(200);
  const options = fetchMock.mock.calls[1][1];
  expect(options.body).toBe(form);
  expect(options.signal).toBe(signal);
  expect(options.headers.get('Authorization')).toBe('Bearer fresh-token');
  expect(options.headers.has('Content-Type')).toBe(false);
});

it('does not replay a request rejected by Groq quota controls', async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 429 }));
  vi.stubGlobal('fetch', fetchMock);
  expect((await authenticatedFetch('/api/ai/v1/chat', { method: 'POST' })).status).toBe(429);
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(tryRefreshToken).not.toHaveBeenCalled();
});
