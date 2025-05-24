/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // Suppress known deprecation warnings
  onDemandEntries: {
    // period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 60 * 60 * 1000,
    // number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 100,
  },
  
  // Disable experimental features that might cause compilation issues
  experimental: {
    optimizeCss: false,
  },
  
  async rewrites() {
    return [
      {
        source: '/research/:path*',
        destination: process.env.BACKEND_URL ? 
          `${process.env.BACKEND_URL}/research/:path*` : 
          'http://localhost:8000/research/:path*'
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8001/api/:path*'
      }
    ];
  },
}

module.exports = nextConfig