/**
 * 通用空状态组件
 * 苏轼口吻，风格统一
 */

'use client';

import { type EmptyStateConfig, renderEmptyState } from '@/lib/empty-state-config';

interface EmptyStateProps {
  config: EmptyStateConfig;
  icon?: 'brush' | 'bowl' | 'map' | 'book';
}

// 线条风格图标
const icons = {
  brush: (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 36C12 36 14 32 20 32C26 32 28 36 28 36" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M28 36L36 20L40 22L32 38" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M36 20L38 18C39 17 39 15 38 14C37 13 35 13 34 14L32 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M12 36V38C12 39 13 40 14 40H26C27 40 28 39 28 38V36" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  bowl: (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 20C12 20 12 32 24 32C36 32 36 20 36 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M10 20H38" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M14 32L12 38H36L34 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M20 14C20 14 22 16 24 16C26 16 28 14 28 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  map: (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 12L8 16V36L16 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M16 12L24 16V36L16 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M32 12L24 16V36L32 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M32 12L40 16V36L32 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="24" cy="24" r="2" stroke="currentColor" strokeWidth="1.5"/>
    </svg>
  ),
  book: (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 10H36C37 10 38 11 38 12V38C38 39 37 40 36 40H12C11 40 10 39 10 38V12C10 11 11 10 12 10Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M16 16H32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M16 22H28" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M16 28H30" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M16 34H24" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
};

export default function EmptyState({ config, icon = 'brush' }: EmptyStateProps) {
  const rendered = renderEmptyState(config);

  return (
    <div className="text-center py-10 px-4">
      {/* 图标 */}
      <div className="mb-5 flex justify-center text-ink-lt/30">
        {icons[icon]}
      </div>

      {/* 标题 */}
      <h3 
        className="font-wenkai mb-3"
        style={{ fontSize: '17px', color: '#1a1410', fontWeight: 500 }}
      >
        {rendered.title}
      </h3>

      {/* 正文 */}
      <div className="space-y-1 mb-4">
        {rendered.bodyLines.map((line, index) => (
          <p 
            key={index}
            className="font-wenkai"
            style={{ fontSize: '14px', color: '#6b5d54', lineHeight: 1.8 }}
          >
            {line}
          </p>
        ))}
      </div>

      {/* 引用诗句 */}
      {rendered.quote && (
        <div className="mb-4 pl-2 border-l-2 border-gold-m/30">
          <p 
            className="font-wenkai italic"
            style={{ fontSize: '13px', color: '#ba7517' }}
          >
            「{rendered.quote}」
          </p>
          {rendered.source && (
            <p className="text-[11px] text-ink-lt/50 mt-1">
              ——{rendered.source}
            </p>
          )}
        </div>
      )}

      {/* 行动引导 */}
      {rendered.actionText && (
        <button
          onClick={() => {
            if (rendered.actionHref) {
              window.location.href = rendered.actionHref;
            }
          }}
          className="font-wenkai text-[13px] text-gold-m hover:text-gold-d underline underline-offset-4 transition-colors"
        >
          {rendered.actionText}
        </button>
      )}
    </div>
  );
}