/**
 * 贺野数据加载层（客户端）
 * CSR: fetch 静态 JSON
 * JSON 字段为 snake_case，映射为 TypeScript camelCase
 */

import type { HeyeLocation, HeyeProvinceStatsMap, HeyeMeta } from '@/types/heye';

const HEYE_BASE = '/data-heye';

/** CSR: fetch 静态 JSON */
async function fetchJson<T>(filename: string): Promise<T> {
  const url = `${HEYE_BASE}/${filename}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`);
  return res.json();
}

/** snake_case → camelCase 映射 */
function mapLocation(raw: any): HeyeLocation {
  return {
    id: raw.id,
    province: raw.province,
    city: raw.city,
    placeName: raw.place_name,
    fullName: raw.full_name,
    region: raw.region,
    lat: raw.lat,
    lng: raw.lng,
    coordinateSource: raw.coordinate_source,
    visitDate: raw.visit_date ?? null,
    visitYear: raw.visit_year ?? null,
    tripTag: raw.trip_tag ?? null,
    excerpt: raw.excerpt,
    snacks: raw.snacks ?? [],
    imageUrl: raw.image_url ?? '',
    articleUrl: raw.article_url ?? '',
    sourceTitle: raw.source_title ?? '',
    featured: raw.featured ?? false,
    visitCount: raw.visit_count ?? 1,
    visitHistory: (() => {
      const vh = raw.visit_history;
      if (Array.isArray(vh)) return vh.join('、');
      if (typeof vh === 'string' && vh.startsWith('[')) {
        try { return JSON.parse(vh).join('、'); } catch { return vh; }
      }
      return vh ?? '';
    })(),
  };
}

/** 获取贺野全量地点索引 */
export async function getHeyeLocations(): Promise<HeyeLocation[]> {
  const data = await fetchJson<{ locations: any[] }>('locations.json');
  return (data.locations ?? []).map(mapLocation);
}

/** 获取单个贺野地点详情 */
export async function getHeyeLocation(id: string): Promise<HeyeLocation | null> {
  const locations = await getHeyeLocations();
  return locations.find((loc) => loc.id === id) ?? null;
}

/** 获取省份统计（着色用） */
export async function getHeyeProvinceStats(): Promise<HeyeProvinceStatsMap> {
  const data = await fetchJson<{ provinces: any }>('province-stats.json');
  const provinces: HeyeProvinceStatsMap = {};
  for (const [key, val] of Object.entries(data.provinces ?? {})) {
    const v = val as any;
    provinces[key] = {
      placeCount: v.place_count,
      cityCount: v.city_count,
      placeIds: v.place_ids,
      densityTier: v.density_tier,
    };
  }
  return provinces;
}

/** 获取全局元信息（首页统计） */
export async function getHeyeMeta(): Promise<HeyeMeta | null> {
  const raw = await fetchJson<any>('meta.json');
  if (!raw) return null;
  return {
    schemaVersion: raw.schema_version,
    generatedAt: raw.generated_at,
    dataSource: raw.data_source,
    disclaimer: raw.disclaimer,
    stats: {
      totalPlaces: raw.stats?.total_places,
      provinceCount: raw.stats?.province_count,
      cityCount: raw.stats?.city_count,
      snackVariety: raw.stats?.snack_variety,
      articleCount: raw.stats?.article_count,
      tripCount: raw.stats?.trip_count,
      featuredCount: raw.stats?.featured_count,
    },
  };
}

/** 获取精选地点（首页轮播用） */
export async function getFeaturedHeyeLocations(): Promise<HeyeLocation[]> {
  const locations = await getHeyeLocations();
  return locations.filter((loc) => loc.featured);
}

/** 按 tripTag 筛选地点 */
export async function getHeyeLocationsByTrip(tag: string): Promise<HeyeLocation[]> {
  const locations = await getHeyeLocations();
  return locations.filter((loc) => loc.tripTag === tag);
}
