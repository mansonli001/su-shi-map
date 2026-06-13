/**
 * 贺野游中国 · 地图容器
 * 独立于苏轼 AMapContainer，数据来源为 heye-loader + heye-store
 * 功能：地点标记 + 省份着色 + 选中卡片 + 筛选 + 省份放大
 */
'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useHeyeStore } from '@/lib/heye-store';
import { getHeyeLocations } from '@/lib/heye-loader';
import { loadAMap } from '@/lib/amap-loader';
import { logger } from '@/lib/logger';
import type { HeyeLocation } from '@/types/heye';

// 省份中心坐标和缩放级别
const PROVINCE_VIEW: Record<string, { center: [number, number]; zoom: number }> = {
  '北京': { center: [116.4, 39.9], zoom: 9 },
  '天津': { center: [117.2, 39.1], zoom: 9 },
  '上海': { center: [121.47, 31.23], zoom: 10 },
  '重庆': { center: [106.55, 29.56], zoom: 9 },
  '河北': { center: [114.5, 38.0], zoom: 7 },
  '山西': { center: [112.5, 37.5], zoom: 7 },
  '辽宁': { center: [123.4, 41.8], zoom: 7 },
  '吉林': { center: [126.5, 43.5], zoom: 7 },
  '黑龙江': { center: [126.6, 45.7], zoom: 6 },
  '江苏': { center: [118.8, 32.0], zoom: 7 },
  '浙江': { center: [120.1, 30.2], zoom: 7 },
  '安徽': { center: [117.3, 31.8], zoom: 7 },
  '福建': { center: [119.3, 26.0], zoom: 7 },
  '江西': { center: [115.9, 28.6], zoom: 7 },
  '山东': { center: [117.0, 36.6], zoom: 7 },
  '河南': { center: [113.6, 34.7], zoom: 7 },
  '湖北': { center: [114.3, 30.5], zoom: 7 },
  '湖南': { center: [112.9, 28.2], zoom: 7 },
  '广东': { center: [113.2, 23.1], zoom: 7 },
  '海南': { center: [110.3, 20.0], zoom: 8 },
  '四川': { center: [104.0, 30.5], zoom: 7 },
  '贵州': { center: [106.7, 26.6], zoom: 7 },
  '云南': { center: [102.7, 25.0], zoom: 7 },
  '陕西': { center: [108.9, 34.2], zoom: 7 },
  '甘肃': { center: [103.8, 36.0], zoom: 6 },
  '青海': { center: [101.7, 36.6], zoom: 6 },
  '台湾': { center: [121.0, 23.7], zoom: 8 },
  '内蒙古': { center: [111.7, 40.8], zoom: 5 },
  '广西': { center: [108.3, 22.8], zoom: 7 },
  '西藏': { center: [91.1, 29.6], zoom: 6 },
  '宁夏': { center: [106.2, 38.5], zoom: 8 },
  '新疆': { center: [87.6, 43.8], zoom: 5 },
  '香港': { center: [114.1, 22.3], zoom: 11 },
  '澳门': { center: [113.5, 22.2], zoom: 12 },
};

// 省份名称到高德行政区查询名的映射
const PROVINCE_ADMAP: Record<string, string> = {
  '北京': '北京市', '天津': '天津市', '上海': '上海市', '重庆': '重庆市',
  '河北': '河北省', '山西': '山西省', '辽宁': '辽宁省', '吉林': '吉林省',
  '黑龙江': '黑龙江省', '江苏': '江苏省', '浙江': '浙江省', '安徽': '安徽省',
  '福建': '福建省', '江西': '江西省', '山东': '山东省', '河南': '河南省',
  '湖北': '湖北省', '湖南': '湖南省', '广东': '广东省', '海南': '海南省',
  '四川': '四川省', '贵州': '贵州省', '云南': '云南省', '陕西': '陕西省',
  '甘肃': '甘肃省', '青海': '青海省', '台湾': '台湾省',
  '内蒙古': '内蒙古自治区', '广西': '广西壮族自治区', '西藏': '西藏自治区',
  '宁夏': '宁夏回族自治区', '新疆': '新疆维吾尔自治区',
  '香港': '香港特别行政区', '澳门': '澳门特别行政区',
};

