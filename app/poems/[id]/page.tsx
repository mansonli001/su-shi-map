'use client';

/**
 * /poems/[id] — 诗词详情页 v2.0
 * 改版：顶部信息栏 → 诗词正文 → 分隔线"深度读" → 解读区 → 金句卡片
 * 向下兼容：reading 为空时隐藏解读区，保留旧 background 卡片
 */

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSuShiStore } from '@/lib/store';
import BottomNav from '@/components/BottomNav';

type Poem = {
  id: string;
  title: string;
  author: string;
  type: string;
  year?: number;
  year_estimate?: number;
  month?: number;
  route_id?: string;
  location?: string;
  paragraphs?: string[];
  fullText?: string;
  background?: string;
  famousQuotes?: string[];
  coreVerse?: string;
  // 新增字段
  age?: string;
  situation?: string;
  formNote?: string;
  reading?: {
    scene?: string;
    lines?: Array<{ quote: string; explain: string }>;
    person?: string;
  };
  gold_quote?: string;
  gold_quote_note?: string;
};

type PoemIndex = {
  id: string;
  title: string;
  type?: string;
  route_id?: string;
};

type RouteIdx = {
  id: string;
  name: string;
};

export default function PoemDetailPage() {
  const router = useRouter();
  const params = useParams();
  const poemId = params.id as string;

  const [poem, setPoem] = useState<Poem | null>(null);
  const [allPoems, setAllPoems] = useState<PoemIndex[]>([]);
  const [routes, setRoutes] = useState<Map<string, RouteIdx>>(new Map());
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [loading, setLoading] = useState(true);
  const { addFavoritePoem, removeFavoritePoem, isPoemFavorited } = useSuShiStore();
  const isFavorite = isPoemFavorited(poemId);

  // 判断是否有解读数据
  const hasReading = poem?.reading && (
    poem.reading.scene || (poem.reading.lines && poem.reading.lines.length > 0) || poem.reading.person
  );

  useEffect(() => {
    setLoading(true);

    Promise.all([
      fetch(`/data-v4/poems/${poemId}.json`).then((r) => {
        if (!r.ok) throw new Error('Poem not found');
        return r.json();
      }).catch(() => ({
        id: poemId, title: '', author: '苏轼', paragraphs: [], type: '诗',
      })),
      fetch('/data-v4/poems-index.json').then((r) => r.json()),
      fetch('/data-v4/routes-index.json').then((r) => r.json()),
    ])
      .then(([poemData, poemsIdx, routesIdx]) => {
        const allPoemsList = poemsIdx.poems || [];
        setAllPoems(allPoemsList);

        const routeMap = new Map<string, RouteIdx>();
        for (const r of routesIdx.routes || []) {
          routeMap.set(r.id, { id: r.id, name: r.name });
        }
        setRoutes(routeMap);

        const idx = allPoemsList.findIndex((p: PoemIndex) => p.id === poemId);
        setCurrentIndex(idx);

        const processedPoem: Poem = {
          ...poemData,
          author: poemData.author || '苏轼',
          paragraphs: [],
          location: poemData.location || '',
        };

        if (!processedPoem.location && poemData.route_id) {
          const route = routeMap.get(poemData.route_id);
          if (route) {
            const locationMatch = route.name.match(/·(.+)$/);
            processedPoem.location = locationMatch ? locationMatch[1] : route.name;
          }
        }

        if (poemData.paragraphs && poemData.paragraphs.length > 0) {
          processedPoem.paragraphs = poemData.paragraphs;
        } else if (poemData.fullText) {
          processedPoem.paragraphs = poemData.fullText
            .split('\n')
            .filter((p: string) => p.trim());
        }

        if (processedPoem.paragraphs && processedPoem.paragraphs.length === 0) {
          const idxPoem = allPoemsList.find((p: PoemIndex) => p.id === poemId);
          if (idxPoem) {
            processedPoem.title = idxPoem.title || '未知诗词';
            processedPoem.type = idxPoem.type || '诗';
            processedPoem.paragraphs = ['诗在路上，尚未抵达', '三千余首，仍在一首一首整理。', '这里的篇章，稍后见。', '', '——「腹有诗书气自华」'];
          }
        }

        setPoem(processedPoem);
      })
      .finally(() => setLoading(false));
  }, [poemId]);

  const goToPrev = () => {
    for (let i = currentIndex - 1; i >= 0; i--) {
      const prevPoem = allPoems[i];
      if (!prevPoem.type || prevPoem.type === poem?.type) {
        router.push(`/poems/${prevPoem.id}`);
        return;
      }
    }
  };

  const goToNext = () => {
    for (let i = currentIndex + 1; i < allPoems.length; i++) {
      const nextPoem = allPoems[i];
      if (!nextPoem.type || nextPoem.type === poem?.type) {
        router.push(`/poems/${nextPoem.id}`);
        return;
      }
    }
  };

  if (loading) {
    return (
      <div className="pd-page">
        <div className="pd-loading">载入中…</div>
      </div>
    );
  }

  if (!poem) {
    return (
      <div className="pd-page">
        <div className="pd-not-found">诗词不存在</div>
      </div>
    );
  }

  return (
    <div className="pd-page">
      {/* ── 顶部导航栏 ── */}
      <header className="pd-header">
        <button onClick={() => router.back()} className="pd-back-btn">←</button>
        <span className="pd-header-label">诗词全文</span>
        <button
          className="pd-fav-btn"
          onClick={() => {
            if (isFavorite) {
              removeFavoritePoem(poemId);
            } else {
              addFavoritePoem({
                poemId,
                title: poem?.title || '未知诗词',
                addedAt: new Date().toISOString(),
              });
            }
          }}
          style={{ color: isFavorite ? '#BA7517' : '#999' }}
        >
          ♥
        </button>
      </header>

      {/* ── 顶部信息栏：地点·年份 + 词题 + 作者·年龄 ── */}
      <section className="pd-phone-header">
        <p className="pd-loc">
          {poem.location || '未知地点'}
          {(poem.year || poem.year_estimate) && ` · ${poem.year || poem.year_estimate}年${poem.month ? poem.month + '月' : ''}`}
        </p>
        <p className="pd-title">{poem.title}</p>
        <p className="pd-author">
          {poem.author}
          {poem.age && ` · ${poem.age}`}
        </p>
      </section>

      {/* ── 诗词正文区 ── */}
      <section className="pd-poem-area">
        <p className="pd-poem-main">
          {poem.paragraphs?.map((paragraph, idx) => (
            <span key={idx}>
              {idx > 0 && <span className="pd-poem-break" />}
              {paragraph.split('').map((char, cIdx, arr) => {
                // 在句号、逗号等标点后换行（中文标点后）
                const isPunctuation = /[，。！？；、]/.test(char);
                const nextChar = arr[cIdx + 1];
                // 标点后且后面还有内容时加 <br/>
                return (
                  <span key={cIdx}>
                    {char}
                    {isPunctuation && nextChar && <br />}
                  </span>
                );
              })}
            </span>
          ))}
        </p>
        {poem.formNote && (
          <p className="pd-poem-note">{poem.formNote}</p>
        )}
      </section>

      {/* ── 分隔线"深度读" ── */}
      {hasReading && (
        <div className="pd-divider-label">
          <span>深度读</span>
        </div>
      )}

      {/* ── 解读区 ── */}
      {hasReading && (
        <section className="pd-reading-area">
          {/* 现场 */}
          {poem.reading!.scene && (
            <div className="pd-read-section">
              <p className="pd-sec-label">现场</p>
              {poem.reading!.scene.split('\n').filter(Boolean).map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
          )}

          {/* 人话 */}
          {poem.reading!.lines && poem.reading!.lines.length > 0 && (
            <div className="pd-read-section">
              <p className="pd-sec-label">人话</p>
              {poem.reading!.lines.map((line, i) => (
                <div key={i}>
                  <div className="pd-quote-line">
                    <p>{line.quote}</p>
                  </div>
                  <p>{line.explain}</p>
                </div>
              ))}
            </div>
          )}

          {/* 这个人 */}
          {poem.reading!.person && (
            <div className="pd-read-section">
              <p className="pd-sec-label">这个人</p>
              {poem.reading!.person.split('\n').filter(Boolean).map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
          )}
        </section>
      )}

      {/* ── 金句卡片（新） ── */}
      {poem.gold_quote ? (
        <div className="pd-gold-box">
          <p className="pd-g-label">本词金句</p>
          <p className="pd-g-quote">{poem.gold_quote}</p>
          {poem.gold_quote_note && (
            <p className="pd-g-note">{poem.gold_quote_note}</p>
          )}
        </div>
      ) : poem.famousQuotes && poem.famousQuotes.length > 0 ? (
        /* 向下兼容：无 gold_quote 时显示旧版名句 */
        <div className="pd-quotes-legacy">
          <div className="pd-quotes-title">核心名句</div>
          {poem.famousQuotes.map((quote, idx) => (
            <div key={idx} className={`pd-quote-item ${idx === 0 ? 'primary' : ''}`}>
              {quote}
            </div>
          ))}
        </div>
      ) : null}

      {/* ── 创作背景（reading 为空时保留） ── */}
      {!hasReading && poem.background && (
        <div className="pd-background">
          <div className="pd-section-title">创作背景</div>
          <div className="pd-section-content">{poem.background}</div>
        </div>
      )}

      {/* ── 底部导航 ── */}
      <nav className="pd-nav">
        <button
          className="pd-nav-btn"
          onClick={goToPrev}
          disabled={!poem || !allPoems.slice(0, currentIndex).some(p => !p.type || p.type === poem.type)}
        >
          ← 上一首
        </button>
        <button className="pd-nav-all" onClick={() => router.push('/poems')}>
          全部
        </button>
        <button
          className="pd-nav-btn"
          onClick={goToNext}
          disabled={!poem || !allPoems.slice(currentIndex + 1).some(p => !p.type || p.type === poem.type)}
        >
          下一首 →
        </button>
      </nav>

      <BottomNav />

      {/* ── 样式 ── */}
      <style jsx>{`
        .pd-page {
          min-height: 100vh;
          background: var(--color-background-secondary, var(--bg, #F1EFE8));
          font-family: var(--font-sans);
          padding-bottom: calc(64px + env(safe-area-inset-bottom));
        }

        /* ── 顶部导航栏 ── */
        .pd-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 16px 10px;
          background: var(--color-background, var(--card, #fff));
          border-bottom: 0.5px solid var(--color-border-tertiary, var(--bdr, #E5E7EB));
        }
        .pd-back-btn {
          background: transparent;
          border: none;
          color: var(--color-text-secondary, var(--tx2));
          font-size: 20px;
          cursor: pointer;
          padding: 0;
          font-family: var(--font-serif);
        }
        .pd-header-label {
          font-size: 11px;
          color: var(--color-text-tertiary, var(--tx3));
          letter-spacing: 0.1em;
        }
        .pd-fav-btn {
          background: transparent;
          border: none;
          font-size: 18px;
          cursor: pointer;
          padding: 0;
        }

        /* ── 顶部信息栏 ── */
        .pd-phone-header {
          padding: 14px 16px 10px;
          border-bottom: 0.5px solid var(--color-border-tertiary, var(--bdr, #E5E7EB));
          background: var(--color-background, var(--card, #fff));
        }
        .pd-loc {
          font-size: 11px;
          color: #BA7517;
          letter-spacing: 0.06em;
          margin: 0 0 4px;
        }
        .pd-title {
          font-size: 22px;
          font-weight: 500;
          color: var(--color-text-primary, var(--tx, #1A1008));
          margin: 0 0 2px;
          line-height: 1.3;
        }
        .pd-author {
          font-size: 13px;
          color: var(--color-text-tertiary, var(--tx3));
          margin: 0;
        }

        /* ── 诗词正文区 ── */
        .pd-poem-area {
          padding: 24px 20px 20px;
          border-bottom: 0.5px solid var(--color-border-tertiary, var(--bdr, #E5E7EB));
          background: var(--color-background, var(--card, #fff));
        }
        .pd-poem-main {
          margin: 0;
          font-family: var(--font-serif);
          font-size: 18px;
          line-height: 2.2;
          color: var(--color-text-primary, var(--tx, #1A1008));
          letter-spacing: 0.08em;
        }
        .pd-poem-break {
          height: 14px;
          display: block;
        }
        .pd-poem-note {
          font-size: 12px;
          color: var(--color-text-tertiary, var(--tx3));
          margin-top: 12px;
          letter-spacing: 0.02em;
        }

        /* ── 分隔线"深度读" ── */
        .pd-divider-label {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 0 20px;
          margin: 20px 0 0;
        }
        .pd-divider-label span {
          font-size: 11px;
          color: var(--color-text-tertiary, var(--tx3));
          letter-spacing: 0.08em;
          white-space: nowrap;
        }
        .pd-divider-label::before,
        .pd-divider-label::after {
          content: '';
          flex: 1;
          height: 0.5px;
          background: var(--color-border-tertiary, var(--bdr, #E5E7EB));
        }

        /* ── 解读区 ── */
        .pd-reading-area {
          padding: 16px 20px 0;
        }
        .pd-read-section {
          margin-bottom: 20px;
        }
        .pd-read-section .pd-sec-label {
          font-size: 11px;
          color: #BA7517;
          letter-spacing: 0.06em;
          margin: 0 0 8px;
        }
        .pd-read-section p {
          font-size: 14px;
          color: var(--color-text-primary, var(--tx, #1A1008));
          line-height: 1.9;
          margin: 0 0 10px;
          letter-spacing: 0.01em;
        }
        .pd-read-section p:last-child {
          margin-bottom: 0;
        }

        /* 引文块 */
        .pd-quote-line {
          border-left: 2px solid #EF9F27;
          padding-left: 10px;
          margin: 4px 0 10px;
          border-radius: 0;
        }
        .pd-quote-line p {
          font-family: var(--font-serif);
          font-size: 14px;
          color: var(--color-text-secondary, var(--tx2));
          line-height: 1.8;
          margin: 0;
        }

        /* ── 金句卡片 ── */
        .pd-gold-box {
          background: #FAEEDA;
          border-radius: 8px;
          padding: 14px 16px;
          margin: 20px 20px 0;
          border: 0.5px solid #EF9F27;
        }
        .pd-g-label {
          font-size: 11px;
          color: #854F0B;
          letter-spacing: 0.06em;
          margin: 0 0 6px;
        }
        .pd-g-quote {
          font-family: var(--font-serif);
          font-size: 17px;
          font-weight: 500;
          color: #633806;
          margin: 0 0 4px;
          line-height: 1.8;
        }
        .pd-g-note {
          font-size: 12px;
          color: #854F0B;
          margin: 0;
          line-height: 1.6;
        }

        /* ── 旧版名句（向下兼容） ── */
        .pd-quotes-legacy {
          margin: 20px 20px 0;
          padding: 14px 16px;
          border-left: 2px solid #EF9F27;
          background: #FAEEDA;
          border-radius: 0 8px 8px 0;
        }
        .pd-quotes-title {
          font-size: 11px;
          color: #854F0B;
          letter-spacing: 0.06em;
          margin-bottom: 6px;
        }
        .pd-quote-item {
          font-family: var(--font-serif);
          font-size: 14px;
          color: #633806;
          line-height: 1.8;
        }
        .pd-quote-item.primary {
          font-size: 17px;
          font-weight: 500;
        }

        /* ── 创作背景（reading 为空时保留） ── */
        .pd-background {
          background: var(--color-background, var(--card, #fff));
          border-radius: 8px;
          padding: 14px 16px;
          border: 0.5px solid var(--color-border-tertiary, var(--bdr, #E5E7EB));
          margin: 20px 20px 0;
        }
        .pd-section-title {
          font-size: 11px;
          color: #BA7517;
          letter-spacing: 0.06em;
          margin-bottom: 8px;
        }
        .pd-section-content {
          font-size: 14px;
          color: var(--color-text-secondary, var(--tx2));
          line-height: 1.9;
        }

        /* ── 底部导航 ── */
        .pd-nav {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          gap: 8px;
          padding: 12px 16px;
          margin-top: 20px;
          background: var(--color-background, var(--card, #fff));
          border-top: 0.5px solid var(--color-border-tertiary, var(--bdr, #E5E7EB));
        }
        .pd-nav-btn {
          font-family: var(--font-serif);
          font-size: 12px;
          color: var(--color-text-secondary, var(--tx2));
          background: transparent;
          border: 0.5px solid var(--color-border-tertiary, var(--bdr, #E5E7EB));
          border-radius: 8px;
          padding: 10px;
          cursor: pointer;
        }
        .pd-nav-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }
        .pd-nav-all {
          font-family: var(--font-serif);
          font-size: 11px;
          color: var(--color-text-tertiary, var(--tx3));
          background: transparent;
          border: none;
          padding: 10px;
          cursor: pointer;
        }

        .pd-loading, .pd-not-found {
          text-align: center;
          padding: 2rem;
          color: var(--color-text-tertiary, var(--tx3));
          font-size: 12px;
        }

        /* ── Dark mode ── */
        @media (prefers-color-scheme: dark) {
          .pd-gold-box {
            background: #412402;
            border-color: #854F0B;
          }
          .pd-g-label {
            color: #FAC775;
          }
          .pd-g-quote {
            color: #FAEEDA;
          }
          .pd-g-note {
            color: #EF9F27;
          }
          .pd-quote-line {
            border-left-color: #BA7517;
          }
          .pd-quotes-legacy {
            background: #412402;
            border-left-color: #BA7517;
          }
          .pd-quotes-title {
            color: #FAC775;
          }
          .pd-quote-item {
            color: #FAEEDA;
          }
        }
      `}</style>
    </div>
  );
}
