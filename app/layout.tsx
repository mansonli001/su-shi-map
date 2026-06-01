/**
 * Root Layout v9.0
 * 服务器组件（无 'use client'），导出 metadata
 * AMap Script 通过客户端组件 <AMapScript /> 加载
 */
import type { Metadata, Viewport } from 'next';
import './globals.css';
import AMapScript from '@/components/AMapScript';

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

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#8B6914' },
    { media: '(prefers-color-scheme: dark)', color: '#1A1405' },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="苏轼足迹" />
        <meta name="mobile-web-app-capable" content="yes" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">
        <AMapScript />
        {children}
      </body>
    </html>
  );
}