/**
 * 地点详情页 v4.1
 * SSG 静态生成，generateStaticParams
 * 修复：服务端用 fs 读取 JSON，避免 dev 模式 404
 */

import { notFound } from 'next/navigation';
import { PlaceDetail } from '@/types';
import PlaceDetailComponent from '@/components/place/PlaceDetail';
import { Metadata } from 'next';
import fs from 'fs';
import path from 'path';

interface PlacePageProps {
  params: { id: string };
}

// 静态生成所有地点详情页
export function generateStaticParams(): { id: string }[] {
  const ids = Array.from({ length: 120 }, (_, i) => ({
    id: `SS${String(i + 1).padStart(3, '0')}`,
  }));
  return ids;
}

// 生成 Metadata（SEO）
export async function generateMetadata({ params }: PlacePageProps): Promise<Metadata> {
  const place = await getPlaceDetail(params.id);
  if (!place) return {};

  return {
    title: `${place.songName} - 读苏轼·游神州`,
    description: place.summary?.slice(0, 150) || '',
  };
}

// ★ v4.1 修复：服务端用 fs 读取本地 JSON，避免 window 判断导致服务端永远返回 null
async function getPlaceDetail(id: string): Promise<PlaceDetail | null> {
  try {
    const filePath = path.join(process.cwd(), 'data', 'places', `${id}.json`);
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(fileContent);
  } catch {
    return null;
  }
}

export default async function PlacePage({ params }: PlacePageProps) {
  const detail = await getPlaceDetail(params.id);

  if (!detail) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-paper">
      {/* 返回按钮 */}
      <div className="fixed top-0 inset-x-0 z-40 bg-paper/80 backdrop-blur-sm border-b border-ink/10 safe-top">
        <div className="flex items-center gap-3 px-4 py-3">
          <a
            href="/"
            className="p-2 -ml-2 rounded-lg hover:bg-ink/5 inline-flex items-center"
          >
            ←
          </a>
          <h1 className="text-lg font-serif text-ink">{detail.songName}</h1>
        </div>
      </div>

      {/* 详情内容 */}
      <div className="pt-16 px-4 pb-8 max-w-2xl mx-auto">
        <PlaceDetailComponent detail={detail} />
      </div>
    </div>
  );
}
