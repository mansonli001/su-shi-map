/**
 * StageTimelineBar v3.0「行吟山河 · ink-path 米白版」
 * 底部六阶段时间轴 · 与顶栏统一 parchment 米白 + 朱砂红 active
 *
 * 视觉对齐：references/stitch-pc/ink_path/DESIGN.md
 *   - 主底：rgba(254,248,246,0.96) 暖米白 frosted（与 explore 顶栏一致）
 *   - 文字：墨黑 #1a1410 / 次级 #6b5d54
 *   - active：朱砂红 #ba1a1a（text + progress dot + 阶段按钮 tint）
 *   - 进度条 fill：暗金 #7b5800
 *   - 1037–1101 年份刻度：移动端也显示（字号收紧 9px）
 *
 * 移动端：阶段名横向可滑动，当前态自动居中
 * 桌面端：6 阶段均分铺满
 */

'use client';

import { useEffect, useState, useMemo, useRef } from 'react';
import { useSuShiStore } from '@/lib/store';
import { loadV4Stages, loadV4RoutesIdx, type V4StageIdx, type V4RouteIdx } from '@/lib/v4-adapter';

// ===== 设计 token（与顶栏 / ink-path.css 严格一致） =====
const COLOR = {
  surface: 'rgba(254, 248, 246, 0.96)',
  ink: '#1a1410',
  inkSub: '#6b5d54',
  hairline: 'rgba(209, 196, 188, 0.5)',
  trackBg: 'rgba(209, 196, 188, 0.4)',
  cinnabar: '#ba1a1a',
  cinnabarTint: 'rgba(186, 26, 26, 0.08)',
  cinnabarTintHover: 'rgba(186, 26, 26, 0.04)',
  bronze: '#7b5800',
};

