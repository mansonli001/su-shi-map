/**
 * 诗词详情页 SEO — 动态 generateMetadata
 * 根据诗词ID生成独立的 title / description / OG
 */
import type { Metadata } from 'next';
import fs from 'fs';
import path from 'path';

const POEMS_DIR = path.join(process.cwd(), 'data-v4', 'poems');

// 安全校验：诗词 ID 仅允许字母/数字/下划线/短横，防止 ../ 路径穿越（CWE-22）
const SAFE_ID_RE = /^[A-Za-z0-9_-]{1,32}$/;

function getPoemData(id: string) {
  // 白名单校验：只允许安全字符的 ID，拒绝 ..、/、\、NUL 等
  if (!SAFE_ID_RE.test(id)) return null;

  // 尝试多种文件名格式（保持原兼容逻辑）
  const candidates = [`${id}.json`, `C${id.replace('C', '')}.json`];
  for (const name of candidates) {
    const fp = path.join(POEMS_DIR, name);
    // 边界检查：解析后的绝对路径必须仍在 POEMS_DIR 之内
    const resolved = path.resolve(fp);
    if (!resolved.startsWith(path.resolve(POEMS_DIR) + path.sep)) continue;
    if (fs.existsSync(resolved)) {
      try {
        return JSON.parse(fs.readFileSync(resolved, 'utf-8'));
      } catch {
        continue;
      }
    }
  }
  return null;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const poem = getPoemData(id);

  if (!poem) {
    return { title: '诗词未找到' };
  }

  const title = poem.title || '苏轼诗词';
  const excerpt = poem.excerpt || poem.coreVerse || poem.content?.slice(0, 60) || '';
  const location = poem.location || '';

  return {
    title: `${title} — 苏轼`,
    description: `${excerpt}${location ? `（作于${location}）` : ''}`,
    openGraph: {
      title: `${title} · 苏轼 · 行吟山河`,
      description: excerpt.slice(0, 120),
      type: 'article',
    },
  };
}

export default function PoemDetailLayout({ children }: { children: React.ReactNode }) {
  return children;
}
