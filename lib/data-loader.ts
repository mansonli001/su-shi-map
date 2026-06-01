/**
 * data-loader.ts
 * ----------------------------------------------------------
 * 数据加载抽象层 — v3 / v4 双源可切换
 *
 * 切换方式：
 *   process.env.NEXT_PUBLIC_DATA_VERSION = 'v3' | 'v4'   （默认 'v3'）
 *
 * 适用场景：
 *   - 浏览器端（fetch 走 /data 或 /data-v4）
 *   - 服务端（Node fs 直读项目根 data/ 或 data-v4/）
 *
 * 设计原则：
 *   - 不破坏现有 v3 字段名（PlaceCore / PlaceIndex 直接复用 @/types）
 *   - v4 模式下增加 v4-only 字段（ancient_name / layer / coordinate_source）
 *   - 提供 PlaceCore[] 兼容视图：v4 → v3 的字段适配
 *   - 单例缓存（避免 client 端重复 fetch）
 *
 * 本轮交付（Phase 2.4）：
 *   ✅ 函数定义 + v3/v4 双源 fetch + 缓存
 *   ❌ 不改 UI（UI 改造留下一轮）
 *   ✅ 通过 verify-data-loader.ts 跑通冒烟
 */

import type { PlaceCore, PlaceIndex } from "@/types";

// ----- 数据版本 -----
export type DataVersion = "v3" | "v4";

export function getDataVersion(): DataVersion {
  // Next.js 中 NEXT_PUBLIC_* 在 client/server 都可读
  const v =
    (typeof process !== "undefined" && process.env.NEXT_PUBLIC_DATA_VERSION) ||
    "v3";
  return v === "v4" ? "v4" : "v3";
}

// ----- 路径解析 -----
const V3_BASE = "/data";
const V4_BASE = "/data-v4";

function basePath(): string {
  return getDataVersion() === "v4" ? V4_BASE : V3_BASE;
}

// ----- v4 原始 schema -----
export interface V4Place {
  id: string; // P001-P234
  ancient_name: string;
  modern_name: string;
  type:
    | "main"
    | "sight"
    | "around"
    | "birth"
    | "official"
    | "study"
    | "stay"
    | "visit"
    | "death"
    | "tomb";
  layer?: "main" | "sight" | "around";
  lat: number;
  lng: number;
  coordinate_source?: string;
  trustworthy?: boolean;
  importance?: number;
  tags?: string[];
  summary?: string;
  related_routes: string[];
  route_layers?: Array<{ route_id: string; layer: string; order: number }>;
  occurrences?: number;
  has_detail?: boolean;
  verified?: boolean;
  legacy?: any;
}

export interface V4PlaceDetail extends V4Place {
  background?: string;
  periods?: Array<{ period: string; title: string; description: string }>;
  global_events?: any[];
  global_works?: any[];
  route_events?: Record<string, any[]>;
  route_works?: Record<string, any[]>;
  memorial_sites?: any[];
  foods?: any[];
  transport?: Record<string, string>;
  sub_places?: any[];
}

export interface V4Route {
  id: string;
  index: number;
  name: string;
  period: string;
  start_year: number;
  end_year: number;
  unique_color: string;
  description_short: string;
  place_count: number;
  main_count?: number;
  sight_count?: number;
  around_count?: number;
}

// ----- v4 → v3 适配 -----
/**
 * 把 v4 PlaceCore 适配成 v3 兼容字段，让现有组件可以无改动消费
 * v3 字段（来自 @/types PlaceCore）：
 *   id / lat / lng / type / stage? / importance? / songName / modernName / routeId? / routeOrder?
 * v4 → v3 映射：
 *   id            → id（仍用 P001-P234，前端不应硬编码 SSxxx）
 *   ancient_name  → songName
 *   modern_name   → modernName
 *   type          → type （v4 多了 main/sight/around/study/stay 等扩展，v3 老组件如未识别会回退默认渲染）
 *   importance    → importance
 *   related_routes[0] → routeId（兼容旧逻辑；多路线场景下应改用 related_routes 数组）
 */
export function v4ToV3PlaceCore(p: V4Place): PlaceCore {
  return {
    id: p.id,
    lat: p.lat,
    lng: p.lng,
    type: (p.type as any) || "around",
    importance: (p.importance as 1 | 2 | 3) ?? 3,
    songName: p.ancient_name,
    modernName: p.modern_name,
    routeId: (p.related_routes && p.related_routes[0]) || undefined,
    // 老字段如 stage/routeOrder 在 v4 已废弃 → 留空
  } as PlaceCore;
}

// ----- 缓存 -----
let _placesCache: PlaceCore[] | null = null;
let _v4PlacesCache: V4Place[] | null = null;
let _v4RoutesCache: V4Route[] | null = null;
const _detailCache = new Map<string, V4PlaceDetail>();

