/**
 * 贺野游中国 · 文章流
 * 按时间线展示所有地点，支持省份筛选
 */
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getHeyeLocations } from '@/lib/heye-loader';
import { useHeyeStore } from '@/lib/heye-store';
import type { HeyeLocation } from '@/types/heye';

export default function HeyeFeedPage() {
  const [locations, setLocations] = useState<HeyeLocation[]>([]);
  const [filterProvince, setFilterProvince] = useState<string | null>(null);
  const { heyeCheckins, addHeyeCheckin } = useHeyeStore();

  useEffect(() => {
    getHeyeLocations().then(setLocations);
  }, []);

  const provinces = [...new Set(locations.map((l) => l.province))].sort();
  const checkedIds = new Set(heyeCheckins.map((c) => c.placeId));

  const filtered = locations
    .filter((l) => !filterProvince || l.province === filterProvince)
    .sort((a, b) => (b.visitYear ?? 0) - (a.visitYear ?? 0));

  // 按年份分组
  const grouped: Record<number, HeyeLocation[]> = {};
  filtered.forEach((loc) => {
    const year = loc.visitYear ?? 0;
    if (!grouped[year]) grouped[year] = [];
    grouped[year].push(loc);
  });

  const years = Object.keys(grouped)
    .map(Number)
    .sort((a, b) => b - a);

  return (
    <div className="he-feed">
      {/* 顶栏 */}
      <div className="he-feed-topbar">
        <h1 className="he-feed-title">文章流</h1>
        <div className="he-feed-stats">{locations.length} 篇</div>
      </div>

      {/* 筛选 */}
      <div className="he-map-filter">
        <button
          className={`he-filter-btn ${!filterProvince ? 'active' : ''}`}
          onClick={() => setFilterProvince(null)}
        >
          全部
        </button>
        {provinces.map((p) => (
          <button
            key={p}
            className={`he-filter-btn ${filterProvince === p ? 'active' : ''}`}
            onClick={() => setFilterProvince(filterProvince === p ? null : p)}
          >
            {p}
          </button>
        ))}
      </div>

      {/* 时间线 */}
      <div className="he-feed-timeline">
        {years.map((year) => (
          <div key={year} className="he-feed-year-group">
            <div className="he-feed-year">{year || '未知年份'}</div>
            <div className="he-feed-cards">
              {grouped[year].map((loc) => (
                <div key={loc.id} className="he-feed-card">
                  <div className="he-feed-card-header">
                    <span className="he-feed-card-province">{loc.city} · {loc.province}</span>
                    {loc.visitDate && (
                      <span className="he-feed-card-date">{loc.visitDate}</span>
                    )}
                  </div>
                  <div className="he-feed-card-name">{loc.fullName}</div>
                  <div className="he-feed-card-excerpt">{loc.excerpt}</div>
                  {loc.snacks.length > 0 && (
                    <div className="he-feed-card-snacks">
                      {loc.snacks.map((s) => (
                        <span key={s} className="he-snack-tag">{s}</span>
                      ))}
                    </div>
                  )}
                  <div className="he-feed-card-actions">
                    <Link
                      href={`/he-ye/explore?focus=${loc.id}`}
                      className="he-feed-card-link"
                    >
                      在地图上看 →
                    </Link>
                    {loc.articleUrl && (
                      <a
                        href={loc.articleUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="he-article-link"
                      >
                        读原文 →
                      </a>
                    )}
                    {checkedIds.has(loc.id) ? (
                      <span className="he-checkin-done">已打卡</span>
                    ) : (
                      <button
                        className="he-checkin-btn-sm"
                        onClick={() =>
                          addHeyeCheckin({
                            placeId: loc.id,
                            placeName: loc.placeName,
                            checkinAt: new Date().toISOString(),
                            checkinType: 'cloud',
                          })
                        }
                      >
                        打卡
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
