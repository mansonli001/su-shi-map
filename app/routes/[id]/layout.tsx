/**
 * 路线详情页 SEO — 动态 generateMetadata
 * 根据路线ID生成独立的 title / description / OG
 */
import type { Metadata } from 'next';
import fs from 'fs';
import path from 'path';

const ROUTES_DIR = path.join(process.cwd(), 'data-v4', 'routes');

function getRouteData(id: string) {
  const fp = path.join(ROUTES_DIR, `${id}.json`);
  if (!fs.existsSync(fp)) return null;
  try {
    return JSON.parse(fs.readFileSync(fp, 'utf-8'));
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const route = getRouteData(id);

  if (!route) {
    return { title: '路线未找到' };
  }

  const name = route.name || route.route_name || '苏轼行迹路线';
  const desc = route.core_essence || route.description_short || `探索${name}，跟随苏轼的脚步。`;

  return {
    title: `${name}`,
    description: desc.slice(0, 160),
    openGraph: {
      title: `${name} · 行吟山河`,
      description: desc.slice(0, 120),
      type: 'article',
    },
  };
}

export default function RouteDetailLayout({ children }: { children: React.ReactNode }) {
  return children;
}
