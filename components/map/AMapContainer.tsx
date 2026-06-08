/**
 * AMapContainer v4.1
 *
 * 本轮（P0）变更：
 * - 删除未启用的死代码：fetchRealRoutePath / createDashedArrowOverlays
 * - 删除黑色调试面板 (#map-debug-logs) + 全局 logs/log 累积器
 * - 删除 window.suShiMapInstance 全局污染（cluster 回调改为 getMap 闭包）
 * - 加载逻辑统一收口到 lib/amap-loader 单例
 * - 调试输出改为 logger.debug，生产模式不打印
 *
 * 行为契约保持不变：
 * - marker 点击 → setSelectedPlace
 * - 19 路线 overview / 单条切换
 * - zoom 缩放 marker
 * - currentStage 过滤 marker 显隐
 *
 * 下一轮（hooks-refactor）会把 6 个 useEffect 拆为
 *   useAMapInit / useMarkers / useRouteOverlay / useMarkerScale。
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore } from '@/types';
import { makeMarkerHtml } from '@/lib/clusterRender';
import {
  ROUTE19_CONFIG,
  ROUTE19_IDS,
  getRoute19Points,
  buildRoutes19FromPlaces,
  setRoute19PointsCache,
} from '@/lib/route19-config';
import { makeHandDrawnPath } from '@/lib/route-utils';
import { loadAMap } from '@/lib/amap-loader';
import { logger } from '@/lib/logger';

export default function AMapContainer() {
  const { places, setSelectedPlace, selectedPlace, currentStage, setMapRef, currentRoute, checkinPlaces, isPlaceCheckedIn } = useSuShiStore();
  const onSelectPlace = setSelectedPlace;

  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const clusterRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [isMapReady, setIsMapReady] = useState(false);

  // 存储所有路线的 polyline 引用 { routeId: { polyline } }
  const routeOverlaysRef = useRef<Record<string, { polyline: any }>>({});

  // ── Effect 1: 等待 AMap 全局对象就绪，然后初始化地图 ──────────────────
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let destroyed = false;

    function initMap(AMap: any) {
      if (destroyed || mapRef.current) return;
      try {
        // 计算底部安全边距（底部导航高度 + 系统安全区）
        const bottomNavHeight = 70; // px
        const safeAreaBottom = parseInt(window.getComputedStyle(document.documentElement).getPropertyValue('--safe-area-bottom')) || 0;
        const totalBottomPadding = bottomNavHeight + safeAreaBottom;

        const map = new AMap.Map(containerRef.current, {
          zoom: 5,
          center: [104.5, 32.0],
          viewMode: '2D',
          zoomControl: true,
          scaleControl: false,
          toolBarControl: false,
          // 行吟山河自定义样式（米白宣纸 + 淡金路网 + POI 全关）
          mapStyle: 'amap://styles/5bcb375541c22ed25703103920a7d5e8',
          // 设置地图内边距，避免控件被底部导航遮挡
          viewPadding: [0, 0, totalBottomPadding, 0],
        });
        mapRef.current = map;
        setMapRef(map);
        setIsMapReady(true);
        logger.info('AMap map instance ready (style: 行吟山河 v1)');
      } catch (err: any) {
        logger.error('地图初始化异常', err?.message || err);
      }
    }

    // 走单例 loader（已处理已加载/未加载/事件错过等场景）
    loadAMap()
      .then((AMap) => {
        if (!destroyed && AMap?.Map) initMap(AMap);
      })
      .catch((err) => {
        logger.error('AMap loader 失败', err?.message || err);
      });

    return () => {
      destroyed = true;
      if (clusterRef.current) {
        clusterRef.current.setMap(null);
        clusterRef.current = null;
      }
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
    };
  }, [setMapRef]);

  // ── Effect 2: 创建/更新标记 ─────────────────────────────────
  useEffect(() => {
    if (!isMapReady || !mapRef.current || !places.length) return;

    try {
      if (clusterRef.current) {
        clusterRef.current.setMap(null);
        clusterRef.current = null;
      }
      markersRef.current.forEach((m) => m.setMap(null));
      markersRef.current = [];

      const AMapLocal = (window as any).AMap;
      const map = mapRef.current;
      if (!AMapLocal || !AMapLocal.LngLat) {
        logger.error('AMap.LngLat 不可用');
        return;
      }

      const markers = places.map((place) => {
        if (place.lng == null || place.lat == null) {
          logger.error('坐标无效:', place.id);
          return null;
        }

        const position = new AMapLocal.LngLat(place.lng, place.lat);
        const wrapper = document.createElement('div');
        // v5：用 designType（v4 真实 8 类）选择 SVG；老 type 自动兜底
        const dt = (place as any).designType || place.type;
        const checkedIn = isPlaceCheckedIn(place.id);
        wrapper.innerHTML = makeMarkerHtml(dt, place.importance, checkedIn);
        const markerEl = wrapper.firstElementChild as HTMLElement | null;
        if (markerEl) {
          markerEl.style.transformOrigin = 'bottom center';
          markerEl.dataset.placeId = place.id;
          markerEl.dataset.routeId = place.routeId || '';
          markerEl.dataset.checkedIn = String(checkedIn);
        }

        const marker = new AMapLocal.Marker({
          position,
          content: markerEl || makeMarkerHtml(dt, place.importance, checkedIn),
          anchor: 'bottom-center',
          extData: place,
        });

        marker.on('click', () => onSelectPlace(place));
        return marker;
      });

      const validMarkers = markers.filter((m): m is any => m !== null);
      markersRef.current = validMarkers;
      map.add(validMarkers);
      logger.debug('标记创建完成:', validMarkers.length);

      if (validMarkers.length > 0) {
        try {
          map.setFitView(validMarkers, false, [50, 50, 50, 50]);
        } catch (e: any) {
          logger.error('setFitView 失败', e?.message || e);
        }
      }
    } catch (err: any) {
      logger.error('创建标记失败', err?.message || err);
    }
  }, [places, onSelectPlace, isMapReady]);

  // ── Effect 3: 从 places 构建路线缓存（v4 模式下 page.tsx 已预先注入，跳过覆盖） ──
  useEffect(() => {
    if (!places.length) return;
    // 仅当 cache 完全为空时才用旧的 buildRoutes19FromPlaces 兜底（v3 模式）
    const existing = getRoute19Points('R10').length || getRoute19Points('route01').length;
    if (existing > 0) {
      logger.debug('路线缓存已注入（v4 模式），跳过 places 重建');
      return;
    }
    const routePoints = buildRoutes19FromPlaces(places);
    setRoute19PointsCache(routePoints);
    logger.debug('路线缓存构建完成（v3 兜底）:', routePoints.length, '点');
  }, [places]);

  // ── Effect 4: 绘制路线 v7（手绘情感路线 · 设计稿 §2.3 规范） ──────
  // 颜色逻辑：绿（少年）→ 蓝（仕途）→ 珊瑚（黄州）→ 琥珀（元祐）→ 深红（南贬）→ 灰（归途）
  // 贬谪路线加粗加深，水路密点线区分，总览也手绘化
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !(window as any).AMap || !isMapReady) return;

    // 确保缓存已构建
    const cached = getRoute19Points('R10');
    if (!cached.length && places.length) {
      const routePoints = buildRoutes19FromPlaces(places);
      setRoute19PointsCache(routePoints);
    }

    // 清除旧路线
    Object.values(routeOverlaysRef.current).forEach(({ polyline }) => {
      if (polyline) map.remove(polyline);
    });
    routeOverlaysRef.current = {};

    const AMapLocal = (window as any).AMap;
    const allRouteIds = ROUTE19_IDS.filter((id) => id !== 'overview');

    // 路线风格配置：按 stage_id 决定粗细和风格
    // 贬谪路线（S3黄州、S5南贬）加粗加深，情感最重
    const EXILE_ROUTES = new Set(['R10', 'R11', 'R18']);
    const RETURN_ROUTE = 'R19'; // 归途

    function getRouteStyle(routeId: string, isOverview: boolean) {
      const isExile = EXILE_ROUTES.has(routeId);
      const isReturn = routeId === RETURN_ROUTE;

      if (isOverview) {
        return {
          strokeWeight: isExile ? 3.5 : 2,
          strokeOpacity: isExile ? 0.85 : 0.72,
          strokeDasharray: isReturn ? [3, 4] : [7, 5],  // 归途用密点线
          showDir: true,
          handDrawnStyle: isExile ? 'heavy' : 'light' as 'heavy' | 'light',
        };
      } else {
        // 单路线模式
        return {
          strokeWeight: isExile ? 4 : 3,
          strokeOpacity: isExile ? 0.95 : 0.88,
          strokeDasharray: isReturn ? [3, 4] : [9, 6],  // 归途用密点线
          showDir: true,
          handDrawnStyle: isExile ? 'heavy' : 'medium' as 'heavy' | 'medium',
        };
      }
    }

    // ─── 总览模式：手绘化 + 情感粗细 + 方向箭头 ──────────────
    if (currentRoute === 'overview' || currentRoute === null) {
      allRouteIds.forEach((routeId: string) => {
        const config = ROUTE19_CONFIG[routeId];
        if (!config) return;
        const points = getRoute19Points(routeId);
        if (points.length < 2) return;

        const style = getRouteStyle(routeId, true);

        // 手绘化路径
        const pathPoints = points.map((p) => ({ lng: p.lng, lat: p.lat }));
        const path = makeHandDrawnPath(pathPoints, style.handDrawnStyle);

        const polyline = new AMapLocal.Polyline({
          path,
          strokeColor: config.mainColor || '#888',
          strokeOpacity: style.strokeOpacity,
          strokeWeight: style.strokeWeight,
          strokeStyle: 'dashed',
          strokeDasharray: style.strokeDasharray,
          showDir: style.showDir,
          lineJoin: 'round',
          lineCap: 'round',
          zIndex: EXILE_ROUTES.has(routeId) ? 60 : 50,
        });
        polyline.setMap(map);

        routeOverlaysRef.current[routeId] = { polyline };
      });

      const allPolylines = Object.values(routeOverlaysRef.current)
        .map((r: any) => r.polyline)
        .filter(Boolean);
      if (allPolylines.length > 0) {
        map.setFitView(allPolylines, false, [80, 80, 80, 80], 12);
      }
      return;
    }

    // ─── 单路线模式：手绘平滑 + 情感粗细 + 方向箭头 ────────
    const config = ROUTE19_CONFIG[currentRoute as string];
    const points = getRoute19Points(currentRoute as string);
    if (!config) return;
    if (points.length < 2) return;

    const style = getRouteStyle(currentRoute as string, false);

    // 手绘化路径
    const pathPoints = points.map((p) => ({ lng: p.lng, lat: p.lat }));
    const path = makeHandDrawnPath(pathPoints, style.handDrawnStyle);

    const polyline = new AMapLocal.Polyline({
      path,
      strokeColor: config.mainColor || '#BA7517',
      strokeOpacity: style.strokeOpacity,
      strokeWeight: style.strokeWeight,
      strokeStyle: 'dashed',
      strokeDasharray: style.strokeDasharray,
      showDir: style.showDir,
      lineJoin: 'round',
      lineCap: 'round',
      zIndex: 200,
    });
    polyline.setMap(map);
    routeOverlaysRef.current[currentRoute as string] = { polyline };

    map.setFitView([polyline], false, [80, 80, 80, 80], 12);
    logger.debug('单路线绘制完成（手绘情感路线）:', currentRoute, points.length, '→', path.length);
  }, [currentRoute, isMapReady, places]);

  // ── Effect 5: zoom 动态缩放 marker（用 --su-scale 不覆盖 hover/selected） ──
  useEffect(() => {
    if (!mapRef.current || !markersRef.current || !markersRef.current.length) return;
    const map = mapRef.current;

    let scaleRafId = 0;
    function updateMarkerScale() {
      if (scaleRafId) cancelAnimationFrame(scaleRafId);
      scaleRafId = requestAnimationFrame(() => {
        const zoom = map.getZoom();
        const scale = Math.max(0.85, Math.min(1.35, 0.7 + (zoom - 3) * 0.10));
        markersRef.current.forEach((m: any) => {
          const el = m.getContent?.();
          if (el instanceof HTMLElement) {
            el.style.setProperty('--su-zoom-scale', String(scale));
            // 避免覆盖 hover/selected 的 transform，统一用 transform: scale(var)
            // 仅当未处于 hover/selected 时主动赋值，否则交给 CSS 类
            if (
              !el.classList.contains('is-selected') &&
              !el.matches(':hover')
            ) {
              el.style.transform = `scale(${scale})`;
            }
          }
        });
      });
    }
    map.on('zoomchange', updateMarkerScale);
    updateMarkerScale();

    return () => {
      map.off('zoomchange', updateMarkerScale);
      if (scaleRafId) cancelAnimationFrame(scaleRafId);
    };
  }, [isMapReady, places]);

  // ── Effect 6: Stage / Route 过滤标记（带淡入淡出动画） ──────────────
  // 单路线模式：只显示该路线 marker，其他淡出隐藏
  // currentStage 过滤仍生效
  useEffect(() => {
    if (!markersRef.current || !markersRef.current.length) return;
    const map = mapRef.current;
    if (!map) return;

    const isSingleRoute =
      currentRoute && currentRoute !== 'overview' && currentRoute !== null;

    markersRef.current.forEach((m: any) => {
      const place: PlaceCore = m.getExtData();
      const el = m.getContent?.();

      // 阶段过滤
      if (currentStage && place.stage !== currentStage) {
        if (el instanceof HTMLElement) {
          el.style.transition = 'opacity 0.3s ease-out';
          el.style.opacity = '0';
          setTimeout(() => m.setMap(null), 300);
        } else {
          m.setMap(null);
        }
        return;
      }
      // 单路线过滤：非该路线点位 → 淡出隐藏
      if (isSingleRoute) {
        const rels = (place as any).relatedRoutes as string[] | undefined;
        const onRoute =
          (rels && rels.includes(currentRoute as string)) ||
          place.routeId === currentRoute;
        if (!onRoute) {
          if (el instanceof HTMLElement) {
            el.style.transition = 'opacity 0.3s ease-out';
            el.style.opacity = '0';
            setTimeout(() => m.setMap(null), 300);
          } else {
            m.setMap(null);
          }
          return;
        }
      }
      // 显示：先设map再淡入
      m.setMap(map);
      if (el instanceof HTMLElement) {
        el.style.transition = 'opacity 0.3s ease-out';
        el.style.opacity = '0';
        requestAnimationFrame(() => {
          el.style.opacity = '1';
        });
      }
    });
  }, [currentStage, currentRoute, isMapReady]);

  // ── Effect 7: 选中态高亮（取消弱化态联动，单路线已隐藏其他点） ──
  useEffect(() => {
    if (!markersRef.current || !markersRef.current.length) return;
    markersRef.current.forEach((m: any) => {
      const el = m.getContent?.();
      if (!(el instanceof HTMLElement)) return;
      const place: PlaceCore = m.getExtData();
      const isSelected = !!selectedPlace && selectedPlace.id === place.id;
      el.classList.toggle('is-selected', isSelected);
      // 不再加 is-faded（旧的"非当前路线 40%"已改为直接隐藏）
      el.classList.remove('is-faded');
    });
  }, [selectedPlace, currentRoute]);

  return (
    <div
      className="absolute"
      style={{
        top: 0,
        left: 0,
        right: 0,
        bottom: 'calc(var(--bottom-nav-height) + var(--safe-area-bottom))',
      }}
    >
      <div ref={containerRef} className="w-full h-full" />
      {/* 水墨风格覆盖层 */}
      <div className="pointer-events-none absolute inset-0 border-2 border-ink/10 rounded-lg" />
    </div>
  );
}
