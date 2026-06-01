/**
 * v4-adapter
 * ----------------------------------------------------------
 * 把 v4 数据（places-index + routes-index + stages-index）
 * 适配成现有 UI 期望的 v3 PlaceCore[] / Route 配置格式
 * 让 AMapContainer/LeftSidebar 等组件不需要大改即可消费 v4。
 *
 * 关键映射：
 *   v4 P{nnn}  → v3 PlaceCore.id 直接复用
 *   v4 R{nn}   → v3 PlaceCore.routeId 直接复用（不再映射 route01-19，弱类型化）
 *   v4 ancient_name → songName
 *   v4 modern_name  → modernName
 *   v4 type      → 智能映射到 PlaceType（birth/office/exile/tour/friend/burial）
 *   v4 stage_id  → 直接保留供 UI 读取
 *
 * 路线轨迹：
 *   走 routes/{R_id}.json 的 places 数组（按 order 排好序）→ 拼出每条路线的轨迹点
 */

import type { PlaceCore, DesignPlaceType } from "@/types";

// ─── v4 原始 schema ─────────────────────────────────
export interface V4PlaceIdx {
  id: string;
  ancient_name: string;
  modern_name: string;
  type: string;
  layer?: string;
  lat: number;
  lng: number;
  importance?: number;
  tags?: string[];
  related_routes: string[];
  has_detail?: boolean;
}

export interface V4RouteIdx {
  id: string;
  index: number;
  name: string;
  period: string;
  start_year: number;
  end_year: number;
  unique_color: string;
  description_short?: string;
  place_count: number;
  stage_id?: string;
}

export interface V4StageIdx {
  id: string;
  index: number;
  name: string;
  alias: string;
  route_ids: string[];
  start_year: number;
  end_year: number;
  duration_years: number;
  theme: string;
  color: string;
  age_range: string;
}

export interface V4RouteDetail {
  id: string;
  name?: string;
  unique_color?: string;
  start_year?: number;
  end_year?: number;
  description_short?: string;
  stage_id?: string;
  // 真实 schema：用 track_segments + sight/around/related place_ids
  track_segments?: Array<{
    segment_id: string;
    label?: string;
    place_ids: string[];
    transport_mode?: string;
  }>;
  sight_place_ids?: string[];
  around_place_ids?: string[];
  related_place_ids?: string[];
  // 兼容字段（早期 schema）
  places?: Array<{
    id: string;
    order?: number;
    layer?: string;
    name?: string;
    lat?: number;
    lng?: number;
  }>;
}

// ─── v4 type → v3 PlaceType 智能映射 ─────────────────
function mapType(p: V4PlaceIdx): PlaceCore["type"] {
  const t = (p.type || "").toLowerCase();
  const tags = (p.tags || []).map((s) => s.toLowerCase());

  // 出生 / 终老（少量）
  if (t === "birth" || tags.includes("birth")) return "birth";
  if (t === "death" || t === "tomb" || tags.includes("burial") || tags.includes("end_life"))
    return "burial";

  // 贬谪（按标签判断，最准）
  if (
    tags.includes("relegated") ||
    tags.includes("banished") ||
    tags.includes("exile") ||
    tags.includes("end_relegate") ||
    tags.includes("master_meet") // 兄弟相会贬途
  )
    return "exile";

  // 任职
  if (
    t === "official" ||
    tags.includes("official") ||
    tags.includes("court") ||
    tags.includes("hub")
  )
    return "office";

  // 友人 / 师生
  if (tags.includes("friend") || tags.includes("master_meet")) return "friend";

  // 默认游历
  return "tour";
}

// ─── v4 type → 设计稿 8 类 DesignPlaceType ─────────────
function mapDesignType(p: V4PlaceIdx): DesignPlaceType {
  const t = (p.type || "").toLowerCase();
  // 直接映射
  if (t === "main") return "main";
  if (t === "stay") return "stay";
  if (t === "study") return "study";
  if (t === "birth") return "birth";
  if (t === "official") return "official";
  if (t === "death") return "death";
  if (t === "tomb") return "tomb";
  // around / sight 归到 visit（沿途游览）
  if (t === "around" || t === "sight" || t === "visit") return "visit";
  // 兜底
  return "visit";
}

