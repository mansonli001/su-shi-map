/**
 * 贺野成就系统
 * 6 类条件：checkin_count / snack_location / province_count / snack_variety / percent / checkin_all
 * 对齐 lib/achievements.ts 的模式
 */

import type { HeyeAchievement, HeyeCheckinPlace } from '@/types/heye';

/**
 * 6 枚贺野成就定义
 * 阈值基于第一版种子数据（≥30 地点 / ≥10 省）设定
 */
export const heyeAchievements: HeyeAchievement[] = [
  {
    id: 'he-001',
    name: '同频旅人',
    description: '打卡贺野推荐的3处地点',
    icon: '🧳',
    tier: 'bronze',
    conditionType: 'checkin_count',
    conditionValue: 3,
    sortOrder: 1,
  },
  {
    id: 'he-002',
    name: '小吃猎人',
    description: '在5个有小吃记录的地点打卡',
    icon: '🍜',
    tier: 'bronze',
    conditionType: 'snack_location',
    conditionValue: 5,
    sortOrder: 2,
  },
  {
    id: 'he-003',
    name: '省省有迹',
    description: '在10个不同省份打卡',
    icon: '🗺️',
    tier: 'silver',
    conditionType: 'province_count',
    conditionValue: 10,
    sortOrder: 3,
  },
  {
    id: 'he-004',
    name: '吃货地图',
    description: '累计经过20种不同小吃所在地',
    icon: '🥢',
    tier: 'silver',
    conditionType: 'snack_variety',
    conditionValue: 20,
    sortOrder: 4,
  },
  {
    id: 'he-005',
    name: '半壁江山',
    description: '打卡超过总地点数50%',
    icon: '⛰️',
    tier: 'gold',
    conditionType: 'percent',
    conditionValue: 50,
    sortOrder: 5,
  },
  {
    id: 'he-006',
    name: '神州同行',
    description: '打卡全部地点',
    icon: '🏆',
    tier: 'gold',
    conditionType: 'checkin_all',
    conditionValue: null,
    sortOrder: 6,
  },
];

/**
 * 计算贺野成就解锁状态
 * @param checkedIds 已打卡地点 ID 集合
 * @param allLocationsCount 全部地点数
 * @param checkins 打卡记录（含 placeName 用于省/小吃统计）
 * @returns 带进度和解锁状态的成就列表
 *
 * 注意：province_count 和 snack_variety 的精确计算需要地点数据。
 * 当前实现基于打卡记录中的 placeId 做简单计数，
 * 精确的省份/小吃统计需要在调用方传入地点数据后增强。
 */
export function calculateHeyeAchievements(
  checkedIds: Set<string>,
  allLocationsCount: number,
  checkins: HeyeCheckinPlace[],
): HeyeAchievement[] {
  const totalChecked = checkedIds.size;

  return heyeAchievements.map((ach) => {
    let current = 0;
    let target = ach.conditionValue ?? allLocationsCount;

    switch (ach.conditionType) {
      case 'checkin_count':
        current = totalChecked;
        target = ach.conditionValue ?? 3;
        break;

      case 'snack_location':
        // 简化：基于打卡数估算，精确计算需地点数据
        current = totalChecked;
        target = ach.conditionValue ?? 5;
        break;

      case 'province_count':
        // 简化：基于打卡数估算，精确计算需地点数据
        current = Math.min(totalChecked, ach.conditionValue ?? 10);
        target = ach.conditionValue ?? 10;
        break;

      case 'snack_variety':
        // 简化：基于打卡数估算，精确计算需地点数据
        current = totalChecked;
        target = ach.conditionValue ?? 20;
        break;

      case 'percent':
        current = allLocationsCount > 0
          ? Math.round((totalChecked / allLocationsCount) * 100)
          : 0;
        target = ach.conditionValue ?? 50;
        break;

      case 'checkin_all':
        current = totalChecked;
        target = allLocationsCount;
        break;
    }

    const unlocked = current >= target;

    return {
      ...ach,
      progress: current,
      total: target,
      unlocked,
    };
  });
}

/**
 * 获取单个成就定义
 */
export function getHeyeAchievement(id: string): HeyeAchievement | undefined {
  return heyeAchievements.find((a) => a.id === id);
}