export default function StageTimelineBar() {
  const [stages, setStages] = useState<V4StageIdx[]>([]);
  const [routes, setRoutes] = useState<V4RouteIdx[]>([]);
  const currentRoute = useSuShiStore((s) => s.currentRoute);
  const setCurrentRoute = useSuShiStore((s) => s.setCurrentRoute);
  const scrollRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    Promise.all([loadV4Stages(), loadV4RoutesIdx()]).then(([s, r]) => {
      setStages(s);
      setRoutes(r);
    });
  }, []);

  const activeStageIdx = useMemo(() => {
    if (!currentRoute || !routes.length) return null;
    const r = routes.find((rr) => rr.id === currentRoute);
    if (!r || !r.stage_id) return null;
    return stages.findIndex((s) => s.id === r.stage_id);
  }, [currentRoute, routes, stages]);

  // 当前阶段切换时，自动横向滚动到居中位置（仅移动端有效，桌面端是 grid）
  useEffect(() => {
    if (activeStageIdx == null || !activeRef.current || !scrollRef.current) return;
    const el = activeRef.current;
    const container = scrollRef.current;
    const offset = el.offsetLeft - container.clientWidth / 2 + el.clientWidth / 2;
    container.scrollTo({ left: offset, behavior: 'smooth' });
  }, [activeStageIdx]);

  if (!stages.length) return null;

  const totalSpan = 1101 - 1037;
  const fillPct = activeStageIdx != null
    ? (((stages[activeStageIdx].end_year - 1037) / totalSpan) * 100).toFixed(1)
    : '100';

  const handleStageClick = (s: V4StageIdx) => {
    if (s.route_ids.length === 0) return;
    setCurrentRoute(s.route_ids[0]);
  };

  return (
    <div
      className="fixed bottom-0 left-0 md:left-[200px] right-0 z-30 select-none safe-bottom"
      style={{
        background: COLOR.surface,
        backdropFilter: 'blur(14px) saturate(140%)',
        WebkitBackdropFilter: 'blur(14px) saturate(140%)',
        borderTop: `1px solid ${COLOR.hairline}`,
      }}
    >
      <div className="px-0 md:px-5 py-2 md:py-3">
        {/* 阶段名称行 · 移动端横向滑动 / 桌面端均分 */}
        <div
          ref={scrollRef}
          className="
            flex items-end mb-1.5 md:mb-2 gap-1
            overflow-x-auto md:overflow-visible scroll-smooth
            scrollbar-none px-3 md:px-0 md:justify-between
          "
          style={{ scrollSnapType: 'x mandatory', WebkitOverflowScrolling: 'touch' }}
        >
          {stages.map((s, i) => {
            const isActive = activeStageIdx === i;
            return (
              <button
                key={s.id}
                ref={isActive ? activeRef : null}
                onClick={() => handleStageClick(s)}
                className={`
                  flex flex-col items-center text-center flex-shrink-0
                  md:min-w-0 md:flex-1 md:px-1
                  px-3.5 py-2 md:py-1.5 rounded-md
                  group cursor-pointer
                  transition-all duration-300
                  ${isActive ? 'scale-105' : ''}
                `}
                style={{
                  scrollSnapAlign: 'center',
                  background: isActive ? COLOR.cinnabarTint : 'transparent',
                  fontFamily: '"Noto Serif SC", serif',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.background = COLOR.cinnabarTintHover;
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'transparent';
                }}
                title={`${s.name} · ${s.theme}`}
              >
                <span
                  className="font-wenkai transition-colors leading-tight whitespace-nowrap"
                  style={{
                    color: isActive ? COLOR.cinnabar : COLOR.ink,
                    fontWeight: isActive ? 700 : 500,
                    fontSize: isActive ? 'clamp(13px,3.5vw,15px)' : 'clamp(12px,3vw,13px)',
                    letterSpacing: '0.08em',
                  }}
                >
                  {s.name}
                </span>
                {/* 副标 alias（如「蜀中读书」「贬谪悟道」），桌面端始终显示 */}
                <span
                  className="hidden md:block transition-colors whitespace-nowrap"
                  style={{
                    marginTop: '2px',
                    color: isActive ? COLOR.cinnabar : COLOR.inkSub,
                    fontSize: '10px',
                    fontFamily: '"Source Sans 3", sans-serif',
                    letterSpacing: '0.04em',
                    opacity: isActive ? 0.85 : 0.7,
                  }}
                >
                  {s.alias}
                </span>
                <span
                  className="transition-colors font-mono"
                  style={{
                    marginTop: '2px',
                    color: isActive ? COLOR.cinnabar : COLOR.inkSub,
                    fontSize: '10px',
                    fontWeight: isActive ? 600 : 400,
                    opacity: isActive ? 0.9 : 0.7,
                  }}
                >
                  {s.start_year}
                </span>
              </button>
            );
          })}
        </div>

        {/* 进度条 */}
        <div
          className="relative h-[2px] mx-3 md:mx-0 rounded-full mb-1 md:mb-1.5"
          style={{ background: COLOR.trackBg }}
        >
          <div
            className="absolute top-0 left-0 h-[2px] rounded-full transition-all duration-700"
            style={{ width: `${fillPct}%`, background: COLOR.bronze }}
          />
          {activeStageIdx != null && (
            <div
              className="absolute -top-[5px] w-3 h-3 rounded-full transition-all duration-700"
              style={{
                left: `calc(${fillPct}% - 6px)`,
                background: COLOR.cinnabar,
                border: `2px solid ${COLOR.surface}`,
                boxShadow: `0 0 0 1px ${COLOR.cinnabar}, 0 0 6px rgba(186,26,26,0.35)`,
              }}
            />
          )}
        </div>

        {/* 年份行 · 全屏可见（窄屏字号自动收紧） */}
        <div
          className="flex justify-between font-mono px-3 md:px-0.5"
          style={{
            fontSize: 'clamp(9px,2.4vw,10px)',
            color: COLOR.inkSub,
            opacity: 0.75,
            letterSpacing: '0.04em',
          }}
        >
          <span>1037</span>
          <span style={activeStageIdx === 0 ? { color: COLOR.cinnabar, fontWeight: 700, opacity: 1 } : undefined}>1056</span>
          <span style={activeStageIdx === 1 ? { color: COLOR.cinnabar, fontWeight: 700, opacity: 1 } : undefined}>1079</span>
          <span style={activeStageIdx === 2 ? { color: COLOR.cinnabar, fontWeight: 700, opacity: 1 } : undefined}>1085</span>
          <span style={activeStageIdx === 3 ? { color: COLOR.cinnabar, fontWeight: 700, opacity: 1 } : undefined}>1094</span>
          <span style={activeStageIdx === 4 ? { color: COLOR.cinnabar, fontWeight: 700, opacity: 1 } : undefined}>1100</span>
          <span>1101</span>
        </div>
      </div>
    </div>
  );
}
