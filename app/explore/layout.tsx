/**
 * 地图探索页 SEO metadata
 */
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '苏轼足迹地图',
  description: '交互式地图探索苏轼一生234处足迹，从眉山到儋州，跟随东坡走遍华夏山河。',
  openGraph: {
    title: '苏轼足迹地图 · 行吟山河',
    description: '交互式地图探索苏轼一生234处足迹，从眉山到儋州，跟随东坡走遍华夏山河。',
  },
};

export default function ExploreLayout({ children }: { children: React.ReactNode }) {
  return children;
}
