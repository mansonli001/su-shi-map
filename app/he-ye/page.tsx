/**
 * 贺野游中国 · 首页 Landing
 * 6 段：Hero / 精选轮播 / 统计 / 最新文章 / 关于 / CTA
 * Server Component — 零客户端 JS，数据从静态 JSON fetch
 */

import Link from 'next/link';
import Image from 'next/image';
import { getHeyeLocationsSSR } from '@/lib/heye-loader-server';
import { Suspense } from 'react';
import HeyeHomeClient from './HeyeHomeClient';
// 样式已在 app/he-ye/layout.tsx 统一加载，无需在此重复 import

export default async function HeyeHome() {
  const locations = getHeyeLocationsSSR();

  // 深度精选：到访>=10次 且 跨>=3个月，按placeName去重取visitCount最高的
  const deepFeaturedMap = new Map<string, typeof locations[0]>();
  for (const loc of locations) {
    const vc = loc.visitCount ?? 1;
    const vh = loc.visitHistory ?? '';
    // 解析visit_history中的月份数
    const months = new Set<string>();
    const parts = vh.split('、');
    for (const p of parts) {
      const m = p.match(/(\d{4})年(\d{1,2})月/);
      if (m) months.add(`${m[1]}-${m[2]}`);
    }
    const mc = months.size;

    if (vc >= 10 && mc >= 3) {
      const existing = deepFeaturedMap.get(loc.placeName);
      if (!existing || vc > (existing.visitCount ?? 0)) {
        deepFeaturedMap.set(loc.placeName, loc);
      }
    }
  }
  const featured = Array.from(deepFeaturedMap.values()).sort((a, b) => (b.visitCount ?? 0) - (a.visitCount ?? 0)).slice(0, 5);
  const latest = locations
    .filter((l) => l.visitYear)
    .sort((a, b) => (b.visitYear ?? 0) - (a.visitYear ?? 0))
    .slice(0, 6);

  const totalPlaces = locations.length;
  const provinces = new Set(locations.map((l) => l.province)).size;
  const allSnacks = new Set(locations.flatMap((l) => l.snacks)).size;

  return (
    <div className="he-home">
      {/* ============ Hero ============ */}
      <section className="he-hero">
        <div className="he-hero-en">HEYE TRAVELS CHINA</div>
        <h1 className="he-hero-brand">贺野游中国</h1>
        <div className="he-hero-tag">跟着贺野，吃遍中国，走遍山河</div>
        <Image
          src="/heye-logo.png"
          alt="贺野游中国"
          width={277}
          height={480}
          className="he-hero-logo"
          style={{ objectFit: 'contain' }}
          priority
        />

        <p className="he-hero-body">
          <span className="he-hero-line">一个人，一辆车，一条路。</span>
          <span className="he-hero-line">从北京的胡同到武夷山的茶田，</span>
          <span className="he-hero-line">从扬州的早茶到潮州的牛肉火锅，</span>
          <span className="he-hero-line">每一步都是风景，每一口都是故事。</span>
        </p>

        <div className="he-hero-btns">
          <Link href="/he-ye/explore" className="he-btn-p">
            开始探索 →
          </Link>
          <a href="#featured" className="he-btn-s">
            看精选
          </a>
        </div>
      </section>

      {/* ============ 精选轮播 ============ */}
      <section id="featured" className="he-sec he-sec--warm">
        <div className="he-sec-lbl">FEATURED</div>
        <h2 className="he-sec-title">精选推荐</h2>

        <Suspense fallback={<div style={{ minHeight: 200 }} />}>
          <HeyeHomeClient featured={featured} />
        </Suspense>
      </section>

      {/* ============ 统计 ============ */}
      <section className="he-sec he-sec--cream">
        <div className="he-sec-lbl">BY THE NUMBERS</div>
        <h2 className="he-sec-title">数字看贺野</h2>

        <div className="he-stats">
          <div className="he-stat">
            <div className="he-stat-n">{totalPlaces}</div>
            <div className="he-stat-l">个足迹</div>
          </div>
          <div className="he-stat">
            <div className="he-stat-n">{provinces}</div>
            <div className="he-stat-l">个省份</div>
          </div>
          <div className="he-stat">
            <div className="he-stat-n">{allSnacks}</div>
            <div className="he-stat-l">种小吃</div>
          </div>
        </div>
      </section>

      {/* ============ 最新文章 ============ */}
      <section className="he-sec he-sec--ivory">
        <div className="he-sec-lbl">LATEST</div>
        <h2 className="he-sec-title">最近去过</h2>
        <div className="he-sec-sub">跟着贺野的脚步，看看他最近去了哪</div>

        <div className="he-latest-grid">
          {latest.map((loc) => (
            <div key={loc.id} className="he-latest-card">
              <div className="he-latest-province">{loc.city} · {loc.province}</div>
              <div className="he-latest-name">{loc.placeName}</div>
              <div className="he-latest-excerpt">{loc.excerpt}</div>
              {loc.snacks.length > 0 && (
                <div className="he-latest-snacks">
                  {loc.snacks.slice(0, 3).map((s) => (
                    <span key={s} className="he-snack-tag">{s}</span>
                  ))}
                </div>
              )}
              {loc.sourceTitle && (
                <Link
                  href={loc.articleUrl || `/he-ye/feed`}
                  className="he-latest-link"
                  target={loc.articleUrl ? '_blank' : undefined}
                  rel={loc.articleUrl ? 'noopener noreferrer' : undefined}
                >
                  读原文 →
                </Link>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ============ 关于 ============ */}
      <section className="he-sec he-sec--warm">
        <div className="he-sec-lbl">ABOUT</div>
        <h2 className="he-sec-title">关于贺野</h2>

        <div className="he-about">
          <div className="he-about-block">
            <div className="he-about-title">一个人在路上</div>
            <div className="he-about-text">
              贺野，公众号「有生余年」作者。一个人开车走遍中国，每到一地必尝当地美食，每走一步必写游记。
            </div>
          </div>
          <div className="he-about-block">
            <div className="he-about-title">不只是攻略</div>
            <div className="he-about-text">
              这不是旅游攻略，不是美食测评。是一个人用自己的脚步丈量这片土地的真实记录。
            </div>
          </div>
        </div>
      </section>

      {/* ============ CTA ============ */}
      <section className="he-cta">
        <h2 className="he-cta-title">在地图上，跟他走一遍</h2>
        <div className="he-cta-sub">
          {totalPlaces} 个足迹 · {provinces} 个省份 · {allSnacks} 种小吃
        </div>
        <div className="he-cta-btns">
          <Link href="/he-ye/explore" className="he-btn-p">
            进入地图 →
          </Link>
          <Link href="/he-ye/feed" className="he-btn-s">
            浏览文章
          </Link>
        </div>
      </section>

      {/* ============ Footer ============ */}
      <footer className="he-footer">
        <div className="he-footer-brand">贺野游中国</div>
        <div className="he-footer-en">HEYE TRAVELS CHINA</div>
        <div className="he-footer-note">
          数据来源：公众号「有生余年」· 贺野原创
        </div>
      </footer>
    </div>
  );
}
