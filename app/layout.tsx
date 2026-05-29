/**
 * Root Layout v4.0
 * Noto Serif SC 字体 + PWA meta + 全局 CSS 挂载
 */

import type { Metadata, Viewport } from 'next';
import './globals.css';
import { PropsWithChildren } from 'react';

export const metadata: Metadata = {
  title: '读苏轼·游神州',
  description: '苏轼一生120地点交互式数字地图（PWA）',
  applicationName: '读苏轼·游神州',
  appleWebApp: {
    capable: true,
    title: '苏轼足迹',
    statusBarStyle: 'black-translucent',
  },
  formatDetection: {
    telephone: false,
  },
  manifest: '/manifest.json',
};

export function generateViewport(): Viewport {
  return {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
    themeColor: [
      { media: '(prefers-color-scheme: light)', color: '#8B6914' },
      { media: '(prefers-color-scheme: dark)', color: '#1A1405' },
    ],
  };
}

export default function RootLayout({ children }: PropsWithChildren) {
  return (
    <html lang="zh-CN">
      <head>
        {/* PWA 兼容 meta */}
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="苏轼足迹" />
        <meta name="mobile-web-app-capable" content="yes" />
        {/* 高德 JSAPI 安全配置（由 lib/navigate.ts 注入） */}
        <script
          dangerouslySetInnerHTML={{
            __html: `window._AMapSecurityConfig = { serviceHost: '/api/_AMapService' };`,
          }}
        />
        {/* Noto Serif SC 字体预连接 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
