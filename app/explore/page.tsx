/**
 * 地图主页 v6.0「行吟山河」（v4 数据切换 + 墨黑+金视觉换皮）
 * 顶栏对齐设计稿 .topnav-luxe（墨黑底+金字+金边）
 */

'use client';

import dynamic from 'next/dynamic';
import { useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useSuShiStore } from '@/lib/store';
import LeftSidebar from '@/components/LeftSidebar';
import PlaceCard from '@/components/place/PlaceCard';
import Search from '@/components/Search';
import TrajectoryAnimation from '@/components/TrajectoryAnimation';
import StageTimelineBar from '@/components/StageTimelineBar';
import {
  loadV4PlaceCores,
  buildV4RouteConfigs,
  buildV4RouteTracks,
  loadV4RoutesIdx,
} from '@/lib/v4-adapter';
import {
  installRouteConfigs,
  setRoute19PointsCache,
} from '@/lib/route19-config';

// 动态导入地图组件（避免SSR报错）
const AMap = dynamic(() => import('@/components/map/AMapContainer'), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center bg-paper">
      <div className="text-center">
        <div className="text-4xl mb-4">🗺️</div>
        <p className="text-ink/60 font-serif tracking-wider">地图加载中…</p>
      </div>
    </div>
  ),
});

export default function HomePage() {
  return (
    <Suspense fallback={<div className="absolute inset-0 flex items-center justify-center bg-paper text-ink/60 font-serif">载入中…</div>}>
      <ExploreInner />
    </Suspense>
  );
}

function ExploreInner() {
  const { setPlaces, selectedPlace, openSearch, setSelectedPlace, setCurrentRoute } = useSuShiStore();
  const searchParams = useSearchParams();
  const focusId = searchParams?.get('focus') || null;
  const routeParam = searchParams?.get('route') || null;

  useEffect(() => {
    let aborted = false;

    (async () => {
      try {
        const [cores, routesIdx, cfgs] = await Promise.all([
          loadV4PlaceCores(),
          loadV4RoutesIdx(),
          buildV4RouteConfigs(),
        ]);
        if (aborted) return;

        const sortedIds = [...routesIdx].sort((a, b) => a.index - b.index).map((r) => r.id);
        installRouteConfigs(cfgs, sortedIds);

        const tracks = await buildV4RouteTracks();
        if (aborted) return;
        setRoute19PointsCache(tracks as any);

        setPlaces(cores);

        // URL ?route=Rxx → 自动激活该路线（聚焦地图到该路线）
        if (routeParam && sortedIds.includes(routeParam)) {
          setTimeout(() => {
            if (!aborted) setCurrentRoute(routeParam);
          }, 400);
        }

        // URL ?focus=Pxxx → 自动打开该 place 详情卡
        if (focusId) {
          const target = cores.find((p: any) => p.id === focusId);
          if (target) {
            setTimeout(() => {
              if (!aborted) setSelectedPlace(target);
            }, 600);
          }
        }

        if (process.env.NODE_ENV !== 'production') {
          // eslint-disable-next-line no-console
          console.log(
            '[page v6] places=', cores.length,
            '· routes=', sortedIds.length,
            '· tracks=', tracks.length,
            '· focus=', focusId || '(none)',
            '· route=', routeParam || '(none)',
          );
        }
      } catch (err: any) {
        // eslint-disable-next-line no-console
        console.error('[page v6] 加载 v4 数据失败:', err?.message || err);
      }
    })();

    return () => { aborted = true; };
  }, [setPlaces, setSelectedPlace, setCurrentRoute, focusId, routeParam]);

  return (
    <main className="relative h-screen overflow-hidden flex bg-[var(--bg)]">
      {/* 左侧边栏 */}
      <LeftSidebar />

      {/* 右侧主区域 */}
      <div className="flex-1 relative">
        {/* === 顶部「行吟山河」深色导航（手机全宽 / 桌面 left-200） === */}
        <div className="fixed top-0 left-0 md:left-[200px] right-0 z-40 topnav-luxe safe-top h-[56px] md:h-[52px]">
          <div className="flex items-center justify-between px-3 md:px-5 h-full gap-2">
            {/* 主标题 + 副标题（双行） */}
            <div className="flex flex-col justify-center gap-[1px] pl-14 md:pl-0 min-w-0 md:flex-row md:items-center md:gap-4">
              <div className="font-wenkai font-semibold text-[17px] md:text-[16px] text-gold tracking-[0.22em] md:tracking-[0.25em] whitespace-nowrap leading-tight">
                行吟山河
              </div>
              <div className="text-[10px] md:hidden text-gold-m/75 tracking-[0.15em] whitespace-nowrap leading-tight">
                读苏轼 · 游神州
              </div>
              <div className="hidden md:block w-px h-[18px] bg-gold/20" />
              <div className="hidden md:flex items-center gap-3">
                <span className="text-[10px] text-gold/60 tracking-[0.18em]">
                  SU SHI · 1037–1101
                </span>
                <span className="text-[10px] text-gold-m/70 tracking-[0.1em]">
                  · 苏轼一生踪迹 · 数据 v4
                </span>
              </div>
            </div>
            <div className="flex items-center gap-0.5 md:gap-1 flex-shrink-0">
              <button
                onClick={() => (window.location.href = '/')}
                className="px-2 md:px-3 py-1.5 rounded text-[11px] md:text-[12px] text-gold/70 hover:text-gold hover:bg-gold/10 transition-colors tracking-wider whitespace-nowrap"
                aria-label="返回首页"
              >
                <span className="md:hidden">←</span>
                <span className="hidden md:inline">← 首页</span>
              </button>
              <button
                onClick={() => (window.location.href = '/routes')}
                className="px-2 md:px-3 py-1.5 rounded text-[11px] md:text-[12px] text-gold/70 hover:text-gold hover:bg-gold/10 transition-colors tracking-wider whitespace-nowrap"
                aria-label="路线列表"
              >
                <span className="md:hidden">📖</span>
                <span className="hidden md:inline">📖 路线</span>
              </button>
              <button
                onClick={openSearch}
                className="px-2 md:px-3 py-1.5 rounded text-[11px] md:text-[12px] text-gold/70 hover:text-gold hover:bg-gold/10 transition-colors tracking-wider whitespace-nowrap"
                aria-label="搜索"
              >
                <span className="md:hidden">🔍</span>
                <span className="hidden md:inline">🔍 搜索</span>
              </button>
              <button
                onClick={() => (window.location.href = '/about')}
                className="hidden md:inline-flex px-3 py-1.5 rounded text-[12px] text-gold/60 hover:text-gold hover:bg-gold/10 transition-colors tracking-wider"
                aria-label="关于"
              >
                关于
              </button>
            </div>
          </div>
        </div>

        {/* 地图容器 */}
        <AMap />

        {/* === 底部六阶段时间轴 === */}
        <StageTimelineBar />

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
