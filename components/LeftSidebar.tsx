/**
 * 左侧边栏 v3.1「行吟山河」（墨黑+金视觉换皮）
 *
 * 桌面端 200px 深色墨黑背景 + 金色文字（左侧固定）
 * 移动端 v3.1：底部抽屉（68vh 弹起 + 顶部把手 + 字号放大），苹果地图风格
 * 中部六阶段折叠分组 R00-R19
 */

'use client';

import { useState, useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';
import { loadV4Stages, loadV4RoutesIdx, type V4StageIdx, type V4RouteIdx } from '@/lib/v4-adapter';

export default function LeftSidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [stages, setStages] = useState<V4StageIdx[]>([]);
  const [routes, setRoutes] = useState<V4RouteIdx[]>([]);
  const [openStages, setOpenStages] = useState<Record<string, boolean>>({});

  const currentRoute = useSuShiStore((s) => s.currentRoute);
  const setCurrentRoute = useSuShiStore((s) => s.setCurrentRoute);
  const clearRoute = useSuShiStore((s) => s.clearRoute);

  useEffect(() => {
    let aborted = false;
    Promise.all([loadV4Stages(), loadV4RoutesIdx()])
      .then(([s, r]) => {
        if (aborted) return;
        setStages(s);
        setRoutes(r);
        const init: Record<string, boolean> = {};
        for (const st of s) init[st.id] = true;
        setOpenStages(init);
      })
      .catch(() => {});
    return () => { aborted = true; };
  }, []);

  useEffect(() => {
    if (mobileOpen) {
      const handleClick = (e: MouseEvent) => {
        const target = e.target as HTMLElement;
        if (!target.closest('[data-sidebar]')) setMobileOpen(false);
      };
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [mobileOpen]);

  const handleRouteClick = (routeId: string | null) => {
    if (routeId === null) clearRoute();
    else setCurrentRoute(routeId as any);
    setMobileOpen(false);
  };

  const toggleStage = (sid: string) => {
    setOpenStages((prev) => ({ ...prev, [sid]: !prev[sid] }));
  };

  const routesByStage = new Map<string, V4RouteIdx[]>();
  for (const r of routes) {
    const sid = r.stage_id || 'unknown';
    if (!routesByStage.has(sid)) routesByStage.set(sid, []);
    routesByStage.get(sid)!.push(r);
  }
  Array.from(routesByStage.values()).forEach((list) =>
    list.sort((a, b) => a.index - b.index),
  );

  // 边栏内容（深色版） - 桌面用
  const sidebarContent = (
    <>
      {/* 标题区 */}
      <div className="px-4 py-3 border-b border-gold/10">
        <h2
          className="font-wenkai text-[14px] font-semibold text-gold tracking-[0.25em]"
        >
          行吟山河
        </h2>
        <p className="text-[10px] text-gold/40 mt-1 tracking-[0.16em]">
          ROUTES · 苏轼一生
        </p>
      </div>

      {/* 一生总览按钮 */}
      <div className="px-2 py-2 border-b border-gold/10">
        <button
          onClick={() => handleRouteClick(null)}
          className={`
            w-full text-left px-3 py-2 rounded-md text-[13px] transition-all duration-200 font-wenkai
            ${currentRoute === null
              ? 'bg-gold/15 text-gold font-semibold shadow-sm border border-gold/20'
              : 'text-gold/65 hover:bg-gold/5 hover:text-gold/90 border border-transparent'}
          `}
        >
          <span className="mr-1.5">●</span>
          一生总览
        </button>
      </div>

      {/* 六阶段分组路线 */}
      <nav className="flex-1 overflow-y-auto py-1">
        {stages.length === 0 ? (
          <div className="px-4 py-3 text-[11px] text-gold/30">加载中…</div>
        ) : (
          stages.map((stage) => {
            const stageRoutes = routesByStage.get(stage.id) || [];
            const isOpen = openStages[stage.id] !== false;
            return (
              <div key={stage.id} className="mb-1">
                {/* 阶段标题 */}
                <button
                  onClick={() => toggleStage(stage.id)}
                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gold/5 transition-colors group"
                  title={stage.theme}
                >
                  <span
                    className="inline-block w-2 h-2 rounded-full flex-shrink-0 ring-1 ring-white/10"
                    style={{ backgroundColor: stage.color }}
                  />
                  <span className="text-[11px] font-medium text-gold/85 flex-1 text-left tracking-[0.06em] font-wenkai">
                    {stage.name}
                  </span>
                  <span className="text-[9px] text-gold-m/55 tracking-[0.05em]">
                    {stage.start_year}-{stage.end_year}
                  </span>
                  <span
                    className={`text-[9px] text-gold/30 transition-transform group-hover:text-gold/60 ${
                      isOpen ? 'rotate-90' : ''
                    }`}
                  >
                    ▶
                  </span>
                </button>

                {/* 阶段下属路线 */}
                {isOpen && (
                  <div className="px-1 pb-1 space-y-0.5">
                    {stageRoutes.map((r) => {
                      const isActive = currentRoute === r.id;
                      return (
                        <div key={r.id} className="relative group/route">
                          <button
                            onClick={() => handleRouteClick(r.id)}
                            className={`
                              w-full text-left pl-3 pr-9 py-1.5 rounded-md transition-all duration-200 font-wenkai
                              ${isActive
                                ? 'bg-gold/15 text-gold font-semibold shadow-sm border border-gold/20'
                                : 'text-gold/55 hover:bg-gold/5 hover:text-gold/85 border border-transparent'}
                            `}
                            title={`${r.name}（${r.start_year}-${r.end_year}）${r.place_count}点`}
                          >
                            <div className="flex items-center gap-1.5">
                              <span
                                className="inline-block w-1.5 h-1.5 rounded-full flex-shrink-0"
                                style={{ backgroundColor: r.unique_color || stage.color }}
                              />
                              <span className="truncate text-[11.5px] tracking-tight">
                                {r.name}
                              </span>
                            </div>
                            <div className="text-[9px] text-gold/30 ml-3.5 mt-0.5 tracking-[0.04em]">
                              {r.period} · {r.place_count}点
                            </div>
                          </button>
                          {/* 跳转介绍页（hover 露出） */}
                          <a
                            href={`/routes/${r.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="absolute right-1.5 top-1.5 text-[12px] px-1.5 py-1 rounded text-gold/40 hover:text-gold hover:bg-gold/10 opacity-0 group-hover/route:opacity-100 transition-opacity"
                            title="查看路线介绍"
                          >
                            📖
                          </a>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })
        )}
      </nav>

      {/* 底部说明 */}
      <div className="px-4 py-2 border-t border-gold/10">
        <p className="text-[9px] text-gold/30 tracking-[0.16em]">
          {routes.length > 0 ? `${routes.length} 条 · 6 阶段 · v4` : '加载中…'}
        </p>
      </div>
    </>
  );

  // 移动端底部抽屉内容（字号放大版）
  const mobileContent = (
    <>
      {/* 顶部把手 + 标题 */}
      <div className="flex flex-col items-center px-4 pt-2 pb-3 border-b border-gold/10 flex-shrink-0">
        <div className="w-10 h-1 rounded-full bg-gold/30 mb-3" />
        <div className="w-full flex items-center justify-between">
          <div>
            <h2 className="font-wenkai text-[17px] font-semibold text-gold tracking-[0.22em]">
              行吟山河
            </h2>
            <p className="text-[10px] text-gold-m/60 mt-0.5 tracking-[0.16em]">
              ROUTES · 苏轼一生
            </p>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="text-gold/60 hover:text-gold text-[20px] px-3 py-1"
            aria-label="关闭"
          >
            ✕
          </button>
        </div>
      </div>

      {/* 一生总览按钮 */}
      <div className="px-3 pt-3 pb-2 flex-shrink-0">
        <button
          onClick={() => handleRouteClick(null)}
          className={`
            w-full text-left px-4 py-3 rounded-lg text-[15px] transition-all duration-200 font-wenkai
            ${currentRoute === null
              ? 'bg-gold/20 text-gold font-semibold border border-gold/30'
              : 'text-gold/75 bg-gold/5 hover:bg-gold/10 border border-transparent'}
          `}
        >
          <span className="mr-2">●</span>
          一生总览
        </button>
      </div>

      {/* 六阶段分组路线（可滚动） */}
      <nav className="flex-1 overflow-y-auto px-1 pb-4 overscroll-contain">
        {stages.length === 0 ? (
          <div className="px-4 py-3 text-[13px] text-gold/30">加载中…</div>
        ) : (
          stages.map((stage) => {
            const stageRoutes = routesByStage.get(stage.id) || [];
            const isOpen = openStages[stage.id] !== false;
            return (
              <div key={stage.id} className="mb-2">
                {/* 阶段标题 */}
                <button
                  onClick={() => toggleStage(stage.id)}
                  className="w-full flex items-center gap-2.5 px-3 py-3 hover:bg-gold/5 active:bg-gold/10 transition-colors rounded-md"
                  title={stage.theme}
                >
                  <span
                    className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0 ring-1 ring-white/10"
                    style={{ backgroundColor: stage.color }}
                  />
                  <span className="text-[14px] font-medium text-gold/90 flex-1 text-left tracking-[0.06em] font-wenkai">
                    {stage.name}
                  </span>
                  <span className="text-[11px] text-gold-m/60 tracking-[0.05em]">
                    {stage.start_year}-{stage.end_year}
                  </span>
                  <span
                    className={`text-[11px] text-gold/40 transition-transform ${
                      isOpen ? 'rotate-90' : ''
                    }`}
                  >
                    ▶
                  </span>
                </button>

                {/* 阶段下属路线 */}
                {isOpen && (
                  <div className="px-1 pb-1 space-y-1">
                    {stageRoutes.map((r) => {
                      const isActive = currentRoute === r.id;
                      return (
                        <div key={r.id} className="relative">
                          <button
                            onClick={() => handleRouteClick(r.id)}
                            className={`
                              w-full text-left pl-4 pr-12 py-2.5 rounded-md transition-all duration-200 font-wenkai
                              ${isActive
                                ? 'bg-gold/20 text-gold font-semibold border border-gold/30'
                                : 'text-gold/70 active:bg-gold/10 border border-transparent'}
                            `}
                          >
                            <div className="flex items-center gap-2">
                              <span
                                className="inline-block w-2 h-2 rounded-full flex-shrink-0"
                                style={{ backgroundColor: r.unique_color || stage.color }}
                              />
                              <span className="text-[14px] tracking-tight">
                                {r.name}
                              </span>
                            </div>
                            <div className="text-[11px] text-gold/40 ml-4 mt-0.5 tracking-[0.04em]">
                              {r.period} · {r.place_count}点
                            </div>
                          </button>
                          {/* 跳转介绍页 */}
                          <a
                            href={`/routes/${r.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="absolute right-2 top-2.5 text-[18px] px-2 py-1 rounded text-gold/50 active:text-gold active:bg-gold/10"
                            title="查看路线介绍"
                          >
                            📖
                          </a>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })
        )}
      </nav>

      {/* 底部说明 */}
      <div className="px-4 py-2 border-t border-gold/10 flex-shrink-0">
        <p className="text-[10px] text-gold/40 tracking-[0.16em] text-center">
          {routes.length > 0 ? `${routes.length} 条 · 6 阶段 · v4` : '加载中…'}
        </p>
      </div>
    </>
  );

  return (
    <>
      {/* 移动端汉堡菜单 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          setMobileOpen(!mobileOpen);
        }}
        className="fixed top-3 left-3 z-50 p-2 rounded-md md:hidden"
        style={{
          background: 'rgba(26, 16, 8, 0.92)',
          border: '1px solid rgba(250,199,117,0.18)',
        }}
        aria-label="打开路线菜单"
      >
        <svg className="w-5 h-5 text-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* 移动端蒙层（半透明，可点击关闭） */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          style={{ background: 'rgba(26, 16, 8, 0.45)' }}
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* 移动端底部抽屉（v3.1 苹果地图风格 · 68vh 弹起） */}
      <aside
        data-sidebar
        className={`
          fixed bottom-0 left-0 right-0 z-40 h-[68vh] rounded-t-2xl
          transform transition-transform duration-300 ease-out shadow-2xl
          md:hidden flex flex-col
          ${mobileOpen ? 'translate-y-0' : 'translate-y-full'}
        `}
        style={{
          background: 'rgba(26, 16, 8, 0.98)',
          backdropFilter: 'blur(12px)',
          borderTop: '1px solid rgba(250,199,117,0.18)',
          boxShadow: '0 -8px 32px rgba(0,0,0,0.4)',
        }}
      >
        {mobileContent}
      </aside>

      {/* 桌面端固定边栏（保持不变） */}
      <aside
        data-sidebar
        className="hidden md:flex flex-col h-screen w-[200px] fixed top-0 left-0 z-30"
        style={{
          background: 'rgba(26, 16, 8, 0.97)',
          backdropFilter: 'blur(8px)',
          borderRight: '1px solid rgba(250,199,117,0.12)',
        }}
      >
        <div className="flex flex-col h-full pt-[52px]">{sidebarContent}</div>
      </aside>
    </>
  );
}
