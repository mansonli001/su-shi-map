/**
 * 诗词详情页 SEO — 动态 generateMetadata
 * 根据诗词ID生成独立的 title / description / OG
 */
import type { Metadata } from 'next';
import fs from 'fs';
import path from 'path';

const POEMS_DIR = path.join(process.cwd(), 'data-v4', 'poems');

function getPoemData(id: string) {
  // 尝试多种文件名格式
  const candidates = [`${id}.json`, `C${id.replace('C', '')}.json`];
  for (const name of candidates) {
    const fp = path.join(POEMS_DIR, name);
    if (fs.existsSync(fp)) {
      try {
        return JSON.parse(fs.readFileSync(fp, 'utf-8'));
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
