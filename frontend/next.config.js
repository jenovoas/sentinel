/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  async rewrites() {
    return {
      afterFiles: [
        {
          source: '/api/v1/:path*',
          destination: 'http://host.docker.internal:8000/api/v1/:path*',
        },
      ],
    };
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  turbopack: { root: __dirname },
};

module.exports = nextConfig;
