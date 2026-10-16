import { afterEach, expect, it, vi } from 'vitest';
import { coreApi } from './client';

vi.mock('@/lib/stores/auth-store', () => ({
  useAuthStore: { getState: () => ({ accessToken: null, clearAuth: vi.fn() }) },
}));

afterEach(() => vi.unstubAllGlobals());

it('rejects an HTML page returned with HTTP 200 instead of passing an empty object to components', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>Workspace page</html>', {
    status: 200, headers: { 'Content-Type': 'text/html' },
  })));
  await expect(coreApi.get('/community/')).rejects.toMatchObject({
    status: 502, code: 'invalid_response',
  });
});

it('keeps a valid empty discussion result as an empty list', async () => {
  const data = { results: [], total: 0, page: 1, page_size: 20 };
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json(data)));
  await expect(coreApi.get('/community/')).resolves.toEqual(data);
});
