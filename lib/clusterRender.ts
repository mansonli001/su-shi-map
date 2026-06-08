/**
 * 朱印圆章聚合渲染 v5.0
 * makeClusterRender() - 自定义聚合标记样式
 * makeMarkerHtml(designType, importance) - 单个 SVG marker（设计稿 8 类）
 */

import type { PlaceType, DesignPlaceType } from '@/types';

/**
 * 类型颜色映射（朱印风格 + v4 10类）
 */
const TYPE_COLORS: Record<string, string> = {
  birth: '#388E3C',    // 竹芽绿
  office: '#37474F',    // 黛青
  exile: '#C62828',     // 朱砂
  tour: '#6D4C41',      // 赭石
  friend: '#F9A825',     // 藤黄
  burial: '#424242',     // 墨灰
  // v4 新增类型
  main: '#8B5A2B',      // 棕色（行经）
  sight: '#1A7A6A',     // 青绿（观景）
  around: '#A67528',    // 藤黄棕（寻访）
  official: '#9E2A1E',  // 朱砂红（官守）
  stay: '#6A468A',      // 紫色（客居）
  visit: '#148170',     // 深青绿（游览）
  study: '#5D4037',     // 赭褐（游学）
  death: '#455A64',     // 铁灰（离世）
  tomb: '#3E2723',      // 深褐（墓葬）
};

/**
 * 类型标签映射
 */
const TYPE_LABELS: Record<string, string> = {
  birth: '生',
  office: '官',
  exile: '谪',
  tour: '游',
  friend: '友',
  burial: '眠',
  main: '行',
  sight: '景',
  around: '访',
  official: '官',
  stay: '居',
  visit: '游',
  study: '学',
  death: '逝',
  tomb: '墓',
};

/**
 * 创建聚合渲染函数 v4.1
 * 高德 JSAPI 2.0 renderClusterMarker 回调签名：
 *   renderClusterMarker(context: { marker, markers, count })
 * 正确做法：修改 context.marker（setContent/setOffset），不返回新 Marker
 *
 * v4.1: 移除 window.suShiMapInstance 全局污染，改为通过 getMap 闭包注入。
 */
export function makeClusterRender(getMap: () => any | null): (context: any) => void {
  return (context: any) => {
    const AMap = (window as any).AMap;
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
      const map = getMap();
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
 * 单个地点标记 HTML v5.0：使用设计稿 9 张专属 SVG（按 designType 选）
 *
 * 尺寸规范（设计稿 §2.4）：
 *   visit / stay / official  → 30px（重点点位）
 *   main                       → 22px（主线行进）
 *   其他（birth/study/death/tomb） → 24px
 *
 * 交互：
 *   - hover：放大 1.10×（CSS）
 *   - 选中：外层柔光晕（drop-shadow 由组件层控制 marker.classList）
 *
 * 兼容：第二参数仍接受 PlaceType（v3 老调用），但实际不影响视觉，
 *      只要传入 DesignPlaceType 就走新 SVG。
 */
export function makeMarkerHtml(
  designType: DesignPlaceType | PlaceType,
  importance: 1 | 2 | 3 = 2,
  isCheckedIn: boolean = false,
): string {
  const t = String(designType || '').toLowerCase();

  // 老 PlaceType 兜底映射 → 新 DesignPlaceType
  const mappedType: DesignPlaceType = ([
    'main', 'visit', 'stay', 'study', 'birth', 'official', 'death', 'tomb', 'sight', 'around',
  ] as const).includes(t as DesignPlaceType)
    ? (t as DesignPlaceType)
    : t === 'office'
      ? 'official'
      : t === 'burial'
        ? 'tomb'
        : t === 'exile'
          ? 'sight'
          : t === 'tour' || t === 'friend'
            ? 'visit'
            : 'visit';

  // §2.4 尺寸规则
  // 关键节点（当官 official / 居住 stay）30px 突出
  // 途经景观 sight 26px（比普通大一点，突出观景属性）
  // 周边寻访 around 22px（最小，辅助信息）
  // 主线行进 main 22px
  let size = 24;
  if (mappedType === 'official' || mappedType === 'stay') size = 30;  // 关键节点
  else if (mappedType === 'sight') size = 26;                          // 途经景观
  else if (mappedType === 'main') size = 22;                           // 主线行进
  else if (mappedType === 'around') size = 22;                         // 周边寻访
  else size = 24;                                                       // visit/birth/study/death/tomb

  // 重要度微调（importance=1 主推 +2px / 3=灰度 -2px）
  if (importance === 1) size += 2;
  else if (importance === 3) size = Math.max(18, size - 2);

  const w = size;
  const h = Math.round(size * 1.25); // 48:60 = 1:1.25
  const url = `/markers/marker-${mappedType}.svg`;

  // 已打卡高亮效果
  const checkinStyle = isCheckedIn ? `
    filter: drop-shadow(0 0 8px rgba(74, 124, 98, 0.8)) brightness(1.1);
  ` : `
    filter: drop-shadow(0 2px 3px rgba(0,0,0,0.25));
  `;

  return `
    <div class="su-marker su-marker--${mappedType} ${isCheckedIn ? 'su-marker--checked' : ''}" data-type="${mappedType}" data-checked="${isCheckedIn}" style="
      width: ${w}px;
      height: ${h}px;
      position: relative;
      cursor: pointer;
      ${checkinStyle}
      will-change: transform, filter;
      transition: transform 0.18s ease-out, filter 0.18s ease-out;
    ">
      <img src="${url}" alt="${mappedType}" draggable="false"
           style="width:100%;height:100%;display:block;pointer-events:none;user-select:none;" />
      ${isCheckedIn ? `
      <div style="
        position: absolute;
        top: -4px;
        right: -4px;
        width: 12px;
        height: 12px;
        background: #4A7C62;
        border: 2px solid #fff;
        border-radius: 50%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
      "></div>
      ` : ''}
    </div>
  `;
}
