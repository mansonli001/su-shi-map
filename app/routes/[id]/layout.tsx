/**
 * 路线详情页 SEO — 动态 generateMetadata
 * 根据路线ID生成独立的 title / description / OG
 */
import type { Metadata } from 'next';
import fs from 'fs';
import path from 'path';

const ROUTES_DIR = path.join(process.cwd(), 'data-v4', 'routes');

// 安全校验：路线 ID 仅允许字母/数字/下划线/短横，防止 ../ 路径穿越（CWE-22）
const SAFE_ID_RE = /^[A-Za-z0-9_-]{1,32}$/;

function getRouteData(id: string) {
  // 白名单校验：只允许安全字符的 ID，拒绝 ..、/、\、NUL 等
  if (!SAFE_ID_RE.test(id)) return null;

  const fp = path.join(ROUTES_DIR, `${id}.json`);
  // 边界检查：解析后的绝对路径必须仍在 ROUTES_DIR 之内
  const resolved = path.resolve(fp);
  if (!resolved.startsWith(path.resolve(ROUTES_DIR) + path.sep)) return null;
  if (!fs.existsSync(resolved)) return null;
  try {
    return JSON.parse(fs.readFileSync(resolved, 'utf-8'));
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
