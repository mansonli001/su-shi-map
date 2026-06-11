/**
 * next.config.js v4.2（2026-06-11 资源加载修复）
 * - 修复：@ducanh2912/next-pwa v10 的正确 API 是 workboxOptions.runtimeCaching，
 *   而非顶层 runtimeCaching（那是旧版 shadowwalker/next-pwa 的写法）。原配置把
 *   runtimeCaching 放在顶层 → 被静默忽略 → SW 退回默认 NetworkFirst 规则，
 *   导致 #88（v4.1）设计的 data-v4 CacheFirst/SWR 缓存策略从未真正生效。
 * - extendDefaultRuntimeCaching: true → 自定义规则排在默认规则之前
 *   （workbox 首个匹配生效），既保留 next 默认（pages/rsc/next-static），
 *   又让 data-v4 / 高德瓦片 / 字体走我们指定的高速缓存策略。
 * - 新增 jsdelivr 霞鹜文楷 webfont CSS 的 SWR 缓存（配合 layout.tsx 字体 <link> 改造）。
 */

const withPWA = require('@ducanh2912/next-pwa').default({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development', // 仅开发环境禁用
  register: true,
  // 自定义规则置于默认规则之前，确保 data-v4/字体命中我们的策略而非默认 NetworkFirst
  extendDefaultRuntimeCaching: true,
  workboxOptions: {
    skipWaiting: true,
    runtimeCaching: [
      // ① StaleWhileRevalidate：data-v4 索引文件（places-index / routes-index / poems-index / stages-index）
      {
        urlPattern: /\/data-v4\/(places-index|routes-index|poems-index|stages-index|map-config|foods-by-place|foods-sushi)\.json$/,
        handler: 'StaleWhileRevalidate',
        options: {
          cacheName: 'su-shi-data-v4-index',
          expiration: { maxEntries: 10, maxAgeSeconds: 86400 * 30 },
        },
      },
      // ② CacheFirst：data-v4 单点详情（places/{P001}.json / routes/{R01}.json / poems/{S001}.json）
      //    数据极少变动，强缓存 30 天，部署后通过 SW 升级清空
      {
        urlPattern: /\/data-v4\/(places|routes|poems)\/[A-Z]\d+\.json$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'su-shi-data-v4-detail',
          expiration: { maxEntries: 500, maxAgeSeconds: 86400 * 30 },
        },
      },
      // ③ CacheFirst：高德瓦片
      {
        urlPattern: /https:\/\/webrd0?\d\.amap\.com\/.*\.(png|jpg|jpeg|webp|woff2?)/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'amap-tiles',
          expiration: { maxEntries: 200, maxAgeSeconds: 86400 * 7 },
        },
      },
      // ④ CacheFirst：本地图片（成就/品牌/icons）
      {
        urlPattern: /\.(png|jpg|jpeg|webp|svg|gif)$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'su-shi-images',
          expiration: { maxEntries: 200, maxAgeSeconds: 86400 * 30 },
        },
      },
      // ⑤ CacheFirst：字体文件（含 Google Fonts gstatic 与 jsdelivr woff2）
      {
        urlPattern: /\.(woff2?|ttf|otf)$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'su-shi-fonts',
          expiration: { maxEntries: 10, maxAgeSeconds: 86400 * 90 },
        },
      },
      // ⑥ StaleWhileRevalidate：Google Fonts CSS（display=swap 已加，二次访问命中缓存）
      {
        urlPattern: /^https:\/\/fonts\.googleapis\.com\//,
        handler: 'StaleWhileRevalidate',
        options: {
          cacheName: 'google-fonts-css',
          expiration: { maxEntries: 10, maxAgeSeconds: 86400 * 30 },
        },
      },
      // ⑦ CacheFirst：Google Fonts 字体文件
      {
        urlPattern: /^https:\/\/fonts\.gstatic\.com\//,
        handler: 'CacheFirst',
        options: {
          cacheName: 'google-fonts-files',
          expiration: { maxEntries: 30, maxAgeSeconds: 86400 * 365 },
        },
      },
      // ⑧ StaleWhileRevalidate：jsdelivr 霞鹜文楷 webfont CSS（style.css）
      //    woff2 字体文件已由规则⑤命中，这里补 CSS 自身的缓存，二次访问/离线更稳
      {
        urlPattern: /^https:\/\/cdn\.jsdelivr\.net\//,
        handler: 'StaleWhileRevalidate',
        options: {
          cacheName: 'jsdelivr-fonts-css',
          expiration: { maxEntries: 10, maxAgeSeconds: 86400 * 90 },
        },
      },
    ],
  },
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
      // API 永不缓存
      {
        source: '/api/:path*',
        headers: [{ key: 'Cache-Control', value: 'no-store' }],
      },
      // data-v4 索引文件（places-index 等）：浏览器短缓存 + CDN 长缓存 + SWR
      {
        source: '/data-v4/:file(places-index|routes-index|poems-index|stages-index|map-config|foods-by-place|foods-sushi).json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=300, s-maxage=86400, stale-while-revalidate=604800',
          },
        ],
      },
      // data-v4 单点详情文件：强缓存 1 天 + CDN 长缓存
      {
        source: '/data-v4/:dir(places|routes|poems)/:file*.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400, s-maxage=2592000, stale-while-revalidate=2592000',
          },
        ],
      },
      // 成就图片 / 品牌资源：强缓存 7 天
      {
        source: '/:path(achievements|brand|icons)/:file*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=604800, s-maxage=2592000, immutable',
          },
        ],
      },
    ];
  },
});

module.exports = nextConfig;
