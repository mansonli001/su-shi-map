/**
 * 贺野数据加载层（仅服务端）
 * SSR: 直接 fs.readFileSync 读取 JSON
 * 仅被 Server Component 引用，不进入客户端 bundle
 * JSON 字段为 snake_case，映射为 TypeScript camelCase
 */

import type { HeyeLocation, HeyeProvinceStatsMap, HeyeMeta } from '@/types/heye';
import { readFileSync } from 'fs';
import { join } from 'path';

const HEYE_DATA_DIR = join(process.cwd(), 'public', 'data-heye');

function readJsonFile<T>(filename: string): T {
  const raw = readFileSync(join(HEYE_DATA_DIR, filename), 'utf-8');
  return JSON.parse(raw);
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
export function getHeyeLocationsSSR(): HeyeLocation[] {
  const data = readJsonFile<{ locations: any[] }>('locations.json');
  return (data.locations ?? []).map(mapLocation);
}

/** 获取省份统计（着色用） */
export function getHeyeProvinceStatsSSR(): HeyeProvinceStatsMap {
  const data = readJsonFile<{ provinces: any }>('province-stats.json');
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
export function getHeyeMetaSSR(): HeyeMeta | null {
  try {
    const raw = readJsonFile<any>('meta.json');
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
  } catch {
    return null;
  }
}
