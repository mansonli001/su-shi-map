/**
 * 苏轼行旅路线配置 v2.0
 * 从120个地点动态生成6条路线，不再硬编码坐标
 */

import { PlaceCore, Stage } from '@/types';

export interface RouteConfig {
  id: string;
  name: string;
  time: string;
  phase: string;
  mainColor: string;
  lineWeight: number;
  dashArray: string;
  desc: string;
}

export interface RouteTrackPoint {
  id: string;      // 地点ID (SSxxx)
  name: string;    // 宋代地名
  lat: number;
  lng: number;
  order: number;
  routeId: string;
  tag: string;
}

/** 6条主线配置 */
export const ROUTE_CONFIG: Record<string, RouteConfig> = {
  route1: {
    id: 'route1',
    name: '少年出蜀·首次进京',
    time: '1056-1061',
    phase: '眉山少年 & 入京初仕',
    mainColor: '#A0522D', // 赭石 — 古道土色
    lineWeight: 2,
    dashArray: '4,3',
    desc: '20岁苏轼离开故乡眉山，沿古道远赴汴京参加科举，一举高中。',
  },
  route2: {
    id: 'route2',
    name: '熙宁外放·江南辗转',
    time: '1069-1079',
    phase: '地方历练',
    mainColor: '#2E8B57', // 墨绿 — 江南山色
    lineWeight: 2,
    dashArray: '4,3',
    desc: '因政见不合，苏轼主动请求外放。十年间辗转江南多地为官。',
  },
  route3: {
    id: 'route3',
    name: '乌台诗案·入狱贬黄',
    time: '1079',
    phase: '乌台诗案',
    mainColor: '#B22222', // 朱砂 — 血案警示
    lineWeight: 2,
    dashArray: '4,3',
    desc: '乌台诗案爆发，苏轼在湖州被捕，押解回京入狱，后贬黄州。',
  },
  route4: {
    id: 'route4',
    name: '黄州悟道·东坡躬耕',
    time: '1080-1084',
    phase: '黄州四年',
    mainColor: '#4682B4', // 灰蓝 — 江天色
    lineWeight: 2,
    dashArray: '4,3',
    desc: '谪居黄州四年，苏轼开荒种地，自号"东坡居士"。',
  },
  route5: {
    id: 'route5',
    name: '元祐回朝·再起外放',
    time: '1085-1093',
    phase: '翰林侍从',
    mainColor: '#DAA520', // 金菊 — 回朝荣耀
    lineWeight: 2,
    dashArray: '4,3',
    desc: '旧党执政，苏轼被召回汴京身居高位，后再度请求外放。',
  },
  route6: {
    id: 'route6',
    name: '南迁儋州·北归终焉',
    time: '1094-1101',
    phase: '岭南儋耳 & 北归长眠',
    mainColor: '#8B008B', // 暗紫 — 暮年苍茫
    lineWeight: 2,
    dashArray: '4,3',
    desc: '晚年接连被贬，一路南行直至海南儋州。遇赦后北归，病逝常州。',
  },
};

/** 所有路线ID */
export const ROUTE_IDS = ['route1', 'route2', 'route3', 'route4', 'route5', 'route6'] as const;
export type RouteId = (typeof ROUTE_IDS)[number] | null;

/** Stage → 路线ID 映射（Timeline点击用） */
export const STAGE_TO_ROUTE: Record<Stage, string> = {
  youth: 'route1',
  early_career: 'route2',
  first_exile: 'route4',
  middle_career: 'route5',
  second_exile: 'route6',
  third_exile: 'route6',
  final_journey: 'route6',
};

/** 路线 → Stage 映射（反向查找） */
export const ROUTE_TO_STAGES: Record<string, Stage[]> = {
  route1: ['youth', 'early_career'],
  route2: ['early_career'],
  route3: ['early_career'],
  route4: ['first_exile'],
  route5: ['middle_career'],
  route6: ['second_exile', 'third_exile', 'final_journey'],
};

/**
 * 从120个PlaceCore动态构建路线轨迹点
 * 规则：按stage归属 + id顺序排列
 */
