/**
 * /routes — 20 条路线卡片列表（按 6 阶段分组）
 * 设计稿对应 v3.html ③ 路线介绍页
 * 适配：移动端纵向卡片流 / 桌面 grid 2-3 列
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

type RouteIdx = {
  id: string;
  index: number;
  name: string;
  period: string;
  start_year: number;
  end_year: number;
  unique_color: string;
  description_short?: string;
  place_count: number;
  stage_id?: string;
};

type StageIdx = {
  id: string;
  index: number;
  name: string;
  alias: string;
  route_ids: string[];
  start_year: number;
  end_year: number;
  theme: string;
  color: string;
};

// stage → 类型徽章（参考设计稿 ③）
function stageBadge(stageId?: string): { label: string; cls: string } {
  switch (stageId) {
    case 'S1':
      return { label: '少年', cls: 'rb-badge-tour' };
    case 'S3':
      return { label: '蜕变', cls: 'rb-badge-exile' };
    case 'S5':
      return { label: '贬谪', cls: 'rb-badge-exile' };
    case 'S2':
    case 'S4':
      return { label: '仕途', cls: 'rb-badge-office' };
    case 'S6':
      return { label: '终老', cls: 'rb-badge-tour' };
    default:
      return { label: '游历', cls: 'rb-badge-tour' };
  }
}

export default function RoutesListPage() {
  const [routes, setRoutes] = useState<RouteIdx[]>([]);
  const [stages, setStages] = useState<StageIdx[]>([]);
  const [filter, setFilter] = useState<'all' | 'office' | 'exile' | 'tour'>('all');

  useEffect(() => {
    Promise.all([
      fetch('/data-v4/routes-index.json').then((r) => r.json()),
      fetch('/data-v4/stages-index.json').then((r) => r.json()),
    ])
      .then(([rd, sd]) => {
        setRoutes(rd.routes || []);
        setStages(sd.stages || []);
      })
      .catch(() => {});
  }, []);

  // 按 stage 分组路线
  const grouped = stages
    .sort((a, b) => a.index - b.index)
    .map((s) => ({
      stage: s,
      routes: routes
        .filter((r) => r.stage_id === s.id)
        .filter((r) => {
          if (filter === 'all') return true;
          const b = stageBadge(r.stage_id).label;
          if (filter === 'office') return b === '仕途';
          if (filter === 'exile') return b === '贬谪' || b === '蜕变';
          if (filter === 'tour') return b === '归途' || b === '终老' || b === '少年';
          return true;
        })
        .sort((a, b) => a.index - b.index),
    }))
    .filter((g) => g.routes.length > 0);

  const total = routes.length;

  return (
    <div className="rb-root">
      {/* 顶栏 */}
      <div className="rb-topnav">
        <Link href="/" className="rb-back">
          ← 首页
        </Link>
        <div className="rb-topnav-title">行旅路线</div>
        <Link href="/explore" className="rb-topnav-cta">
          地图 →
        </Link>
      </div>

      {/* 标题区 */}
      <div className="rb-header">
        <div className="rb-header-en">ROUTES</div>
        <h1 className="rb-header-title">苏轼行旅路线</h1>
        <div className="rb-header-sub">
          {total} 条路线 · 64 年踪迹 · 6 大人生阶段
        </div>

        {/* 筛选 chips */}
        <div className="rb-chips">
          {[
            { k: 'all', label: `全部 ${total}` },
            { k: 'office', label: '仕途' },
            { k: 'exile', label: '贬谪' },
            { k: 'tour', label: '归途' },
          ].map((c) => (
            <button
              key={c.k}
              onClick={() => setFilter(c.k as 'all' | 'office' | 'exile' | 'tour')}
              className={`rb-chip ${filter === c.k ? 'rb-chip-act' : ''}`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* 按阶段分组 */}
      <div className="rb-list">
        {grouped.map((g) => (
          <div key={g.stage.id} className="rb-stage-group">
            <div className="rb-stage-bar">
              <span className="rb-stage-idx">{g.stage.index + 1}</span>
              <span className="rb-stage-name">{g.stage.name}</span>
              <span className="rb-stage-yrs">
                {g.stage.start_year}–{g.stage.end_year}
              </span>
              <span className="rb-stage-cnt">{g.routes.length} 条</span>
            </div>

            {g.routes.map((r) => {
              const badge = stageBadge(r.stage_id);
              return (
                <Link
                  key={r.id}
                  href={`/routes/${r.id}`}
                  className="rb-card"
                  style={{ borderLeftColor: r.unique_color }}
                >
                  <div className="rb-card-head">
                    <div className="rb-card-name">{r.name}</div>
                    <span className={`rb-badge ${badge.cls}`}>{badge.label}</span>
                  </div>
                  <div className="rb-card-meta">
                    {r.period} · {r.place_count} 个站点
                  </div>
                  {r.description_short && (
                    <div className="rb-card-desc">{r.description_short}</div>
                  )}
                  <div className="rb-card-footer">
                    <span className="rb-card-link">查看完整路线 →</span>
                    <span className="rb-card-id">{r.id}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* 底部 CTA */}
      <div className="rb-footer">
        <Link href="/explore" className="rb-cta-btn">
          在地图上看完整 20 条路线 →
        </Link>
      </div>
    </div>
  );
}
