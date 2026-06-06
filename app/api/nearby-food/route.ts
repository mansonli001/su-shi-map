/**
 * 附近美食搜索 — 服务端代理（AMap Web Service v3）
 *
 * 设计动机：
 *   旧实现走 JSAPI `AMap.PlaceSearch`，在浏览器侧不稳定（key 权限/域名白名单/配额/securityJsCode
 *   校验等都可能让 status!=='complete' 直接返回空数组，前端只能展示「连高德也沉默了」空状态）。
 *   迁移到服务端 Web Service：
 *     - key 不再暴露浏览器
 *     - 走 https://restapi.amap.com/v3/place/around，schema 稳定且配额充足
 *     - 服务端可以做兜底/重试/详细日志
 *
 * 安全：
 *   - 入参 lat/lng/radius 严格校验（数值/范围），拒绝越界输入（RULE3 路径/SSRF 防护一并兜住）
 *   - 仅访问固定的 https://restapi.amap.com 域名，禁绝用户控制 URL
 *   - AMAP_WEB_SERVICE_KEY 从 env 读取，缺失 fail-fast（RULE5）
 *   - 不在响应/日志里打印 key
 */

import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// 服务端缓存：同坐标 60s 内复用，减少高德调用
interface CacheItem {
  ts: number;
  body: unknown;
}
const CACHE_TTL = 60 * 1000;
const cache = new Map<string, CacheItem>();

function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

export async function GET(req: NextRequest) {
  const key = process.env.AMAP_WEB_SERVICE_KEY;
  if (!key) {
    return NextResponse.json(
      { error: 'AMAP_WEB_SERVICE_KEY not configured', pois: [] },
      { status: 500 },
    );
  }

  const sp = req.nextUrl.searchParams;
  const latRaw = sp.get('lat');
  const lngRaw = sp.get('lng');
  const radiusRaw = sp.get('radius');

  const lat = Number(latRaw);
  const lng = Number(lngRaw);
  let radius = Number(radiusRaw);

  // 入参校验（RULE3：严格校验，拒绝可疑值）
  if (
    !Number.isFinite(lat) ||
    !Number.isFinite(lng) ||
    lat < -90 ||
    lat > 90 ||
    lng < -180 ||
    lng > 180
  ) {
    return NextResponse.json({ error: 'invalid lat/lng', pois: [] }, { status: 400 });
  }
  if (!Number.isFinite(radius) || radius <= 0) radius = 2000;
  radius = clamp(Math.round(radius), 100, 5000); // 高德支持 0-50000，我们收口到 5km

  // 4 位精度做缓存 key（≈11m）
  const cacheKey = `${lat.toFixed(4)}_${lng.toFixed(4)}_${radius}`;
  const hit = cache.get(cacheKey);
  if (hit && Date.now() - hit.ts < CACHE_TTL) {
    return NextResponse.json(hit.body, {
      headers: { 'Cache-Control': 'public, max-age=60, s-maxage=60' },
    });
  }

  // 用 URLSearchParams 拼，绝不用字符串拼接（防注入/编码错误）
  const params = new URLSearchParams({
    key,
    location: `${lng},${lat}`, // 高德要求 lng,lat 顺序
    types: '050000', // 餐饮服务大类
    radius: String(radius),
    extensions: 'all',
    offset: '20',
    page: '1',
    output: 'JSON',
  });
  const url = `https://restapi.amap.com/v3/place/around?${params.toString()}`;

  // 5s 超时，防止上游卡死把我们的函数撑爆
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 5000);
  try {
    const resp = await fetch(url, {
      signal: ctrl.signal,
      // Vercel Node 运行时默认会跟随 redirect，这里禁掉以防 SSRF（RULE4）
      redirect: 'manual',
      headers: { Accept: 'application/json' },
    });
    if (!resp.ok) {
      return NextResponse.json(
        { error: `amap http ${resp.status}`, pois: [] },
        { status: 502 },
      );
    }
    const data: unknown = await resp.json();
    const pois = normalizePois(data);
    const body = { pois, count: pois.length };
    cache.set(cacheKey, { ts: Date.now(), body });
    return NextResponse.json(body, {
      headers: { 'Cache-Control': 'public, max-age=60, s-maxage=60' },
    });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json(
      { error: 'amap request failed', detail: msg, pois: [] },
      { status: 502 },
    );
  } finally {
    clearTimeout(timer);
  }
}

// ── 高德返回体规整 ──────────────────────────────────────────────
interface AmapWebPoi {
  id?: string;
  name?: string;
  type?: string;
  address?: string | unknown[];
  tel?: string | unknown[];
  distance?: string | number;
  location?: string; // "lng,lat"
  photos?: { url?: string }[] | unknown;
  biz_ext?: { rating?: string | number } | unknown;
}

interface NormalizedPoi {
  id: string;
  name: string;
  type: string;
  address: string;
  location: { lat: number; lng: number };
  distance?: number;
  rating?: number;
  photos?: string[];
  tel?: string;
  categories?: string[];
  comment_count?: string;
}

function asStr(v: unknown): string {
  if (v == null) return '';
  if (Array.isArray(v)) return v.length > 0 ? String(v[0]) : '';
  return String(v);
}

function normalizePois(raw: unknown): NormalizedPoi[] {
  if (!raw || typeof raw !== 'object') return [];
  const r = raw as { status?: string; pois?: AmapWebPoi[] };
  // status === '1' 表示成功；其他状态（'0'+infocode）我们一律视作无结果
  if (r.status !== '1' || !Array.isArray(r.pois)) return [];

  return r.pois
    .map((p): NormalizedPoi | null => {
      const locStr = asStr(p.location);
      const [lngStr, latStr] = locStr.split(',');
      const lng = parseFloat(lngStr);
      const lat = parseFloat(latStr);
      if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null;

      const typeStr = asStr(p.type);
      const categories = typeStr
        .split(/[;；]/)
        .map((s) => s.trim())
        .filter(Boolean);

      const photosArr =
        Array.isArray(p.photos) && p.photos.length > 0
          ? (p.photos as { url?: string }[])
              .map((ph) => asStr(ph?.url))
              .filter(Boolean)
          : undefined;

      const ratingRaw =
        p.biz_ext && typeof p.biz_ext === 'object'
          ? (p.biz_ext as { rating?: string | number }).rating
          : undefined;
      const ratingNum =
        ratingRaw === undefined || ratingRaw === null || ratingRaw === ''
          ? undefined
          : Number.isFinite(Number(ratingRaw)) && Number(ratingRaw) > 0
            ? Number(ratingRaw)
            : undefined;

      const distanceNum = (() => {
        const n = Number(p.distance);
        return Number.isFinite(n) ? Math.round(n) : undefined;
      })();

      // photos 数量代理"热度"（高德 Web Service 也不直接返回评论数）
      const photosCount = photosArr ? photosArr.length : 0;

      return {
        id: asStr(p.id),
        name: asStr(p.name),
        type: typeStr,
        address: asStr(p.address),
        location: { lat, lng },
        distance: distanceNum,
        rating: ratingNum,
        photos: photosArr,
        tel: asStr(p.tel) || undefined,
        categories,
        comment_count: String(photosCount),
      };
    })
    .filter((x): x is NormalizedPoi => x !== null);
}
