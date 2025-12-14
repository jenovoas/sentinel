/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false,
  compress: true,
  async rewrites() {
    return {
      afterFiles: [
        {
          source: '/api/v1/:path*',
          destination: 'http://backend:8000/api/v1/:path*',
        },
      ],
    };
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async redirects() {
    return [
      {
        source: '/dashboard',
        destination: '/',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;
