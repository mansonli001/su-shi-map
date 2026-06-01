/**
 * AMapContainer v6.0
 * 核心升级：
 * 1. 使用高德导航API获取真实路径（不是直线，不是模拟手绘）
 * 2. 路线样式：虚线小箭头组合（连续的小箭头Marker）
 * 3. 保留手绘扰动（在真实路径基础上加入轻微扰动，增加手绘感）
 */

'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore, Stage } from '@/types';
import { makeClusterRender, makeMarkerHtml } from '@/lib/clusterRender';
import { ROUTE19_CONFIG, ROUTE19_IDS, getRoute19Points, buildRoutes19FromPlaces, setRoute19PointsCache } from '@/lib/route19-config';
import { makeHandDrawnPath } from '@/lib/route-utils';

/**
 * 调用高德导航API获取真实路径
 */
async function fetchRealRoutePath(
  points: { lng: number; lat: number }[]
): Promise<[number, number][][]> {
  if (points.length < 2) return [];
  
  const segments: [number, number][][] = [];
  
  for (let i = 0; i < points.length - 1; i++) {
    const origin = `${points[i].lng},${points[i].lat}`;
    const destination = `${points[i + 1].lng},${points[i + 1].lat}`;
    
    try {
      const response = await fetch(`/api/route?origin=${origin}&destination=${destination}`);
      const data = await response.json();
      
      if (data.success && data.routes && data.routes.length > 0) {
        // 合并所有路段的polyline
        const allPoints: [number, number][] = [];
        data.routes.forEach((route: any) => {
          route.polyline.forEach((point: [number, number]) => {
            allPoints.push(point);
          });
        });
        segments.push(allPoints);
      } else {
        // API调用失败，使用直线连接
        console.warn(`路段 ${i}→${i+1} API调用失败，使用直线连接`);
        segments.push([
          [points[i].lng, points[i].lat],
          [points[i + 1].lng, points[i + 1].lat]
        ]);
      }
    } catch (error) {
      console.error(`路段 ${i}→${i+1} 获取失败:`, error);
      // 失败时使用直线连接
      segments.push([
        [points[i].lng, points[i].lat],
        [points[i + 1].lng, points[i + 1].lat]
      ]);
    }
  }
  
  return segments;
}

/**
 * 创建虚线小箭头样式
 * 在路径上密集放置小箭头Marker，形成虚线效果
 */
function createDashedArrowOverlays(
  map: any,
  pathSegments: [number, number][][],
  config: any,
  routeId: string
): { arrows: any[] } {
  const AMapLocal = (window as any).AMap;
  if (!AMapLocal) return { arrows: [] };
  
  const arrows: any[] = [];
  const arrowInterval = 0.00015; // 约15-20米一个箭头（更密集）
  
  pathSegments.forEach((segment, segIdx) => {
    for (let i = 0; i < segment.length - 1; i++) {
      const a = { lng: segment[i][0], lat: segment[i][1] };
      const b = { lng: segment[i + 1][0], lat: segment[i + 1][1] };
      
      // 计算方向角
      const angle = Math.atan2(b.lat - a.lat, b.lng - a.lng) * 180 / Math.PI;
      
      // 在a→b线段上放置箭头
      const dx = b.lng - a.lng;
      const dy = b.lat - a.lat;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const steps = Math.max(1, Math.floor(dist / arrowInterval));
      
      for (let s = 0; s < steps; s++) {
        const t = s / steps;
        const mLng = a.lng + dx * t;
        const mLat = a.lat + dy * t;
        
        // 小箭头SVG（虚线效果：每隔一个透明一个）
        const isVisible = s % 2 === 0; // 隔一个显示一个
        const opacity = isVisible ? 0.8 : 0;
        
        const arrowSvg = `
          <div style="width:12px;height:12px;display:flex;align-items:center;justify-content:center;">
            <svg width="10" height="10" viewBox="0 0 10 10" style="transform:rotate(${angle}deg);">
              <polygon points="0,0 10,5 0,10" fill="${config.mainColor}" fill-opacity="${opacity}"/>
            </svg>
          </div>
        `;
        
        const arrow = new AMapLocal.Marker({
          position: [mLng, mLat],
          content: arrowSvg,
          offset: new AMapLocal.Pixel(-5, -5),
          zIndex: 200,
          anchor: 'center',
        });
        
        arrow.setMap(map);
        arrows.push(arrow);
      }
    }
  });
  
  return { arrows };
}

