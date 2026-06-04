/**
 * StageTimelineBar v2.0「行吟山河」
 * 底部六阶段时间轴 · 横向可滑动版（参考用户设计稿）
 *
 * 视觉：墨黑底 + 金色当前态 + 横向滚动（不强塞屏）
 * 移动端：当前阶段放大居中 + 左右可滑动
 * 桌面端：保持均分铺满
 */

'use client';

import { useEffect, useState, useMemo, useRef } from 'react';
import { useSuShiStore } from '@/lib/store';
import { loadV4Stages, loadV4RoutesIdx, type V4StageIdx, type V4RouteIdx } from '@/lib/v4-adapter';

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
    // 平滑滚动到当前 button 居中
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
        background: 'var(--ink)',
        borderTop: '1px solid rgba(250,199,117,0.14)',
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
                  ${isActive ? 'bg-gold/15 scale-105' : 'hover:bg-gold/5'}
                `}
                style={{ scrollSnapAlign: 'center' }}
                title={`${s.name} · ${s.theme}`}
              >
                <span
                  className={`
                    font-wenkai transition-colors leading-tight whitespace-nowrap
                    ${isActive
                      ? 'text-gold font-semibold text-[16px] md:text-[12px]'
                      : 'text-gold/55 group-hover:text-gold/80 text-[14px] md:text-[11px]'}
                  `}
                  style={{ letterSpacing: '0.06em' }}
                >
                  {s.name}
                </span>
                <span
                  className={`
                    mt-0.5 transition-colors font-mono
                    ${isActive
                      ? 'text-gold-d/95 text-[12px] md:text-[9px] font-semibold'
                      : 'text-ink-lt/65 group-hover:text-gold-m/65 text-[11px] md:text-[9px]'}
                  `}
                >
                  {s.start_year}
                </span>
              </button>
            );
          })}
        </div>

        {/* 进度条 */}
        <div className="relative h-[2px] mx-3 md:mx-0 bg-[#2C2C2A] rounded-full mb-1 md:mb-1.5">
          <div
            className="absolute top-0 left-0 h-[2px] bg-gold-m rounded-full transition-all duration-700"
            style={{ width: `${fillPct}%` }}
          />
          {activeStageIdx != null && (
            <div
              className="absolute -top-[5px] w-3 h-3 bg-gold rounded-full border-2 border-[var(--ink)] transition-all duration-700"
              style={{ left: `calc(${fillPct}% - 6px)` }}
            />
          )}
        </div>

        {/* 年份行 · 桌面端展示 */}
        <div className="hidden md:flex justify-between text-[10px] text-ink-lt/60 font-mono px-0.5">
          <span>1037</span>
          <span className={activeStageIdx === 0 ? 'text-gold' : ''}>1056</span>
          <span className={activeStageIdx === 1 ? 'text-gold' : ''}>1079</span>
          <span className={activeStageIdx === 2 ? 'text-gold' : ''}>1085</span>
          <span className={activeStageIdx === 3 ? 'text-gold' : ''}>1094</span>
          <span className={activeStageIdx === 4 ? 'text-gold' : ''}>1100</span>
          <span>1101</span>
        </div>
      </div>
    </div>
  );
}