export default function HeyeMapContainer() {
  const { heyeCheckins, addHeyeCheckin } = useHeyeStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const provinceOverlayRef = useRef<any>(null); // 省份边界覆盖物
  const [locations, setLocations] = useState<HeyeLocation[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<HeyeLocation | null>(null);
  const [filterProvince, setFilterProvince] = useState<string | null>(null);
  const [isMapReady, setIsMapReady] = useState(false);

  // 加载数据
  useEffect(() => {
    getHeyeLocations().then(setLocations).catch((err) => {
      logger.error('贺野地点加载失败', err?.message || err);
    });
  }, []);

  // 初始化地图
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    let destroyed = false;

    loadAMap()
      .then((AMap: any) => {
        if (destroyed || mapRef.current || !AMap?.Map) return;
        const map = new AMap.Map(containerRef.current, {
          zoom: 5,
          center: [108, 32],
          viewMode: '2D',
          zoomControl: true,
          scaleControl: false,
          toolBarControl: false,
          mapStyle: 'amap://styles/5bcb375541c22ed25703103920a7d5e8',
          viewPadding: [0, 0, 70, 0],
        });
        mapRef.current = map;
        setIsMapReady(true);
      })
      .catch((err: any) => {
        logger.error('贺野地图初始化失败', err?.message || err);
      });

    return () => {
      destroyed = true;
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
    };
  }, []);

  // 创建标记
  useEffect(() => {
    if (!isMapReady || !mapRef.current || !locations.length) return;
    const AMapLocal = (window as any).AMap;
    const map = mapRef.current;
    if (!AMapLocal?.LngLat) return;

    // 清除旧标记
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    const checkedIds = new Set(heyeCheckins.map((c) => c.placeId));

    const filtered = locations.filter((loc) => !filterProvince || loc.province === filterProvince);

    const markers = filtered.map((loc) => {
      const position = new AMapLocal.LngLat(loc.lng, loc.lat);
      const checkedIn = checkedIds.has(loc.id);

      const wrapper = document.createElement('div');
      wrapper.innerHTML = `
        <div style="
          width: 20px; height: 20px;
          border-radius: 50%;
          background: url('/heye-avatar.png') center/cover no-repeat;
          border: 2px solid ${checkedIn ? '#8C3A18' : '#C4612A'};
          box-shadow: 0 1px 4px rgba(196,97,42,0.35);
          cursor: pointer;
          transform-origin: bottom center;
          transition: transform 0.15s ease;
        " data-place-id="${loc.id}" />
      `;
      const markerEl = wrapper.firstElementChild as HTMLElement;

      const marker = new AMapLocal.Marker({
        position,
        content: markerEl,
        anchor: 'center',
        extData: loc,
      });

      marker.on('click', () => setSelectedLocation(loc));
      return marker;
    });

    markersRef.current = markers;
    map.add(markers);

    // 根据筛选调整视图
    if (filterProvince && PROVINCE_VIEW[filterProvince]) {
      const view = PROVINCE_VIEW[filterProvince];
      map.setZoomAndCenter(view.zoom, view.center, false, 600);
    } else if (markers.length > 0) {
      map.setFitView(markers, false, [50, 50, 50, 50]);
    }
  }, [locations, isMapReady, heyeCheckins, filterProvince]);

  // 省份边界高亮
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isMapReady) return;

    // 清除旧的边界覆盖物
    if (provinceOverlayRef.current) {
      map.remove(provinceOverlayRef.current);
      provinceOverlayRef.current = null;
    }

    if (!filterProvince) return;

    const AMapLocal = (window as any).AMap;
    if (!AMapLocal?.DistrictSearch) return;

    const adName = PROVINCE_ADMAP[filterProvince] || filterProvince;
    const districtSearch = new AMapLocal.DistrictSearch({
      subdistrict: 0,
      extensions: 'all',
      level: 'province',
    });

    districtSearch.search(adName, (status: string, result: any) => {
      if (status === 'complete' && result?.districtList?.[0]) {
        const bounds = result.districtList[0].boundaries;
        if (bounds && bounds.length > 0) {
          const polygons = bounds.map((bound: any) => new AMapLocal.Polygon({
            path: bound,
            strokeColor: '#C4612A',
            strokeWeight: 3,
            strokeOpacity: 0.9,
            fillColor: '#C4612A',
            fillOpacity: 0.12,
            zIndex: 10,
          }));
          map.add(polygons);
          provinceOverlayRef.current = polygons;
        }
      }
    });
  }, [filterProvince, isMapReady]);

  // 打卡
  const handleCheckin = useCallback(() => {
    if (!selectedLocation) return;
    addHeyeCheckin({
      placeId: selectedLocation.id,
      placeName: selectedLocation.placeName,
      checkinAt: new Date().toISOString(),
      checkinType: 'cloud',
    });
  }, [selectedLocation, addHeyeCheckin]);

  // 省份筛选（点击放大）
  const handleProvinceClick = useCallback((province: string | null) => {
    setFilterProvince(province);
    setSelectedLocation(null);
  }, []);

  // 返回全国视图
  const handleResetView = useCallback(() => {
    setFilterProvince(null);
    setSelectedLocation(null);
    if (mapRef.current) {
      // 清除省份边界覆盖物
      if (provinceOverlayRef.current) {
        mapRef.current.remove(provinceOverlayRef.current);
        provinceOverlayRef.current = null;
      }
      mapRef.current.setZoomAndCenter(5, [108, 32], false, 600);
    }
  }, []);

  // 省份筛选
  const provinces = [...new Set(locations.map((l) => l.province))].sort();
  const filteredCount = filterProvince
    ? locations.filter((l) => l.province === filterProvince).length
    : locations.length;

  return (
    <div className="he-map-root">
      {/* 顶栏 */}
      <div className="he-map-topbar">
        <div className="he-map-topbar-title">
          {filterProvince ? `${filterProvince} · 足迹地图` : '贺野 · 足迹地图'}
        </div>
        <div className="he-map-topbar-stats">
          {filterProvince ? (
            <button className="he-map-back-btn" onClick={handleResetView}>
              ← 返回全国 ({filteredCount} 地点)
            </button>
          ) : (
            `${locations.length} 地点 · ${provinces.length} 省`
          )}
        </div>
      </div>

      {/* 筛选栏 */}
      <div className="he-map-filter">
        <button
          className={`he-filter-btn ${!filterProvince ? 'active' : ''}`}
          onClick={() => handleProvinceClick(null)}
        >
          全部
        </button>
        {provinces.map((p) => (
          <button
            key={p}
            className={`he-filter-btn ${filterProvince === p ? 'active' : ''}`}
            onClick={() => handleProvinceClick(filterProvince === p ? null : p)}
          >
            {p}
          </button>
        ))}
      </div>

      {/* 地图 */}
      <div
        className="he-map-container"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 'calc(var(--bottom-nav-height) + var(--safe-area-bottom))',
        }}
      >
        <div ref={containerRef} className="w-full h-full" />
      </div>

      {/* 地点卡片 */}
      {selectedLocation && (
        <div className="he-map-card">
          <button
            className="he-map-card-close"
            onClick={() => setSelectedLocation(null)}
          >
            ✕
          </button>
          <div className="he-map-card-province">{selectedLocation.city} · {selectedLocation.province}</div>
          <div className="he-map-card-name">{selectedLocation.placeName}</div>
          {selectedLocation.visitCount > 1 && (
            <div className="he-map-card-visit-count">
              到访 {selectedLocation.visitCount} 次
            </div>
          )}
          {selectedLocation.visitHistory && (
            <div className="he-map-card-visit-history">{selectedLocation.visitHistory}</div>
          )}
          {selectedLocation.visitDate && selectedLocation.visitCount <= 1 && (
            <div className="he-map-card-date">{selectedLocation.visitDate}</div>
          )}
          <div className="he-map-card-excerpt">{selectedLocation.excerpt}</div>
          {selectedLocation.snacks.length > 0 && (
            <div className="he-map-card-snacks">
              {selectedLocation.snacks.map((s) => (
                <span key={s} className="he-snack-tag">{s}</span>
              ))}
            </div>
          )}
          <div className="he-map-card-actions">
            {heyeCheckins.some((c) => c.placeId === selectedLocation.id) ? (
              <span className="he-checkin-done">已打卡</span>
            ) : (
              <button className="he-checkin-btn" onClick={handleCheckin}>
                打卡
              </button>
            )}
            {selectedLocation.articleUrl && (
              <a
                href={selectedLocation.articleUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="he-article-link"
              >
                读原文 →
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
