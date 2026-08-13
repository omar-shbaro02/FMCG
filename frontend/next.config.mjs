/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  poweredByHeader: false,
  turbopack: { root: process.cwd() },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_INTERNAL_URL || "http://api:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
