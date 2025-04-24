/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverActions: true,
  },
  // Configure proxying of API requests to the FastAPI backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  // Allow image optimization for Supabase storage URLs if needed
  images: {
    domains: [
      // Add your Supabase project domain if you're using Storage
      // e.g. 'yourproject.supabase.co'
    ],
  },
};

export default nextConfig; 