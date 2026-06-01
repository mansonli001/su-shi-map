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
 * 高德 JSAPI 2.0 renderClusterMarker 回调签名：
 *   renderClusterMarker(context: { marker, markers, count })
 * 正确做法：修改 context.marker（setContent/setOffset），不返回新 Marker
 */
export function makeClusterRender(): (context: any) => void {
  return (context: any) => {
    const AMap = (window as any).AMap;
    console.log('[clusterRender] 回调被调用', { hasMarker: !!context?.marker, count: context?.count, markerCount: context?.markers?.length });
    if (!AMap || !context?.marker) {
      console.error('[clusterRender] 缺少 AMap 或 context.marker');
      return;
    }

    const markers: any[] = context.markers || [];
    const count = context.count ?? markers.length;

    // 从聚合标记的 extData 中统计类型分布
    const typeSet = new Set<string>();
    markers.forEach((m: any) => {
      const place = m.getExtData?.() || {};
      const type = place?.type;
      if (type) typeSet.add(type);
    });

    // 颜色：单一类型用该类型颜色，多类型用朱印灰
    let dominantType: PlaceType | null = null;
    if (typeSet.size === 1) {
      for (const t of typeSet) { dominantType = t as PlaceType; break; }
    }
    const color = dominantType ? TYPE_COLORS[dominantType] || '#8B6914' : '#8B6914';

    // 尺寸：根据聚合数量动态计算
    const size = Math.min(40 + count * 2, 80);

    // 创建 HTML（修复 rgba 空格问题）
    const html = `
      <div style="
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: ${color};
        opacity: 0.85;
        border: 2px solid rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: ${count > 99 ? '10px' : count > 9 ? '12px' : '14px'};
        font-weight: bold;
        font-family: 'Noto Serif SC', serif;
        cursor: pointer;
        user-select: none;
      ">${count > 9 ? '⋯' : count}</div>
    `;

    // ★ 正确：修改 context.marker，不返回新 Marker
    context.marker.setContent(html);
    context.marker.setOffset(new AMap.Pixel(0, -size / 2));

    // 点击聚合标记，放大地图
    context.marker.on('click', () => {
      const map = (window as any).suShiMapInstance;
      if (map && AMap && AMap.Bounds && AMap.LngLat) {
        const bounds = new AMap.Bounds();
        markers.forEach((m: any) => {
          const place = m.getExtData?.() || {};
          const coord = place?.lng != null ? [place.lng, place.lat] : null;
          if (coord) bounds.extend(new AMap.LngLat(coord[0], coord[1]));
        });
        if (bounds.isEmpty?.() === false) {
          map.setBounds(bounds, { padding: [50, 50, 50, 50] });
        }
      }
    });
  };
}

/**
 * 创建单个地点标记的 HTML
 * v1.4：文字垂直居中 + 基础尺寸再加大 + viewBox 适配
 */
export function makeMarkerHtml(type: PlaceType, importance: 1 | 2 | 3): string {
  const color = TYPE_COLORS[type] || '#8B6914';
  const label = TYPE_LABELS[type] || '·';
  // ★ 基础尺寸再加大（全图可见 + zoom 缩放空间）
  const size = importance === 1 ? 28 : importance === 2 ? 25 : 22;

  return `
    <div style="
      width: ${size}px;
      height: ${Math.round(size * 1.375)}px;
      position: relative;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 44" width="${size}" height="${Math.round(size * 1.375)}">
        <!-- 尖头向下：rotate(180deg) 绕中心点(16,22)旋转 -->
        <g transform="rotate(180, 16, 22)">
          <path d="M16 2C16 2 6 14 6 22a10 10 0 0020 0c0-8-10-20-10-20z" fill="${color}" stroke="#fff" stroke-width="1.5" opacity="0.9"/>
        </g>
        <!-- alignment-baseline:middle 让文字中心线与 y 对齐（兼容性更好） -->
        <text x="16" y="22" text-anchor="middle" alignment-baseline="middle"
              font-size="11"
              fill="#fff" font-weight="bold" font-family="Noto Serif SC">${label}</text>
      </svg>
    </div>
  `;
}
