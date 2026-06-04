/**
 * 成就墙组件
 * 展示6张成就卡，已解锁/未解锁两种状态
 */

import { useState } from 'react';
import { achievements } from '@/lib/achievements';
import { generateAchievementCard } from '@/lib/achievement-card';
import { getUID } from '@/lib/uid';
import { useSuShiStore } from '@/lib/store';
import AchievementCardModal from './AchievementCardModal';
import type { Achievement } from '@/lib/achievements';

export default function AchievementWall() {
  const { unlockedAchievements, checkinPlaces, places } = useSuShiStore();
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null);
  const [cardDataUrl, setCardDataUrl] = useState<string>('');

  const handleAchievementClick = (ach: Achievement) => {
    if (unlockedAchievements.includes(ach.id)) {
      // 生成成就卡
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
    
    if (ach.id === 'exile') {
      // 贬谪三地
      const exilePlaces = places.filter((p) => {
        const name = p.songName?.toLowerCase() || '';
        const modernName = p.modernName?.toLowerCase() || '';
        return name.includes('黄州') || modernName.includes('黄州') ||
               name.includes('惠州') || modernName.includes('惠州') ||
               name.includes('儋州') || modernName.includes('儋州');
      });
      const checked = exilePlaces.filter((p) => 
        checkinPlaces.some((c) => c.placeId === p.id)
      ).length;
      return Math.min((checked / Math.max(exilePlaces.length, 3)) * 100, 100);
    }
    
    if (ach.id === 'westlake') {
      // 西湖苏堤
      const westlakePlaces = places.filter((p) => {
        const name = p.songName?.toLowerCase() || '';
        const modernName = p.modernName?.toLowerCase() || '';
        return name.includes('杭州') || modernName.includes('杭州') ||
               name.includes('西湖') || modernName.includes('西湖');
      });
      const checked = westlakePlaces.filter((p) => 
        checkinPlaces.some((c) => c.placeId === p.id)
      ).length;
      return Math.min((checked / Math.max(westlakePlaces.length, 5)) * 100, 100);
    }
    
    if (ach.minPlaces) {
      return Math.min((checkedCount / ach.minPlaces) * 100, 100);
    }
    
    return 0;
  };

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {achievements.map((ach) => {
          const isUnlocked = unlockedAchievements.includes(ach.id);
          const progress = getProgress(ach);

          return (
            <div
              key={ach.id}
              onClick={() => handleAchievementClick(ach)}
              className={`
                relative rounded-2xl p-4 cursor-pointer transition-all duration-300
                ${isUnlocked 
                  ? 'bg-gradient-to-br from-amber-900/30 to-amber-950/50 border-2 border-amber-600/50 hover:border-amber-500/80 hover:shadow-lg hover:shadow-amber-500/10' 
                  : 'bg-stone-800/30 border border-stone-600/30 opacity-60 hover:opacity-80'}
              `}
              style={{
                background: isUnlocked ? `linear-gradient(135deg, rgba(186, 117, 23, 0.1) 0%, rgba(201, 151, 58, 0.05) 100%)` : undefined,
              }}
            >
              {/* 已解锁徽章 */}
              {isUnlocked && (
                <div className="absolute -top-2 -right-2 bg-amber-500 text-xs px-2 py-0.5 rounded-full text-stone-900 font-semibold">
                  已解锁
                </div>
              )}

              {/* Emoji */}
              <div className={`text-4xl mb-2 ${!isUnlocked ? 'grayscale' : ''}`}>
                {ach.emoji}
              </div>

              {/* 成就名称 */}
              <h3 className={`font-semibold mb-1 ${isUnlocked ? 'text-amber-100' : 'text-stone-400'}`}>
                {ach.name}
              </h3>

              {/* 描述 */}
              <p className="text-xs text-stone-400 mb-3">{ach.desc}</p>

              {/* 进度条（未解锁时显示） */}
              {!isUnlocked && (
                <div className="w-full bg-stone-700/50 rounded-full h-1.5">
                  <div
                    className="bg-amber-500 rounded-full h-1.5 transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}

              {/* 已解锁提示 */}
              {isUnlocked && (
                <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">
                  <span>👆</span> 点击查看成就卡
                </p>
              )}
            </div>
          );
        })}
      </div>

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