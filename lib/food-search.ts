/**
 * 美食搜索模块
 * v6.5 关键变更：附近美食搜索从 JSAPI `AMap.PlaceSearch` 切到服务端 Web Service
 *   - 旧链路在浏览器侧因 key 权限/securityJsCode/JSAPI 配额波动经常 status!=='complete' 直接返回空，
 *     用户只能看到「连高德也沉默了」的空状态，但其实是 API 调用失败而非"附近真没餐厅"
 *   - 新链路走 /api/nearby-food（AMAP_WEB_SERVICE_KEY 服务端持有），schema 稳定且不暴露 key
 * - 1 分钟同地点客户端缓存避免重复请求
 * - 服务端再叠 60s 缓存（见 /api/nearby-food/route.ts）
 * - 任何异常一律返回 []，不阻塞 UI
 */

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

// 高德 POI 餐饮服务大类编码（保留供未来扩展，当前由服务端写死）
// 参考：https://lbs.amap.com/api/webservice/download

/**
 * 搜索附近美食（v6.5 改走服务端 /api/nearby-food，AMap Web Service v3）
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
    const params = new URLSearchParams({
      lat: String(lat),
      lng: String(lng),
      radius: String(Math.max(1, Math.round(radius))),
    });
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 6000);
    const resp = await fetch(`/api/nearby-food?${params.toString()}`, {
      signal: ctrl.signal,
      cache: 'no-store',
    }).finally(() => clearTimeout(timer));

    if (!resp.ok) {
      logger.warn('[food-search] /api/nearby-food HTTP', resp.status);
      foodCache.set(cacheKey, { timestamp: Date.now(), data: [] });
      return [];
    }
    const data = (await resp.json()) as { pois?: AMapPOIResult[] };
    const pois: AMapPOIResult[] = Array.isArray(data?.pois) ? data.pois : [];
    foodCache.set(cacheKey, { timestamp: Date.now(), data: pois });
    return pois;
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    logger.warn('[food-search] 附近美食搜索失败，返回空数组', msg);
    return [];
  }
}

/**
 * 新的按地点绑定的苏轼美食数据类型
 */
export interface LocalFoodItem {
  id: string;
  name: string;
  alias?: string;
  desc: string;
  source_text: string;
  source_work: string;
  confidence: "A" | "B" | "C";
  story?: string;
  tags?: string[];
}

interface FoodsByPlace {
  version: string;
  updatedAt: string;
  description: string;
  places: Record<string, {
    name: string;
    foods: LocalFoodItem[];
  }>;
  shared_foods?: {
    description: string;
    items: any[];
  };
}

/**
 * 兼容性保留：旧的 FoodItem 接口
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
let _foodsByPlacePromise: Promise<FoodsByPlace | null> | null = null;

/**
 * 获取按地点绑定的美食数据（新数据结构）
 */
export async function getFoodsByPlace(): Promise<FoodsByPlace | null> {
  // 每次调用都重新加载，确保获取最新数据
  try {
    const response = await fetch('/data-v4/foods-by-place.json?' + Date.now());
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const data = await response.json();
    return data as FoodsByPlace;
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    logger.warn('[food-search] foods-by-place.json 加载失败', msg);
    return null;
  }
}

/**
 * 获取特定地点的苏轼特供美食
 * @param placeId 地点ID
 */
export async function getSushiFoodsByPlace(placeId: string): Promise<LocalFoodItem[]> {
  const foodsByPlace = await getFoodsByPlace();
  if (!foodsByPlace) return [];
  
  const placeData = foodsByPlace.places[placeId];
  if (!placeData) return [];
  
  return placeData.foods || [];
}

/**
 * 兼容性保留：旧的 getSushiSpecialFoods 函数（返回旧格式数据）
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
