/**
 * 诗词库页 SEO metadata
 */
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '苏轼诗词库',
  description: '苏轼68篇代表作品，涵盖诗、词、文、赋，按创作地点与时期分类浏览。',
  openGraph: {
    title: '苏轼诗词库 · 行吟山河',
    description: '苏轼68篇代表作品，涵盖诗、词、文、赋，按创作地点与时期分类浏览。',
  },
};

export default function PoemsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
