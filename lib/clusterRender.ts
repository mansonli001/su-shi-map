/**
 * 朱印圆章聚合渲染 v4.0
 * makeClusterRender() - 自定义聚合标记样式
 */

import type { PlaceType } from '@/types';

/**
 * 类型颜色映射（朱印风格）
 */
const TYPE_COLORS: Record<PlaceType, string> = {
  birth: '#4CAF50',    // 竹芽绿
  office: '#37474F',    // 黛青
  exile: '#C62828',     // 朱砂
  tour: '#6D4C41',      // 赭石
  friend: '#F9A825',     // 藤黄
  burial: '#424242',     // 墨灰
};

/**
 * 类型标签映射
 */
const TYPE_LABELS: Record<PlaceType, string> = {
  birth: '生',
  office: '官',
  exile: '谪',
  tour: '游',
  friend: '友',
  burial: '眠',
};

/**
 * 创建聚合渲染函数
 * 返回 (features) => AMap.Marker
 */
export function makeClusterRender(): (features: any[]) => any {
  return (features: any[]) => {
    const count = features.length;

    // 统计聚合内的类型分布
    const typeSet = new Set<string>();
    features.forEach((f) => {
      const type = f.properties?.type;
      if (type) typeSet.add(type);
    });

    // 颜色：单一类型用该类型颜色，多类型用朱印灰
    const color = typeSet.size === 1 ? TYPE_COLORS[typeSet.values().next().value as PlaceType] || '#8B6914' : '#8B6914';

    // 尺寸：根据聚合数量动态计算
    const size = Math.min(40 + count * 2, 80);

    // 创建 SVG HTML
    const html = `
      <div style="
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: ${color};
        opacity: 0.85;
        border: 2px solid rgba(255,255,255,0.9);
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: ${count > 99 ? '10px' : count > 9 ? '12px' : '14px'};
        font-weight: bold;
        font-family: 'Noto Serif SC', serif;
        cursor: pointer;
      ">${count > 9 ? '⋯' : count}</div>
    `;

    // 创建高德 Marker
    const marker = new (window as any).AMap.Marker({
      content: html,
      anchor: 'center',
      offset: new (window as any).AMap.Pixel(0, 0),
    });

    // 点击聚合标记，放大地图
    marker.on('click', () => {
      const map = (window as any).suShiMapInstance;
      if (map) {
        const bounds = new (window as any).AMap.Bounds();
        features.forEach((f) => {
          const coord = f.geometry?.coordinates;
          if (coord) bounds.extend(new (window as any).AMap.LngLat(coord[0], coord[1]));
        });
        map.setBounds(bounds, { padding: [50, 50, 50, 50] });
      }
    });

    return marker;
  };
}

/**
 * 创建单个地点标记的 HTML
 */
export function makeMarkerHtml(type: PlaceType, importance: 1 | 2 | 3): string {
  const color = TYPE_COLORS[type] || '#8B6914';
  const label = TYPE_LABELS[type] || '·';
  const size = importance === 1 ? 32 : importance === 2 ? 28 : 24;

  return `
    <div style="
      width: ${size}px;
      height: ${size * 1.375}px;
      position: relative;
      cursor: pointer;
    ">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 44" width="${size}" height="${size * 1.375}">
        <path d="M16 2C16 2 6 14 6 22a10 10 0 0020 0c0-8-10-20-10-20z" fill="${color}" stroke="#fff" stroke-width="1.5" opacity="0.9"/>
        <text x="16" y="${size > 28 ? 25 : 22}" text-anchor="middle" font-size="${size > 28 ? 10 : 8}" fill="#fff" font-weight="bold" font-family="Noto Serif SC">${label}</text>
      </svg>
    </div>
  `;
}
