/**
 * 个人中心页 SEO metadata
 */
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '我的足迹',
  description: '查看你的苏轼足迹打卡记录、成就进度和收藏诗词。',
  openGraph: {
    title: '我的足迹 · 行吟山河',
    description: '查看你的苏轼足迹打卡记录、成就进度和收藏诗词。',
  },
};

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return children;
}
