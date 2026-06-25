/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8200",
    NEXT_PUBLIC_WIDGET_KEY: process.env.NEXT_PUBLIC_WIDGET_KEY || "demo-public-key",
  },
};
export default nextConfig;
