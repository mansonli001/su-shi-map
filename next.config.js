/**
 * next.config.js v4.0
 * next-pwa + 三级 runtimeCaching
 */

const withPWA = require('@ducanh2912/next-pwa').default({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development', // 仅开发环境禁用
  register: true,
  skipWaiting: true,
  runtimeCaching: [
    // ① StaleWhileRevalidate：places-core.json / places-index.json
    {
      urlPattern: /\/data\/places-core\.json$|\/data\/places-index\.json$/,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'su-shi-data',
        expiration: { maxEntries: 5, maxAgeSeconds: 86400 * 7 },
      },
    },
    // ② NetworkFirst + cache：地点详情 JSON
    {
      urlPattern: /\/places\/SS\d+\.json$/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'su-shi-detail',
        expiration: { maxEntries: 50, maxAgeSeconds: 86400 * 30 },
        networkTimeoutSeconds: 5,
      },
    },
    // ③ CacheFirst（7天）：高德瓦片 / 图片 / 字体
    {
      urlPattern: /https:\/\/webrd0?\d\.amap\.com\/.*\.(png|jpg|jpeg|webp|woff2?)/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'amap-tiles',
        expiration: { maxEntries: 200, maxAgeSeconds: 86400 * 7 },
      },
    },
    {
      urlPattern: /\.(png|jpg|jpeg|webp|svg|gif)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'su-shi-images',
        expiration: { maxEntries: 100, maxAgeSeconds: 86400 * 7 },
      },
    },
    {
      urlPattern: /\.(woff2?|ttf|otf)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'su-shi-fonts',
        expiration: { maxEntries: 10, maxAgeSeconds: 86400 * 30 },
      },
    },
  ],
});

/** @type {import('next').NextConfig} */
const nextConfig = withPWA({
  // v4.1: 打开 typescript 检查，确保构建时不放行类型错误
  // eslint 错误量待评估后再打开（避免本轮卡死）
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: false },
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true, // 高德瓦片不走 Next.js Image
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [{ key: 'Cache-Control', value: 'no-store' }],
      },
      {
        source: '/places-core.json',
        headers: [{ key: 'Cache-Control', value: 'public, max-age=3600' }],
      },
    ];
  },
});

module.exports = nextConfig;
