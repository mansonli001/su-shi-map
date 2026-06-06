/**
 * /routes/[id] — 单条路线沉浸阅读页（手机优先）
 * 设计稿 ⑨ 路线详情 + 内容增强
 *
 * 内容结构：
 *   ① Hero：路线名 + 时段 + 起止 + unique_color 大色块
 *   ② core_essence — 核心精神（金色引语块）
 *   ③ description_long — 史诗叙事
 *   ④ key_locations_summary — 地理脉络
 *   ⑤ key_events 时间轴
 *   ⑥ literary_output — 文学风格 + 代表作
 *   ⑦ 底部 CTA：在地图上看 →
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

/**
 * 把 markdown 风格 **bold** 标记安全地转成 React 节点
 * 修复 v6.1: 替换 dangerouslySetInnerHTML，杜绝数据源被污染时的 XSS 风险
 */
function renderBoldMarkers(line: string): React.ReactNode {
  if (!line.includes('**')) return line;
  const parts = line.split(/\*\*(.+?)\*\*/g);
  // split 结果：偶数 index 为普通文本，奇数 index 为加粗内容
  return parts.map((seg, i) =>
    i % 2 === 1 ? <strong key={i}>{seg}</strong> : <span key={i}>{seg}</span>,
  );
}

type RouteDetail = {
  id: string;
  index: number;
  name: string;
  period: string;
  start_year: number;
  end_year: number;
  unique_color: string;
  description_short?: string;
  description_long?: string;
  core_essence?: string;
  key_locations_summary?: string;
  key_events?: Array<{
    title: string;
    content: string;
    year?: number;
    age?: number;
  }>;
  literary_output?: {
    description?: string;
    style_features?: string;
    representative_works?: Array<{
      title: string;
      category?: string;
      year_estimate?: string | number;
      note?: string;
      poem_id?: string;
    }>;
  };
  track_segments?: Array<{
    segment_id: string;
    label?: string;
    place_ids: string[];
  }>;
  stage_id?: string;
};

type PlaceIdx = {
  id: string;
  ancient_name: string;
  modern_name: string;
};

