/**
 * 地图主页 v5.0
 * AMapContainer + LeftSidebar + PlaceCard + Search + Trajectory
 */

'use client';

import dynamic from 'next/dynamic';
import { useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore } from '@/types';
import LeftSidebar from '@/components/LeftSidebar';
import PlaceCard from '@/components/place/PlaceCard';
import Search from '@/components/Search';
import TrajectoryAnimation from '@/components/TrajectoryAnimation';

// 动态导入地图组件（避免SSR报错）
const AMap = dynamic(() => import('@/components/map/AMapContainer'), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center bg-paper">
      <div className="text-center">
        <div className="text-4xl mb-4">🗺️</div>
        <p className="text-ink/60 font-serif">地图加载中...</p>
      </div>
    </div>
  ),
});

export default function HomePage() {
  const { places, setPlaces, selectedPlace, openSearch } = useSuShiStore();

  // 加载地点核心数据 + 索引数据（合并后写入 store）
  useEffect(() => {
    // URL + 时间戳强制破坏缓存，确保拿到最新 JSON（含 routeId / routeOrder）
    const ts = Date.now();
    Promise.all([
      fetch(`/data/places-core.json?t=${ts}`).then(res => {
        if (!res.ok) throw new Error('core HTTP ' + res.status);
        return res.json();
      }),
      fetch(`/data/places-index.json?t=${ts}`).then(res => {
        if (!res.ok) throw new Error('index HTTP ' + res.status);
        return res.json() as Promise<import('@/types').PlaceIndex[]>;
      }),
    ])
      .then(([coreData, indexData]) => {
        if (!Array.isArray(coreData)) {
          throw new Error('core 数据格式错误：期望数组，得到 ' + typeof coreData);
        }
        // 用 index 数据补全 summary / famousLine
        const indexMap = new Map(indexData.map((p: any) => [p.id, p]));
        const merged: PlaceCore[] = coreData.map((p: PlaceCore) => {
          const idx = indexMap.get(p.id);
          return {
            ...p,
            summary: idx?.summary || '',
            famousLine: idx?.famousLine || '',
            routeId: p.routeId || idx?.routeId || undefined,
            routeOrder: p.routeOrder || idx?.routeOrder || undefined,
          };
        });
        if (merged.length > 0) {
          console.log('[page] 第一条数据:', JSON.stringify(merged[0]));
          console.log('[page] 前3条坐标:', merged.slice(0, 3).map((p: any) => p.id + ': [' + p.lng + ', ' + p.lat + ']').join(', '));
        }
        setPlaces(merged);
        console.log('[page] merged[0].routeId =', merged[0]?.routeId, '| merged[0].routeOrder =', merged[0]?.routeOrder);
        const msg = '✅ 加载 ' + merged.length + ' 个苏轼地点（含简介）';
        console.log(msg);
        const el = document.getElementById('map-debug-logs');
        if (el) el.innerText = (el.innerText ? el.innerText + '\n' : '') + msg;
      })
      .catch(err => {
        const msg = '❌ 加载地点数据失败: ' + (err?.message || String(err));
        console.error(msg);
        const el = document.getElementById('map-debug-logs');
        if (el) el.innerText = (el.innerText ? el.innerText + '\n' : '') + msg;
      });
  }, [setPlaces]);

  return (
    <main className="relative h-screen overflow-hidden flex">
      {/* 左侧边栏 */}
      <LeftSidebar />

      {/* 右侧主区域 */}
      <div className="flex-1 relative">
        {/* 地图容器 */}
        <AMap />

        {/* 顶部标题栏 */}
        <div className="fixed top-0 left-[200px] right-0 z-40 bg-paper/80 backdrop-blur-sm border-b border-ink/10 safe-top">
          <div className="flex items-center justify-between px-4 py-3">
            <div>
              <h1 className="text-lg font-serif text-ink">读苏轼·游神州</h1>
              <p className="text-xs text-ink/40">苏轼一生127地点</p>
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

        {/* 地点卡片 */}
        {selectedPlace && <PlaceCard place={selectedPlace} />}

        {/* 搜索面板 */}
        <Search />

        {/* 轨迹动画 */}
        <TrajectoryAnimation />
      </div>
    </main>
  );
}