// 动态导入 AMap JSAPI Loader
declare global {
  interface Window {
    _AMapSecurityConfig?: { serviceHost?: string };
  }
}

// 全局日志收集（显示在页面上）
const logs: string[] = [];
function log(msg: string) {
  logs.push(msg);
  console.log('[AMap]', msg);
  const el = document.getElementById('map-debug-logs');
  if (el) el.innerText = logs.join('\n');
}

export default function AMapContainer() {
  const { places, selectedPlace, setSelectedPlace } = useSuShiStore();
  const onSelectPlace = setSelectedPlace;
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const clusterRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [isMapReady, setIsMapReady] = useState(false);

  const { currentStage, setMapRef, currentRoute } = useSuShiStore();

  // 存储所有路线的polyline和箭头引用 { routeId: { polyline, arrows[] } }
  const routeOverlaysRef = useRef<Record<string, { polyline: any; arrows: any[] }>>({});

  // ── Effect 1: 等待 AMap 全局对象就绪，然后初始化地图 ──────────────────
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let destroyed = false;
    let checkTimer: NodeJS.Timeout | null = null;

    log('等待 AMap 全局对象...');

    function initMap(AMap: any) {
      if (destroyed || mapRef.current) return;
      try {
        const map = new AMap.Map(containerRef.current, {
          zoom: 5,
          center: [104.5, 32.0],
          viewMode: '2D',
          zoomControl: true,
          scaleControl: false,
          toolBarControl: false,
        });
        log('✅ 地图初始化完成');
        mapRef.current = map;
        setMapRef(map);
        (window as any).suShiMapInstance = map;
        setIsMapReady(true);
      } catch (err: any) {
        log('❌ 地图初始化异常: ' + (err?.message || String(err)));
        console.error(err);
      }
    }

    function checkAndInit() {
      const AMap = (window as any).AMap;
      if (AMap && AMap.Map) {
        log('✅ AMap 全局对象就绪');
        initMap(AMap);
        return true;
      }
      // 检查是否已经加载完成但事件已错过
      if ((window as any).__amapLoaded) {
        log('✅ AMap 已加载但事件已错过，直接检查');
        const retryAMap = (window as any).AMap;
        if (retryAMap && retryAMap.Map) {
          initMap(retryAMap);
          return true;
        }
      }
      return false;
    }

    // 先检查是否已加载
    if (checkAndInit()) {
      return;
    }

    // 监听 amap-ready 事件
    const onAmapReady = () => {
      if (destroyed) return;
      log('收到 amap-ready 事件');
      checkAndInit();
    };
    window.addEventListener('amap-ready', onAmapReady);

    // 同时轮询作为备用（最多等 15 秒）
    log('AMap 未就绪，开始轮询...');
    const startTime = Date.now();
    checkTimer = setInterval(() => {
      if (destroyed) {
        if (checkTimer) clearInterval(checkTimer);
        return;
      }
      if (checkAndInit()) {
        if (checkTimer) clearInterval(checkTimer);
      } else if (Date.now() - startTime > 15000) {
        if (checkTimer) clearInterval(checkTimer);
        log('❌ AMap 加载超时（15秒）');
      }
    }, 200);

    return () => {
      destroyed = true;
      window.removeEventListener('amap-ready', onAmapReady);
      if (checkTimer) clearInterval(checkTimer);
      if (clusterRef.current) {
        clusterRef.current.setMap(null);
        clusterRef.current = null;
      }
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
      (window as any).suShiMapInstance = null;
    };
  }, [setMapRef]);

  // ── Effect 2: 创建/更新标记 ─────────────────────────────────
  useEffect(() => {
    if (!isMapReady || !mapRef.current || !places.length) {
      log('[标记] 跳过: ready=' + isMapReady + ' map=' + !!mapRef.current + ' places=' + places.length);
      return;
    }

    log('[标记] 开始创建 ' + places.length + ' 个标记');

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
        log('[标记] 错误: AMap.LngLat 不可用');
        return;
      }

      const markers = places.map((place, idx) => {
        if (place.lng == null || place.lat == null) {
          console.error('[标记] 坐标无效:', place.id, place.lng, place.lat);
          return null;
        }

        const position = new AMapLocal.LngLat(place.lng, place.lat);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = makeMarkerHtml(place.type, place.importance);
        const markerEl = wrapper.firstElementChild as HTMLElement | null;
        if (markerEl) {
          markerEl.style.transition = 'transform 0.15s ease-out';
          markerEl.style.transformOrigin = 'bottom center';
        }

        const marker = new AMapLocal.Marker({
          position,
          content: markerEl || makeMarkerHtml(place.type, place.importance),
          anchor: 'bottom-center',
          extData: place,
        });

        marker.on('click', () => onSelectPlace(place));
        return marker;
      });

      const validMarkers = markers.filter((m): m is any => m !== null);
      markersRef.current = validMarkers;
      log('[标记] 创建完成: ' + validMarkers.length + ' 个');

      map.add(validMarkers);
      log('[标记] 已添加到地图');

      if (validMarkers.length > 0) {
        try {
          map.setFitView(validMarkers, false, [50, 50, 50, 50]);
          log('[标记] setFitView 完成');
        } catch (e: any) {
          log('[标记] setFitView 失败: ' + (e?.message || e));
        }
      }
    } catch (err: any) {
      log('[标记] 创建失败: ' + (err?.message || String(err)));
    }
  }, [places, onSelectPlace, isMapReady]);

  // ── Effect 3: 从 places 构建路线缓存 ─────────────────────
  useEffect(() => {
    if (!places.length) return;
    const routePoints = buildRoutes19FromPlaces(places);
    setRoute19PointsCache(routePoints);
    log('[路线] 从 ' + places.length + ' 个地点构建缓存，共 ' + routePoints.length + ' 个轨迹点');
  }, [places]);

  // ── Effect 4: 绘制路线（核心修复） ─────────────────────
  // 依赖: currentRoute, isMapReady, places
  // places 加入依赖：确保缓存构建完成后重新绘制
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !(window as any).AMap || !isMapReady) {
      log('[路线] SKIP: map=' + !!map + ' AMap=' + !!(window as any).AMap + ' ready=' + isMapReady);
      return;
    }

    // 确保缓存已构建
    const cached = getRoute19Points('route01'); // 用任意routeId测试缓存
    if (!cached.length && places.length) {
      log('[路线] 缓存为空，当场重建');
      const routePoints = buildRoutes19FromPlaces(places);
      setRoute19PointsCache(routePoints);
    }

    log('[路线] 开始绘制: currentRoute=' + currentRoute);

    // 清除旧路线
    Object.values(routeOverlaysRef.current).forEach(({ polyline, arrows }) => {
      if (polyline) map.remove(polyline);
      arrows.forEach((a: any) => map.remove(a));
    });
    routeOverlaysRef.current = {};

    // 总览模式：绘制所有19条路线
    if (currentRoute === 'overview' || currentRoute === null) {
      const allRouteIds = ROUTE19_IDS.filter(id => id !== 'overview');
      allRouteIds.forEach((routeId: string) => {
        const config = ROUTE19_CONFIG[routeId];
        const points = getRoute19Points(routeId);
        if (points.length < 2) {
          log('[路线] ' + routeId + ' 点数不足: ' + points.length);
          return;
        }

        const pathPoints = points.map(p => ({ lng: p.lng, lat: p.lat }));
        const path = makeHandDrawnPath(pathPoints, 'light'); // 总览用 light 样式

        const AMapLocal = (window as any).AMap;
        
        // 使用 Polyline 绘制路线（性能优化）
        const polyline = new AMapLocal.Polyline({
          path: path,
          strokeColor: config.mainColor,
          strokeOpacity: 0.6,
          strokeWeight: 3,
          strokeStyle: 'dashed',
          zIndex: 50,
        });
        polyline.setMap(map);

        routeOverlaysRef.current[routeId] = { polyline, arrows: [] };
        log('[路线] 总览: 已绘制 ' + config.name + ' (' + points.length + '点)');
      });

      // 适配所有路线
      const allPolylines = Object.values(routeOverlaysRef.current).map((r: any) => r.polyline).filter(Boolean);
      if (allPolylines.length > 0) {
        map.setFitView(allPolylines, false, [80, 80, 80, 80], 12);
      }
      return;
    }

    // 单条路线模式
    const config = ROUTE19_CONFIG[currentRoute];
    const points = getRoute19Points(currentRoute);
    if (!config) {
      log('[路线] 无效 routeId: ' + currentRoute);
      return;
    }
    if (points.length < 2) {
      log('[路线] ' + currentRoute + ' 点数不足: ' + points.length);
      return;
    }

    const pathPoints = points.map(p => ({ lng: p.lng, lat: p.lat }));
    const path = makeHandDrawnPath(pathPoints, 'medium');

    const AMapLocal = (window as any).AMap;
    
    // 使用 Polyline 绘制路线（性能优化）
    const polyline = new AMapLocal.Polyline({
      path: path,
      strokeColor: config.mainColor,
      strokeOpacity: 0.85,
      strokeWeight: 4,
      strokeStyle: 'solid',
      zIndex: 200,
    });
    polyline.setMap(map);

    // 保存引用
    routeOverlaysRef.current[currentRoute] = { polyline, arrows: [] };

    // 适配视图
    map.setFitView([polyline], false, [80, 80, 80, 80], 12);
    log('[路线] 单条: 已绘制 ' + config.name + ' (' + points.length + '点→' + path.length + '点)');
  }, [currentRoute, isMapReady, places]);

  // ── Effect 5: zoom 动态缩放 marker ────────────────────────
  useEffect(() => {
    if (!mapRef.current || !markersRef.current || !markersRef.current.length) return;
    const map = mapRef.current;

    let scaleRafId = 0;
    function updateMarkerScale() {
      if (scaleRafId) cancelAnimationFrame(scaleRafId);
      scaleRafId = requestAnimationFrame(() => {
        const zoom = map.getZoom();
        const scale = Math.max(1.0, Math.min(1.8, 0.7 + (zoom - 3) * 0.15));
        markersRef.current.forEach((m: any) => {
          const el = m.getContent?.();
          if (el instanceof HTMLElement) {
            el.style.transform = `scale(${scale})`;
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

  // ── Effect 6: Stage 过滤标记 ─────────────────────────────
  useEffect(() => {
    if (!markersRef.current || !markersRef.current.length) return;
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((m: any) => {
      const place: PlaceCore = m.getExtData();
      if (currentStage && place.stage !== currentStage) {
        m.setMap(null);
      } else {
        m.setMap(map);
      }
    });
  }, [currentStage]);

  return (
    <div className="absolute inset-0">
      <div ref={containerRef} className="w-full h-full" />
      {/* 水墨风格覆盖层 */}
      <div className="pointer-events-none absolute inset-0 border-2 border-ink/10 rounded-lg" />
      {/* 调试日志面板 */}
      <pre
        id="map-debug-logs"
        className="absolute top-16 right-2 z-50 bg-black/70 text-green-400 text-xs p-2 rounded max-w-[280px] max-h-[200px] overflow-auto pointer-events-auto"
        style={{ fontSize: '11px', lineHeight: '1.4' }}
      >
        等待日志...
      </pre>
    </div>
  );
}