export default function RouteDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [route, setRoute] = useState<RouteDetail | null>(null);
  const [placesMap, setPlacesMap] = useState<Map<string, PlaceIdx>>(new Map());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch(`/data-v4/routes/${params.id}.json`).then((r) =>
        r.ok ? r.json() : null,
      ),
      fetch('/data-v4/places-index.json').then((r) => r.json()),
    ])
      .then(([rd, pd]) => {
        if (!rd) {
          setRoute(null);
        } else {
          setRoute(rd as RouteDetail);
        }
        const m = new Map<string, PlaceIdx>();
        for (const p of pd.places || []) m.set(p.id, p);
        setPlacesMap(m);
      })
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="rd-root">
        <div className="rd-loading">载入路线中…</div>
      </div>
    );
  }

  if (!route) {
    return (
      <div className="rd-root">
        <div className="rd-empty">
          <div className="text-center py-10 px-4">
            <div className="mb-5 flex justify-center text-ink-lt/30">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 12L8 16V36L16 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M16 12L24 16V36L16 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M32 12L24 16V36L32 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M32 12L40 16V36L32 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="24" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
            </div>
            <h3 className="font-wenkai mb-3" style={{ fontSize: '17px', color: '#1a1410', fontWeight: 500 }}>
              二十条路线，正在铺开
            </h3>
            <p className="font-wenkai" style={{ fontSize: '14px', color: '#6b5d54', lineHeight: 1.8 }}>
              每条路线都是一段独立故事，
            </p>
            <p className="font-wenkai" style={{ fontSize: '14px', color: '#6b5d54', lineHeight: 1.8 }}>
              正在逐条整理史料与地点。
            </p>
            <p className="font-wenkai" style={{ fontSize: '14px', color: '#6b5d54', lineHeight: 1.8 }}>
              地图上的足迹已在，
            </p>
            <p className="font-wenkai" style={{ fontSize: '14px', color: '#6b5d54', lineHeight: 1.8 }}>
              路线叙事稍后见。
            </p>
            <Link href="/routes" className="font-wenkai text-[13px] text-gold-m hover:text-gold-d underline underline-offset-4 transition-colors mt-4 inline-block">
              ← 返回路线列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 拼出主路径站点
  const trackPids: string[] = [];
  for (const seg of route.track_segments || []) {
    for (const pid of seg.place_ids || []) {
      if (!trackPids.includes(pid)) trackPids.push(pid);
    }
  }

  return (
    <div className="rd-root">
      {/* 顶栏 */}
      <div className="rb-topnav" style={{ background: route.unique_color }}>
        <button onClick={() => router.back()} className="rb-back">
          ← 返回
        </button>
        <div className="rb-topnav-title" style={{ color: '#fff' }}>
          {route.id} · {route.name}
        </div>
        <Link
          href={`/explore?route=${route.id}`}
          className="rb-topnav-cta"
          style={{ color: '#fff' }}
        >
          地图 →
        </Link>
      </div>

      {/* Hero 色块 */}
      <div
        className="rd-hero"
        style={{
          background: `linear-gradient(180deg, ${route.unique_color} 0%, ${route.unique_color}dd 100%)`,
        }}
      >
        <div className="rd-hero-en">{route.id} · ROUTE</div>
        <h1 className="rd-hero-title">{route.name}</h1>
        <div className="rd-hero-period">
          {route.start_year} — {route.end_year}　·　{route.period}
        </div>
        {route.description_short && (
          <p className="rd-hero-short">{route.description_short}</p>
        )}
      </div>

      {/* core_essence 核心精神 */}
      {route.core_essence && (
        <section className="rd-section rd-section--cream">
          <div className="rd-sec-lbl">CORE ESSENCE</div>
          <h2 className="rd-sec-title">核心精神</h2>
          <div className="rd-essence">
            {route.core_essence.split('\n').map((line, i) =>
              line.trim() ? (
                <p key={i}>{line}</p>
              ) : null,
            )}
          </div>
        </section>
      )}

      {/* description_long 史诗叙事 */}
      {route.description_long && (
        <section className="rd-section">
          <div className="rd-sec-lbl">NARRATIVE</div>
          <h2 className="rd-sec-title">史诗叙事</h2>
          <div className="rd-narrative">
            {route.description_long.split('\n').map((line, i) =>
              line.trim() ? (
                <p key={i}>{renderBoldMarkers(line)}</p>
              ) : null,
            )}
          </div>
        </section>
      )}

      {/* key_locations_summary 地理脉络 */}
      {route.key_locations_summary && (
        <section className="rd-section rd-section--cream">
          <div className="rd-sec-lbl">GEOGRAPHY</div>
          <h2 className="rd-sec-title">地理脉络</h2>
          <p className="rd-locations">
            {route.key_locations_summary.split('\n').map((line, i) =>
              line.trim() ? (
                <span key={i}>
                  {renderBoldMarkers(line)}
                  <br />
                </span>
              ) : null,
            )}
          </p>
        </section>
      )}

      {/* key_events 关键事件时间轴 */}
      {(route.key_events?.length ?? 0) > 0 && (
        <section className="rd-section">
          <div className="rd-sec-lbl">KEY EVENTS</div>
          <h2 className="rd-sec-title">关键事件</h2>
          <div className="rd-events">
            {route.key_events!.map((ev, i) => (
              <div key={i} className="rd-event">
                <div className="rd-event-dot" style={{ background: route.unique_color }} />
                <div className="rd-event-body">
                  <div className="rd-event-meta">
                    {ev.year && <span className="rd-event-year">{ev.year}</span>}
                    {ev.age && <span className="rd-event-age">{ev.age}岁</span>}
                  </div>
                  <div className="rd-event-title">{ev.title}</div>
                  <div className="rd-event-content">{ev.content}</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 站点链 */}
      {trackPids.length > 0 && (
        <section className="rd-section rd-section--cream">
          <div className="rd-sec-lbl">TRACK STATIONS</div>
          <h2 className="rd-sec-title">主路径站点 · {trackPids.length} 站</h2>
          <div className="rd-track">
            {trackPids.map((pid, i) => {
              const p = placesMap.get(pid);
              return (
                <div key={pid} className="rd-track-item">
                  <div className="rd-track-num" style={{ background: route.unique_color }}>
                    {i + 1}
                  </div>
                  <div className="rd-track-info">
                    <div className="rd-track-name">{p?.ancient_name || pid}</div>
                    <div className="rd-track-modern">{p?.modern_name || ''}</div>
                  </div>
                  {i < trackPids.length - 1 && <div className="rd-track-arrow">↓</div>}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* 文学风格 */}
      {route.literary_output && (
        <section className="rd-section">
          <div className="rd-sec-lbl">LITERARY OUTPUT</div>
          <h2 className="rd-sec-title">文学创作</h2>
          {route.literary_output.description && (
            <p className="rd-literary">{route.literary_output.description}</p>
          )}
          {route.literary_output.style_features && (
            <div className="rd-style">
              <div className="rd-style-lbl">风格特征</div>
              <div className="rd-style-text">{route.literary_output.style_features}</div>
            </div>
          )}
          {(route.literary_output.representative_works?.length ?? 0) > 0 && (
            <div className="rd-works">
              <div className="rd-works-lbl">代表作 · {route.literary_output.representative_works!.length} 篇</div>
              <div className="rd-works-list">
                {route.literary_output.representative_works!.map((w, i) => (
                  <div 
                    key={i} 
                    className="rd-work"
                    onClick={() => {
                      if (w.poem_id) {
                        router.push(`/poems/${w.poem_id}`);
                      }
                    }}
                    style={{ cursor: w.poem_id ? 'pointer' : 'default' }}
                  >
                    <div className="rd-work-title">《{w.title}》</div>
                    {w.category && <span className="rd-work-cat">{w.category}</span>}
                    {w.year_estimate && (
                      <span className="rd-work-year">{w.year_estimate}</span>
                    )}
                    {w.note && <div className="rd-work-note">{w.note}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* 底部 CTA */}
      <div className="rd-footer">
        <Link href={`/explore?route=${route.id}`} className="rb-cta-btn">
          在地图上看「{route.name}」 →
        </Link>
        <Link href="/routes" className="rd-back-link">
          ← 返回路线列表
        </Link>
      </div>
    </div>
  );
}
