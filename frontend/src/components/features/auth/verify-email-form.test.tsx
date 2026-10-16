import { afterEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { VerifyEmailForm } from './verify-email-form';

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams('email=recipient%40example.test'),
}));
vi.mock('@/lib/hooks', () => ({ useAuth: () => ({ verifyEmail: vi.fn() }) }));
vi.mock('@/lib/api', () => ({ isApiError: () => false }));
afterEach(() => { vi.unstubAllGlobals(); vi.unstubAllEnvs(); });

it('resends through the local API when no public API URL is configured', async () => {
  vi.stubEnv('NEXT_PUBLIC_API_URL', '');
  const request = vi.fn().mockResolvedValue(Response.json({ message: 'Verification email resent.' }));
  vi.stubGlobal('fetch', request);
  render(<VerifyEmailForm />);
  fireEvent.click(screen.getByRole('button', { name: /^resend$/i }));
  await waitFor(() => expect(request).toHaveBeenCalledWith('/api/auth/resend-verification/', expect.objectContaining({
    method: 'POST', body: JSON.stringify({ email: 'recipient@example.test' }),
  })));
  expect(await screen.findByText('Verification email resent.')).toBeInTheDocument();
});
