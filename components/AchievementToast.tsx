/**
 * 成就解锁Toast组件
 * 当解锁成就时显示动画提示
 */

import { useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';

export default function AchievementToast() {
  const { lastUnlockedAchievement, setLastUnlockedAchievement } = useSuShiStore();

  useEffect(() => {
    if (lastUnlockedAchievement) {
      // 3秒后自动关闭
      const timer = setTimeout(() => {
        setLastUnlockedAchievement(null);
      }, 4000);

      return () => clearTimeout(timer);
    }
  }, [lastUnlockedAchievement, setLastUnlockedAchievement]);

  if (!lastUnlockedAchievement) {
    return null;
  }

  return (
    <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 animate-slide-up">
      <div 
        className="bg-gradient-to-r from-amber-900 to-amber-800 border-2 border-amber-500/50 rounded-2xl px-6 py-4 shadow-2xl shadow-amber-500/20"
        style={{
          boxShadow: `0 0 30px ${lastUnlockedAchievement.glow}, 0 25px 50px -12px rgba(0, 0, 0, 0.5)`,
        }}
      >
        {/* 顶部装饰 */}
        <div className="flex justify-center mb-3">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center text-4xl"
            style={{
              background: lastUnlockedAchievement.glow,
              boxShadow: `0 0 20px ${lastUnlockedAchievement.glow}`,
            }}
          >
            {lastUnlockedAchievement.emoji}
          </div>
        </div>

        {/* 标题 */}
        <div className="text-center">
          <p className="text-amber-300 text-sm mb-1 animate-pulse">成就解锁</p>
          <h3 
            className="text-xl font-bold mb-2"
            style={{ color: lastUnlockedAchievement.color }}
          >
            {lastUnlockedAchievement.name}
          </h3>
          <p className="text-stone-300 text-sm">
            {lastUnlockedAchievement.desc}
          </p>
        </div>

        {/* 诗词金句 */}
        <div className="mt-3 pt-3 border-t border-amber-500/30">
          <p className="text-amber-100 text-sm italic text-center">
            「{lastUnlockedAchievement.poem}」
          </p>
          <p className="text-stone-400 text-xs text-center mt-1">
            —— {lastUnlockedAchievement.poemSrc}
          </p>
        </div>
      </div>
    </div>
  );
}