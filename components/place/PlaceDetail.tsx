/**
 * PlaceDetail v4.0
 * 详情页内容，react-markdown + remark-gfm
 */

'use client';

import dynamic from 'next/dynamic';
import { PropsWithChildren } from 'react';
import { PlaceDetail as PlaceDetailType, Poem, Attraction, Food } from '@/types';

const ReactMarkdown = dynamic(() => import('react-markdown'), { ssr: false });
const remarkGfm = dynamic(() => import('remark-gfm'), { ssr: false });

interface PlaceDetailProps {
  detail: PlaceDetailType;
}

export default function PlaceDetail({ detail }: PlaceDetailProps) {
  return (
    <div className="prose-ancient max-w-none">
      {/* 地点标题 */}
      <div className="mb-6">
        <h1 className="text-2xl font-serif text-ink mb-1">
          {detail.songName}
        </h1>
        <p className="text-sm text-ink/50">{detail.modernName}</p>
        <div className="flex items-center gap-2 mt-2">
          <span className={`px-2 py-0.5 rounded text-xs ${detail.importance === 1 ? 'bg-ink text-paper' : detail.importance === 2 ? 'bg-ink/10 text-ink' : 'bg-ink/5 text-ink/60'}`}>
            {detail.importance === 1 ? '必看' : detail.importance === 2 ? '推荐' : '了解'}
          </span>
        </div>
      </div>

      {/* 事迹概述 */}
      <div className="mb-8">
        <h2 className="text-lg font-serif text-ink/80 mb-3">事迹概述</h2>
        <p className="text-ink/70 leading-relaxed">{detail.summary}</p>
      </div>

      {/* 详细故事 (Markdown) */}
      {detail.story && (
        <div className="mb-8">
          <h2 className="text-lg font-serif text-ink/80 mb-3">详细故事</h2>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {detail.story}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* 相关诗词 */}
      {detail.poems && detail.poems.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-serif text-ink/80 mb-3">相关诗词</h2>
          <div className="space-y-4">
            {detail.poems.map((poem: Poem) => (
              <div key={poem.id} className="border-l-2 border-ink/20 pl-4">
                <h3 className="text-base font-serif text-ink">{poem.title}</h3>
                {poem.year && (
                  <p className="text-xs text-ink/40 mt-0.5">创作于 {poem.year} 年</p>
                )}
                <pre className="prose-poem text-sm mt-2 whitespace-pre-wrap font-serif text-ink/80">
                  {poem.content}
                </pre>
                {poem.translation && (
                  <details className="mt-2">
                    <summary className="text-xs text-ink/50 cursor-pointer">查看今译</summary>
                    <p className="text-sm text-ink/60 mt-1">{poem.translation}</p>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 现代景点 */}
      {detail.attractions && detail.attractions.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-serif text-ink/80 mb-3">现代景点</h2>
          <div className="space-y-3">
            {detail.attractions.map((attr: Attraction) => (
              <div key={attr.id} className="border border-ink/10 rounded-lg p-3">
                <h3 className="text-base font-medium text-ink">{attr.name}</h3>
                <p className="text-sm text-ink/60 mt-1">{attr.description}</p>
                {(attr.ticket || attr.openTime) && (
                  <div className="flex gap-3 mt-2 text-xs text-ink/40">
                    {attr.ticket && <span>🎫 {attr.ticket}</span>}
                    {attr.openTime && <span>🕐 {attr.openTime}</span>}
                  </div>
                )}
                <p className="text-xs text-ink/30 mt-1">* 信息以现场为准</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 当地美食 */}
      {detail.food && detail.food.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-serif text-ink/80 mb-3">当地美食</h2>
          <div className="space-y-2">
            {detail.food.map((f: Food, idx: number) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-ink/30">•</span>
                <div>
                  <span className="text-sm font-medium text-ink/80">{f.name}</span>
                  {f.description && (
                    <p className="text-xs text-ink/50">{f.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
