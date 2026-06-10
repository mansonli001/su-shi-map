/**
 * data-loader.ts
 * ----------------------------------------------------------
 * 数据加载层 — 统一 v4 数据源
 *
 * 所有 v3 分支已移除，getDataVersion() 直接返回 'v4'
 * v4→PlaceCore 转换由 lib/v4-adapter.ts 唯一负责
 *
 * 本文件保留的职责：
 *   - loadPlaceDetail(): 加载单个地点详情 JSON
 *   - readPlaceDetailServer(): 服务端直读（SSG / API Route）
 *   - 类型导出（V4Place / V4PlaceDetail / V4Route）
 */

import type { PlaceCore, PlaceIndex } from "@/types";

// ----- 数据版本（固定 v4）-----
export type DataVersion = "v4";

export function getDataVersion(): DataVersion {
  return "v4";
}

// ----- 路径 -----
const V4_BASE = "/data-v4";

function basePath(): string {
  return V4_BASE;
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

// ----- 缓存 -----
const _detailCache = new Map<string, V4PlaceDetail>();

export function clearDataLoaderCache(): void {
  _detailCache.clear();
}

// ----- 通用 fetch -----
async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`fetch ${url} failed: HTTP ${res.status}`);
  return (await res.json()) as T;
}

// ----- 公开 API -----

/**
 * 获取单个地点详情
 * 统一走 v4 路径：/data-v4/places/{P001}.json
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

// ----- 服务端直读（Node.js fs，用于 SSG / API Route） -----
/**
 * 仅在 server 端使用（SSG / RSC / API Route）
 * 统一走 v4 路径
 */
export async function readPlaceDetailServer(id: string): Promise<any | null> {
  const fs = await import("node:fs/promises");
  const path = await import("node:path");
  const root = process.cwd();

  const tryPaths = [
    path.join(root, "public", "data-v4", "places", `${id}.json`),
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
