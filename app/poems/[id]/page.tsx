'use client';

/**
 * /poems/[id] — 诗词详情页（设计稿 p7）
 * 完全按照设计文件实现
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

  useEffect(() => {
    setLoading(true);
    
    Promise.all([
      fetch(`/data-v4/poems/${poemId}.json`).then((r) => {
        if (!r.ok) {
          throw new Error('Poem not found');
        }
        return r.json();
      }).catch(() => {
        return { id: poemId, title: '', author: '苏轼', paragraphs: [], type: '诗' };
      }),
      fetch('/data-v4/poems-index.json').then((r) => r.json()),
      fetch('/data-v4/routes-index.json').then((r) => r.json()),
    ])
      .then(([poemData, poemsIdx, routesIdx]) => {
        const allPoemsList = poemsIdx.poems || [];
        setAllPoems(allPoemsList);
        
        // 构建路线映射
        const routeMap = new Map<string, RouteIdx>();
        for (const r of routesIdx.routes || []) {
          routeMap.set(r.id, { id: r.id, name: r.name });
        }
        setRoutes(routeMap);
        
        // 查找当前诗词在列表中的位置
        const idx = allPoemsList.findIndex((p: PoemIndex) => p.id === poemId);
        setCurrentIndex(idx);
        
        // 处理数据：适配 fullText 和 paragraphs 两种格式
        const processedPoem = {
          ...poemData,
          author: poemData.author || '苏轼',
          paragraphs: [] as string[],
          location: poemData.location || '',
        };
        
        // 如果没有 location，尝试从 route_id 获取路线名称
        if (!processedPoem.location && poemData.route_id) {
          const route = routeMap.get(poemData.route_id);
          if (route) {
            // 从路线名称中提取地点信息
            const locationMatch = route.name.match(/·(.+)$/);
            processedPoem.location = locationMatch ? locationMatch[1] : route.name;
          }
        }
        
        // 优先使用 paragraphs，如果没有则从 fullText 拆分
        if (poemData.paragraphs && poemData.paragraphs.length > 0) {
          processedPoem.paragraphs = poemData.paragraphs;
        } else if (poemData.fullText) {
          // 将 fullText 按换行符拆分成段落
          processedPoem.paragraphs = poemData.fullText
            .split('\n')
            .filter((p: string) => p.trim());
        }
        
        // 如果仍然没有内容，尝试从索引补充
        if (processedPoem.paragraphs.length === 0) {
          const idxPoem = allPoemsList.find((p: PoemIndex) => p.id === poemId);
          if (idxPoem) {
            processedPoem.title = idxPoem.title || '未知诗词';
            processedPoem.type = idxPoem.type || '诗';
            processedPoem.paragraphs = ['诗词内容暂未收录，请期待后续更新'];
          }
        }
        
        setPoem(processedPoem);
      })
      .finally(() => setLoading(false));
  }, [poemId]);

  const goToPrev = () => {
    // 只在同类型诗词之间跳转
    for (let i = currentIndex - 1; i >= 0; i--) {
      const prevPoem = allPoems[i];
      if (!prevPoem.type || prevPoem.type === poem?.type) {
        router.push(`/poems/${prevPoem.id}`);
        return;
      }
    }
  };

  const goToNext = () => {
    // 只在同类型诗词之间跳转
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
      <div className="poem-detail">
        <div className="poem-loading">载入中…</div>
      </div>
    );
  }

  if (!poem) {
    return (
      <div className="poem-detail">
        <div className="poem-not-found">诗词不存在</div>
      </div>
    );
  }

  return (
    <div className="poem-detail">
      {/* 顶部导航 */}
      <div className="poem-header">
        <button onClick={() => router.back()} className="poem-back-btn">
          ←
        </button>
        <span className="poem-header-label">诗词全文</span>
        <button 
          className="poem-fav-btn" 
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
      </div>

      {/* 诗词信息 */}
      <div className="poem-info">
        <div className="poem-location">
          {poem.location || '未知地点'} · {(poem.year || poem.year_estimate) && `${poem.year || poem.year_estimate}年${poem.month || ''}`}
        </div>
        <div className="poem-title">{poem.title}</div>
        <div className="poem-author">{poem.author}</div>
      </div>

      {/* 诗词正文 */}
      <div className="poem-content">
        <div className="poem-text">
          {poem.paragraphs?.map((paragraph, idx) => (
            <div key={idx} className="poem-paragraph">
              {paragraph.split('。').map((sentence, sIdx) => (
                <div key={sIdx} className="poem-line">
                  {sentence}
                  {sIdx < paragraph.split('。').length - 1 && '。'}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* 创作背景 */}
      {poem.background && (
        <div className="poem-background">
          <div className="poem-section-title">创作背景</div>
          <div className="poem-section-content">{poem.background}</div>
        </div>
      )}

      {/* 核心名句 */}
      {poem.famousQuotes && poem.famousQuotes.length > 0 && (
        <div className="poem-quotes">
          <div className="poem-quotes-title">核心名句</div>
          {poem.famousQuotes.map((quote, idx) => (
            <div key={idx} className={`poem-quote ${idx === 0 ? 'primary' : ''}`}>
              {quote}
            </div>
          ))}
        </div>
      )}

      {/* 底部导航 */}
      <div className="poem-nav">
        <button 
          className="poem-nav-btn" 
          onClick={goToPrev}
          disabled={!poem || !allPoems.slice(0, currentIndex).some(p => !p.type || p.type === poem.type)}
        >
          ← 上一首
        </button>
        <button className="poem-nav-all" onClick={() => router.push('/poems')}>
          全部
        </button>
        <button 
          className="poem-nav-btn" 
          onClick={goToNext}
          disabled={!poem || !allPoems.slice(currentIndex + 1).some(p => !p.type || p.type === poem.type)}
        >
          下一首 →
        </button>
      </div>

      {/* Tab底部导航 */}
      <BottomNav />

      {/* 样式 */}
      <style jsx>{`
        .poem-detail {
          min-height: 100vh;
          background: var(--bg);
          font-family: var(--font-serif);
          padding-bottom: calc(64px + env(safe-area-inset-bottom));
        }

        /* 顶部导航 */
        .poem-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 1rem 0.6rem;
          background: var(--card);
          border-bottom: 0.5px solid var(--bdr);
        }

        .poem-back-btn {
          background: transparent;
          border: none;
          color: var(--tx2);
          font-size: 20px;
          cursor: pointer;
          padding: 0;
          font-family: var(--font-serif);
        }

        .poem-header-label {
          font-size: 11px;
          color: var(--tx3);
          letter-spacing: 0.1em;
        }

        .poem-fav-btn {
          background: transparent;
          border: none;
          color: ${isFavorite ? '#E57373' : 'var(--gold-m)'};
          font-size: 18px;
          cursor: pointer;
          padding: 0;
        }

        /* 诗词信息 */
        .poem-info {
          background: var(--card);
          padding: 0 1rem 1rem;
        }

        .poem-location {
          font-size: 10px;
          color: var(--gold-m);
          letter-spacing: 0.2em;
          margin-bottom: 0.4rem;
        }

        .poem-title {
          font-size: 22px;
          font-weight: 600;
          color: var(--tx);
          letter-spacing: 0.06em;
          margin-bottom: 0.3rem;
        }

        .poem-author {
          font-size: 11px;
          color: var(--tx3);
          letter-spacing: 0.06em;
        }

        /* 诗词正文 */
        .poem-content {
          padding: 1.5rem 1.75rem;
          background: var(--sec);
        }

        .poem-text {
          margin-bottom: 1.5rem;
        }

        .poem-paragraph {
          margin-bottom: 1.2rem;
          padding-top: 0.2rem;
        }

        .poem-paragraph:first-child {
          padding-top: 0;
        }

        .poem-paragraph:last-child {
          margin-bottom: 0;
        }

        .poem-line {
          font-size: 16px;
          color: var(--tx);
          line-height: 2.3;
          letter-spacing: 0.1em;
          text-align: center;
        }

        /* 创作背景 */
        .poem-background {
          background: var(--card);
          border-radius: 12px;
          padding: 1rem;
          border: 0.5px solid var(--bdr);
          margin: 0 1rem 1rem;
        }

        .poem-section-title {
          font-size: 10px;
          color: var(--gold-m);
          letter-spacing: 0.18em;
          margin-bottom: 8px;
        }

        .poem-section-content {
          font-size: 12px;
          color: var(--tx2);
          line-height: 1.9;
        }

        /* 核心名句 */
        .poem-quotes {
          margin: 0 1rem 1rem;
          padding: 0.75rem 1rem;
          border-left: 3px solid var(--gold-m);
          background: #FAEEDA;
          border-radius: 0 8px 8px 0;
        }

        .poem-quotes-title {
          font-size: 10px;
          color: var(--gold-m);
          letter-spacing: 0.12em;
          margin-bottom: 5px;
        }

        .poem-quote {
          font-size: 12px;
          color: var(--ink-mid);
          line-height: 2;
        }

        .poem-quote.primary {
          font-size: 13px;
          color: var(--tx);
        }

        /* 底部导航 */
        .poem-nav {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          gap: 8px;
          padding: 12px 16px;
          background: var(--card);
          border-top: 0.5px solid var(--bdr);
        }

        .poem-nav-btn {
          font-family: var(--font-serif);
          font-size: 12px;
          color: var(--tx2);
          background: transparent;
          border: 0.5px solid var(--bdr);
          border-radius: 8px;
          padding: 10px;
          cursor: pointer;
        }

        .poem-nav-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .poem-nav-all {
          font-family: var(--font-serif);
          font-size: 11px;
          color: var(--tx3);
          background: transparent;
          border: none;
          padding: 10px;
          cursor: pointer;
        }

        .poem-loading, .poem-not-found {
          text-align: center;
          padding: 2rem;
          color: var(--tx3);
          font-size: 12px;
        }
      `}</style>
    </div>
  );
}
