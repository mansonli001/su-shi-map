/**
 * 贺野 Zustand 状态管理
 * 独立 persist key he-ye-user-data，与苏轼 su-shi-user-data 互不干扰
 * 结构对齐 lib/store.ts
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { HeyeCheckinPlace, HeyeAchievement } from '@/types/heye';
import { calculateHeyeAchievements } from './heye-achievements';

interface HeyeStore {
  // 打卡地点
  heyeCheckins: HeyeCheckinPlace[];
  addHeyeCheckin: (checkin: HeyeCheckinPlace) => void;
  removeHeyeCheckin: (placeId: string) => void;
  isHeyeCheckedIn: (placeId: string) => boolean;

  // 成就系统
  unlockedHeyeAchievements: string[];
  lastUnlockedHeyeAchievement: HeyeAchievement | null;
  setLastUnlockedHeyeAchievement: (achievement: HeyeAchievement | null) => void;
  checkAndUnlockHeyeAchievements: (allLocationsCount: number) => void;
}

export const useHeyeStore = create<HeyeStore>()(
  persist(
    (set, get) => ({
      // 打卡地点
      heyeCheckins: [],
      addHeyeCheckin: (checkin) => {
        set((state) => ({
          heyeCheckins: [...state.heyeCheckins, checkin]
            .sort((a, b) => new Date(b.checkinAt).getTime() - new Date(a.checkinAt).getTime()),
        }));
        // 打卡后检查成就
        // allLocationsCount 需要调用方传入，这里用 0 占位，实际由 checkAndUnlockHeyeAchievements 处理
      },
      removeHeyeCheckin: (placeId) =>
        set((state) => ({
          heyeCheckins: state.heyeCheckins.filter((c) => c.placeId !== placeId),
        })),
      isHeyeCheckedIn: (placeId) =>
        get().heyeCheckins.some((c) => c.placeId === placeId),

      // 成就系统
      unlockedHeyeAchievements: [],
      lastUnlockedHeyeAchievement: null,
      setLastUnlockedHeyeAchievement: (achievement) =>
        set({ lastUnlockedHeyeAchievement: achievement }),

      checkAndUnlockHeyeAchievements: (allLocationsCount) => {
        const { heyeCheckins, unlockedHeyeAchievements } = get();
        const checkedIds = new Set(heyeCheckins.map((c) => c.placeId));

        const results = calculateHeyeAchievements(
          checkedIds,
          allLocationsCount,
          heyeCheckins,
        );

        // 找出新解锁的成就
        const newlyUnlocked = results
          .filter((a) => a.unlocked && !unlockedHeyeAchievements.includes(a.id))
          .map((a) => a.id);

        if (newlyUnlocked.length > 0) {
          set((state) => ({
            unlockedHeyeAchievements: [...state.unlockedHeyeAchievements, ...newlyUnlocked],
          }));

          // 取最后解锁的成就触发 toast
          const latestId = newlyUnlocked[newlyUnlocked.length - 1];
          const latestAchievement = results.find((a) => a.id === latestId);
          if (latestAchievement) {
            set({ lastUnlockedHeyeAchievement: latestAchievement });
          }
        }
      },
    }),
    {
      name: 'he-ye-user-data',
      partialize: (state) => ({
        heyeCheckins: state.heyeCheckins,
        unlockedHeyeAchievements: state.unlockedHeyeAchievements,
      }),
    }
  )
);
