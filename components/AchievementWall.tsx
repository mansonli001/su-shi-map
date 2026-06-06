/**
 * 成就墙组件 v2.0
 * 展示25张成就卡，按分类分组展示
 * 支持隐藏成就模糊效果
 */

import { useState, useMemo } from 'react';
import { achievements, getAchievement, type Achievement } from '@/lib/achievements';
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

  const getProgress = (ach: Achievement): number => {
    const checkedCount = checkinPlaces.length;

    // 贬谪三地合成成就
    if (ach.isSynthesis && ach.synthesisFrom) {
      const unlockedCount = ach.synthesisFrom.filter(id => 
        unlockedAchievements.includes(id)
      ).length;
      return Math.min((unlockedCount / ach.synthesisFrom.length) * 100, 100);
    }

    // 特定地点成就
    if (ach.requiredPlaces && ach.requiredPlaces.length > 0) {
      const checked = ach.requiredPlaces.filter(placeId => 
        checkinPlaces.some((c) => c.placeId === placeId)
      ).length;
      return Math.min((checked / ach.requiredPlaces.length) * 100, 100);
    }

    // 诗词收藏成就
    if (ach.id.startsWith('poem-')) {
      return Math.min((favoritePoems.length / (ach.minPlaces || 1)) * 100, 100);
    }

    // 打卡数量成就
    if (ach.minPlaces) {
      return Math.min((checkedCount / ach.minPlaces) * 100, 100);
    }

    return 0;
  };

  // 获取品级样式
  const getTierStyle = (tier: Achievement['tier']) => {
    switch (tier) {
      case 'gold':
        return {
          borderColor: 'rgba(255, 215, 0, 0.6)',
          glow: 'rgba(255, 215, 0, 0.3)',
          textColor: '#FFD700',
        };
      case 'silver':
        return {
          borderColor: 'rgba(192, 192, 192, 0.6)',
          glow: 'rgba(192, 192, 192, 0.3)',
          textColor: '#C0C0C0',
        };
      case 'bronze':
      default:
        return {
          borderColor: 'rgba(205, 127, 50, 0.6)',
          glow: 'rgba(205, 127, 50, 0.3)',
          textColor: '#CD7F32',
        };
    }
  };

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

            {/* 成就卡片网格 —— 卡更大、图标更大 */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {categoryAchievements.map((ach) => {
                const isUnlocked = unlockedAchievements.includes(ach.id);
                const progress = getProgress(ach);
                const tierStyle = getTierStyle(ach.tier);

                // 隐藏成就未解锁时显示模糊效果
                const isHiddenAndLocked = ach.isHidden && !isUnlocked;

                return (
                  <div
                    key={ach.id}
                    onClick={() => handleAchievementClick(ach)}
                    className={`
                      relative rounded-2xl p-4 cursor-pointer transition-all duration-300
                      ${isUnlocked
                        ? 'border-2 hover:shadow-xl hover:-translate-y-0.5'
                        : 'border border-stone-600/30 opacity-70'}
                      ${isHiddenAndLocked ? 'blur-sm hover:blur-none' : ''}
                    `}
                    style={{
                      background: isUnlocked
                        ? `linear-gradient(135deg, ${ach.color}15 0%, ${ach.color}08 100%)`
                        : 'rgba(30, 30, 30, 0.6)',
                      borderColor: isUnlocked ? ach.color + '80' : undefined,
                      boxShadow: isUnlocked ? `0 4px 15px ${ach.glow}` : undefined,
                    }}
                  >
                    {/* 隐藏成就标记 */}
                    {isHiddenAndLocked && (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-stone-500 text-xs text-center">
                          <div className="text-lg mb-1">❓</div>
                          <div>???</div>
                        </div>
                      </div>
                    )}

                    {/* 已解锁徽章 */}
                    {isUnlocked && (
                      <div 
                        className="absolute -top-1.5 -right-1.5 text-xs px-2 py-0.5 rounded-full text-white font-semibold text-[10px]"
                        style={{ backgroundColor: ach.color }}
                      >
                        ✨
                      </div>
                    )}

                    {/* 合成成就标记 */}
                    {ach.isSynthesis && isUnlocked && (
                      <div className="absolute -top-1.5 -left-1.5 bg-purple-500 text-[8px] px-1.5 py-0.5 rounded-full text-white">
                        合成
                      </div>
                    )}

                    {/* 品级标记 */}
                    {isUnlocked && (
                      <div 
                        className="absolute top-1 right-1 text-[10px] opacity-60"
                        style={{ color: tierStyle.textColor }}
                      >
                        {ach.tier === 'gold' ? '金' : ach.tier === 'silver' ? '银' : '铜'}
                      </div>
                    )}

                    {/* 图标 —— 优先 /achievements/{icon}.png（高清原图 2048×2048），
                        缺失 fallback 到 base64 icons.ts，再 fallback emoji */}
                    <div
                      className={`w-24 h-24 sm:w-28 sm:h-28 mb-3 mx-auto flex items-center justify-center ${!isUnlocked && !isHiddenAndLocked ? 'grayscale opacity-60' : ''}`}
                    >
                      {isHiddenAndLocked ? (
                        <span className="text-5xl">❓</span>
                      ) : ach.icon ? (
                        <img
                          src={`/achievements/${encodeURIComponent(ach.icon)}.png`}
                          alt={ach.name}
                          className="w-full h-full object-contain drop-shadow-md"
                          onError={(e) => {
                            // PNG 文件缺失 → 回退 base64 SVG
                            const img = e.currentTarget;
                            if (achievementIcons[ach.icon] && img.src !== achievementIcons[ach.icon]) {
                              img.src = achievementIcons[ach.icon];
                            } else {
                              // base64 也没有 → 显示 emoji
                              img.style.display = 'none';
                              const span = document.createElement('span');
                              span.className = 'text-5xl';
                              span.textContent = ach.emoji;
                              img.parentElement?.appendChild(span);
                            }
                          }}
                        />
                      ) : (
                        <span className="text-5xl">{ach.emoji}</span>
                      )}
                    </div>

                    {/* 成就名称 */}
                    <h3 
                      className={`text-base font-semibold mb-1.5 truncate text-center ${isUnlocked ? '' : 'text-stone-400'}`}
                      style={{ color: isUnlocked ? ach.color : undefined }}
                    >
                      {isHiddenAndLocked ? '???' : ach.name}
                    </h3>

                    {/* 描述 */}
                    <p 
                      className="text-xs mb-2 line-clamp-2 text-center leading-relaxed"
                      style={{ 
                        color: isUnlocked ? '#9CA3AF' : '#6B7280',
                        opacity: isHiddenAndLocked ? 0 : 1,
                      }}
                    >
                      {isHiddenAndLocked ? '达成条件未知...' : ach.desc}
                    </p>

                    {/* 进度条（未解锁时显示） */}
                    {!isUnlocked && !isHiddenAndLocked && (
                      <div className="w-full bg-stone-700/50 rounded-full h-1">
                        <div
                          className="rounded-full h-1 transition-all duration-500"
                          style={{ 
                            width: `${progress}%`,
                            backgroundColor: ach.color,
                          }}
                        />
                      </div>
                    )}

                    {/* 已解锁提示 */}
                    {isUnlocked && (
                      <p className="text-xs mt-2 flex items-center gap-1" style={{ color: ach.color }}>
                        <span>👆</span> 点击查看
                      </p>
                    )}
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