export function clearDataLoaderCache(): void {
  _placesCache = null;
  _v4PlacesCache = null;
  _v4RoutesCache = null;
  _detailCache.clear();
}

// ----- 通用 fetch（client 端） -----
async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`fetch ${url} failed: HTTP ${res.status}`);
  return (await res.json()) as T;
}

// ----- 公开 API -----

/**
 * 获取 v3 兼容格式的 PlaceCore[] —— 现有 UI 直接消费
 */
export async function loadPlacesCore(): Promise<PlaceCore[]> {
  if (_placesCache) return _placesCache;

  const version = getDataVersion();

  if (version === "v4") {
    const raw = await fetchJSON<{ places: V4Place[] }>(
      `${V4_BASE}/places-index.json`,
    );
    _v4PlacesCache = raw.places;
    _placesCache = raw.places.map(v4ToV3PlaceCore);
  } else {
    _placesCache = await fetchJSON<PlaceCore[]>(`${V3_BASE}/places-core.json`);
  }

  return _placesCache;
}

/**
 * 获取轻量 PlaceIndex[]（搜索专用，仅含 id/songName/modernName 等少量字段）
 */
export async function loadPlacesIndex(): Promise<PlaceIndex[]> {
  const version = getDataVersion();

  if (version === "v4") {
    const cores = await loadPlacesCore();
    // PlaceIndex 是 PlaceCore 的子集，直接复用
    return cores.map((c) => ({
      id: c.id,
      lat: c.lat,
      lng: c.lng,
      type: c.type,
      importance: c.importance,
      songName: c.songName,
      modernName: c.modernName,
    })) as unknown as PlaceIndex[];
  } else {
    return fetchJSON<PlaceIndex[]>(`${V3_BASE}/places-index.json`);
  }
}

/**
 * 获取 v4 原始 places（需要 v4 模式）
 */
export async function loadV4Places(): Promise<V4Place[]> {
  if (_v4PlacesCache) return _v4PlacesCache;
  if (getDataVersion() !== "v4") {
    throw new Error(
      "[data-loader] loadV4Places 只能在 NEXT_PUBLIC_DATA_VERSION=v4 时调用",
    );
  }
  await loadPlacesCore(); // 这一步会顺便填充 _v4PlacesCache
  return _v4PlacesCache!;
}

/**
 * 获取单个地点详情
 *  - v3 模式：fetch /data/places/{SS001}.json
 *  - v4 模式：fetch /data-v4/places/{P001}.json
 */
export async function loadPlaceDetail(
  id: string,
): Promise<V4PlaceDetail | any> {
  if (_detailCache.has(id)) return _detailCache.get(id)!;

  const url = `${basePath()}/places/${id}.json`;
  const data = await fetchJSON<any>(url);
  _detailCache.set(id, data);
  return data;
}

/**
 * 获取路线索引（v4 only；v3 模式下 routes 由 lib/route19-config.ts 静态产出）
 */
export async function loadV4RoutesIndex(): Promise<V4Route[]> {
  if (_v4RoutesCache) return _v4RoutesCache;
  if (getDataVersion() !== "v4") {
    // v3 模式回空数组，不抛异常（让调用方自行兜底）
    return [];
  }
  const raw = await fetchJSON<{ routes: V4Route[] }>(
    `${V4_BASE}/routes-index.json`,
  );
  _v4RoutesCache = raw.routes;
  return raw.routes;
}

/**
 * 获取单条路线详情（含 track_segments）
 */
export async function loadV4Route(id: string): Promise<any> {
  if (getDataVersion() !== "v4") {
    throw new Error(
      "[data-loader] loadV4Route 只能在 NEXT_PUBLIC_DATA_VERSION=v4 时调用",
    );
  }
  return fetchJSON<any>(`${V4_BASE}/routes/${id}.json`);
}

// ----- 服务端直读（Node.js fs，用于 SSG / API Route） -----
/**
 * 仅在 server 端使用（SSG / RSC / API Route）
 * 优先 v4 → 回退 v3
 */
export async function readPlaceDetailServer(id: string): Promise<any | null> {
  // 动态 import 仅 server 端可用的模块
  const fs = await import("node:fs/promises");
  const path = await import("node:path");
  const root = process.cwd();
  const version = getDataVersion();

  const tryPaths =
    version === "v4"
      ? [
          path.join(root, "data-v4", "places", `${id}.json`),
          path.join(root, "data", "places", `${id}.json`),
        ]
      : [
          path.join(root, "data", "places", `${id}.json`),
          path.join(root, "data-v4", "places", `${id}.json`),
        ];

  for (const p of tryPaths) {
    try {
      const buf = await fs.readFile(p, "utf-8");
      return JSON.parse(buf);
    } catch {
      // 路径不存在，继续下一个
    }
  }
  return null;
}
