/**
 * 地图主页 v4.0
 * AMapContainer + PlaceCard + Timeline + Search + Trajectory
 */

'use client';

import dynamic from 'next/dynamic';
import { useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore } from '@/types';
import Timeline from '@/components/Timeline';
import PlaceCard from '@/components/place/PlaceCard';
import Search from '@/components/Search';
import TrajectoryAnimation from '@/components/TrajectoryAnimation';

// 动态导入地图组件（避免SSR报错）
const AMap = dynamic(() => import('@/components/map/AMapContainer'), {
  ssr: false,
  loading: () => (
    <div className="map-fullscreen flex items-center justify-center bg-paper">
      <div className="text-center">
        <div className="text-4xl mb-4">🗺️</div>
        <p className="text-ink/60 font-serif">地图加载中...</p>
      </div>
    </div>
  ),
});

export default function HomePage() {
  const { places, setPlaces, selectedPlace, openSearch } = useSuShiStore();

  // 加载地点核心数据（写入 store）
  useEffect(() => {
    fetch('/data/places-core.json')
      .then(res => res.json())
      .then((data: PlaceCore[]) => {
        setPlaces(data);
        console.log(`✅ 加载 ${data.length} 个苏轼地点`);
      })
      .catch(err => console.error('加载地点数据失败', err));
  }, [setPlaces]);

  return (
    <main className="relative h-screen overflow-hidden">
      {/* 地图容器 */}
      <AMap />

      {/* 顶部标题栏 */}
      <div className="fixed top-0 inset-x-0 z-40 bg-paper/80 backdrop-blur-sm border-b border-ink/10 safe-top">
        <div className="flex items-center justify-between px-4 py-3">
          <div>
            <h1 className="text-lg font-serif text-ink">读苏轼·游神州</h1>
            <p className="text-xs text-ink/40">苏轼一生120地点</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={openSearch}
              className="p-2 rounded-lg hover:bg-ink/5 transition-colors"
              aria-label="搜索"
            >
              🔍
            </button>
            <button
              onClick={() => (window.location.href = '/checkin')}
              className="p-2 rounded-lg hover:bg-ink/5 transition-colors"
              aria-label="足迹"
            >
              📍
            </button>
            <button
              onClick={() => (window.location.href = '/about')}
              className="p-2 rounded-lg hover:bg-ink/5 transition-colors"
              aria-label="关于"
            >
              ℹ️
            </button>
          </div>
        </div>
      </div>

      {/* 时间轴 */}
      <Timeline />

      {/* 地点卡片 */}
      {selectedPlace && <PlaceCard place={selectedPlace} />}

      {/* 搜索面板 */}
      <Search />

      {/* 轨迹动画 */}
      <TrajectoryAnimation />
    </main>
  );
}
