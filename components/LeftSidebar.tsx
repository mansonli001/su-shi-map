/**
 * 左侧边栏 v1.0
 * 桌面端固定200px边栏，移动端汉堡菜单抽屉
 * 包含20个路线按钮（19条路线 + 一生总览）
 */

'use client';

import { useState, useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';
import { ROUTE19_CONFIG, ROUTE19_IDS } from '@/lib/route19-config';

export default function LeftSidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const currentRoute = useSuShiStore(s => s.currentRoute);
  const setCurrentRoute = useSuShiStore(s => s.setCurrentRoute);
  const clearRoute = useSuShiStore(s => s.clearRoute);

  // 移动端点击地图区域自动收起边栏
  useEffect(() => {
    if (mobileOpen) {
      const handleClick = (e: MouseEvent) => {
        const target = e.target as HTMLElement;
        if (!target.closest('[data-sidebar]')) {
          setMobileOpen(false);
        }
      };
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [mobileOpen]);

  const handleRouteClick = (routeId: string | null) => {
    if (routeId === null) {
      clearRoute();
    } else {
      setCurrentRoute(routeId as any);
    }
    setMobileOpen(false);
  };

  // 边栏内容（复用）
  const sidebarContent = (
    <>
      {/* 标题区 */}
      <div className="px-4 py-3 border-b border-ink/10">
        <h2 className="text-sm font-serif text-ink/80">苏轼行踪路线</h2>
        <p className="text-xs text-ink/40 mt-0.5">基于史料考据 · 一生行踪</p>
      </div>

      {/* 一生总览按钮 */}
      <div className="px-2 py-2 border-b border-ink/5">
        <button
          onClick={() => handleRouteClick(null)}
          className={`
            w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-200
            ${currentRoute === null
              ? 'bg-ink/10 text-ink font-medium shadow-sm'
              : 'text-ink/60 hover:bg-ink/5 hover:text-ink/80'
            }
          `}
        >
          <span className="mr-2">🗺️</span>
          一生总览
        </button>
      </div>

      {/* 19条路线按钮 */}
      <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
        {ROUTE19_IDS.map((id) => {
          const config = ROUTE19_CONFIG[id];
          if (!config) return null;
          const isActive = currentRoute === id;
          return (
            <button
              key={id}
              onClick={() => handleRouteClick(id)}
              className={`
                w-full text-left px-3 py-1.5 rounded-lg text-sm transition-all duration-200
                ${isActive
                  ? 'bg-ink/10 text-ink font-medium shadow-sm'
                  : 'text-ink/60 hover:bg-ink/5 hover:text-ink/80'
                }
              `}
              title={`${config.name}（${config.time}）`}
            >
              <div className="flex items-center gap-2">
                {/* 路线颜色指示点 */}
                <span
                  className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: config.mainColor }}
                />
                <span className="truncate">{config.name}</span>
              </div>
              {/* 时间标签 */}
              <div className="text-xs text-ink/30 ml-5 mt-0.5">{config.time}</div>
            </button>
          );
        })}
      </nav>

      {/* 底部说明 */}
      <div className="px-4 py-2 border-t border-ink/10">
        <p className="text-xs text-ink/30">共19条路线 · 127个地点</p>
      </div>
    </>
  );

  return (
    <>
      {/* 移动端汉堡菜单按钮 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          setMobileOpen(!mobileOpen);
        }}
        className="fixed top-3 left-3 z-50 p-2 rounded-lg bg-paper/90 backdrop-blur-sm border border-ink/10 shadow-sm md:hidden"
        aria-label="打开路线菜单"
      >
        <svg className="w-5 h-5 text-ink/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* 移动端抽屉遮罩 */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-ink/20 z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* 移动端抽屉边栏 */}
      <aside
        data-sidebar
        className={`
          fixed top-0 left-0 z-40 h-full w-[280px] bg-paper/95 backdrop-blur-sm border-r border-ink/10
          transform transition-transform duration-300 ease-out shadow-lg
          md:hidden
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full pt-safe-top">
          {sidebarContent}
        </div>
      </aside>

      {/* 桌面端固定边栏 */}
      <aside
        data-sidebar
        className="hidden md:flex flex-col h-screen w-[200px] fixed top-0 left-0 z-30 bg-paper/95 backdrop-blur-sm border-r border-ink/10"
      >
        <div className="flex flex-col h-full pt-16">
          {sidebarContent}
        </div>
      </aside>
    </>
  );
}
