/**
 * 地点详情页 v4.0
 * SSG 静态生成，generateStaticParams
 */

import { notFound } from 'next/navigation';
import { PlaceDetail, PlaceCore } from '@/types';
import PlaceDetailComponent from '@/components/place/PlaceDetail';
import { Metadata } from 'next';

interface PlacePageProps {
  params: { id: string };
}

// 静态生成所有地点详情页
export function generateStaticParams(): { id: string }[] {
  // 构建时从 places-core.json 读取所有id
  // 实际构建时会被替换为真实数据
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
    description: place.summary.slice(0, 150),
  };
}

// 获取地点详情
async function getPlaceDetail(id: string): Promise<PlaceDetail | null> {
  try {
    // 客户端运行时
    if (typeof window !== 'undefined') {
      const res = await fetch(`/data/places/${id}.json`);
      if (!res.ok) return null;
      return res.json();
    }
    // 服务端构建时
    return null;
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
          <button
            onClick={() => window.history.back()}
            className="p-2 -ml-2 rounded-lg hover:bg-ink/5"
          >
            ←
          </button>
          <h1 className="text-lg font-serif text-ink">{detail?.songName}</h1>
        </div>
      </div>

      {/* 详情内容 */}
      <div className="pt-16 px-4 pb-8 max-w-2xl mx-auto">
        {detail && <PlaceDetailComponent detail={detail} />}
      </div>
    </div>
  );
}
