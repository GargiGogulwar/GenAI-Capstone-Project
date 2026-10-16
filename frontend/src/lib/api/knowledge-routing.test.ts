import { expect, it } from 'vitest';
import nextConfig from '../../../next.config';

it('routes knowledge detail, asset, and save requests to Core before matching workspace pages', async () => {
  const rewrites = await nextConfig.rewrites!();
  expect(rewrites).toHaveProperty('afterFiles');
  if (Array.isArray(rewrites)) throw new Error('Expected ordered rewrite groups');
  expect(rewrites.afterFiles).toContainEqual({
    source: '/api/knowledge/:path*',
    destination: 'http://core:8002/api/knowledge/:path*/',
  });
});
