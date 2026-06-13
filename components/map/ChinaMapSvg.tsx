'use client';

import { useEffect, useState, useMemo } from 'react';

interface ProvinceFeature {
  name: string;
  shortName: string;
  d: string;
  cx: number;
  cy: number;
}

interface ChinaMapGeoProps {
  litProvinces: Set<string>;
  onProvinceClick?: (name: string) => void;
}

// 省份全名 -> 简称映射
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

// Mercator投影（简化版，适合中国区域）
function project(lng: number, lat: number, w: number, h: number): [number, number] {
  const centerLng = 104;
  const centerLat = 35;
  const scale = w / 75; // 约75度经度范围

  const x = (lng - centerLng) * scale + w / 2;
  const y = (centerLat - lat) * scale + h / 2;
  return [x, y];
}

// 将GeoJSON坐标转为SVG path
function coordsToPath(coords: number[][][], w: number, h: number): string {
  const parts: string[] = [];
  for (const ring of coords) {
    for (let i = 0; i < ring.length; i++) {
      const [x, y] = project(ring[i][0], ring[i][1], w, h);
      parts.push(i === 0 ? `M${x.toFixed(1)},${y.toFixed(1)}` : `L${x.toFixed(1)},${y.toFixed(1)}`);
    }
    parts.push('Z');
  }
  return parts.join(' ');
}

function multiCoordsToPath(coords: number[][][][], w: number, h: number): string {
  return coords.map(c => coordsToPath(c, w, h)).join(' ');
}

export default function ChinaMapGeo({ litProvinces, onProvinceClick }: ChinaMapGeoProps) {
  const [provinces, setProvinces] = useState<ProvinceFeature[]>([]);

  useEffect(() => {
    fetch('/data-heye/china-provinces.json')
      .then(r => r.json())
      .then(data => {
        const w = 600;
        const h = 500;
        const features: ProvinceFeature[] = [];

        for (const f of data.features) {
          const fullName = f.properties.name;
          const shortName = NAME_MAP[fullName] || fullName;
          const geom = f.geometry;

          let d = '';
          if (geom.type === 'Polygon') {
            d = coordsToPath(geom.coordinates, w, h);
          } else if (geom.type === 'MultiPolygon') {
            d = multiCoordsToPath(geom.coordinates, w, h);
          }

          // 计算中心点（使用properties中的center或centroid）
          const center = f.properties.center || f.properties.centroid;
          let cx = w / 2, cy = h / 2;
          if (center) {
            [cx, cy] = project(center[0], center[1], w, h);
          }

          if (d) {
            features.push({ name: shortName, d, cx, cy });
          }
        }
        setProvinces(features);
      })
      .catch(console.error);
  }, []);

  return (
    <svg
      viewBox="0 0 600 500"
      xmlns="http://www.w3.org/2000/svg"
      className="he-china-svg"
      style={{ width: '100%', height: 'auto' }}
    >
      {provinces.map((p) => {
        const isLit = litProvinces.has(p.name);
        return (
          <g key={p.name} onClick={() => onProvinceClick?.(p.name)} style={{ cursor: 'pointer' }}>
            <path
              d={p.d}
              fill={isLit ? '#C4612A' : '#e8ddd2'}
              stroke={isLit ? '#8C3A18' : '#c4b5a5'}
              strokeWidth={isLit ? 1.2 : 0.5}
              style={{ transition: 'fill 0.4s ease, stroke 0.3s ease' }}
            />
            <text
              x={p.cx}
              y={p.cy}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize={p.name.length > 2 ? 6 : 7}
              fontWeight={isLit ? 700 : 500}
              fill={isLit ? '#fff' : '#6b5c4e'}
              style={{ pointerEvents: 'none', transition: 'fill 0.3s ease' }}
            >
              {p.name}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
