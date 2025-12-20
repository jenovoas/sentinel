/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false,
  compress: true,
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
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
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
