/**
 * 美食Tab空状态组件
 * 苏轼口吻，风格统一
 */

'use client';

import { FOOD_SUSHI_EMPTY, FOOD_NEARBY_EMPTY, FOOD_ALL_EMPTY, renderEmptyState } from '@/lib/empty-state-config';

interface FoodEmptyStateProps {
  foodTab: 'all' | 'sushi' | 'nearby';
  onSwitchToNearby?: () => void;
}

export default function FoodEmptyState({ foodTab, onSwitchToNearby }: FoodEmptyStateProps) {
  // 根据当前tab选择对应的空状态配置
  const getConfig = () => {
    switch (foodTab) {
      case 'sushi':
        return FOOD_SUSHI_EMPTY;
      case 'nearby':
        return FOOD_NEARBY_EMPTY;
      case 'all':
        return FOOD_ALL_EMPTY;
      default:
        return FOOD_ALL_EMPTY;
    }
  };

  const config = renderEmptyState(getConfig());

  return (
    <div className="text-center py-10 px-4">
      {/* 空碗图标（线条风格） */}
      <div className="mb-5 flex justify-center">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-ink-lt/30">
          <path d="M12 20C12 20 12 32 24 32C36 32 36 20 36 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M10 20H38" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M14 32L12 38H36L34 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M20 14C20 14 22 16 24 16C26 16 28 14 28 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>

      {/* 标题 */}
      <h3 
        className="font-wenkai mb-3"
        style={{ fontSize: '17px', color: '#1a1410', fontWeight: 500 }}
      >
        {config.title}
      </h3>

      {/* 正文 */}
      <div className="space-y-1 mb-4">
        {config.bodyLines.map((line, index) => (
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
      {config.quote && (
        <div className="mb-4 pl-2 border-l-2 border-gold-m/30">
          <p 
            className="font-wenkai italic"
            style={{ fontSize: '13px', color: '#ba7517' }}
          >
            「{config.quote}」
          </p>
          {config.source && (
            <p className="text-[11px] text-ink-lt/50 mt-1">
              ——{config.source}
            </p>
          )}
        </div>
      )}

      {/* 行动引导 */}
      {config.actionText && (
        <button
          onClick={() => {
            if (config.actionOnClick === 'switchToNearby' && onSwitchToNearby) {
              onSwitchToNearby();
            }
          }}
          className="font-wenkai text-[13px] text-gold-m hover:text-gold-d underline underline-offset-4 transition-colors"
        >
          {config.actionText}
        </button>
      )}
    </div>
  );
}