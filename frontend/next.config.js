/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Disable ESLint during builds
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable TypeScript during builds
    ignoreBuildErrors: true,
  },
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
    ENV: process.env.NEXT_PUBLIC_ENV || 'development',
    AUTH_ENABLED: process.env.NEXT_PUBLIC_AUTH_ENABLED || 'true',
    JWT_COOKIE_NAME: process.env.NEXT_PUBLIC_JWT_COOKIE_NAME || 'auth_token',
    ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS || 'true',
    ENABLE_NOTIFICATIONS: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS || 'false',
  },
  async rewrites() {
    return [
      // API routes
      {
        source: '/api/login',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/login`,
      },
      {
        source: '/api/domains',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/domains`,
      },
      {
        source: '/api/domains/:domain',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/domains/:domain`,
      },
      {
        source: '/api/metrics/:domain',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/metrics/:domain`,
      },
      // Fallback for any other API routes
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig; 