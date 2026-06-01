/**
 * 读苏轼·游神州 - 数据类型定义
 * v4.0 规范
 */

/** 地点类型 - v3 旧分类（保留兼容） */
export type PlaceType = 'birth' | 'office' | 'exile' | 'tour' | 'friend' | 'burial';

/** 地点类型 - v4 设计稿 8 类（marker SVG 选择用） */
export type DesignPlaceType =
  | 'main'      // 主线行进
  | 'visit'     // 沿途游览（含 around / sight）
  | 'stay'      // 普通驻留
  | 'study'     // 游学地
  | 'birth'     // 出生地
  | 'official'  // 任职地
  | 'death'     // 离世地
  | 'tomb';     // 墓葬地

/** 7阶段 */
export const STAGES = [
  'youth',      // 眉山少年 (1036-1057)
  'early_career', // 入京初仕 (1057-1079)
  'first_exile',  // 黄州四年 (1080-1084)
  'middle_career', // 翰林侍从 (1085-1091)
  'second_exile',  // 岭南三年 (1094-1097)
  'third_exile',   // 儋耳三年 (1097-1100)
  'final_journey', // 北归长眠 (1100-1101)
] as const;

export type Stage = (typeof STAGES)[number];

/** 地点核心数据（首屏全量加载） */
export interface PlaceCore {
  id: string;           // SS001 ~ SS120
  lat: number;          // GCJ-02
  lng: number;          // GCJ-02
  type: PlaceType;
  stage: Stage;
  importance: 1 | 2 | 3; // 1=必看 2=推荐 3=了解
  songName: string;     // 宋代地名
  modernName: string;   // 当代地名
  summary?: string;     // 50字摘要（从 index 合并）
  famousLine?: string;  // 最著名诗句（从 index 合并）
  routeId?: string;     // 所属19条路线之一（route01~route19）或总览（overview）
  routeOrder?: number;   // 在路线中的行进顺序（从1开始）
  tag?: string;          // 进京/出京/途经/被捕/谪居/终老
  designType?: DesignPlaceType; // v4 设计稿 8 类，用于 marker SVG 选择
  relatedRoutes?: string[]; // v4 该地点关联的所有路线 id（多对多）
}

/** 地点索引（搜索用，轻量） */
export interface PlaceIndex {
  id: string;
  songName: string;
  modernName: string;
  summary: string;      // 50字摘要
  famousLine?: string;  // 最著名诗句
  type: PlaceType;
  stage: Stage;
}

/** 诗词 */
export interface Poem {
  id: string;
  title: string;
  content: string;      // 完整文本
  year?: number;        // 创作年份
  locationId?: string;  // 创作地点
  translation?: string; // 今译（可选）
 赏析?: string;         // 赏析（可选）
}

/** 景点 */
export interface Attraction {
  id: string;
  name: string;
  description: string;
  ticket?: string;      // 门票信息
  openTime?: string;    // 开放时间
  address?: string;     // 当代地址
}

/** 美食 */
export interface Food {
  name: string;
  description: string;
  modernName?: string;  // 当代菜名
  recipeUrl?: string;   // 菜谱链接
}

/** 本地打卡 */
export interface LocalCheckin {
  placeId: string;
  checkedAt: number;    // Unix timestamp
  note?: string;
}

/** 时间段叙事（支持多时间段详细叙事） */
export interface PeriodNarrative {
  period: string;        // 如 "1080-1084"
  title: string;         // 时段标题，如 "黄州贬谪"
  description: string;   // 该时段详细叙事（支持Markdown）
}

/** 外部链接 */
export interface ExternalLink {
  title: string;         // 链接标题
  url: string;           // URL
}

/** 地点详情（按需加载） */
export interface PlaceDetail extends PlaceCore {
  summary: string;            // 200字事迹概述
  periods: PeriodNarrative[]; // 多时间段叙事（支持长篇）
  extendedStory: string;       // 长篇叙事文章（Markdown格式）
  poems: Poem[];             // 该地点相关诗词（本地全文）
  attractions: Attraction[];   // 该地点现代景点（0-5个）
  food: Food[];               // 该地点美食（0-3个）
  images?: string[];           // 图片URL列表
  externalLinks?: ExternalLink[]; // 外部链接（古诗文网等）
}

/** 时间轴阶段信息 */
export interface StageInfo {
  key: Stage;
  label: string;
  yearRange: string;
  color: string;
  icon: string;
  summary: string;
}

/** 导航结果 */
export interface NavigateResult {
  success: boolean;
  message: string;
  appUri?: string;      // 高德App URI
  webUrl?: string;      // 网页版URL
}
