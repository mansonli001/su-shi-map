/**
 * 美食搜索模块
 * 封装高德地图 PlaceSearch 接口，实现附近美食推荐功能
 * - 真接入 AMap.PlaceSearch（type=050000 餐饮服务）
 * - 1 分钟同地点缓存避免重复请求
 * - SDK 加载失败 / API 调用失败一律返回 []，不阻塞 UI
 */

import { loadAMap } from './amap-loader';
import { logger } from './logger';

// 高德地图 POI 搜索结果类型（保持向后兼容，PlaceCard 已依赖此 schema）
export interface AMapPOIResult {
  id: string;
  name: string;
  type: string;
  address: string;
  location: {
    lat: number;
    lng: number;
  };
  distance?: number;
  rating?: number;
  photos?: string[];
  businessHours?: string;
  tel?: string;
  categories?: string[];
  comment_count?: string;
}

// 缓存接口
interface FoodCacheItem {
  timestamp: number;
  data: AMapPOIResult[];
}

// 1 分钟缓存
const CACHE_DURATION = 60 * 1000;
const foodCache = new Map<string, FoodCacheItem>();

function getCacheKey(lat: number, lng: number, radius: number): string {
  // 4 位小数 ≈ 11 米精度，足以聚合"同一地点"的请求
  return `${lat.toFixed(4)}_${lng.toFixed(4)}_${radius}`;
}

// 高德 POI 餐饮服务大类编码
// 参考：https://lbs.amap.com/api/webservice/download
const FOOD_POI_TYPE = '050000';

/**
 * 搜索附近美食（真接入高德 PlaceSearch）
 * @param lat 纬度
 * @param lng 经度
 * @param radius 搜索半径（米），默认 2000
 * @returns POI 结果数组，失败/异常返回 []
 */
export async function searchNearbyFood(
  lat: number,
  lng: number,
  radius: number = 2000,
): Promise<AMapPOIResult[]> {
  // 参数校验
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return [];
  }

  const cacheKey = getCacheKey(lat, lng, radius);
  const cached = foodCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  // 浏览器侧才能跑（SSR 直接返回空）
  if (typeof window === 'undefined') {
    return [];
  }

  try {
    const AMap = await loadAMap();
    if (!AMap) {
      return [];
    }

    // 动态加载 PlaceSearch 插件（与基础 plugins 隔离，按需触发）
    await new Promise<void>((resolve, reject) => {
      AMap.plugin(['AMap.PlaceSearch'], () => resolve());
      // 5 秒超时兜底
      setTimeout(() => reject(new Error('AMap.PlaceSearch plugin load timeout')), 5000);
    });

    if (!AMap.PlaceSearch) {
      logger.warn('[food-search] AMap.PlaceSearch 插件未注入，跳过附近美食搜索');
      return [];
    }

    const placeSearch = new AMap.PlaceSearch({
      type: FOOD_POI_TYPE,
      pageSize: 20,
      pageIndex: 1,
      extensions: 'all',
    });

    const results = await new Promise<AMapPOIResult[]>((resolve) => {
      const center: [number, number] = [lng, lat];
      placeSearch.searchNearBy(
        '',
        center,
        radius,
        (status: string, result: { poiList?: { pois?: AMapPOIPoi[] } }) => {
          if (status !== 'complete' || !result?.poiList?.pois) {
            resolve([]);
            return;
          }
          const pois: AMapPOIPoi[] = result.poiList.pois || [];
          const mapped: AMapPOIResult[] = pois.map((p) => {
            const typeStr = String(p.type || '');
            // v6.2 修复：高德 type 字段格式如 "餐饮服务;粤菜;茶餐厅"，按 ; 拆出可用作菜系匹配的类目
            // 之前未填 categories → PlaceCard 的 isCuisineMatch 永远返回 0 → 本地菜系维度（20%权重）形同虚设
            const categories = typeStr
              .split(/[;；]/)
              .map((s) => s.trim())
              .filter(Boolean);
            // v6.2 修复：高德 PlaceSearch 不直接返回评论数，用 photos 数量作为热度代理
            // 之前未填 comment_count → PlaceCard 中 parseInt(undefined||'0')=0 → 评论数维度（25%权重）形同虚设
            // photos 数量虽不等于评论数，但与商家曝光度正相关，可作为 popularity proxy
            const photosArr =
              Array.isArray(p.photos) && p.photos.length > 0
                ? p.photos.map((ph) => String(ph?.url || '')).filter(Boolean)
                : undefined;
            const photosCount = photosArr ? photosArr.length : 0;
            return {
              id: String(p.id || ''),
              name: String(p.name || ''),
              type: typeStr,
              address: String(p.address || ''),
              location: {
                lat: typeof p.location?.lat === 'number' ? p.location.lat : lat,
                lng: typeof p.location?.lng === 'number' ? p.location.lng : lng,
              },
              distance: typeof p.distance === 'number' ? Math.round(p.distance) : undefined,
              tel: p.tel ? String(p.tel) : undefined,
              photos: photosArr,
              // 高德返回的 rating 多数为空字符串，做容错
              rating: parseRating(p.biz_ext?.rating),
              categories,
              comment_count: String(photosCount),
            };
          });
          resolve(mapped);
        },
      );
    });

    foodCache.set(cacheKey, { timestamp: Date.now(), data: results });
    return results;
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    logger.warn('[food-search] 附近美食搜索失败，返回空数组', msg);
    return [];
  }
}

// 高德 PlaceSearch POI 内部类型（仅本模块使用）
interface AMapPOIPoi {
  id?: string;
  name?: string;
  type?: string;
  address?: string;
  tel?: string;
  distance?: number;
  location?: { lat?: number; lng?: number };
  photos?: { url?: string }[];
  biz_ext?: { rating?: string | number };
}

function parseRating(raw: unknown): number | undefined {
  if (raw === undefined || raw === null || raw === '') return undefined;
  const n = typeof raw === 'number' ? raw : parseFloat(String(raw));
  return Number.isFinite(n) && n > 0 ? n : undefined;
}

/**
 * 苏轼特供美食 JSON 数据类型
 */
export interface FoodItem {
  id: string;
  name: string;
  alias: string;
  desc: string;
  origin: string;
  routeId: string;
  tags: string[];
  relatedPoem?: string;
}

let _sushiFoodsPromise: Promise<FoodItem[]> | null = null;

/**
 * 获取苏轼特供美食列表（带模块级单 Promise 缓存）
 * @param routeId 可选，按路线筛选
 */
export async function getSushiSpecialFoods(routeId?: string): Promise<FoodItem[]> {
  if (!_sushiFoodsPromise) {
    _sushiFoodsPromise = (async () => {
      try {
        const response = await fetch('/data-v4/foods-sushi.json');
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const data = await response.json();
        return Array.isArray(data?.foods) ? (data.foods as FoodItem[]) : [];
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        logger.warn('[food-search] 苏轼特供美食加载失败', msg);
        return [];
      }
    })();
  }
  const all = await _sushiFoodsPromise;
  if (routeId) {
    return all.filter((f) => f.routeId === routeId);
  }
  return all;
}

/**
 * 清理缓存（用于测试或手动刷新）
 */
export function clearFoodCache(): void {
  foodCache.clear();
}

/**
 * 检查是否有缓存数据
 */
export function hasCachedFood(lat: number, lng: number, radius: number): boolean {
  const cacheKey = getCacheKey(lat, lng, radius);
  const cached = foodCache.get(cacheKey);
  return !!cached && Date.now() - cached.timestamp < CACHE_DURATION;
}
