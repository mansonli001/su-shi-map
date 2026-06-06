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
        setRoute19PointsCache(tracks);

        setPlaces(cores);

        // URL ?route=Rxx → 自动激活该路线（聚焦地图到该路线）
        if (routeParam && sortedIds.includes(routeParam)) {
          setTimeout(() => {
            if (!aborted) setCurrentRoute(routeParam);
          }, 400);
        }

        // URL ?focus=Pxxx → 自动打开该 place 详情卡
        if (focusId) {
          const target = cores.find((p) => p.id === focusId);
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
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('[page v6] 加载 v4 数据失败:', err instanceof Error ? err.message : String(err));
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
        {/* === 顶部「读苏轼·游神州」副标题导航 v4.0 ink-path 风
              米白 frosted parchment + 墨黑文字 + 朱砂红 hover === */}
        <div
          className="fixed top-0 left-0 md:left-[200px] right-0 z-40 safe-top h-[60px] md:h-[56px]"
          style={{
            background: 'rgba(254, 248, 246, 0.96)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            borderBottom: '1px solid rgba(209, 196, 188, 0.4)',
          }}
        >
          <div className="relative flex items-center justify-between px-3 md:px-5 h-full gap-3">
            {/* 左侧：汉堡菜单按钮（移动端） */}
            <div className="flex-shrink-0 md:hidden">
              <button
                onClick={() => (window.location.href = '/')}
                className="min-w-[44px] min-h-[44px] flex items-center justify-center px-2 rounded transition-colors"
                style={{ fontSize: '14px', color: '#3d342e' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#ba1a1a';
                  e.currentTarget.style.background = 'rgba(186, 26, 26, 0.06)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#3d342e';
                  e.currentTarget.style.background = 'transparent';
                }}
                aria-label="返回首页"
              >
                ←
              </button>
            </div>

            {/* 副标题（移动端绝对定位居中 / 桌面端左对齐） */}
            <div className="absolute left-1/2 -translate-x-1/2 md:static md:translate-x-0 md:left-0 md:mr-auto flex items-center gap-2 md:gap-4 min-w-0 pointer-events-none md:pointer-events-auto">
              <div
                className="whitespace-nowrap"
                style={{
                  fontFamily: '"Noto Serif SC", serif',
                  fontSize: '15px',
                  fontWeight: 600,
                  color: '#1a1410',
                  letterSpacing: '0.18em',
                  lineHeight: 1.2,
                }}
              >
                读苏轼 · 游神州
              </div>
              <div className="hidden md:block w-px h-[18px]" style={{ background: 'rgba(209, 196, 188, 0.6)' }} />
              <div className="hidden md:flex items-center gap-3">
                <span style={{ fontSize: '10px', color: '#6b5d54', letterSpacing: '0.18em', fontFamily: '"Source Sans 3", sans-serif' }}>
                  SU SHI · 1037–1101
                </span>
                <span style={{ fontSize: '10px', color: '#9b7a3a', letterSpacing: '0.1em', fontFamily: '"Noto Serif SC", serif' }}>
                  · 苏轼一生踪迹 · 数据 v4
                </span>
              </div>
            </div>

            {/* 右侧图标组 */}
            <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
              {[
                { label: '路线', mobileIcon: '📍', onClick: () => (window.location.href = '/routes'), aria: '路线列表' },
                { label: '诗词', mobileIcon: '诗', onClick: () => (window.location.href = '/poems'), aria: '诗词' },
                { label: '搜索', mobileIcon: '🔍', onClick: openSearch, aria: '搜索' },
              ].map((b) => (
                <button
                  key={b.label}
                  onClick={b.onClick}
                  className="min-w-[44px] min-h-[44px] flex items-center justify-center px-2 md:px-3 py-1.5 rounded transition-colors"
                  style={{
                    fontFamily: '"Noto Serif SC", serif',
                    fontSize: '12px',
                    color: '#3d342e',
                    letterSpacing: '0.08em',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#ba1a1a';
                    e.currentTarget.style.background = 'rgba(186, 26, 26, 0.06)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#3d342e';
                    e.currentTarget.style.background = 'transparent';
                  }}
                  aria-label={b.aria}
                >
                  <span className="md:hidden">{b.mobileIcon}</span>
                  <span className="hidden md:inline">{b.label}</span>
                </button>
              ))}

              {/* 关于（仅桌面端） */}
              <button
                onClick={() => (window.location.href = '/about')}
                className="hidden md:inline-flex min-w-[44px] min-h-[44px] items-center justify-center px-3 py-1.5 rounded transition-colors"
                style={{
                  fontFamily: '"Noto Serif SC", serif',
                  fontSize: '12px',
                  color: '#6b5d54',
                  letterSpacing: '0.08em',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#ba1a1a';
                  e.currentTarget.style.background = 'rgba(186, 26, 26, 0.06)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#6b5d54';
                  e.currentTarget.style.background = 'transparent';
                }}
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