// ─── PlaceIndex → PlaceCore（v3 兼容） ──────────────
export function v4PlaceToPlaceCore(p: V4PlaceIdx, stageMap?: Map<string, string>): PlaceCore {
  // 尝试从 related_routes[0] 推 stage
  const r0 = (p.related_routes || [])[0];
  const stageId = r0 && stageMap ? stageMap.get(r0) : undefined;

  return {
    id: p.id,
    lat: p.lat,
    lng: p.lng,
    type: mapType(p),
    designType: mapDesignType(p),
    stage: (stageId || "early_career") as any, // 兜底
    importance: ((p.importance as 1 | 2 | 3) ?? 3) as 1 | 2 | 3,
    songName: p.ancient_name,
    modernName: p.modern_name,
    routeId: r0 || undefined,
    routeOrder: undefined, // 路线 order 在 routes/{Rid}.json 里
    relatedRoutes: p.related_routes || [],
    tag:
      (p.tags || [])[0] ||
      (p.layer === "main" ? "主线" : p.layer === "water" ? "水路" : p.layer === "surrounding" ? "周边" : "途经"),
  } as PlaceCore;
}

// ─── 数据加载（带缓存） ──────────────────────────────
const V4_BASE = "/data-v4";

let _cache: {
  places?: V4PlaceIdx[];
  routes?: V4RouteIdx[];
  stages?: V4StageIdx[];
  placeCores?: PlaceCore[];
  stageOfRoute?: Map<string, string>;
  routeDetails?: Map<string, V4RouteDetail>;
} = {};

