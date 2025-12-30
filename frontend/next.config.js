/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false,
  compress: true,
  transpilePackages: ['three'],
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Enable WebAssembly support
  webpack: (config, { isServer }) => {
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
    };

    // WASM files should be treated as assets
    config.module.rules.push({
      test: /\.wasm$/,
      type: 'webassembly/async',
    });

    return config;
  },

  // Proxy API requests to backend
  async rewrites() {
    // Use Docker service name in production, localhost in development
    const backendUrl = process.env.BACKEND_URL || 'http://sentinel-vault-backend:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Removed redirect that was causing infinite loop
  // async redirects() {
  //   return [];
  // },
};

module.exports = nextConfig;
