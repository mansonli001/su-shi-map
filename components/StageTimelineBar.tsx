/**
 * StageTimelineBar v1.0「行吟山河」
 * 底部六阶段时间轴（设计稿 ②地图页 底部进度条对齐）
 *
 * 视觉：墨黑底 + 金色填充进度 + 鼠标悬停高亮
 * 交互：点阶段 → 切到该阶段第一条路线
 */

'use client';

import { useEffect, useState, useMemo } from 'react';
import { useSuShiStore } from '@/lib/store';
import { loadV4Stages, loadV4RoutesIdx, type V4StageIdx, type V4RouteIdx } from '@/lib/v4-adapter';

export default function StageTimelineBar() {
  const [stages, setStages] = useState<V4StageIdx[]>([]);
  const [routes, setRoutes] = useState<V4RouteIdx[]>([]);
  const currentRoute = useSuShiStore((s) => s.currentRoute);
  const setCurrentRoute = useSuShiStore((s) => s.setCurrentRoute);

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

  if (!stages.length) return null;

  const totalSpan = 1101 - 1037;
  const fillPct = activeStageIdx != null
    ? (((stages[activeStageIdx].end_year - 1037) / totalSpan) * 100).toFixed(1)
    : '100';

  const handleStageClick = (s: V4StageIdx) => {
    if (s.route_ids.length === 0) return;
    setCurrentRoute(s.route_ids[0] as any);
  };

  return (
    <div
      className="fixed bottom-0 left-0 md:left-[200px] right-0 z-30 select-none safe-bottom"
      style={{
        background: 'var(--ink)',
        borderTop: '1px solid rgba(250,199,117,0.14)',
      }}
    >
      <div className="px-2 md:px-5 py-2 md:py-3">
        {/* 阶段名称行 */}
        <div className="flex justify-between items-end mb-1.5 md:mb-2 gap-0.5">
          {stages.map((s, i) => {
            const isActive = activeStageIdx === i;
            return (
              <button
                key={s.id}
                onClick={() => handleStageClick(s)}
                className="flex flex-col items-center text-center min-w-0 flex-1 px-0.5 md:px-1 group cursor-pointer"
                title={`${s.name} · ${s.theme}`}
              >
                <span
                  className={`text-[9px] md:text-[11px] font-wenkai transition-colors leading-tight whitespace-nowrap ${
                    isActive ? 'text-gold font-semibold' : 'text-gold/40 group-hover:text-gold/70'
                  }`}
                  style={{ letterSpacing: '0.04em' }}
                >
                  {isActive && '◀ '}
                  {s.name}
                </span>
                <span
                  className={`hidden md:block text-[9px] mt-0.5 transition-colors ${
                    isActive ? 'text-gold-d/90' : 'text-ink-lt/50 group-hover:text-gold-m/60'
                  }`}
                  style={{ letterSpacing: '0.06em' }}
                >
                  {s.alias}
                </span>
              </button>
            );
          })}
        </div>

        {/* 进度条 */}
        <div className="relative h-[2px] bg-[#2C2C2A] rounded-full mb-1 md:mb-1.5">
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

        {/* 年份行 */}
        <div className="flex justify-between text-[8px] md:text-[10px] text-ink-lt/60 font-mono px-0.5">
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