export function buildRoutesFromPlaces(places: PlaceCore[]): RouteTrackPoint[] {
  const points: RouteTrackPoint[] = [];

  // route1: youth + early_career 前半段（眉山 → 开封，出蜀入京）
  // 包含 youth 全部 + early_career 中从四川出发到开封的点
  const route1Stages = new Set<Stage>(['youth', 'early_career']);
  const route1Places = places
    .filter(p => route1Stages.has(p.stage))
    .sort((a, b) => a.id.localeCompare(b.id));
  route1Places.forEach((p, i) => {
    points.push({
      id: p.id,
      name: p.songName,
      lat: p.lat,
      lng: p.lng,
      order: i + 1,
      routeId: 'route1',
      tag: p.type === 'birth' ? '故里' : p.type === 'office' ? '任职' : '途经',
    });
  });

  // route2: early_career 中江南辗转部分（杭州、密州、徐州）
  // 从 early_career 中排除 route1 和 route3 的点
  // 策略：按地理位置分组 — 江南地区（浙江、江苏）+ 山东东部
  const route2Places = places
    .filter(p => {
      if (p.stage !== 'early_career') return false;
      // 排除已在 route1 中的点（通过id范围：SS001~SS013 是出蜀入京主线）
      const num = parseInt(p.id.replace('SS', ''), 10);
      // SS015~SS023 是杭州密州徐州湖州
      return num >= 15 && num <= 23;
    })
    .sort((a, b) => a.id.localeCompare(b.id));
  route2Places.forEach((p, i) => {
    points.push({
      id: p.id,
      name: p.songName,
      lat: p.lat,
      lng: p.lng,
      order: i + 1,
      routeId: 'route2',
      tag: p.type === 'office' ? '任职' : '途经',
    });
  });

  // route3: 乌台诗案（湖州 → 开封 → 黄州）
  // 从 early_career 末尾 + first_exile 开头提取
  const route3Places = places
    .filter(p => {
      const num = parseInt(p.id.replace('SS', ''), 10);
      // SS023 湖州（案发地）+ SS024 开封（受审）+ SS025 黄州（贬谪）
      return num === 23 || num === 24 || num === 25;
    })
    .sort((a, b) => a.id.localeCompare(b.id));
  route3Places.forEach((p, i) => {
    points.push({
      id: p.id,
      name: p.songName,
      lat: p.lat,
      lng: p.lng,
      order: i + 1,
      routeId: 'route3',
      tag: p.id === 'SS023' ? '被捕' : p.id === 'SS024' ? '受审' : '贬谪',
    });
  });

  // route4: 黄州四年（first_exile 全部）
  const route4Places = places
    .filter(p => p.stage === 'first_exile')
    .sort((a, b) => a.id.localeCompare(b.id));
  route4Places.forEach((p, i) => {
    points.push({
      id: p.id,
      name: p.songName,
      lat: p.lat,
      lng: p.lng,
      order: i + 1,
      routeId: 'route4',
      tag: p.type === 'exile' ? '谪居' : '游历',
    });
  });

  // route5: 元祐回朝（middle_career 全部）
  const route5Places = places
    .filter(p => p.stage === 'middle_career')
    .sort((a, b) => a.id.localeCompare(b.id));
  route5Places.forEach((p, i) => {
    points.push({
      id: p.id,
      name: p.songName,
      lat: p.lat,
      lng: p.lng,
      order: i + 1,
      routeId: 'route5',
      tag: p.type === 'office' ? '任职' : p.type === 'friend' ? '访友' : '途经',
    });
  });

  // route6: 南迁北归（second_exile + third_exile + final_journey）
  const route6Stages = new Set<Stage>(['second_exile', 'third_exile', 'final_journey']);
  const route6Places = places
    .filter(p => route6Stages.has(p.stage))
    .sort((a, b) => a.id.localeCompare(b.id));
  route6Places.forEach((p, i) => {
    points.push({
      id: p.id,
      name: p.songName,
      lat: p.lat,
      lng: p.lng,
      order: i + 1,
      routeId: 'route6',
      tag: p.type === 'exile' ? '贬谪' : p.type === 'burial' ? '终老' : '途经',
    });
  });

  return points;
}

/**
 * 获取某条路线的轨迹点（从预构建的缓存读取）
 * 调用方应在 places 加载后调用 buildRoutesFromPlaces() 并缓存结果
 */
let _cachedRoutePoints: RouteTrackPoint[] | null = null;

export function setRoutePointsCache(points: RouteTrackPoint[]) {
  _cachedRoutePoints = points;
}

export function getRoutePoints(routeId: string): RouteTrackPoint[] {
  if (!_cachedRoutePoints) return [];
  return _cachedRoutePoints
    .filter(p => p.routeId === routeId)
    .sort((a, b) => a.order - b.order);
}

/** 获取所有路线的轨迹点（用于全图显示） */
export function getAllRoutePoints(): RouteTrackPoint[] {
  return _cachedRoutePoints || [];
}

/** 获取某条路线的统计信息 */
export function getRouteStats(routeId: string) {
  const points = getRoutePoints(routeId);
  return {
    count: points.length,
    start: points[0]?.name || '',
    end: points[points.length - 1]?.name || '',
  };
}