export function clearV4AdapterCache() {
  _cache = {};
}

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${url}?t=${Date.now()}`);
  if (!res.ok) throw new Error(`fetch ${url} failed: HTTP ${res.status}`);
  return (await res.json()) as T;
}

export async function loadV4Stages(): Promise<V4StageIdx[]> {
  if (_cache.stages) return _cache.stages;
  const data = await fetchJSON<{ stages: V4StageIdx[] }>(`${V4_BASE}/stages-index.json`);
  _cache.stages = data.stages;
  return data.stages;
}

export async function loadV4RoutesIdx(): Promise<V4RouteIdx[]> {
  if (_cache.routes) return _cache.routes;
  const data = await fetchJSON<{ routes: V4RouteIdx[] }>(`${V4_BASE}/routes-index.json`);
  _cache.routes = data.routes;
  return data.routes;
}

export async function loadV4PlacesIdx(): Promise<V4PlaceIdx[]> {
  if (_cache.places) return _cache.places;
  const data = await fetchJSON<{ places: V4PlaceIdx[] }>(`${V4_BASE}/places-index.json`);
  _cache.places = data.places;
  return data.places;
}

export async function loadStageOfRouteMap(): Promise<Map<string, string>> {
  if (_cache.stageOfRoute) return _cache.stageOfRoute;
  const routes = await loadV4RoutesIdx();
  const m = new Map<string, string>();
  for (const r of routes) if (r.stage_id) m.set(r.id, r.stage_id);
  _cache.stageOfRoute = m;
  return m;
}

/**
 * 加载所有 places 并转换为 v3 PlaceCore[]
 * 同时合并 routes/{Rid}.json 中的 order 信息（让每个 place 在所属路线中有 routeOrder）
 */
export async function loadV4PlaceCores(): Promise<PlaceCore[]> {
  if (_cache.placeCores) return _cache.placeCores;

  const [places, stageMap, routes] = await Promise.all([
    loadV4PlacesIdx(),
    loadStageOfRouteMap(),
    loadV4RoutesIdx(),
  ]);

  // 先把 places 全部转换
  const cores: PlaceCore[] = places.map((p) => v4PlaceToPlaceCore(p, stageMap));
  const coreMap = new Map(cores.map((c) => [c.id, c]));

  // 加载所有路线 detail，给每个 place 注入 routeOrder（按它所属的第 1 条路线）
  const detailMap = new Map<string, V4RouteDetail>();
  await Promise.all(
    routes.map(async (r) => {
      try {
        const d = await fetchJSON<V4RouteDetail>(`${V4_BASE}/routes/${r.id}.json`);
        detailMap.set(r.id, d);
      } catch {
        /* 路线 detail 可能缺失，跳过 */
      }
    }),
  );
  _cache.routeDetails = detailMap;

  // 给每个 PlaceCore 打 routeOrder（基于它的 routeId 在该路线 places[] 中的位置）
  for (const c of cores) {
    if (!c.routeId) continue;
    const d = detailMap.get(c.routeId);
    if (!d) continue;
    // 优先用 track_segments[*].place_ids 拼出主路径顺序
    let orderedIds: string[] = [];
    if (d.track_segments && d.track_segments.length > 0) {
      for (const seg of d.track_segments) {
        for (const pid of seg.place_ids || []) orderedIds.push(pid);
      }
    } else if (d.places) {
      // 兼容旧 schema
      orderedIds = [...d.places]
        .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
        .map((pp) => pp.id);
    }
    const idx = orderedIds.indexOf(c.id);
    if (idx >= 0) {
      c.routeOrder = idx + 1;
    }
  }

  _cache.placeCores = cores;
  return cores;
}

// ─── 路线轨迹构建（替代 buildRoutes19FromPlaces） ───────
export interface V4TrackPoint {
  id: string;
  name: string;
  lat: number;
  lng: number;
  order: number;
  routeId: string;
  tag: string;
}

export async function buildV4RouteTracks(): Promise<V4TrackPoint[]> {
  const [routes, places] = await Promise.all([loadV4RoutesIdx(), loadV4PlaceCores()]);
  const placeMap = new Map(places.map((p) => [p.id, p]));
  const detailMap = _cache.routeDetails || new Map();

  const points: V4TrackPoint[] = [];
  for (const r of routes) {
    const d = detailMap.get(r.id);
    if (!d) continue;
    // 优先 track_segments
    let orderedIds: string[] = [];
    if (d.track_segments && d.track_segments.length > 0) {
      for (const seg of d.track_segments) {
        for (const pid of seg.place_ids || []) orderedIds.push(pid);
      }
    } else if (d.places) {
      orderedIds = [...d.places]
        .sort((a: any, b: any) => (a.order ?? 0) - (b.order ?? 0))
        .map((pp: any) => pp.id);
    }
    orderedIds.forEach((pid, idx) => {
      const core = placeMap.get(pid);
      if (!core) return;
      points.push({
        id: core.id,
        name: core.songName,
        lat: core.lat,
        lng: core.lng,
        order: idx + 1,
        routeId: r.id,
        tag: core.tag || '途经',
      });
    });
  }
  return points;
}

// ─── 路线配置（替代 ROUTE19_CONFIG） ───────────────
export interface V4RouteConfig {
  id: string;
  name: string;
  time: string;
  mainColor: string;
  desc: string;
  startPlace: string;
  endPlace: string;
  stageId?: string;
}

export async function buildV4RouteConfigs(): Promise<Record<string, V4RouteConfig>> {
  const [routes, places] = await Promise.all([loadV4RoutesIdx(), loadV4PlaceCores()]);
  const placeMap = new Map(places.map((p) => [p.id, p]));
  const detailMap = _cache.routeDetails || new Map();

  const cfg: Record<string, V4RouteConfig> = {};
  for (const r of routes) {
    const d = detailMap.get(r.id);
    let startPlace = '';
    let endPlace = '';
    if (d) {
      let orderedIds: string[] = [];
      if (d.track_segments && d.track_segments.length > 0) {
        for (const seg of d.track_segments) {
          for (const pid of seg.place_ids || []) orderedIds.push(pid);
        }
      } else if (d.places) {
        orderedIds = [...d.places]
          .sort((a: any, b: any) => (a.order ?? 0) - (b.order ?? 0))
          .map((pp: any) => pp.id);
      }
      if (orderedIds.length > 0) {
        const first = placeMap.get(orderedIds[0]);
        const last = placeMap.get(orderedIds[orderedIds.length - 1]);
        startPlace = first?.songName || '';
        endPlace = last?.songName || '';
      }
    }
    cfg[r.id] = {
      id: r.id,
      name: r.name,
      time: r.period || `${r.start_year}-${r.end_year}`,
      mainColor: r.unique_color || '#888',
      desc: r.description_short || '',
      startPlace,
      endPlace,
      stageId: r.stage_id,
    };
  }
  return cfg;
}

export function getV4RouteIds(): string[] {
  if (!_cache.routes) return [];
  return _cache.routes.map((r) => r.id).sort();
}
