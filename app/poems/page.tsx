'use client';

/**
 * /poems — 诗词列表页（设计稿 p6）
 * 完全按照设计文件实现
 */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

type PoemIndex = {
  id: string;
  title: string;
  type: string;
  year?: number;
  route_id?: string;
  has_full_text: boolean;
  coreVerse?: string;
};

type RouteIdx = {
  id: string;
  name: string;
  start_year: number;
  end_year: number;
  unique_color: string;
};

export default function PoemsListPage() {
  const router = useRouter();
  const [poems, setPoems] = useState<PoemIndex[]>([]);
  const [routes, setRoutes] = useState<Map<string, RouteIdx>>(new Map());
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<string>('全部');
  const [searchQuery] = useState('');

  const filters = ['全部', '词', '诗', '文', '赋'];

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch('/data-v4/poems-index.json').then((r) => r.json()),
      fetch('/data-v4/routes-index.json').then((r) => r.json()),
    ])
      .then(([poemsIdx, routesIdx]) => {
        setPoems(poemsIdx.poems || []);
        const m = new Map<string, RouteIdx>();
        for (const r of routesIdx.routes || []) m.set(r.id, r);
        setRoutes(m);
      })
      .finally(() => setLoading(false));
  }, []);

  // 筛选诗词
  const filteredPoems = poems.filter((poem) => {
    // 类型筛选
    if (activeFilter !== '全部' && poem.type !== activeFilter) return false;
    // 搜索筛选
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        poem.title.toLowerCase().includes(q) ||
        (poem.coreVerse && poem.coreVerse.toLowerCase().includes(q))
      );
    }
    return true;
  });

  // 按路线分组
  const groupedByRoute: Record<string, PoemIndex[]> = {};
  filteredPoems.forEach((poem) => {
    const key = poem.route_id || 'unassigned';
    if (!groupedByRoute[key]) groupedByRoute[key] = [];
    groupedByRoute[key].push(poem);
  });

  if (loading) {
    return (
      <div className="poems-list">
        <div className="poems-loading">载入中…</div>
      </div>
    );
  }

  return (
    <div className="poems-list">
      {/* 顶部导航 */}
      <div className="poems-header">
        <button onClick={() => router.back()} className="poems-back-btn">
          ←
        </button>
        <div className="poems-header-text">
          <div className="poems-title">苏轼诗词全集</div>
          <div className="poems-count">共 {filteredPoems.length} 首 · 按创作时间</div>
        </div>
      </div>

      {/* 筛选标签 */}
      <div className="poems-filters">
        {filters.map((filter) => (
          <button
            key={filter}
            className={`filter-chip ${activeFilter === filter ? 'active' : ''}`}
            onClick={() => setActiveFilter(filter)}
          >
            {filter}
          </button>
        ))}
      </div>

      {/* 诗词列表 */}
      <div className="poems-content">
        {Object.entries(groupedByRoute).map(([routeId, routePoems]) => {
          const route = routes.get(routeId);
          return (
            <div key={routeId}>
              {route && (
                <div className="route-header">
                  {route.name} · {route.start_year}—{route.end_year}年
                </div>
              )}
              {routePoems.map((poem) => (
                <div key={poem.id} className="poem-card">
                  <div className="poem-card-header">
                    <div className="poem-title">{poem.title}</div>
                    <span className={`poem-type ${getTypeClass(poem.type)}`}>
                      {poem.type}
                    </span>
                  </div>
                  <div className="poem-meta">
                    {poem.year && `${poem.year}年`}
                  </div>
                  {poem.coreVerse && (
                    <div className="poem-verse">
                      {poem.coreVerse}
                    </div>
                  )}
                  <Link href={`/poems/${poem.id}`} className="poem-action" style={{
                    display: 'block',
                    textAlign: 'right',
                    fontSize: '10px',
                    fontWeight: 500,
                    color: '#BA7517',
                    padding: '8px 0 2px',
                    marginTop: '8px',
                    textDecoration: 'none',
                    letterSpacing: '0.04em',
                    lineHeight: 1.5
                  }}>
                    查看全文与赏析 →
                  </Link>
                </div>
              ))}
            </div>
          );
        })}

        {filteredPoems.length === 0 && (
          <div className="poems-empty">
            暂无匹配的诗词
          </div>
        )}
      </div>

      {/* 样式 */}
      <style jsx>{`
        .poems-list {
          min-height: 100vh;
          background: var(--bg);
          font-family: var(--font-sans);
        }

        /* 顶部导航 */
        .poems-header {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 1.1rem 1rem 0.7rem;
          background: var(--card);
        }

        .poems-back-btn {
          background: transparent;
          border: none;
          color: var(--tx2);
          font-size: 20px;
          cursor: pointer;
          padding: 0;
          font-family: var(--font-sans);
        }

        .poems-header-text {
          flex: 1;
        }

        .poems-title {
          font-size: 15px;
          font-weight: 600;
          color: var(--tx);
        }

        .poems-count {
          font-size: 11px;
          color: var(--gold-m);
          letter-spacing: 0.05em;
          margin-top: 2px;
        }

        /* 筛选标签 */
        .poems-filters {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
          padding: 0 1rem 0.7rem;
          background: var(--card);
          border-bottom: 0.5px solid var(--bdr);
        }

        .filter-chip {
          font-family: var(--font-serif);
          font-size: 11px;
          padding: 5px 13px;
          border: 0.5px solid var(--bdr);
          border-radius: 14px;
          color: var(--tx2);
          background: transparent;
          cursor: pointer;
        }

        .filter-chip.active {
          background: var(--gold-m);
          color: #FAEEDA;
          border-color: var(--gold-m);
        }

        /* 内容区 */
        .poems-content {
          padding: 0.5rem 1rem 1rem;
          background: var(--sec);
        }

        /* 路线标题 */
        .route-header {
          font-size: 10px;
          color: var(--tx3);
          margin: 12px 0 8px;
          padding-left: 4px;
        }

        /* 诗词卡片 */
        .poem-card {
          background: var(--card);
          border: 0.5px solid var(--bdr);
          border-radius: 12px;
          padding: 0.9rem;
          margin-bottom: 10px;
        }

        .poem-card-header {
          display: flex;
          justify-content: space-between;
          align-items: start;
          margin-bottom: 0.3rem;
        }

        .poem-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--tx);
        }

        .poem-type {
          font-size: 9px;
          padding: 2px 9px;
          border-radius: 7px;
        }

        .poem-type.词 {
          background: #FAEEDA;
          color: var(--tour);
        }

        .poem-type.诗 {
          background: #E1F5EE;
          color: #04342C;
        }

        .poem-type.文 {
          background: #F3E8FF;
          color: #4C1D95;
        }

        .poem-type.赋 {
          background: #FEF3C7;
          color: #92400E;
        }

        .poem-type.策 {
          background: #DBEAFE;
          color: #1D4ED8;
        }

        .poem-meta {
          font-size: 10px;
          color: var(--tx3);
          margin-bottom: 9px;
        }

        .poem-verse {
          border-left: 2px solid var(--gold-d);
          padding: 4px 10px;
          font-size: 12px;
          color: var(--tx);
          line-height: 1.9;
          background: var(--sec);
        }

        .poem-action,
        .poem-card .poem-action,
        .poem-action:link,
        .poem-action:visited {
          display: block !important;
          text-align: right !important;
          font-size: 10px !important;
          font-weight: 500 !important;
          color: #BA7517 !important;
          padding: 8px 0 2px !important;
          margin-top: 8px !important;
          text-decoration: none !important;
          letter-spacing: 0.04em !important;
          line-height: 1.5 !important;
        }

        .poems-empty {
          text-align: center;
          padding: 2rem;
          color: var(--tx3);
          font-size: 12px;
        }
      `}</style>
    </div>
  );
}

function getTypeClass(type: string): string {
  const typeClasses: Record<string, string> = {
    '词': '词',
    '诗': '诗',
    '文': '文',
    '赋': '赋',
    '策': '策',
  };
  return typeClasses[type] || '';
}
