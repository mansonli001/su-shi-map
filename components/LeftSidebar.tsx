/**
 * 左侧边栏 v4.0「Ink & Path」（米白宣纸 + 墨黑 + 朱砂红视觉）
 *
 * 桌面端 200px 米白 parchment 背景 + 墨黑文字（左侧固定）
 * 移动端 v4.0：底部抽屉（68vh 弹起 + 顶部把手 + 字号放大），苹果地图风格
 * 中部六阶段折叠分组 R00-R19
 *
 * v4.0 修复：底部 padding-bottom 兜住 BottomNav 64px，CTA 按钮不再被遮
 */

'use client';

import { useState, useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';
import { loadV4Stages, loadV4RoutesIdx, type V4StageIdx, type V4RouteIdx } from '@/lib/v4-adapter';

// ink-path tokens（与 ink-path.css 一致）
const INK = {
  parchment: '#fef8f6',
  parchmentSoft: '#f7f0ec',
  ink: '#1a1410',
  inkSoft: '#3d342e',
  inkLite: '#6b5d54',
  cinnabar: '#ba1a1a',
  goldM: '#9b7a3a',
  goldLite: '#d1c4bc',
  hairline: 'rgba(209, 196, 188, 0.5)',
  hairlineSoft: 'rgba(209, 196, 188, 0.28)',
};

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
    else setCurrentRoute(routeId);
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

  // 边栏内容（米白宣纸版） - 桌面用
  const sidebarContent = (
    <>
      {/* 标题区 */}
      <div
        className="px-4 py-3"
        style={{ borderBottom: `1px solid ${INK.hairlineSoft}` }}
      >
        <h2
          style={{
            fontFamily: '"Noto Serif SC", serif',
            fontSize: '18px',
            fontWeight: 600,
            color: INK.ink,
            letterSpacing: '0.04em',
            margin: 0,
          }}
        >
          行吟山河
        </h2>
        <p
          style={{
            fontFamily: '"Source Sans 3", sans-serif',
            fontSize: '10px',
            color: INK.inkLite,
            marginTop: '4px',
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
          }}
        >
          ROUTES · 苏轼一生
        </p>
      </div>

      {/* 一生总览按钮 */}
      <div
        className="px-2 py-2"
        style={{ borderBottom: `1px solid ${INK.hairlineSoft}` }}
      >
        <button
          onClick={() => handleRouteClick(null)}
          className="w-full text-left px-3 py-2 rounded-md transition-all duration-200"
          style={{
            fontFamily: '"Noto Serif SC", serif',
            fontSize: '13px',
            background: currentRoute === null ? INK.ink : 'transparent',
            color: currentRoute === null ? INK.parchment : INK.inkSoft,
            fontWeight: currentRoute === null ? 600 : 400,
            border: `1px solid ${currentRoute === null ? INK.ink : 'transparent'}`,
          }}
        >
          <span style={{ marginRight: '6px', color: currentRoute === null ? INK.parchment : INK.cinnabar }}>●</span>
          一生总览
        </button>
      </div>

      {/* 六阶段分组路线 */}
      <nav className="flex-1 overflow-y-auto py-1">
        {stages.length === 0 ? (
          <div className="px-4 py-3" style={{ fontSize: '11px', color: INK.inkLite }}>加载中…</div>
        ) : (
          stages.map((stage) => {
            const stageRoutes = routesByStage.get(stage.id) || [];
            const isOpen = openStages[stage.id] !== false;
            return (
              <div key={stage.id} className="mb-1">
                {/* 阶段标题 */}
                <button
                  onClick={() => toggleStage(stage.id)}
                  className="w-full flex items-center gap-2 px-3 py-2 transition-colors group"
                  style={{ background: 'transparent' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = INK.parchmentSoft)}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  title={stage.theme}
                >
                  <span
                    className="inline-block w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: stage.color, boxShadow: `0 0 0 1px ${INK.hairlineSoft}` }}
                  />
                  <span
                    className="flex-1 text-left"
                    style={{
                      fontFamily: '"Noto Serif SC", serif',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: INK.ink,
                      letterSpacing: '0.06em',
                    }}
                  >
                    {stage.name}
                  </span>
                  <span style={{ fontSize: '9px', color: INK.inkLite, letterSpacing: '0.05em' }}>
                    {stage.start_year}-{stage.end_year}
                  </span>
                  <span
                    className={`transition-transform ${isOpen ? 'rotate-90' : ''}`}
                    style={{ fontSize: '9px', color: INK.inkLite }}
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
                            className="w-full text-left pl-3 pr-9 py-1.5 rounded-md transition-all duration-200"
                            style={{
                              fontFamily: '"Noto Serif SC", serif',
                              background: isActive ? 'rgba(186, 26, 26, 0.08)' : 'transparent',
                              color: isActive ? INK.cinnabar : INK.inkSoft,
                              fontWeight: isActive ? 600 : 400,
                              border: `1px solid ${isActive ? 'rgba(186, 26, 26, 0.2)' : 'transparent'}`,
                            }}
                            onMouseEnter={(e) => {
                              if (!isActive) e.currentTarget.style.background = INK.parchmentSoft;
                            }}
                            onMouseLeave={(e) => {
                              if (!isActive) e.currentTarget.style.background = 'transparent';
                            }}
                            title={`${r.name}（${r.start_year}-${r.end_year}）${r.place_count}点`}
                          >
                            <div className="flex items-center gap-1.5">
                              <span
                                className="inline-block w-1.5 h-1.5 rounded-full flex-shrink-0"
                                style={{ backgroundColor: r.unique_color || stage.color }}
                              />
                              <span
                                className="truncate"
                                style={{ fontSize: '11.5px', letterSpacing: 'normal' }}
                              >
                                {r.name}
                              </span>
                            </div>
                            <div
                              style={{
                                fontSize: '9px',
                                color: INK.inkLite,
                                marginLeft: '14px',
                                marginTop: '2px',
                                letterSpacing: '0.04em',
                              }}
                            >
                              {r.period} · {r.place_count}点
                            </div>
                          </button>
                          {/* 跳转介绍页（桌面端：hover 露出右箭头） */}
                          <a
                            href={`/routes/${r.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="absolute right-1.5 top-2 px-1.5 py-1 rounded opacity-0 group-hover/route:opacity-100 transition-opacity"
                            style={{
                              fontSize: '16px',
                              lineHeight: 1,
                              color: INK.inkLite,
                              fontWeight: 300,
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.color = INK.cinnabar;
                              e.currentTarget.style.background = 'rgba(186, 26, 26, 0.06)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.color = INK.inkLite;
                              e.currentTarget.style.background = 'transparent';
                            }}
                            title="查看路线介绍"
                          >
                            ›
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

      {/* 底部：仅保留极简 footer 标记，删除醒目 CTA（与右侧顶栏「路线」按钮重复 + 易被 BottomNav 遮）
          v4.1 修复：padding-bottom 兜住 BottomNav 80px + safe-area */}
      <div
        className="px-2 py-3"
        style={{
          borderTop: `1px solid ${INK.hairlineSoft}`,
          paddingBottom: 'calc(80px + env(safe-area-inset-bottom, 0px))',
        }}
      >
        <p
          style={{
            fontSize: '9px',
            color: INK.inkLite,
            letterSpacing: '0.16em',
            textAlign: 'center',
            margin: 0,
          }}
        >
          {routes.length > 0 ? `${routes.length} 条 · 6 阶段 · v4` : '加载中…'}
        </p>
      </div>
    </>
  );

  // 移动端底部抽屉内容（字号放大版 · ink-path 米白）
  const mobileContent = (
    <>
      {/* 顶部把手 + 标题 */}
      <div
        className="flex flex-col items-center px-4 pt-2 pb-3 flex-shrink-0"
        style={{ borderBottom: `1px solid ${INK.hairlineSoft}` }}
      >
        <div className="w-10 h-1 rounded-full mb-3" style={{ background: INK.hairline }} />
        <div className="w-full flex items-center justify-between">
          <div>
            <h2
              style={{
                fontFamily: '"Noto Serif SC", serif',
                fontSize: '18px',
                fontWeight: 600,
                color: INK.ink,
                margin: 0,
                letterSpacing: '0.04em',
              }}
            >
              行吟山河
            </h2>
            <p
              style={{
                fontSize: '10px',
                color: INK.inkLite,
                marginTop: '2px',
                letterSpacing: '0.16em',
              }}
            >
              ROUTES · 苏轼一生
            </p>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="px-3 py-1"
            style={{ color: INK.inkSoft, fontSize: '20px', background: 'transparent', border: 'none' }}
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
          className="w-full text-left px-4 py-3 rounded-lg transition-all duration-200"
          style={{
            fontFamily: '"Noto Serif SC", serif',
            fontSize: '15px',
            background: currentRoute === null ? INK.ink : INK.parchmentSoft,
            color: currentRoute === null ? INK.parchment : INK.inkSoft,
            fontWeight: currentRoute === null ? 600 : 400,
            border: `1px solid ${currentRoute === null ? INK.ink : 'transparent'}`,
          }}
        >
          <span style={{ marginRight: '8px', color: currentRoute === null ? INK.parchment : INK.cinnabar }}>●</span>
          一生总览
        </button>
      </div>

      {/* 六阶段分组路线（可滚动） */}
      <nav className="flex-1 overflow-y-auto px-1 pb-4 overscroll-contain">
        {stages.length === 0 ? (
          <div className="px-4 py-3" style={{ fontSize: '13px', color: INK.inkLite }}>加载中…</div>
        ) : (
          stages.map((stage) => {
            const stageRoutes = routesByStage.get(stage.id) || [];
            const isOpen = openStages[stage.id] !== false;
            return (
              <div key={stage.id} className="mb-2">
                {/* 阶段标题 */}
                <button
                  onClick={() => toggleStage(stage.id)}
                  className="w-full flex items-center gap-2.5 px-3 py-3 rounded-md transition-colors"
                  style={{ background: 'transparent' }}
                  title={stage.theme}
                >
                  <span
                    className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: stage.color, boxShadow: `0 0 0 1px ${INK.hairlineSoft}` }}
                  />
                  <span
                    className="flex-1 text-left"
                    style={{
                      fontFamily: '"Noto Serif SC", serif',
                      fontSize: '14px',
                      fontWeight: 500,
                      color: INK.ink,
                      letterSpacing: '0.06em',
                    }}
                  >
                    {stage.name}
                  </span>
                  <span style={{ fontSize: '11px', color: INK.inkLite, letterSpacing: '0.05em' }}>
                    {stage.start_year}-{stage.end_year}
                  </span>
                  <span
                    className={`transition-transform ${isOpen ? 'rotate-90' : ''}`}
                    style={{ fontSize: '11px', color: INK.inkLite }}
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
                            className="w-full text-left pl-4 pr-12 py-2.5 rounded-md transition-all duration-200"
                            style={{
                              fontFamily: '"Noto Serif SC", serif',
                              background: isActive ? 'rgba(186, 26, 26, 0.08)' : 'transparent',
                              color: isActive ? INK.cinnabar : INK.inkSoft,
                              fontWeight: isActive ? 600 : 400,
                              border: `1px solid ${isActive ? 'rgba(186, 26, 26, 0.2)' : 'transparent'}`,
                            }}
                          >
                            <div className="flex items-center gap-2">
                              <span
                                className="inline-block w-2 h-2 rounded-full flex-shrink-0"
                                style={{ backgroundColor: r.unique_color || stage.color }}
                              />
                              <span style={{ fontSize: '14px' }}>{r.name}</span>
                            </div>
                            <div
                              style={{
                                fontSize: '11px',
                                color: INK.inkLite,
                                marginLeft: '16px',
                                marginTop: '2px',
                                letterSpacing: '0.04em',
                              }}
                            >
                              {r.period} · {r.place_count}点
                            </div>
                          </button>
                          <a
                            href={`/routes/${r.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="absolute right-2 top-3 px-2 py-1 rounded"
                            style={{
                              fontSize: '20px',
                              lineHeight: 1,
                              color: INK.inkLite,
                              fontWeight: 300,
                            }}
                            title="查看路线介绍"
                          >
                            ›
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

      {/* 底部：极简 footer（移动版，不再有醒目 CTA 与顶栏路线 chip 重复） */}
      <div
        className="px-3 py-3 flex-shrink-0"
        style={{
          borderTop: `1px solid ${INK.hairlineSoft}`,
          paddingBottom: 'calc(16px + env(safe-area-inset-bottom, 0px))',
        }}
      >
        <p
          style={{
            fontSize: '10px',
            color: INK.inkLite,
            letterSpacing: '0.16em',
            textAlign: 'center',
            margin: 0,
          }}
        >
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
          background: 'rgba(254, 248, 246, 0.96)',
          backdropFilter: 'blur(12px)',
          border: `1px solid ${INK.hairline}`,
          boxShadow: '0 2px 8px rgba(26, 20, 16, 0.08)',
        }}
        aria-label="打开路线菜单"
      >
        <svg className="w-5 h-5" fill="none" stroke={INK.ink} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* 移动端蒙层（半透明，可点击关闭） */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          style={{ background: 'rgba(26, 20, 16, 0.35)' }}
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* 移动端底部抽屉（v4.0 ink-path 米白宣纸 · 68vh 弹起） */}
      <aside
        data-sidebar
        className={`
          fixed bottom-0 left-0 right-0 z-40 h-[68vh] rounded-t-2xl
          transform transition-transform duration-300 ease-out shadow-2xl
          md:hidden flex flex-col
          ${mobileOpen ? 'translate-y-0' : 'translate-y-full'}
        `}
        style={{
          background: 'rgba(254, 248, 246, 0.98)',
          backdropFilter: 'blur(12px)',
          borderTop: `1px solid ${INK.hairline}`,
          boxShadow: '0 -8px 32px rgba(26, 20, 16, 0.12)',
        }}
      >
        {mobileContent}
      </aside>

      {/* 桌面端固定边栏（v4.0 米白宣纸） */}
      <aside
        data-sidebar
        className="hidden md:flex flex-col h-screen w-[200px] fixed top-0 left-0 z-30"
        style={{
          background: 'rgba(254, 248, 246, 0.98)',
          backdropFilter: 'blur(8px)',
          borderRight: `1px solid ${INK.hairline}`,
        }}
      >
        <div className="flex flex-col h-full pt-[52px]">{sidebarContent}</div>
      </aside>
    </>
  );
}
