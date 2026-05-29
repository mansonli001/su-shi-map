/**
 * AMapContainer v4.0 修正版
 * 修复：聚合器持有/stage过滤/GeoJSON插件
 */

'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore, Stage } from '@/types';
import { makeClusterRender, makeMarkerHtml } from '@/lib/clusterRender';
// 动态导入 AMap JSAPI Loader（next/dynamic 不支持直接加载非React组件）
// 改用 useEffect + 动态 import()
declare global {
  interface Window {
    _AMapSecurityConfig?: { serviceHost?: string };
  }
}

export default function AMapContainer() {
  const { places, selectedPlace, setSelectedPlace } = useSuShiStore();
  const onSelectPlace = setSelectedPlace;
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const clusterRef = useRef<any>(null);
  const geoJsonRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  const { currentStage, setMapRef } = useSuShiStore();

  /**
   * 初始化地图
   */
  const initMap = useCallback(async () => {
    if (!containerRef.current || mapRef.current) return;

    const AMapLoader = (await import('@amap/amap-jsapi-loader')).default;
    const AMap = await AMapLoader.load({
      key: process.env.NEXT_PUBLIC_AMAP_KEY || '',
      version: '2.0',
      plugins: ['AMap.MarkerClusterer', 'AMap.GeoJSON'],
    });

    // 安全代理：高德 JS API 通过 /api/_AMapService 转发
    (window as any)._AMapSecurityConfig = {
      serviceHost: '/api/_AMapService',
    };

    // 创建地图实例
    const map = new AMap.Map(containerRef.current, {
      zoom: 5,
      center: [104.5, 32.0], // 中国中心
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke', // 水墨风格
      zoomControl: true,
      scaleControl: false,
      toolBarControl: false,
    });

    // 保存地图引用
    mapRef.current = map;
    setMapRef(map);

    // 挂载到 window（供 clusterRender 使用）
    (window as any).suShiMapInstance = map;

    // 创建聚合标记
    const markers = places.map((place) => {
      const marker = new AMap.Marker({
        position: [place.lng, place.lat],
        content: makeMarkerHtml(place.type, place.importance),
        anchor: 'bottom-center',
        extData: place,
      });

      marker.on('click', () => {
        onSelectPlace(place);
      });

      return marker;
    });

    markersRef.current = markers;

    // 创建聚合器
    const cluster = new AMap.MarkerClusterer(map, markers, {
      renderClusterMarker: makeClusterRender(),
      gridSize: 60,
      maxZoom: 14,
    });

    clusterRef.current = cluster;
  }, [places, onSelectPlace, setMapRef]);

  // 初始化
  useEffect(() => {
    initMap();

    return () => {
      // ★ v4.0 修复：先移除聚合器，再销毁地图
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
  }, [initMap]);

  /**
   * Stage 过滤：根据时间轴过滤标记
   * ★ v4.0 修复：依赖项改为 [currentStage]，places 通过 markersRef 访问
   */
  useEffect(() => {
    if (!clusterRef.current || !markersRef.current.length) return;

    const filtered = currentStage
      ? markersRef.current.filter((m) => {
          const place: PlaceCore = m.getExtData();
          return place.stage === currentStage;
        })
      : markersRef.current;

    clusterRef.current.setMarkers(filtered);
  }, [currentStage]);

  return (
    <div className="map-fullscreen relative">
      <div ref={containerRef} className="w-full h-full" />
      {/* 水墨风格覆盖层 */}
      <div className="pointer-events-none absolute inset-0 border-2 border-ink/10 rounded-lg" />
    </div>
  );
}
