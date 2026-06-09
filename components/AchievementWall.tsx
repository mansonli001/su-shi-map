/**
 * 成就墙组件 v2.0
 * 展示25张成就卡，按分类分组展示
 * 支持隐藏成就模糊效果
 */

import { useState, useMemo } from 'react';
import { achievements, evaluateAchievements, type Achievement } from '@/lib/achievements';
import { achievementIcons } from '@/lib/icons';
import { generateAchievementCard } from '@/lib/achievement-card';
import { getUID } from '@/lib/uid';
import { useSuShiStore } from '@/lib/store';
import AchievementCardModal from './AchievementCardModal';

// 分类配置
const CATEGORIES = [
  { id: 'grow', name: '成长阶梯', emoji: '📈', color: '#B8860B' },
  { id: 'banish', name: '贬谪专题', emoji: '🌙', color: '#8B4513' },
  { id: 'jiangnan', name: '江南专题', emoji: '🌸', color: '#E63946' },
  { id: 'poem', name: '诗词珍藏', emoji: '📜', color: '#2A9D8F' },
  { id: 'secret', name: '隐秘彩蛋', emoji: '🎁', color: '#9B5DE5' },
];

export default function AchievementWall() {
  const { unlockedAchievements, checkinPlaces, places, favoritePoems } = useSuShiStore();
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null);
  const [cardDataUrl, setCardDataUrl] = useState<string>('');

  // 按分类分组成就
  const achievementsByCategory = useMemo(() => {
    const grouped: Record<string, Achievement[]> = {};
    CATEGORIES.forEach(cat => {
      grouped[cat.id] = achievements.filter(ach => ach.category === cat.id);
    });
    return grouped;
  }, []);

  const handleAchievementClick = (ach: Achievement) => {
    // 隐藏成就未解锁时不响应点击
    if (ach.isHidden && !unlockedAchievements.includes(ach.id)) {
      return;
    }

    if (unlockedAchievements.includes(ach.id)) {
      const placeNames = checkinPlaces.map((c) => c.placeName);
      const stats = {
        count: checkinPlaces.length,
        placeNames,
        uid: getUID(),
      };
      const dataUrl = generateAchievementCard(ach, stats);
      setCardDataUrl(dataUrl);
      setSelectedAchievement(ach);
    }
  };

  const handleCloseModal = () => {
    setSelectedAchievement(null);
    setCardDataUrl('');
  };

  // 使用 evaluateAchievements 统一计算进度
  const achievementProgress = useMemo(() => {
    const checkedIds = new Set(checkinPlaces.map(c => c.placeId));
    const favoritePoemIds = new Set(favoritePoems.map(p => p.poemId));
    const checkinDates = checkinPlaces.map(c => new Date(c.checkinAt));
    const { progress } = evaluateAchievements(checkedIds, places, favoritePoemIds, checkinDates);
    return progress;
  }, [checkinPlaces, places, favoritePoems]);

  const getProgress = (ach: Achievement): number => {
    const p = achievementProgress[ach.id];
    if (!p || p.target === 0) return 0;
    return Math.min((p.current / p.target) * 100, 100);
  };

  // 获取品级样式
  const getTierStyle = (tier: Achievement['tier']) => {
    switch (tier) {
      case 'gold':
        return {
          borderColor: 'rgba(255, 215, 0, 0.6)',
          glow: 'rgba(255, 215, 0, 0.3)',
          textColor: '#FFD700',
          crownColor: '#FFD700',
          crownLabel: '金',
        };
      case 'silver':
        return {
          borderColor: 'rgba(192, 192, 192, 0.6)',
          glow: 'rgba(192, 192, 192, 0.3)',
          textColor: '#C0C0C0',
          crownColor: '#D6D6D6',
          crownLabel: '银',
        };
      case 'bronze':
      default:
        return {
          borderColor: 'rgba(205, 127, 50, 0.6)',
          glow: 'rgba(205, 127, 50, 0.3)',
          textColor: '#CD7F32',
          crownColor: '#E0964F',
          crownLabel: '铜',
        };
    }
  };

  // SVG 皇冠（按品级上色，未解锁传 #6B7280）
  const CrownSVG = ({ color, locked }: { color: string; locked: boolean }) => (
    <svg
      viewBox="0 0 32 32"
      width="28"
      height="28"
      fill="none"
      style={{
        filter: locked
          ? 'none'
          : `drop-shadow(0 0 4px ${color}88) drop-shadow(0 1px 2px rgba(0,0,0,0.5))`,
      }}
      aria-hidden
    >
      <path
        d="M4 22 L7 10 L12 16 L16 7 L20 16 L25 10 L28 22 Z"
        fill={locked ? '#6B7280' : color}
        stroke={locked ? '#4B5563' : '#00000050'}
        strokeWidth="0.8"
        strokeLinejoin="round"
      />
      <rect
        x="4"
        y="22"
        width="24"
        height="3.2"
        rx="0.6"
        fill={locked ? '#4B5563' : color}
        opacity="0.85"
      />
      {!locked && (
        <>
          <circle cx="7" cy="10" r="1.4" fill="#fff" opacity="0.9" />
          <circle cx="16" cy="7" r="1.6" fill="#fff" opacity="0.95" />
          <circle cx="25" cy="10" r="1.4" fill="#fff" opacity="0.9" />
        </>
      )}
    </svg>
  );

  return (
    <>
      {CATEGORIES.map((category) => {
        const categoryAchievements = achievementsByCategory[category.id];
        if (!categoryAchievements || categoryAchievements.length === 0) return null;

        return (
          <div key={category.id} className="mb-8">
            {/* 分类标题 */}
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">{category.emoji}</span>
              <h2 
                className="text-lg font-semibold font-wenkai"
                style={{ color: category.color }}
              >
                {category.name}
              </h2>
              <span className="text-sm text-stone-400">
                ({categoryAchievements.filter(a => unlockedAchievements.includes(a.id)).length}/{categoryAchievements.length})
              </span>
            </div>

            {/* 成就卡片网格 —— 满铺图 + SVG 皇冠覆盖 */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {categoryAchievements.map((ach) => {
                const isUnlocked = unlockedAchievements.includes(ach.id);
                const progress = getProgress(ach);
                const tierStyle = getTierStyle(ach.tier);

                // 隐藏成就未解锁时显示模糊效果
                const isHiddenAndLocked = ach.isHidden && !isUnlocked;
                // 隐藏成就用紫色皇冠
                const crownColor = ach.category === 'secret' ? '#C9A0E8' : tierStyle.crownColor;

                return (
                  <div
                    key={ach.id}
                    onClick={() => handleAchievementClick(ach)}
                    className={`
                      relative aspect-[3/4] rounded-2xl overflow-hidden cursor-pointer
                      transition-all duration-300
                      ${isUnlocked ? 'border-2 hover:-translate-y-1 hover:shadow-2xl' : 'border border-stone-700/50'}
                    `}
                    style={{
                      background: '#1a1a1a',
                      borderColor: isUnlocked ? ach.color + 'aa' : undefined,
                      boxShadow: isUnlocked ? `0 6px 24px ${ach.glow}` : '0 2px 8px rgba(0,0,0,0.4)',
                    }}
                  >
                    {/* 主题色底层 */}
                    <div
                      className="absolute inset-0"
                      style={{
                        background: `linear-gradient(160deg, ${ach.color}66 0%, ${ach.color}22 50%, #1a1a1a 100%)`,
                      }}
                    />
                    {/* 满铺背景图 —— scale-125 大幅裁外围，藏掉烘进图里的格子边 */}
                    {ach.icon && (
                      <img
                        src={`/achievements/${encodeURIComponent(ach.icon)}.jpg`}
                        alt={ach.name}
                        loading="lazy"
                        decoding="async"
                        className={`
                          absolute inset-0 w-full h-full object-cover
                          transition-all duration-500
                          ${isUnlocked ? 'scale-125' : 'grayscale opacity-50 scale-110'}
                          ${isHiddenAndLocked ? 'blur-md scale-150' : ''}
                        `}
                        style={{ objectPosition: 'center 30%' }}
                        onError={(e) => {
                          const img = e.currentTarget;
                          if (achievementIcons[ach.icon] && img.src !== achievementIcons[ach.icon]) {
                            img.src = achievementIcons[ach.icon];
                          } else {
                            img.style.display = 'none';
                          }
                        }}
                      />
                    )}
                    {/* 四边内阴影 —— 渐变到主题色，盖住残余格子 */}
                    {isUnlocked && (
                      <div
                        className="absolute inset-0 pointer-events-none"
                        style={{
                          background: `
                            radial-gradient(ellipse 120% 100% at 50% 50%, transparent 35%, ${ach.color}33 70%, ${ach.color}66 100%),
                            linear-gradient(180deg, ${ach.color}55 0%, transparent 18%, transparent 75%, transparent 100%)
                          `,
                          mixBlendMode: 'multiply',
                        }}
                      />
                    )}
                    {/* 顶部主题色光晕 */}
                    {isUnlocked && (
                      <div
                        className="absolute inset-x-0 top-0 h-1/3 pointer-events-none"
                        style={{
                          background: `radial-gradient(ellipse at top, ${ach.color}30 0%, transparent 70%)`,
                          mixBlendMode: 'screen',
                        }}
                      />
                    )}
                    {!ach.icon && (
                      <div className="absolute inset-0 flex items-center justify-center text-7xl opacity-40">
                        {ach.emoji}
                      </div>
                    )}

                    {/* 底部渐变蒙层 */}
                    <div
                      className="absolute inset-x-0 bottom-0 h-2/3 pointer-events-none"
                      style={{
                        background:
                          'linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.55) 45%, rgba(0,0,0,0.92) 100%)',
                      }}
                    />

                    {/* 左上：SVG 皇冠（按品级/未解锁上色） */}
                    <div className="absolute top-2 left-2 z-10">
                      <CrownSVG color={crownColor} locked={!isUnlocked} />
                    </div>

                    {/* 右上：品级文字 / 已解锁 ✨ */}
                    <div className="absolute top-2 right-2 z-10 flex items-center gap-1">
                      {isUnlocked && (
                        <span
                          className="text-[10px] px-1.5 py-0.5 rounded-full text-white font-semibold"
                          style={{ backgroundColor: ach.color }}
                        >
                          ✨
                        </span>
                      )}
                      <span
                        className="text-[10px] font-bold px-1.5 py-0.5 rounded-md backdrop-blur"
                        style={{
                          color: isUnlocked ? tierStyle.textColor : '#9CA3AF',
                          background: 'rgba(0,0,0,0.4)',
                          border: `1px solid ${isUnlocked ? tierStyle.borderColor : 'rgba(120,120,120,0.4)'}`,
                        }}
                      >
                        {tierStyle.crownLabel}
                      </span>
                    </div>

                    {/* 合成成就标记 */}
                    {ach.isSynthesis && isUnlocked && (
                      <div className="absolute top-12 left-2 z-10 bg-purple-500/90 text-[9px] px-1.5 py-0.5 rounded-md text-white font-semibold">
                        合成
                      </div>
                    )}

                    {/* 隐藏未解锁：?? 浮层 */}
                    {isHiddenAndLocked && (
                      <div className="absolute inset-0 flex flex-col items-center justify-center z-10 text-stone-300">
                        <div className="text-5xl mb-2">❓</div>
                        <div className="text-sm font-semibold tracking-widest">???</div>
                      </div>
                    )}

                    {/* 底部信息区 */}
                    <div className="absolute inset-x-0 bottom-0 p-3 z-10">
                      <h3
                        className="text-base font-bold mb-1 truncate font-wenkai"
                        style={{
                          color: isUnlocked ? '#fff' : '#D1D5DB',
                          textShadow: '0 1px 3px rgba(0,0,0,0.8)',
                        }}
                      >
                        {isHiddenAndLocked ? '???' : ach.name}
                      </h3>
                      <p
                        className="text-[11px] leading-snug line-clamp-2 mb-2"
                        style={{
                          color: isUnlocked ? 'rgba(255,255,255,0.85)' : 'rgba(209,213,219,0.7)',
                          textShadow: '0 1px 2px rgba(0,0,0,0.7)',
                        }}
                      >
                        {isHiddenAndLocked ? '达成条件未知...' : ach.desc}
                      </p>

                      {/* 已解锁：点击查看；未解锁：进度条 */}
                      {isUnlocked ? (
                        <div
                          className="text-[11px] font-medium flex items-center gap-1"
                          style={{ color: ach.color, textShadow: '0 1px 2px rgba(0,0,0,0.7)' }}
                        >
                          <span>👆</span>
                          <span>点击查看</span>
                        </div>
                      ) : !isHiddenAndLocked ? (
                        <div className="space-y-1">
                          <div className="w-full bg-black/50 rounded-full h-1 overflow-hidden">
                            <div
                              className="rounded-full h-1 transition-all duration-500"
                              style={{
                                width: `${progress}%`,
                                backgroundColor: ach.color,
                                boxShadow: `0 0 6px ${ach.color}`,
                              }}
                            />
                          </div>
                          <div className="text-[10px] text-stone-300/80 text-right">
                            {Math.round(progress)}%
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* 成就卡预览Modal */}
      {selectedAchievement && cardDataUrl && (
        <AchievementCardModal
          achievement={selectedAchievement}
          cardDataUrl={cardDataUrl}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
}
