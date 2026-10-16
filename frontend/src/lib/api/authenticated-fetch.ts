import { tryRefreshToken } from './client';

/** Retry once after the shared cookie-based refresh; preserve streams and uploads. */
export async function authenticatedFetch(url: string, init: RequestInit = {}): Promise<Response> {
  let response = await fetch(url, init);
  if (response.status === 401 && !init.signal?.aborted) {
    const token = await tryRefreshToken();
    if (token) {
      const headers = new Headers(init.headers);
      headers.set('Authorization', `Bearer ${token}`);
      response = await fetch(url, { ...init, headers });
    }
  }
  return response;
}
