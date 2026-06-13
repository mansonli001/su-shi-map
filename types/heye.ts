/**
 * 贺野游中国 - 数据类型定义
 * 对齐 HEYE-DEV-PLAN §二·五 数据字段核心规划
 * 命名规范：JSON/CSV snake_case，TypeScript camelCase，loader 层做映射
 */

/** 行者 ID */
export type CharacterId = 'su-shi' | 'he-ye';

/** 坐标来源标记 */
export type CoordinateSource = 'amap_search' | 'manual' | 'inferred';

/** 贺野地点（展示层，对齐 data-v4 的 place schema） */
export interface HeyeLocation {
  id: string;                    // HY001 起，3位零填充
  province: string;              // 省份（聚合/着色主键）
  city: string;                  // 城市
  placeName: string;             // 具体地点名
  fullName: string;              // 展示全称 "福建·武夷山"
  region: string;                // PDF 原始地区标签（IP归属地，交叉校验用）
  lat: number;                   // GCJ-02 纬度
  lng: number;                   // GCJ-02 经度
  coordinateSource: CoordinateSource; // 坐标来源标记
  visitDate: string | null;      // "YYYY年M月"，模糊日期
  visitYear: number | null;      // 从 visitDate 派生的年份
  tripTag: string | null;        // 弱标签，同次出行软关联
  excerpt: string;               // 原文原话，50-150字
  snacks: string[];              // 吃过的食物，空则不渲染
  imageUrl: string;              // 配图，空则渐变占位
  articleUrl: string;            // 公众号原文外链，空则隐藏
  sourceTitle: string;           // "读原文"标题/溯源
  featured: boolean;             // 首页精选轮播，默认 false
  visitCount: number;            // 到访次数
  visitHistory: string;          // 多次到访历史，如"2022年8月（2022南下之旅）、2024年3月"
}

/** 贺野成就 */
export interface HeyeAchievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  tier: 'bronze' | 'silver' | 'gold';
  conditionType: 'checkin_count' | 'snack_location' | 'province_count'
    | 'snack_variety' | 'percent' | 'checkin_all';
  conditionValue: number | null;
  sortOrder: number;
  // 计算结果，运行时注入
  progress?: number;
  total?: number;
  unlocked?: boolean;
}

/** 省份统计（单省） */
export interface ProvinceStats {
  placeCount: number;
  cityCount: number;
  placeIds: string[];
  densityTier: 0 | 1 | 2 | 3;  // 0=无 / 1=1-2 / 2=3-5 / 3=6+
}

/** 省份统计（全量映射） */
export interface HeyeProvinceStatsMap {
  [province: string]: ProvinceStats;
}

/** 首页统计 + 全局元信息 */
export interface HeyeMeta {
  schemaVersion: string;
  generatedAt: string;
  dataSource: string;
  disclaimer: string;
  stats: {
    totalPlaces: number;
    provinceCount: number;
    cityCount: number;
    snackVariety: number;
    articleCount: number;
    tripCount: number;
    featuredCount: number;
  };
}

/** 贺野打卡类型 */
export type HeyeCheckinType = 'cloud' | 'photo' | 'gps';

/** 贺野打卡记录 */
export interface HeyeCheckinPlace {
  placeId: string;
  placeName: string;
  checkinAt: string;
  checkinType: HeyeCheckinType;
  note?: string;
}
