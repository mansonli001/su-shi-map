'use client';

import { useEffect, useState } from 'react';

// ─── 类型 ────────────────────────────────────────────────────────────────────

interface ProvinceFeature {
  name: string;
  d: string;
  cx: number;
  cy: number;
  viewBox: string;
}

interface ChinaMapMaskProps {
  litProvinces: Set<string>;
  onProvinceClick?: (name: string) => void;
  className?: string;
}

// ─── 省份全名映射 ─────────────────────────────────────────────────────────────

const NAME_MAP: Record<string, string> = {
  '北京市': '北京', '天津市': '天津', '河北省': '河北', '山西省': '山西',
  '内蒙古自治区': '内蒙古', '辽宁省': '辽宁', '吉林省': '吉林', '黑龙江省': '黑龙江',
  '上海市': '上海', '江苏省': '江苏', '浙江省': '浙江', '安徽省': '安徽',
  '福建省': '福建', '江西省': '江西', '山东省': '山东', '河南省': '河南',
  '湖北省': '湖北', '湖南省': '湖南', '广东省': '广东', '广西壮族自治区': '广西',
  '海南省': '海南', '重庆市': '重庆', '四川省': '四川', '贵州省': '贵州',
  '云南省': '云南', '西藏自治区': '西藏', '陕西省': '陕西', '甘肃省': '甘肃',
  '青海省': '青海', '宁夏回族自治区': '宁夏', '新疆维吾尔自治区': '新疆',
  '台湾省': '台湾', '香港特别行政区': '香港', '澳门特别行政区': '澳门',
};

// ─── 统一配色（苏轼暖色系）─────────────────────────────────────────────────

const LIT_FILL = '#C4612A';   // 暖橙主色
const LIT_STROKE = '#A04818'; // 深橙描边
const UNLIT_FILL = '#E8E0D4'; // 米色
const UNLIT_STROKE = '#C8C0B0'; // 灰棕描边

// ─── 投影：包围盒归一化 ──────────────────────────────────────────────────────

const MAP_W = 900;
const MAP_H = 720;
const MAP_PAD = 24;

let _projReady = false;
let _minLng = 0, _maxLng = 0, _minLat = 0, _maxLat = 0, _scale = 1;

interface GeoJSONGeometry {
  type: 'Polygon' | 'MultiPolygon';
  coordinates: number[][][][] | number[][][];
}

interface GeoJSONFeature {
  type: 'Feature';
  properties: { name: string; center?: number[]; centroid?: number[] };
  geometry: GeoJSONGeometry;
}

function initProjection(features: GeoJSONFeature[]) {
  if (_projReady) return;
  const allCoords: number[][] = [];
  for (const f of features) {
    const g = f.geometry;
    if (g.type === 'Polygon') {
      allCoords.push(...(g.coordinates as number[][][])[0]);
    } else if (g.type === 'MultiPolygon') {
      (g.coordinates as number[][][][]).forEach((p) => allCoords.push(...p[0]));
    }
  }
  _minLng = Math.min(...allCoords.map(c => c[0]));
  _maxLng = Math.max(...allCoords.map(c => c[0]));
  _minLat = Math.min(...allCoords.map(c => c[1]));
  _maxLat = Math.max(...allCoords.map(c => c[1]));
  const sx = (MAP_W - MAP_PAD * 2) / (_maxLng - _minLng);
  const sy = (MAP_H - MAP_PAD * 2) / (_maxLat - _minLat);
  _scale = Math.min(sx, sy);
  _projReady = true;
}

function proj(lng: number, lat: number): [number, number] {
  return [
    MAP_PAD + (lng - _minLng) * _scale,
    MAP_H - MAP_PAD - (lat - _minLat) * _scale,
  ];
}

