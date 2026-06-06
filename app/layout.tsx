/**
 * Root Layout v9.2（全站点统一底部导航）
 * 服务器组件（无 'use client'），导出 metadata + viewport + Open Graph
 * AMap Script 通过客户端组件 <AMapScript /> 加载
 */
import type { Metadata, Viewport } from 'next';
import './globals.css';
import AMapScript from '@/components/AMapScript';
import BottomNav from '@/components/BottomNav';

const SITE_URL = 'https://su-shi.starfluxes.com';

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: '行吟山河',
    template: '%s · 行吟山河',
  },
  description: '行吟山河 — 苏轼一生 234 处足迹、20 条主题路线、68 篇代表作的交互式数字地图。米白宣纸地图风，跟着东坡走一遍。',
  keywords: ['苏轼', '苏轼足迹地图', '苏轼一生路线', '东坡行旅', '苏轼诗词溯源', '行吟山河', '苏轼地图', '黄州赤壁', '西湖苏堤'],
  applicationName: '行吟山河',
  authors: [{ name: 'mansonli001' }],
  appleWebApp: {
    capable: true,
    title: '行吟山河',
    statusBarStyle: 'black-translucent',
  },
  formatDetection: {
    telephone: false,
    email: false,
    address: false,
  },
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/icons/pwa-192.png', type: 'image/png', sizes: '192x192' },
      { url: '/icons/pwa-512.png', type: 'image/png', sizes: '512x512' },
    ],
    apple: [
      { url: '/icons/pwa-152.png', sizes: '152x152' },
      { url: '/icons/pwa-192.png', sizes: '192x192' },
    ],
  },
  // Open Graph（微信分享卡片 / 朋友圈预览）
  openGraph: {
    title: '行吟山河 · 读苏轼游神州',
    description: '苏轼一生 234 处足迹、20 条主题路线，跟着东坡走一遍华夏山河。',
    url: SITE_URL,
    siteName: '行吟山河',
    locale: 'zh_CN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '行吟山河 · 读苏轼游神州',
    description: '苏轼一生 234 处足迹、20 条主题路线的交互式地图。',
  },
  // 微信分享时禁用搜索结果中的不必要预览
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  minimumScale: 1,
  userScalable: false,
  // viewportFit:cover 让微信内置浏览器/iOS 全屏支持安全区
  viewportFit: 'cover',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#1A1008' },
    { media: '(prefers-color-scheme: dark)', color: '#1A1008' },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        {/* iOS PWA */}
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="行吟山河" />
        <meta name="mobile-web-app-capable" content="yes" />

        {/* 微信内置浏览器适配 */}
        {/* 禁用微信浏览器的"复制链接"提示气泡（部分版本支持） */}
        <meta name="format-detection" content="telephone=no, email=no, address=no, date=no" />
        {/* 禁用 360/UC/QQ 浏览器的极速模式提示 */}
        <meta name="renderer" content="webkit" />
        <meta name="force-rendering" content="webkit" />
        {/* iOS Safari 禁止双指缩放（viewport 已设但加保险） */}
        <meta name="HandheldFriendly" content="true" />

        {/* 微信分享 og 图（待补真实分享图后取消注释） */}
        {/* <meta property="og:image" content="/og-share-1200x630.jpg" /> */}

        {/* 字体预连接 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://cdn.jsdelivr.net" crossOrigin="anonymous" />

        {/* Ink & Path 设计系统字体（Noto Serif SC + Source Sans 3 + Material Symbols） */}
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Source+Sans+3:wght@400;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased overflow-x-hidden min-h-screen flex flex-col">
        <AMapScript />
        {/* 主内容区：预留底部安全边距，适配底部Tab高度+系统安全区 */}
        <main className="flex-1 pb-[calc(70px+env(safe-area-inset-bottom))]">
          {children}
        </main>
        {/* 全局底部导航：所有页面共用，无例外（除特例全屏弹窗） */}
        <BottomNav />
      </body>
    </html>
  );
}