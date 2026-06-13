/**
 * 贺野游中国 · Layout
 * - 独立 metadata（SEO）
 * - 暖橙配色 body class
 */
import type { Metadata } from 'next';
// 贺野全站样式：在 layout 统一加载，确保 /he-ye/* 所有子路由（首页/旅人录/文章流/探索）
// 在直接硬加载或刷新时都能拿到布局样式，而非仅依赖首页 page.tsx 的 import。
import './heye-home.css';

export const metadata: Metadata = {
  title: '贺野游中国',
  description: '跟着贺野走遍中国，吃遍山河。一个人、一辆车、一条路，每一步都是风景，每一口都是故事。',
  keywords: ['贺野', '有生余年', '旅行', '美食', '中国旅行', '自驾游', '地方美食'],
  openGraph: {
    title: '贺野游中国 · 有生余年',
    description: '跟着贺野走遍中国，吃遍山河。',
    type: 'website',
  },
};

export default function HeyeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="he-root">
      {children}
    </div>
  );
}
