import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  skipTrailingSlashRedirect: true,
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      '@phosphor-icons/react',
    ],
  },
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'kraivor-uploads.s3.amazonaws.com' },
      { protocol: 'https', hostname: 'avatars.githubusercontent.com' },
      { protocol: 'https', hostname: 'lh3.googleusercontent.com' },
      { protocol: 'http', hostname: 'localhost' },
    ],
  },
  logging: {
    fetches: {
      fullUrl: process.env.NODE_ENV === 'development',
    },
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  async rewrites() {
    return { beforeFiles: [], afterFiles: [
      { source: '/analysis-api/:path*', destination: 'http://analysis:8003/:path*' },
      // Resolve Core APIs before workspace pages such as /[workspace]/community.
      ...['community', 'projects', 'knowledge', 'notifications', 'search', 'chat', 'oauth', 'github-app'].map(service => ({
        source: `/api/${service}/:path*`, destination: `http://core:8002/api/${service}/:path*/`,
      })),
      { source: '/api/profiles/:path*', destination: 'http://identity:8001/api/profiles/:path*/' },
      {
        source: '/s3-proxy/:path*',
        destination: 'https://kraivor-uploads.s3.amazonaws.com/:path*',
      },
      {
        source: '/api/auth/refresh',
        destination: 'http://identity:8001/api/auth/refresh/',
      },
      {
        source: '/api/auth/:path*',
        destination: 'http://identity:8001/api/auth/:path*/',
      },
      {
        source: '/api/workspaces',
        destination: 'http://core:8002/api/workspaces/',
      },
      {
        source: '/api/workspaces/:path*',
        destination: 'http://core:8002/api/workspaces/:path*/',
      },
    ], fallback: [
      { source: '/api/:path*', destination: 'http://core:8002/api/:path*/' },
    ] };
  },
};

export default nextConfig;