function ringToD(ring: number[][]): string {
  return ring.map((c, i) => {
    const [x, y] = proj(c[0], c[1]);
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ') + 'Z';
}

function geomToD(geometry: GeoJSONGeometry): string {
  if (geometry.type === 'Polygon') {
    return (geometry.coordinates as number[][][]).map(ringToD).join(' ');
  } else if (geometry.type === 'MultiPolygon') {
    return (geometry.coordinates as number[][][][]).map(poly => poly.map(ringToD).join(' ')).join(' ');
  }
  return '';
}

function computeCenter(geometry: GeoJSONGeometry): [number, number] {
  let ring: number[][] = [];
  if (geometry.type === 'Polygon') {
    ring = geometry.coordinates[0] as number[][];
  } else if (geometry.type === 'MultiPolygon') {
    let maxLen = 0;
    for (const poly of geometry.coordinates as number[][][][]) {
      if (poly[0].length > maxLen) { maxLen = poly[0].length; ring = poly[0]; }
    }
  }
  const lng = ring.reduce((s, c) => s + c[0], 0) / ring.length;
  const lat = ring.reduce((s, c) => s + c[1], 0) / ring.length;
  return proj(lng, lat);
}

function computeViewBox(geometry: GeoJSONGeometry): string {
  const pts: number[][] = [];
  if (geometry.type === 'Polygon') {
    pts.push(...(geometry.coordinates[0] as number[][]));
  } else if (geometry.type === 'MultiPolygon') {
    (geometry.coordinates as number[][][][]).forEach(p => pts.push(...p[0]));
  }
  const projected = pts.map(c => proj(c[0], c[1]));
  const xs = projected.map(p => p[0]);
  const ys = projected.map(p => p[1]);
  const minX = Math.min(...xs) - 4;
  const minY = Math.min(...ys) - 4;
  const w = Math.max(...xs) - minX + 8;
  const h = Math.max(...ys) - minY + 8;
  return `${minX.toFixed(1)} ${minY.toFixed(1)} ${w.toFixed(1)} ${h.toFixed(1)}`;
}

// ─── 组件：整体地图 ───────────────────────────────────────────────────────────

export default function ChinaMapMask({ litProvinces, onProvinceClick, className }: ChinaMapMaskProps) {
  return (
    <div className={`he-china-map-svg-wrapper ${className ?? ''}`}>
      <img
        src="/heye-map/china-map-lit.png"
        alt="贺野足迹 · 中国地图"
        width={900}
        height={720}
        decoding="async"
        loading="lazy"
        style={{
          display: 'block',
          width: '100%',
          height: 'auto',
          objectFit: 'contain',
          margin: '0 auto',
          opacity: litProvinces.size > 0 ? 1 : 0.6,
          transition: 'opacity 0.5s ease',
        }}
      />
    </div>
  );
}

// ─── 导出：单省缩略图（SVG路径版，用于成就卡）─────────────────────────────────

interface ProvinceThumbProps {
  name: string;
  lit: boolean;
  provinces: ProvinceFeature[];
  size?: number;
}

export function ProvinceThumb({ name, lit, provinces, size = 80 }: ProvinceThumbProps) {
  const p = provinces.find(f => f.name === name);

  if (!p) {
    return (
      <svg width={size} height={size} viewBox="0 0 80 80">
        <rect x="4" y="4" width="72" height="72" rx="8"
          fill={lit ? LIT_FILL : UNLIT_FILL} stroke={lit ? LIT_STROKE : UNLIT_STROKE} strokeWidth="1.5" />
        <text x="40" y="44" textAnchor="middle" dominantBaseline="central"
          fontSize="14" fontFamily="sans-serif" fill={lit ? '#fff' : '#8A7A6A'}>
          {name}
        </text>
      </svg>
    );
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox={p.viewBox}
      style={{ display: 'block' }}
    >
      <path
        d={p.d}
        fill={lit ? LIT_FILL : UNLIT_FILL}
        stroke={lit ? LIT_STROKE : UNLIT_STROKE}
        strokeWidth={lit ? 2 : 1}
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── 导出：成就卡网格 ──────────────────────────────────────────────────────

interface ProvinceAchievementGridProps {
  litProvinces: Set<string>;
  checkinCounts: Record<string, number>;
  threshold?: number;
  onCardClick?: (name: string) => void;
}

const ALL_PROVINCES_ORDERED = [
  '河北','山西','内蒙古',
  '辽宁','吉林','黑龙江',
  '江苏','浙江','安徽','福建','江西','山东',
  '河南','湖北','湖南','广东','广西','海南',
  '四川','贵州','云南',
  '西藏','陕西','甘肃','青海','宁夏','新疆',
];

export function ProvinceAchievementGrid({
  litProvinces,
  checkinCounts,
  threshold = 3,
  onCardClick,
}: ProvinceAchievementGridProps) {
  const [provinces, setProvinces] = useState<ProvinceFeature[]>([]);

  useEffect(() => {
    fetch('/data-heye/china-provinces.json')
      .then(r => r.json())
      .then(data => {
        initProjection(data.features);
        const features: ProvinceFeature[] = [];
        for (const f of data.features) {
          const name = NAME_MAP[f.properties.name] || f.properties.name;
          const d = geomToD(f.geometry);
          if (!d) continue;
          const [cx, cy] = computeCenter(f.geometry);
          const viewBox = computeViewBox(f.geometry);
          features.push({ name, d, cx, cy, viewBox });
        }
        setProvinces(features);
      })
      .catch(console.error);
  }, []);

  if (provinces.length === 0) return null;

  return (
    <div className="he-province-cards-grid">
      {ALL_PROVINCES_ORDERED.map((name) => {
        const isLit = litProvinces.has(name);
        const count = checkinCounts[name] ?? 0;
        const progress = Math.min(count / threshold, 1);

        return (
          <div
            key={name}
            className={`he-province-card ${isLit ? 'lit' : ''}`}
            onClick={() => onCardClick?.(name)}
          >
            <div className="he-province-card-inner">
              {/* 正面：未点亮 */}
              <div className="he-province-card-front" style={{ background: '#FBF7F4' }}>
                <ProvinceThumb name={name} lit={false} provinces={provinces} size={80} />
                <div className="he-province-card-name">{name}</div>
                <div className="he-province-card-progress-track">
                  <div
                    className="he-province-card-progress-bar"
                    style={{ width: `${Math.round(progress * 100)}%`, background: LIT_FILL }}
                  />
                </div>
                <div className="he-province-card-count" style={{ color: '#8C6A58' }}>
                  {count}/{threshold}
                </div>
              </div>
              {/* 背面：已点亮 */}
              <div
                className="he-province-card-back"
                style={{ background: LIT_FILL, borderColor: LIT_STROKE }}
              >
                <ProvinceThumb name={name} lit={true} provinces={provinces} size={80} />
                <div className="he-province-card-name" style={{ color: '#fff' }}>
                  {name}
                </div>
                <div className="he-province-card-unlocked" style={{ color: '#fff', opacity: 0.85 }}>
                  已解锁
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
