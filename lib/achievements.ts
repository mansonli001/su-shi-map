/**
 * 成就系统核心模块
 * 定义6枚成就及其解锁规则
 */

import { PlaceCore } from '@/types';

export interface Achievement {
  id: 'bronze' | 'silver' | 'gold' | 'exile' | 'westlake' | 'full';
  name: string;
  emoji: string;
  color: string;     // 主色
  glow: string;      // rgba 光晕
  desc: string;      // 解锁描述
  poem: string;      // 诗词金句
  poemSrc: string;   // 出处
  minPlaces?: number;
  requiredPlaces?: string[]; // 特殊成就需要打卡的地点ID列表
}

/**
 * 6枚成就定义
 */
export const achievements: Achievement[] = [
  {
    id: 'bronze',
    name: '苏轼青铜爱好者',
    emoji: '🥉',
    color: '#CD7F32',
    glow: 'rgba(205, 127, 50, 0.4)',
    desc: '打卡5个苏轼足迹',
    poem: '人生到处知何似，应似飞鸿踏雪泥',
    poemSrc: '《和子由渑池怀旧》',
    minPlaces: 5,
  },
  {
    id: 'silver',
    name: '苏轼白银探索者',
    emoji: '🥈',
    color: '#A8A9AD',
    glow: 'rgba(168, 169, 173, 0.4)',
    desc: '打卡20个苏轼足迹',
    poem: '竹外桃花三两枝，春江水暖鸭先知',
    poemSrc: '《惠崇春江晚景》',
    minPlaces: 20,
  },
  {
    id: 'gold',
    name: '苏轼黄金追寻者',
    emoji: '🥇',
    color: '#FFD700',
    glow: 'rgba(255, 215, 0, 0.4)',
    desc: '打卡50个苏轼足迹',
    poem: '明月几时有，把酒问青天',
    poemSrc: '《水调歌头》',
    minPlaces: 50,
  },
  {
    id: 'exile',
    name: '贬谪三地行者',
    emoji: '🌙',
    color: '#C9973A',
    glow: 'rgba(201, 151, 58, 0.4)',
    desc: '打卡黄州、惠州、儋州三大贬谪地',
    poem: '一蓑烟雨任平生',
    poemSrc: '《定风波》',
  },
  {
    id: 'westlake',
    name: '西湖苏堤漫步',
    emoji: '🌊',
    color: '#0EA5E9',
    glow: 'rgba(14, 165, 233, 0.4)',
    desc: '打卡杭州系列地点',
    poem: '欲把西湖比西子，淡妆浓抹总相宜',
    poemSrc: '《饮湖上初晴后雨》',
  },
  {
    id: 'full',
    name: '集大成者',
    emoji: '🏆',
    color: '#BA7517',
    glow: 'rgba(186, 117, 23, 0.4)',
    desc: '打卡全部苏轼足迹（120地）',
    poem: '大江东去，浪淘尽，千古风流人物',
    poemSrc: '《念奴娇·赤壁怀古》',
    minPlaces: 120,
  },
];

/**
 * 解析特殊成就所需的地点ID列表
 * 根据地点名称/标签/路线ID匹配
 */
export function resolveSpecialPlaces(allPlaces: PlaceCore[]): Record<string, string[]> {
  const result: Record<string, string[]> = {
    exile: [],    // 黄州、惠州、儋州
    westlake: [], // 杭州系列
  };

  for (const place of allPlaces) {
    const name = place.songName?.toLowerCase() || '';
    const modernName = place.modernName?.toLowerCase() || '';
    const tag = place.tag?.toLowerCase() || '';
    const routeId = place.routeId || '';

    // 贬谪三地：黄州、惠州、儋州
    if (name.includes('黄州') || modernName.includes('黄州') || 
        name.includes('惠州') || modernName.includes('惠州') ||
        name.includes('儋州') || modernName.includes('儋州') ||
        tag.includes('黄州') || tag.includes('惠州') || tag.includes('儋州')) {
      result.exile.push(place.id);
    }

    // 西湖苏堤：杭州系列
    if (name.includes('杭州') || modernName.includes('杭州') ||
        name.includes('西湖') || modernName.includes('西湖') ||
        name.includes('苏堤') || tag.includes('杭州') || tag.includes('西湖')) {
      result.westlake.push(place.id);
    }
  }

  return result;
}

/**
 * 评估成就解锁状态
 * @param checkedIds 已打卡的地点ID集合
 * @param allPlaces 所有地点数据
 * @returns 解锁的成就ID列表和各成就进度
 */
export function evaluateAchievements(
  checkedIds: Set<string>,
  allPlaces: PlaceCore[],
): {
  unlocked: string[];
  progress: Record<string, { current: number; target: number }>;
} {
  const unlocked: string[] = [];
  const progress: Record<string, { current: number; target: number }> = {};
  
  const specialPlaces = resolveSpecialPlaces(allPlaces);
  const totalChecked = checkedIds.size;
  const totalPlaces = allPlaces.length;

  for (const ach of achievements) {
    let current = 0;
    let target = ach.minPlaces || 0;

    if (ach.id === 'exile') {
      // 贬谪三地：检查是否打卡了所有贬谪地点
      const exileIds = specialPlaces.exile;
      current = exileIds.filter(id => checkedIds.has(id)).length;
      target = Math.max(exileIds.length, 3); // 至少3个
      if (current >= 3) {
        unlocked.push(ach.id);
      }
    } else if (ach.id === 'westlake') {
      // 西湖苏堤：检查是否打卡了杭州地点
      const westlakeIds = specialPlaces.westlake;
      current = westlakeIds.filter(id => checkedIds.has(id)).length;
      target = Math.max(westlakeIds.length, 5); // 至少5个
      if (current >= 5) {
        unlocked.push(ach.id);
      }
    } else if (ach.minPlaces) {
      // 数量型成就
      current = totalChecked;
      target = ach.minPlaces;
      if (totalChecked >= ach.minPlaces) {
        unlocked.push(ach.id);
      }
    }

    progress[ach.id] = { current, target };
  }

  return { unlocked, progress };
}

/**
 * 获取单个成就详情
 */
export function getAchievement(id: Achievement['id']): Achievement | undefined {
  return achievements.find(a => a.id === id);
}

/**
 * 获取成就进度百分比
 */
export function getAchievementProgress(
  id: Achievement['id'],
  checkedIds: Set<string>,
  allPlaces: PlaceCore[],
): number {
  const { progress } = evaluateAchievements(checkedIds, allPlaces);
  const p = progress[id];
  if (!p || p.target === 0) return 0;
  return Math.min((p.current / p.target) * 100, 100);
}